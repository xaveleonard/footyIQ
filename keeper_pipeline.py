import time
import json
import html
import logging
from pathlib import Path

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =====================
# CONFIGURATION
# =====================

LEAGUE_ID = 619526
USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"

BASE_URL = "https://keeperfantasy.com"

# where raw data will be stored
DATA_DIR = Path("data/raw/2026")

# max rounds to attempt (safe upper bound)
MAX_ROUNDS = 25
MATCHUPS_PER_ROUND = 8

logging.basicConfig(level=logging.INFO)


# =====================
# DRIVER SETUP
# =====================

def create_driver():
    """
    Creates a Selenium Chrome driver.
    Headless mode can be enabled later if desired.
    """
    options = Options()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # enable once stable

    return webdriver.Chrome(options=options)


# =====================
# LOGIN
# =====================

def login(driver):
    """
    Logs into keeper fantasy using credentials.
    Uses a simple wait rather than fragile URL checks.
    """
    driver.get(f"{BASE_URL}/login")

    wait = WebDriverWait(driver, 15)

    email_input = wait.until(
        EC.presence_of_element_located((By.NAME, "_username"))
    )
    password_input = driver.find_element(By.NAME, "_password")

    email_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # allow login to complete (JS-based)
    time.sleep(5)

    logging.info("Login attempt complete")


# =====================
# EXISTING DATA CHECK
# =====================

def get_existing_rounds():
    """
    Reads existing parquet file (if present) and returns
    a set of rounds that have already been scraped.

    This enables incremental scraping.
    """
    path = DATA_DIR / "teams.parquet"

    if not path.exists():
        return set()

    df = pd.read_parquet(path)
    return set(df["round"].unique())


# =====================
# JSON EXTRACTION
# =====================

def extract_matchup_json(driver):
    """
    Extracts the React JSON payload from the matchup page.

    The data is embedded in a div attribute and must be:
    - HTML unescaped
    - JSON parsed

    Returns full JSON object.
    """
    wait = WebDriverWait(driver, 15)

    # wait for React component container
    wait.until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "div[data-symfony--ux-react--react-component-value='Matchup']"
        ))
    )

    # give React time to hydrate fully
    time.sleep(3)

    divs = driver.find_elements(
        By.CSS_SELECTOR,
        "div[data-symfony--ux-react--react-component-value='Matchup']"
    )

    for div in divs:
        raw = div.get_attribute("data-symfony--ux-react--react-props-value")

        if not raw:
            continue

        try:
            cleaned = html.unescape(raw)
            data = json.loads(cleaned)

            if "staticData" in data:
                return data

        except Exception:
            continue

    raise Exception("No valid JSON found")


# =====================
# PARSING FUNCTIONS
# =====================

def parse_teams(data, round_number, matchup_number):
    """
    Extracts team-level stats from JSON into a dataframe.
    """
    rows = []

    static = data.get("staticData", {})

    for side in ["team1", "team2"]:
        team = static.get(side, {})
        stats = team.get("stats", {})
        meta = team.get("teamSeason", {})

        rows.append({
            "round": round_number,
            "matchup": matchup_number,
            "team_id": meta.get("id"),
            "team_name": meta.get("seasonName"),

            "score": stats.get("score"),
            "kicks": stats.get("kicks"),
            "handballs": stats.get("handballs"),
            "marks": stats.get("marks"),
            "hitouts": stats.get("hitouts"),
            "tackles": stats.get("tackles"),
            "cp": stats.get("contestedPossessions"),
            "clearances": stats.get("clearances"),
            "r50": stats.get("rebound50s"),
            "spoils": stats.get("spoils"),
        })

    return pd.DataFrame(rows)


def parse_players(data, round_number, matchup_number):
    """
    Extracts player-level stats from JSON into a dataframe.
    """
    rows = []

    static = data.get("staticData", {})

    for p in static.get("playerStats", []):
        goals = p.get("goals", 0)
        behinds = p.get("behinds", 0)

        rows.append({
            "round": round_number,
            "matchup": matchup_number,
            "player_id": p.get("player_id"),

            "goals": goals,
            "behinds": behinds,
            "score": goals * 6 + behinds,

            "kicks": p.get("kicks"),
            "handballs": p.get("handballs"),
            "marks": p.get("marks"),
            "hitouts": p.get("hitouts"),
            "tackles": p.get("tackles"),
            "cp": p.get("contestedPossessions"),
            "clearances": p.get("clearances"),
            "r50": p.get("rebound50s"),
            "spoils": p.get("spoils"),
        })

    return pd.DataFrame(rows)


# =====================
# ROUND STATE CHECK
# =====================

def is_unplayed_round(data):
    """
    Determines whether a round has not yet been played.

    If no player stats exist, we assume the matchup is still in preview mode.
    """
    static = data.get("staticData", {})
    return len(static.get("playerStats", [])) == 0


# =====================
# SCRAPE SINGLE MATCHUP
# =====================

def scrape_matchup(driver, round_number, matchup_number):
    """
    Navigates to a matchup page and extracts team + player data.

    Returns:
        (team_df, player_df) OR (None, None) if round not started
    """
    url = f"{BASE_URL}/afl/{LEAGUE_ID}/matchup?round={round_number}&m={matchup_number}"

    logging.info(f"Scraping Round {round_number}, Matchup {matchup_number}")
    driver.get(url)

    try:
        data = extract_matchup_json(driver)
    except Exception:
        # happens when future round → preview page
        logging.info(f"Round {round_number} not started (preview mode)")
        return None, None

    if is_unplayed_round(data):
        return None, None

    team_df = parse_teams(data, round_number, matchup_number)
    player_df = parse_players(data, round_number, matchup_number)

    return team_df, player_df


# =====================
# SAVE (INCREMENTAL)
# =====================

def save(team_dfs, player_dfs):
    """
    Appends new data to existing parquet files.

    Prevents duplicates and ensures idempotent runs.
    """
    team_path = DATA_DIR / "teams.parquet"
    player_path = DATA_DIR / "players.parquet"

    if team_dfs:
        new_teams = pd.concat(team_dfs)

        if team_path.exists():
            existing = pd.read_parquet(team_path)
            combined = pd.concat([existing, new_teams]).drop_duplicates()
        else:
            combined = new_teams

        combined.to_parquet(team_path, index=False)

    if player_dfs:
        new_players = pd.concat(player_dfs)

        if player_path.exists():
            existing = pd.read_parquet(player_path)
            combined = pd.concat([existing, new_players]).drop_duplicates()
        else:
            combined = new_players

        combined.to_parquet(player_path, index=False)

    logging.info("Saved incremental data successfully")


# =====================
# MAIN PIPELINE
# =====================

def run():
    """
    Main execution loop:
    - logs in
    - skips already scraped rounds
    - scrapes new rounds only
    - stops automatically at future rounds
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    existing_rounds = get_existing_rounds()
    logging.info(f"Existing rounds: {sorted(existing_rounds)}")

    driver = create_driver()

    try:
        login(driver)

        all_teams = []
        all_players = []

        for rnd in range(1, MAX_ROUNDS + 1):

            # skip rounds already scraped
            if rnd in existing_rounds:
                logging.info(f"Skipping round {rnd} (already scraped)")
                continue

            logging.info(f"=== ROUND {rnd} ===")

            for m in range(1, MATCHUPS_PER_ROUND + 1):

                try:
                    team_df, player_df = scrape_matchup(driver, rnd, m)

                    # stop when future round reached
                    if team_df is None:
                        logging.info(f"Stopping at round {rnd} (not started)")
                        return save(all_teams, all_players)

                    all_teams.append(team_df)
                    all_players.append(player_df)

                except Exception as e:
                    logging.warning(f"Failed matchup r{rnd} m{m}: {e}")

        save(all_teams, all_players)

    finally:
        driver.quit()


# =====================
# ENTRY POINT
# =====================

if __name__ == "__main__":
    run()
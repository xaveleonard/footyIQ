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

from pipeline.config import LEAGUE_ID, USERNAME, PASSWORD


# =====================
# CONFIGURATION
# =====================

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

def save(team_dfs, player_dfs, target_rounds=None):
    """
    Saves newly scraped data into the parquet files.

    If `target_rounds` is given, any existing rows for those rounds are
    dropped before the new data is written in - this makes re-scraping a
    round (to fix bad data, or backfill one explicitly) replace it cleanly
    instead of piling up alongside the old rows, which plain
    concat + drop_duplicates can't do since it only removes exact-match
    duplicate rows. For a normal incremental run, `target_rounds` is just
    the newly scraped rounds, which can't already be in `existing`, so
    this is a no-op filter there.
    """
    team_path = DATA_DIR / "teams.parquet"
    player_path = DATA_DIR / "players.parquet"

    if team_dfs:
        new_teams = pd.concat(team_dfs)

        if team_path.exists():
            existing = pd.read_parquet(team_path)
            if target_rounds is not None:
                existing = existing[~existing["round"].isin(target_rounds)]
            combined = pd.concat([existing, new_teams]).drop_duplicates()
        else:
            combined = new_teams

        combined.to_parquet(team_path, index=False)

    if player_dfs:
        new_players = pd.concat(player_dfs)

        if player_path.exists():
            existing = pd.read_parquet(player_path)
            if target_rounds is not None:
                existing = existing[~existing["round"].isin(target_rounds)]
            combined = pd.concat([existing, new_players]).drop_duplicates()
        else:
            combined = new_players

        combined.to_parquet(player_path, index=False)

    logging.info("Saved data successfully")


# =====================
# MAIN PIPELINE
# =====================

def run(rounds=None):
    """
    Main execution loop.

    - rounds=None (default): incremental mode. Skips rounds already in the
      parquet files, scrapes forward, and stops automatically at the first
      round that hasn't been played yet.
    - rounds=[14, 15, 16]: explicit mode. Scrapes exactly those rounds,
      regardless of what's already saved, replacing any existing data for
      them. Useful for backfilling specific rounds or re-scraping one that
      had bad/incomplete data. If one of the requested rounds turns out to
      not be played yet, it's skipped (logged) rather than aborting the
      rest of the batch.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    existing_rounds = get_existing_rounds()
    logging.info(f"Existing rounds: {sorted(existing_rounds)}")

    explicit_mode = rounds is not None
    candidate_rounds = rounds if explicit_mode else range(1, MAX_ROUNDS + 1)

    driver = create_driver()

    try:
        login(driver)

        all_teams = []
        all_players = []
        scraped_rounds = []

        for rnd in candidate_rounds:

            # in incremental mode, skip rounds already scraped;
            # in explicit mode, always (re-)attempt the requested rounds
            if not explicit_mode and rnd in existing_rounds:
                logging.info(f"Skipping round {rnd} (already scraped)")
                continue

            logging.info(f"=== ROUND {rnd} ===")

            round_teams = []
            round_players = []
            round_unplayed = False

            for m in range(1, MATCHUPS_PER_ROUND + 1):

                try:
                    team_df, player_df = scrape_matchup(driver, rnd, m)

                    if team_df is None:
                        round_unplayed = True
                        break

                    round_teams.append(team_df)
                    round_players.append(player_df)

                except Exception as e:
                    logging.warning(f"Failed matchup r{rnd} m{m}: {e}")

            if round_unplayed:
                logging.info(f"Round {rnd} not started - skipping")
                if not explicit_mode:
                    # incremental mode stops entirely at the first unplayed round
                    break
                continue

            all_teams.extend(round_teams)
            all_players.extend(round_players)
            scraped_rounds.append(rnd)

        save(all_teams, all_players, target_rounds=scraped_rounds)

    finally:
        driver.quit()


# =====================
# ENTRY POINT
# =====================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Scrape footyIQ round data.")
    parser.add_argument(
        "--rounds",
        type=int,
        nargs="+",
        default=None,
        metavar="N",
        help=(
            "Specific round number(s) to scrape, e.g. --rounds 14 15 16. "
            "Replaces any existing data for these rounds. If omitted, scrapes "
            "incrementally from the last saved round until the first unplayed round."
        ),
    )
    args = parser.parse_args()

    run(rounds=args.rounds)

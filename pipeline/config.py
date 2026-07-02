import os

from dotenv import load_dotenv

load_dotenv()

LEAGUE_ID = int(os.environ["LEAGUE_ID"])
USERNAME = os.environ["KEEPER_USERNAME"]
PASSWORD = os.environ["KEEPER_PASSWORD"]

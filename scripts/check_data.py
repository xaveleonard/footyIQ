import pandas as pd

teams = pd.read_parquet("data/raw/2026/teams.parquet")
players = pd.read_parquet("data/raw/2026/players.parquet")

print("Teams shape:", teams.shape)
print("Players shape:", players.shape)

print("\nRounds:", teams["round"].unique())
print("Teams:", teams["team_name"].nunique())

print("\nTeam stats summary:")
print(teams.describe())

print("\nMissing values (teams):")
print(teams.isnull().sum())

print("\nSample teams:")
print(teams.head())

print("\nSample players:")
print(players.head())
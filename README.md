# footyIQ

Fantasy league analytics and visualization platform built with Python and Streamlit.

## Features

- Power rankings
- Category leaderboards
- Head-to-head matchup analysis
- Recent form tracking
- Volatility / consistency metrics
- Interactive Streamlit dashboard

## Tech Stack

- Python
- Pandas
- Streamlit
- Parquet data storage

## Project Structure

analysis/
- analytics engine
- rankings engine
- matchup engine

visualization/
- Streamlit application

data/
- raw parquet datasets

## Run Locally

Activate virtual environment:

source venv/bin/activate

Run Streamlit app:

streamlit run visualization/app.py
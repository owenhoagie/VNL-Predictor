

# VNL Predictor: Developer Documentation

**Live Demo:** [https://vnl-predictor.vercel.app](https://vnl-predictor.vercel.app)

**A full-stack, automated pipeline for scraping, processing, modeling, and visualizing Volleyball Nations League (VNL) player and match data.**

---

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Data Pipeline](#data-pipeline)
   - [1. Web Scraping](#1-web-scraping)
   - [2. Data Merging](#2-data-merging)
   - [3. Player Rating System](#3-player-rating-system)
   - [4. Machine Learning Pipeline](#4-machine-learning-pipeline)
- [Frontend (vnl-visualizer)](#frontend-vnl-visualizer)
- [File/Folder Structure](#filefolder-structure)
- [Setup & Usage](#setup--usage)
- [Development Notes](#development-notes)
- [Tech Stack](#tech-stack)

---

## Project Overview
VNL Predictor is a modular, production-grade system for:
- **Scraping** official VNL stats (players, teams, matches) from dynamic web pages
- **Merging and cleaning** raw data into unified CSVs
- **Rating** players by position using custom formulas
- **Training machine learning models** to predict match outcomes and set scores
- **Serving a modern React web app** for interactive exploration and visualization

This project demonstrates advanced skills in data engineering, automation, ML, and frontend development. It is designed for extensibility, reproducibility, and clarity for future contributors.

---

## Architecture

```
Web (Selenium) Scrapers
    │
    ▼
Raw CSVs (Dataset/)
    │
    ▼
Data Merge & Player Ratings (Collection/, RatingSystem/)
    │
    ▼
Merged Stats (merged_stats.csv)
    │
    ▼
ML Pipeline (ML/)
    │
    ▼
Trained Models (.pkl)
    │
    ▼
Frontend (vnl-visualizer/)
```

---

## Data Pipeline

### 1. Web Scraping
**Scripts:**
- `Collection/webscraper.py`: Scrapes per-player stats (attacking, blocking, serving, etc.) from VNL website using Selenium. Configurable via `Collection/config.py`.
- `Collection/personalscraper.py`: Scrapes player profile details (position, age, height) for all players.
- `ML/matchdata.py`: Scrapes match-level data (set scores, teams, winner/loser, per-match stats) for all matches in a season.
- `ML/teamdata.py`: Scrapes team-level season stats from the standings page.

**Output:**
- Individual CSVs in `Dataset/` and `ML/` (e.g., `attacking_stats.csv`, `player_profiles.csv`, `match_set_stats.csv`, `team_stats.csv`)

### 2. Data Merging
**Scripts:**
- `Collection/merge.py`: Merges all per-player stat CSVs into a single `merged_stats.csv` (outer join on Player Name, Team).
- `RatingSystem/mergeratings.py`: Merges player ratings into `merged_stats.csv` as new columns (Impact, Attacking Rating, etc.).

### 3. Player Rating System
**Script:**
- `RatingSystem/playerrankings.py`: Calculates advanced, position-weighted player ratings using custom formulas for each skill (attacking, blocking, serving, etc.), normalizes by position, and outputs `player_rankings.csv`.

### 4. Machine Learning Pipeline
**Script:**
- `ML/ml.py`:
   - Loads merged player, team, and match stats
   - Aggregates features for each match (player impact, team stats, stat differences)
   - Trains a logistic regression model to predict match winners
   - Trains a multinomial logistic regression model to predict set scores
   - Saves trained models as `.pkl` files
   - Provides CLI for head-to-head predictions and stat importance analysis

---

## Frontend (`vnl-visualizer/`)

- **React + TypeScript + Vite** app for exploring and visualizing VNL data
- Features:
   - Player lookup with advanced filtering and stat breakdowns
   - Custom scatterplot visualizations (compare players by any stat)
   - Team, position, and age filters
   - Responsive, modern UI (desktop/mobile)
   - CSV parsing with PapaParse, charts with Chart.js and Recharts
- Consumes `merged_stats.csv` and other outputs from the backend pipeline

---

## File/Folder Structure

```
Collection/           # Webscraping scripts & config
   ├─ config.py        # Website configs for scraping
   ├─ webscraper.py    # Scrape per-player stats
   ├─ personalscraper.py # Scrape player profiles
   └─ merge.py         # Merge all player stats

Dataset/              # Raw scraped CSVs (attacking, blocking, etc.)

ML/                   # Machine learning pipeline & match/team scrapers
   ├─ ml.py            # Main ML pipeline (feature engineering, training, CLI)
   ├─ matchdata.py     # Scrape match-level stats
   ├─ teamdata.py      # Scrape team-level stats
   ├─ match_set_stats.csv, team_stats.csv, ...

RatingSystem/         # Player rating system
   ├─ playerrankings.py # Compute advanced player ratings
   ├─ mergeratings.py   # Merge ratings into merged_stats.csv
   └─ player_rankings.csv

merged_stats.csv      # Final merged player stats (input for ML & frontend)

vnl-visualizer/        # React frontend app
   ├─ src/
   ├─ public/
   ├─ package.json, ...

```

---

## Setup & Usage

### 1. Data Collection & Processing

**Requirements:** Python 3.10+, Selenium, pandas, numpy, scikit-learn, joblib

**Install dependencies:**
```sh
pip install -r requirements.txt
# Or manually: pip install selenium pandas numpy scikit-learn joblib
```

**Run scrapers:**
```sh
# Scrape per-player stats
python Collection/webscraper.py
# Scrape player profiles
python Collection/personalscraper.py
# Scrape match-level stats
python ML/matchdata.py
# Scrape team-level stats
python ML/teamdata.py
```

**Merge and rate players:**
```sh
python Collection/merge.py
python RatingSystem/playerrankings.py
python RatingSystem/mergeratings.py
```

### 2. Machine Learning

**Train models:**
```sh
python ML/ml.py
```

**Predict a match (CLI):**
```sh
python ML/ml.py "Team A" "Team B"
```

**Analyze stat importance:**
```sh
python ML/ml.py analyze_stats
```

### 3. Frontend (vnl-visualizer)

**Requirements:** Node.js 18+, npm

**Setup:**
```sh
cd vnl-visualizer
npm install
npm run dev
# Visit http://localhost:5173
```

---

## Development Notes

- All scrapers use Selenium and require WebDriver installed and in PATH
- Data pipeline is modular: you can re-run any step independently
- All CSVs are UTF-8 encoded
- ML pipeline is fully reproducible; retrain with new data as needed
- Frontend expects `merged_stats.csv` in the appropriate location (see code)
- For production, consider Dockerizing the pipeline and/or deploying the frontend

---

## Tech Stack

- **Backend/Data:** Python, Selenium, pandas, numpy, scikit-learn, joblib
- **Frontend:** React, TypeScript, Vite, Chart.js, Recharts, PapaParse
- **Other:** CSV, modern CSS, ESLint, Prettier

---

**Author:** Owen Hoag

For questions, collaboration, or contributions, please reach out!

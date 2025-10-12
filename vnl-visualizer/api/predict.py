import json
import os
import pandas as pd
import numpy as np
import joblib
from http.server import BaseHTTPRequestHandler

# --- Paths ---

# All required files are now in the same directory as this script
API_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_FILE = os.path.join(API_DIR, "merged_stats.csv")
TEAM_FILE = os.path.join(API_DIR, "team_stats.csv")
MODEL_PATH = os.path.join(API_DIR, "logistic_regression_model.pkl")
SET_SCORE_MODEL_PATH = os.path.join(API_DIR, "set_score_model.pkl")

# --- Load Data ---
player_df = pd.read_csv(PLAYER_FILE)
team_df = pd.read_csv(TEAM_FILE)

# --- Feature Functions ---
def aggregate_team_players(team_name, top_n=8):
    team_players = player_df[player_df['Team'] == team_name]
    if team_players.empty:
        return {f"impact_{func}": np.nan for func in ['mean','median','std','max','min','top8mean']}
    impact = team_players['Impact'].astype(float)
    feats = {
        'impact_mean': impact.mean(),
        'impact_median': impact.median(),
        'impact_std': impact.std(),
        'impact_max': impact.max(),
        'impact_min': impact.min(),
        'impact_top8mean': impact.sort_values(ascending=False).head(top_n).mean()
    }
    return feats

def get_team_season_stats(team_name):
    row = team_df[team_df['Team'].str.lower() == team_name.lower()]
    if row.empty:
        row = team_df[team_df['Team'].str.contains(team_name, case=False, na=False)]
    if row.empty:
        return {f"season_{col}": np.nan for col in team_df.columns if col != 'Team'}
    d = row.iloc[0].to_dict()
    return {f"season_{k}": v for k, v in d.items() if k != 'Team'}

def build_matchup_features(teamA, teamB):
    teamA_player = aggregate_team_players(teamA)
    teamB_player = aggregate_team_players(teamB)
    teamA_season = get_team_season_stats(teamA)
    teamB_season = get_team_season_stats(teamB)
    feats = {}
    feats.update({f"A_{k}": v for k, v in teamA_player.items()})
    feats.update({f"B_{k}": v for k, v in teamB_player.items()})
    feats.update({f"A_{k}": v for k, v in teamA_season.items()})
    feats.update({f"B_{k}": v for k, v in teamB_season.items()})
    for k in teamA_player:
        feats[f"diff_{k}"] = feats[f"A_{k}"] - feats[f"B_{k}"]
    for k in teamA_season:
        feats[f"diff_{k}"] = feats[f"A_{k}"] - feats[f"B_{k}"]
    return feats

def predict_match(teamA, teamB):
    feats = build_matchup_features(teamA, teamB)
    if not os.path.exists(MODEL_PATH):
        return {"error": "Model file not found."}
    model_data = joblib.load(MODEL_PATH)
    clf_full = model_data['model']
    columns = model_data['columns']
    X_pred = pd.DataFrame([feats])
    X_pred = X_pred.reindex(columns=columns, fill_value=0)
    X_pred = X_pred.apply(pd.to_numeric, errors='coerce').fillna(0)
    proba = clf_full.predict_proba(X_pred)[0]
    probA, probB = proba[1], proba[0]
    if probA >= probB:
        winner, loser, conf = teamA, teamB, float(probA)
    else:
        winner, loser, conf = teamB, teamA, float(probB)
    result = {
        "winner": winner,
        "loser": loser,
        "confidence": conf,
        "probabilities": {teamA: float(probA), teamB: float(probB)}
    }
    # Set score prediction
    if os.path.exists(SET_SCORE_MODEL_PATH):
        set_score_data = joblib.load(SET_SCORE_MODEL_PATH)
        set_score_clf = set_score_data['model']
        set_score_columns = set_score_data['columns']
        set_score_classes = set_score_data.get('set_score_classes', set_score_clf.classes_)
        X_pred_set = X_pred.reindex(columns=set_score_columns, fill_value=0)
        for col in set_score_columns:
            if col.startswith('winner_'):
                X_pred_set[col] = 1 if col == f'winner_{winner}' else 0
        X_pred_set['win_prob'] = conf
        X_pred_set['feature_diff'] = X_pred.abs().sum(axis=1).values[0]
        set_score_proba = set_score_clf.predict_proba(X_pred_set)[0]
        top_idx = set_score_proba.argmax()
        result["set_score"] = {
            "score": set_score_classes[top_idx],
            "probability": float(set_score_proba[top_idx])
        }
    return result

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)
        teamA = data.get("team1")
        teamB = data.get("team2")
        if not teamA or not teamB:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Missing team1 or team2"}).encode())
            return
        result = predict_match(teamA, teamB)
        print(json.dumps(result))  # Log the result to Vercel logs
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

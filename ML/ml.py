
# Volleyball Match Outcome Predictor Pipeline
# Author: Volleyball Data Science Expert
#
# Loads player, team, and match stats, aggregates features, merges, and trains a binary classifier.
# Modular, interpretable, and ready for updates.

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, cross_val_score, cross_validate
from sklearn.metrics import accuracy_score, roc_auc_score
import os
import joblib

# --- Config ---
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_FILE = os.path.join(DATA_DIR, "merged_stats.csv")
TEAM_FILE = os.path.join(DATA_DIR, "team_stats.csv")
MATCH_FILE = os.path.join(DATA_DIR, "match_set_stats.csv")

# --- 1. Load Data ---
player_df = pd.read_csv(PLAYER_FILE)
team_df = pd.read_csv(TEAM_FILE)
match_df = pd.read_csv(MATCH_FILE)

# --- 2. Aggregate Player Stats to Team Level ---
def aggregate_team_players(team_name, agg_funcs=None, top_n=8):
    """
    Aggregates player stats for a team using specified aggregation functions.
    Returns a dict of aggregated features.
    """
    team_players = player_df[player_df['Team'] == team_name]
    if team_players.empty:
        # Return NaNs for all features if no players found
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
    # Optionally add more aggregations here
    return feats

# --- 3. Merge Team Stats ---
def get_team_season_stats(team_name):
    row = team_df[team_df['Team'].str.lower() == team_name.lower()]
    if row.empty:
        # Try fuzzy match (for minor name mismatches)
        row = team_df[team_df['Team'].str.contains(team_name, case=False, na=False)]
    if row.empty:
        # Return NaNs for all columns
        return {f"season_{col}": np.nan for col in team_df.columns if col != 'Team'}
    d = row.iloc[0].to_dict()
    return {f"season_{k}": v for k, v in d.items() if k != 'Team'}

# --- 4. Build Match-Level Dataset ---
def build_match_features(match_row):
    # Team names
    teamA = match_row['Home Team']
    teamB = match_row['Away Team']
    # Aggregated player stats
    teamA_player = aggregate_team_players(teamA)
    teamB_player = aggregate_team_players(teamB)
    # Season stats
    teamA_season = get_team_season_stats(teamA)
    teamB_season = get_team_season_stats(teamB)
    # Only use pre-match features (no per-match stats)
    feats = {}
    feats.update({f"A_{k}": v for k, v in teamA_player.items()})
    feats.update({f"B_{k}": v for k, v in teamB_player.items()})
    feats.update({f"A_{k}": v for k, v in teamA_season.items()})
    feats.update({f"B_{k}": v for k, v in teamB_season.items()})
    # Difference features
    for k in teamA_player:
        feats[f"diff_{k}"] = feats[f"A_{k}"] - feats[f"B_{k}"]
    for k in teamA_season:
        feats[f"diff_{k}"] = feats[f"A_{k}"] - feats[f"B_{k}"]
    return feats

# --- 5. Build Full Feature Matrix ---
feature_rows = []
labels = []
groups = []
for idx, row in match_df.iterrows():
    feats = build_match_features(row)
    feature_rows.append(feats)
    # Label: 1 if Home Team wins, 0 if not
    labels.append(1 if row['Winner'] == row['Home Team'] else 0)
    # Group by Home Team for GroupKFold
    groups.append(row['Home Team'])
X = pd.DataFrame(feature_rows)
y = np.array(labels)
groups = np.array(groups)

# --- 6. Preprocessing: Fill missing values ---
X = X.apply(pd.to_numeric, errors='coerce')
X.fillna(0, inplace=True)


# --- 7. Modeling: Logistic Regression (baseline) ---
MODEL_PATH = os.path.join(DATA_DIR, "logistic_regression_model.pkl")
clf = LogisticRegression(max_iter=1000, solver='liblinear')
cv = GroupKFold(n_splits=5)
scoring = {'accuracy': 'accuracy', 'roc_auc': 'roc_auc'}
cv_results = cross_validate(clf, X, y, groups=groups, cv=cv, scoring=scoring, return_estimator=True)

print("\n--- Cross-Validation Results (Logistic Regression) ---")
print("Accuracy (folds):", cv_results['test_accuracy'])
print("ROC-AUC (folds):", cv_results['test_roc_auc'])
print("Mean Accuracy:", np.mean(cv_results['test_accuracy']))
print("Mean ROC-AUC:", np.mean(cv_results['test_roc_auc']))

# --- 8. Feature Importances (Coefficients) ---
coefs = np.mean([est.coef_[0] for est in cv_results['estimator']], axis=0)
feat_importance = pd.Series(coefs, index=X.columns).sort_values(key=np.abs, ascending=False)
print("\nTop 15 Most Important Features (by abs(coef)):")
print(feat_importance.head(15))

# --- Save the trained model and columns ---
clf_full = LogisticRegression(max_iter=1000, solver='liblinear')
clf_full.fit(X, y)
joblib.dump({'model': clf_full, 'columns': X.columns.tolist()}, MODEL_PATH)
print(f"\nTrained model saved to {MODEL_PATH}")

# --- 9. Optional: Random Forest/GBM comparison ---
# Uncomment to compare
# rf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
# rf_cv = cross_validate(rf, X, y, groups=groups, cv=cv, scoring=scoring)
# print("\nRandom Forest Mean Accuracy:", np.mean(rf_cv['test_accuracy']))
# print("Random Forest Mean ROC-AUC:", np.mean(rf_cv['test_roc_auc']))


# --- CLI for head-to-head prediction ---
import sys
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
    # Load model and columns
    MODEL_PATH = os.path.join(DATA_DIR, "logistic_regression_model.pkl")
    if not os.path.exists(MODEL_PATH):
        print("Model file not found. Please train the model first.")
        return
    model_data = joblib.load(MODEL_PATH)
    clf_full = model_data['model']
    columns = model_data['columns']
    X_pred = pd.DataFrame([feats])
    X_pred = X_pred.reindex(columns=columns, fill_value=0)  # align columns
    X_pred = X_pred.apply(pd.to_numeric, errors='coerce').fillna(0)
    proba = clf_full.predict_proba(X_pred)[0]
    probA, probB = proba[1], proba[0]
    if probA >= probB:
        winner, loser, conf = teamA, teamB, probA
    else:
        winner, loser, conf = teamB, teamA, probB
    print(f"\nPrediction: {winner} wins")
    print(f"Confidence (probability {winner} wins): {conf:.2f}")
def analyze_match_stat_importance():
    """
    Analyze which per-match stats are most predictive of winning using only match_set_stats.csv.
    """
    print("\n--- Analyzing Per-Match Stat Importance for Winning ---")
    # Only use per-match stats (no player/season features)
    match_df_local = pd.read_csv(MATCH_FILE, encoding='utf-8-sig')
    # Print actual column names for debugging
    print("\nColumn names in match_set_stats.csv (repr):")
    for col in match_df_local.columns:
        print(repr(col))
    # Strip whitespace from all column names
    match_df_local.columns = match_df_local.columns.str.strip()
    # Print first 5 rows of Home Team and Winner for direct inspection
    print("\nFirst 5 rows of 'Home Team' and 'Winner' (repr):")
    for i, row in match_df_local.head().iterrows():
        print(f"Row {i}: Home Team={repr(row.get('Home Team'))}, Winner={repr(row.get('Winner'))}")
    # Remove rows with missing outcome
    match_df_local = match_df_local.dropna(subset=['Winner', 'Home Team'])
    print("\nAfter dropna: columns (repr):")
    for col in match_df_local.columns:
        print(repr(col))
    print("After dropna: first 5 rows of 'Home Team' and 'Winner' (repr):")
    for i, row in match_df_local.head().iterrows():
        print(f"Row {i}: Home Team={repr(row.get('Home Team'))}, Winner={repr(row.get('Winner'))}")
    # Build features: difference between Home and Away for each stat
    # Only include stat columns, not team name columns
    stat_cols = [c for c in match_df_local.columns if (
        'Home' in c and
        c.replace('Home','Away') in match_df_local.columns and
        not c.endswith('Team') and
        not c.endswith('Teams') and
        not c.startswith('Home Team') and
        not c.startswith('Away Team')
    )]
    # Convert all stat columns to numeric before subtraction
    for c in stat_cols:
        match_df_local[c] = pd.to_numeric(match_df_local[c], errors='coerce')
        match_df_local[c.replace('Home','Away')] = pd.to_numeric(match_df_local[c.replace('Home','Away')], errors='coerce')
    X_stats = pd.DataFrame({f"diff_{c.replace(' Home','').replace('Home','')}": match_df_local[c] - match_df_local[c.replace('Home','Away')] for c in stat_cols})
    # Robust comparison: strip whitespace and lower case
    winners = match_df_local['Winner'].astype(str).str.strip().str.lower()
    home_teams = match_df_local['Home Team'].astype(str).str.strip().str.lower()
    y_stats = (winners == home_teams).astype(int)
    # Debug: print first 10 comparisons
    print("\nFirst 10 Winner vs Home Team comparisons (repr):")
    for i in range(min(10, len(winners))):
        print(f"Row {i+1}: Winner={repr(winners.iloc[i])} | Home Team={repr(home_teams.iloc[i])}")
    print("\nIf you see unexpected whitespace or characters, update the code to use the exact column names as shown above.")
    X_stats = X_stats.fillna(0)
    # Diagnostic: print class distribution
    class_counts = y_stats.value_counts()
    print("Class distribution (1 = Home win, 0 = Away win):")
    print(class_counts)
    if len(class_counts) < 2:
        print("ERROR: Only one class present in the data. Check your match_set_stats.csv for correct Winner and Home Team columns.")
        return
    clf_stats = LogisticRegression(max_iter=1000, solver='liblinear')
    clf_stats.fit(X_stats, y_stats)
    importances = pd.Series(clf_stats.coef_[0], index=X_stats.columns).sort_values(key=np.abs, ascending=False)
    print("Top 15 Most Important Per-Match Stats (by abs(coef)):")
    print(importances.head(15))

if __name__ == "__main__":
    if len(sys.argv) == 3:
        teamA, teamB = sys.argv[1], sys.argv[2]
        predict_match(teamA, teamB)
    elif len(sys.argv) == 2 and sys.argv[1] == "analyze_stats":
        analyze_match_stat_importance()

"""Vercel serverless endpoint for VNL match predictions."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from http.server import BaseHTTPRequestHandler
from typing import Any

import joblib
import numpy as np
import pandas as pd

API_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_FILE = os.path.join(API_DIR, "merged_stats.csv")
TEAM_FILE = os.path.join(API_DIR, "team_stats.csv")
MODEL_PATH = os.path.join(API_DIR, "logistic_regression_model.pkl")
SET_SCORE_MODEL_PATH = os.path.join(API_DIR, "set_score_model.pkl")
MAX_REQUEST_BYTES = 16_384


@dataclass(frozen=True)
class Team:
    requested_name: str
    player_code: str
    season_name: str


TEAM_IDENTITIES = (
    ("ARG", "Argentina"),
    ("BRA", "Brazil"),
    ("BUL", "Bulgaria"),
    ("CAN", "Canada"),
    ("CHN", "China"),
    ("CUB", "Cuba"),
    ("FRA", "France"),
    ("GER", "Germany"),
    ("IRI", "Iran"),
    ("ITA", "Italy"),
    ("JPN", "Japan"),
    ("NED", "Netherlands"),
    ("POL", "Poland"),
    ("SLO", "Slovenia"),
    ("SRB", "Serbia"),
    ("TUR", "Türkiye"),
    ("UKR", "Ukraine"),
    ("USA", "USA"),
)

TEAM_ALIASES: dict[str, tuple[str, str]] = {}
for code, season_name in TEAM_IDENTITIES:
    TEAM_ALIASES[code.casefold()] = (code, season_name)
    TEAM_ALIASES[season_name.casefold()] = (code, season_name)
TEAM_ALIASES.update(
    {
        "turkey": ("TUR", "Türkiye"),
        "united states": ("USA", "USA"),
        "united states of america": ("USA", "USA"),
    }
)


def _load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    player_data = pd.read_csv(PLAYER_FILE)
    team_data = pd.read_csv(TEAM_FILE)
    player_data["Impact"] = pd.to_numeric(player_data["Impact"], errors="coerce")
    numeric_team_columns = [column for column in team_data.columns if column != "Team"]
    team_data[numeric_team_columns] = team_data[numeric_team_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )
    return player_data, team_data


PLAYER_DATA, TEAM_DATA = _load_data()
TEAM_DATA_BY_NAME = {
    str(row["Team"]).casefold(): row
    for _, row in TEAM_DATA.iterrows()
}


def _aggregate_players() -> dict[str, dict[str, float]]:
    aggregates: dict[str, dict[str, float]] = {}
    for team_code, players in PLAYER_DATA.groupby("Team", sort=False):
        impact = players["Impact"].dropna()
        aggregates[str(team_code)] = {
            "impact_mean": float(impact.mean()),
            "impact_median": float(impact.median()),
            "impact_std": float(impact.std()) if len(impact) > 1 else 0.0,
            "impact_max": float(impact.max()),
            "impact_min": float(impact.min()),
            "impact_top8mean": float(
                impact.nlargest(8).mean()
            ),
        }
    return aggregates


PLAYER_AGGREGATES = _aggregate_players()


@lru_cache(maxsize=1)
def _load_models() -> tuple[dict[str, Any], dict[str, Any] | None]:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Winner model file not found.")
    winner_model = joblib.load(MODEL_PATH)
    set_score_model = (
        joblib.load(SET_SCORE_MODEL_PATH)
        if os.path.exists(SET_SCORE_MODEL_PATH)
        else None
    )
    return winner_model, set_score_model


def resolve_team(team_name: str) -> Team:
    normalized = team_name.strip().casefold()
    identity = TEAM_ALIASES.get(normalized)
    if identity is None:
        raise ValueError(f"Unknown team: {team_name}")
    player_code, season_name = identity
    if player_code not in PLAYER_AGGREGATES:
        raise ValueError(f"Player data is unavailable for {team_name}")
    if season_name.casefold() not in TEAM_DATA_BY_NAME:
        raise ValueError(f"Season data is unavailable for {team_name}")
    return Team(team_name.strip(), player_code, season_name)


def aggregate_team_players(team: Team) -> dict[str, float]:
    return PLAYER_AGGREGATES[team.player_code]


def get_team_season_stats(team: Team) -> dict[str, float]:
    row = TEAM_DATA_BY_NAME[team.season_name.casefold()]
    return {
        f"season_{key}": float(value) if pd.notna(value) else np.nan
        for key, value in row.items()
        if key != "Team"
    }


def build_matchup_features(team_a: Team, team_b: Team) -> dict[str, float]:
    team_a_player = aggregate_team_players(team_a)
    team_b_player = aggregate_team_players(team_b)
    team_a_season = get_team_season_stats(team_a)
    team_b_season = get_team_season_stats(team_b)

    features: dict[str, float] = {}
    features.update({f"A_{key}": value for key, value in team_a_player.items()})
    features.update({f"B_{key}": value for key, value in team_b_player.items()})
    features.update({f"A_{key}": value for key, value in team_a_season.items()})
    features.update({f"B_{key}": value for key, value in team_b_season.items()})
    for key in team_a_player:
        features[f"diff_{key}"] = features[f"A_{key}"] - features[f"B_{key}"]
    for key in team_a_season:
        features[f"diff_{key}"] = features[f"A_{key}"] - features[f"B_{key}"]
    return features


def predict_match(team_a_name: str, team_b_name: str) -> dict[str, Any]:
    team_a = resolve_team(team_a_name)
    team_b = resolve_team(team_b_name)
    if team_a.player_code == team_b.player_code:
        raise ValueError("Please select two different teams.")

    winner_model_data, set_score_model_data = _load_models()
    features = build_matchup_features(team_a, team_b)
    winner_columns = winner_model_data["columns"]
    prediction_frame = pd.DataFrame([features]).reindex(
        columns=winner_columns,
        fill_value=0,
    )
    prediction_frame = prediction_frame.apply(
        pd.to_numeric,
        errors="coerce",
    ).fillna(0)

    probabilities = winner_model_data["model"].predict_proba(prediction_frame)[0]
    probability_a = float(probabilities[1])
    probability_b = float(probabilities[0])
    if probability_a >= probability_b:
        winner, loser, confidence = team_a, team_b, probability_a
    else:
        winner, loser, confidence = team_b, team_a, probability_b

    result: dict[str, Any] = {
        "winner": winner.requested_name,
        "loser": loser.requested_name,
        "confidence": confidence,
        "probabilities": {
            team_a.requested_name: probability_a,
            team_b.requested_name: probability_b,
        },
    }

    if set_score_model_data is not None:
        set_score_model = set_score_model_data["model"]
        set_score_columns = set_score_model_data["columns"]
        set_score_frame = prediction_frame.reindex(
            columns=set_score_columns,
            fill_value=0,
        )
        for column in set_score_columns:
            if column.startswith("winner_"):
                set_score_frame[column] = int(
                    column == f"winner_{winner.season_name}"
                )
        set_score_frame["win_prob"] = confidence
        set_score_frame["feature_diff"] = float(
            prediction_frame.abs().sum(axis=1).iloc[0]
        )
        set_score_probabilities = set_score_model.predict_proba(set_score_frame)[0]
        set_score_classes = set_score_model_data.get(
            "set_score_classes",
            set_score_model.classes_,
        )
        top_index = int(set_score_probabilities.argmax())
        result["set_score"] = {
            "score": str(set_score_classes[top_index]),
            "probability": float(set_score_probabilities[top_index]),
        }

    return result


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > MAX_REQUEST_BYTES:
                self._send_json(400, {"error": "Invalid request size."})
                return
            data = json.loads(self.rfile.read(content_length))
            if not isinstance(data, dict):
                raise ValueError("Request body must be a JSON object.")
            team_a = data.get("team1")
            team_b = data.get("team2")
            if not isinstance(team_a, str) or not isinstance(team_b, str):
                raise ValueError("Missing team1 or team2.")
            result = predict_match(team_a, team_b)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as error:
            self._send_json(400, {"error": str(error)})
            return
        except FileNotFoundError as error:
            self._send_json(503, {"error": str(error)})
            return
        except Exception:
            self._send_json(500, {"error": "Prediction service failed."})
            return
        self._send_json(200, result)

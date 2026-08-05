"""Calculate normalized skill and position ratings for VNL players."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT_DIR / "merged_stats.csv"
OUTPUT_FILE = ROOT_DIR / "RatingSystem" / "player_rankings.csv"

POSITIONAL_WEIGHTS = {
    "OUTSIDE HITTER": {
        "att": 0.25,
        "blk": 0.15,
        "serv": 0.10,
        "set": 0.05,
        "def": 0.15,
        "recv": 0.30,
    },
    "OPPOSITE SPIKER": {
        "att": 0.40,
        "blk": 0.30,
        "serv": 0.15,
        "set": 0.05,
        "def": 0.10,
        "recv": 0.0,
    },
    "MIDDLE BLOCKER": {
        "att": 0.25,
        "blk": 0.45,
        "serv": 0.15,
        "set": 0.05,
        "def": 0.05,
        "recv": 0.05,
    },
    "SETTER": {
        "att": 0.10,
        "blk": 0.20,
        "serv": 0.15,
        "set": 0.45,
        "def": 0.10,
        "recv": 0.0,
    },
    "LIBERO": {
        "att": 0.0,
        "blk": 0.0,
        "serv": 0.10,
        "set": 0.10,
        "def": 0.40,
        "recv": 0.40,
    },
}

POSITION_ALIASES = {
    "OPPOSITE HITTER": "OPPOSITE SPIKER",
}

OUTPUT_COLUMNS = [
    "Player Name",
    "Team",
    "Position",
    "positional_rating",
    "rating_att",
    "att_eff",
    "att_vol",
    "att_raw",
    "rating_blk",
    "blk_eff",
    "blk_vol",
    "blk_raw",
    "rating_serv",
    "serv_eff",
    "serv_vol",
    "serv_raw",
    "rating_set",
    "set_eff",
    "set_vol",
    "set_raw",
    "rating_def",
    "def_eff",
    "def_vol",
    "def_raw",
    "rating_recv",
    "recv_eff",
    "recv_vol",
    "recv_raw",
]


def safe_divide(numerator: pd.Series, denominator: pd.Series | float) -> pd.Series:
    if isinstance(denominator, pd.Series):
        return numerator.div(denominator.where(denominator > 0)).fillna(0)
    if denominator <= 0:
        return pd.Series(0.0, index=numerator.index)
    return numerator / denominator


def add_rating(
    frame: pd.DataFrame,
    category: str,
    efficiency: pd.Series,
    volume: pd.Series,
    efficiency_power: float,
    volume_power: float,
) -> None:
    raw = efficiency.clip(lower=0).pow(efficiency_power) * (
        volume.clip(lower=0).pow(volume_power)
    )
    frame[f"{category}_eff"] = efficiency
    frame[f"{category}_vol"] = volume
    frame[f"{category}_raw"] = raw
    maximum = raw.max()
    frame[f"rating_{category}"] = (
        (100 * raw / maximum).round(2)
        if maximum > 0
        else 0.0
    )


def calculate_ratings(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()

    attacking_efficiency = safe_divide(
        data["Kills"] - data["Attacking Errors"],
        data["Attacking Attempts"],
    )
    attack_volume_column = (
        "Kills Per Match"
        if "Kills Per Match" in data
        else "Attacks Per Match"
    )
    add_rating(
        data,
        "att",
        attacking_efficiency,
        safe_divide(
            data[attack_volume_column],
            data[attack_volume_column].max(),
        ),
        0.5,
        1.2,
    )

    block_attempts = (
        data["Blocks"] + data["Blocking Errors"] + data["Rebounds"]
    )
    add_rating(
        data,
        "blk",
        safe_divide(data["Blocks"], block_attempts),
        safe_divide(data["Blocks Per Match"], data["Blocks Per Match"].max()),
        0.4,
        1.3,
    )

    serve_volume_column = (
        "Aces Per Match"
        if "Aces Per Match" in data
        else "Serves Per Match"
    )
    add_rating(
        data,
        "serv",
        safe_divide(data["Aces"], data["Service Attempts"]),
        safe_divide(
            data[serve_volume_column],
            data[serve_volume_column].max(),
        ),
        0.6,
        1.1,
    )

    set_attempts = (
        data["Running Sets"] + data["Still Sets"] + data["Setting Errors"]
    )
    add_rating(
        data,
        "set",
        safe_divide(data["Running Sets"], set_attempts),
        safe_divide(data["Sets Per Match"], data["Sets Per Match"].max()),
        0.5,
        1.2,
    )

    add_rating(
        data,
        "def",
        safe_divide(
            data["Great Saves"] - data["Defensive Errors"],
            data["Defensive Receptions"],
        ),
        safe_divide(data["Digs Per Match"], data["Digs Per Match"].max()),
        0.4,
        1.3,
    )

    add_rating(
        data,
        "recv",
        safe_divide(
            data["Successful Receives"] - data["Receiving Errors"],
            data["Service Receptions"],
        ),
        safe_divide(
            data["Receives Per Match"],
            data["Receives Per Match"].max(),
        ),
        0.5,
        1.2,
    )

    normalized_positions = (
        data["Position"]
        .str.strip()
        .str.upper()
        .replace(POSITION_ALIASES)
    )
    weight_frame = pd.DataFrame(
        [
            POSITIONAL_WEIGHTS.get(
                position,
                POSITIONAL_WEIGHTS["OUTSIDE HITTER"],
            )
            for position in normalized_positions
        ],
        index=data.index,
    )
    rating_columns = [
        f"rating_{category}"
        for category in ("att", "blk", "serv", "set", "def", "recv")
    ]
    data["raw_positional_rating"] = (
        data[rating_columns].to_numpy() * weight_frame.to_numpy()
    ).sum(axis=1)

    data["positional_rating"] = 0.0
    for position in POSITIONAL_WEIGHTS:
        mask = normalized_positions == position
        maximum = data.loc[mask, "raw_positional_rating"].max()
        if pd.notna(maximum) and maximum > 0:
            data.loc[mask, "positional_rating"] = (
                100
                * data.loc[mask, "raw_positional_rating"]
                / maximum
            ).round(2)

    numeric_columns = data[OUTPUT_COLUMNS].select_dtypes(
        include=[np.number]
    ).columns
    data[numeric_columns] = data[numeric_columns].round(2)
    return data[OUTPUT_COLUMNS]


def main() -> None:
    player_stats = pd.read_csv(INPUT_FILE)
    rankings = calculate_ratings(player_stats)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    rankings.to_csv(OUTPUT_FILE, index=False)
    print(f"Player rankings saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

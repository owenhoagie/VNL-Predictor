"""Add calculated rating columns to the canonical player dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
RANKINGS_FILE = ROOT_DIR / "RatingSystem" / "player_rankings.csv"
PLAYER_FILE = ROOT_DIR / "merged_stats.csv"
MERGE_KEYS = ["Player Name", "Team", "Position"]
RATING_COLUMNS = {
    "positional_rating": "Impact",
    "rating_att": "Attacking Rating",
    "rating_blk": "Blocking Rating",
    "rating_serv": "Serving Rating",
    "rating_set": "Setting Rating",
    "rating_def": "Defense Rating",
    "rating_recv": "Receiving Rating",
}


def merge_ratings(
    players: pd.DataFrame,
    rankings: pd.DataFrame,
) -> pd.DataFrame:
    selected = rankings[
        [*MERGE_KEYS, *RATING_COLUMNS]
    ].drop_duplicates(subset=MERGE_KEYS)
    selected = selected.rename(columns=RATING_COLUMNS)
    merged = players.merge(
        selected,
        on=MERGE_KEYS,
        how="left",
        validate="many_to_one",
    )

    base_columns = ["Player Name", "Team", "Position", "Age", "Height"]
    rating_columns = list(RATING_COLUMNS.values())
    remaining_columns = [
        column
        for column in merged.columns
        if column not in base_columns + rating_columns
    ]
    return merged[base_columns + rating_columns + remaining_columns]


def main() -> None:
    players = pd.read_csv(PLAYER_FILE)
    rankings = pd.read_csv(RANKINGS_FILE)
    merged = merge_ratings(players, rankings)
    merged.to_csv(PLAYER_FILE, index=False)
    print(f"Merged ratings into {PLAYER_FILE}")


if __name__ == "__main__":
    main()

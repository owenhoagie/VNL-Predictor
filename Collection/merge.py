"""Merge the player-stat CSV exports into the canonical player dataset."""

from __future__ import annotations

from functools import reduce
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT_DIR / "Dataset"
OUTPUT_FILE = ROOT_DIR / "merged_stats.csv"
MERGE_KEYS = ["Player Name", "Team"]
PLAYER_DATASETS = [
    "player_profiles.csv",
    "attacking_stats.csv",
    "blocking_stats.csv",
    "serving_stats.csv",
    "setting_stats.csv",
    "defense_stats.csv",
    "receiving_stats.csv",
]


def load_player_datasets(dataset_dir: Path = DATASET_DIR) -> list[pd.DataFrame]:
    """Load and validate only CSVs that belong to the player-stat pipeline."""
    frames: list[pd.DataFrame] = []
    for filename in PLAYER_DATASETS:
        path = dataset_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Required dataset is missing: {path}")
        frame = pd.read_csv(path)
        missing_keys = set(MERGE_KEYS).difference(frame.columns)
        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise ValueError(f"{path} is missing merge columns: {missing}")
        frames.append(frame)
    return frames


def merge_player_stats(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """Outer-join player datasets while retaining each source's column order."""
    if not frames:
        raise ValueError("At least one player dataset is required.")

    merged = reduce(
        lambda left, right: left.merge(
            right,
            on=MERGE_KEYS,
            how="outer",
            validate="many_to_many",
        ),
        frames,
    )
    return merged.fillna(0)


def main() -> None:
    merged = merge_player_stats(load_player_datasets())
    merged.to_csv(OUTPUT_FILE, index=False)
    print(f"Merged {len(merged)} player rows into {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

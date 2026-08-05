"""Synchronize generated data/model artifacts with their deployment copies."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS = {
    ROOT_DIR / "merged_stats.csv": [
        ROOT_DIR / "ML" / "merged_stats.csv",
        ROOT_DIR / "vnl-visualizer" / "api" / "merged_stats.csv",
        ROOT_DIR / "vnl-visualizer" / "public" / "merged_stats.csv",
    ],
    ROOT_DIR / "ML" / "team_stats.csv": [
        ROOT_DIR / "vnl-visualizer" / "api" / "team_stats.csv",
    ],
    ROOT_DIR / "ML" / "logistic_regression_model.pkl": [
        ROOT_DIR / "vnl-visualizer" / "api" / "logistic_regression_model.pkl",
    ],
    ROOT_DIR / "ML" / "set_score_model.pkl": [
        ROOT_DIR / "vnl-visualizer" / "api" / "set_score_model.pkl",
    ],
}


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(65_536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def synchronize(check_only: bool) -> bool:
    synchronized = True
    for source, destinations in ARTIFACTS.items():
        if not source.exists():
            raise FileNotFoundError(f"Source artifact is missing: {source}")
        source_digest = digest(source)
        for destination in destinations:
            matches = (
                destination.exists()
                and digest(destination) == source_digest
            )
            if matches:
                continue
            synchronized = False
            if check_only:
                print(f"OUT OF SYNC: {destination.relative_to(ROOT_DIR)}")
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            print(
                f"Synced {source.relative_to(ROOT_DIR)} -> "
                f"{destination.relative_to(ROOT_DIR)}"
            )
    return synchronized


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report stale copies without changing files.",
    )
    args = parser.parse_args()
    synchronized = synchronize(check_only=args.check)
    if args.check and not synchronized:
        raise SystemExit(1)
    if synchronized:
        print("All generated artifacts are synchronized.")


if __name__ == "__main__":
    main()

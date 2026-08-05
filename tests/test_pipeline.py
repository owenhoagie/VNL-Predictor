from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "vnl-visualizer" / "api"))

from Collection.merge import load_player_datasets, merge_player_stats
from RatingSystem.mergeratings import merge_ratings
from RatingSystem.playerrankings import calculate_ratings
from scripts.sync_artifacts import synchronize
import predict


class PlayerPipelineTests(unittest.TestCase):
    def test_merge_uses_only_player_datasets(self) -> None:
        frames = load_player_datasets()
        self.assertEqual(len(frames), 7)
        merged = merge_player_stats(frames)
        self.assertIn("Player Name", merged)
        self.assertNotIn("match_url", merged)

    def test_ratings_pipeline_is_complete_and_unique(self) -> None:
        merged = merge_player_stats(load_player_datasets())
        rankings = calculate_ratings(merged)
        final = merge_ratings(merged, rankings)
        self.assertEqual(len(final), 337)
        self.assertEqual(final.duplicated().sum(), 0)
        self.assertFalse(
            final[
                [
                    "Impact",
                    "Attacking Rating",
                    "Blocking Rating",
                    "Serving Rating",
                    "Setting Rating",
                    "Defense Rating",
                    "Receiving Rating",
                ]
            ].isna().any().any()
        )

    def test_generated_artifacts_are_synchronized(self) -> None:
        self.assertTrue(synchronize(check_only=True))

    def test_checked_in_player_data_matches_pipeline(self) -> None:
        expected = merge_ratings(
            merge_player_stats(load_player_datasets()),
            calculate_ratings(merge_player_stats(load_player_datasets())),
        )
        actual = pd.read_csv(ROOT_DIR / "merged_stats.csv")
        pd.testing.assert_frame_equal(actual, expected, check_dtype=False)


class PredictionTests(unittest.TestCase):
    def test_team_aliases_resolve_to_identical_features(self) -> None:
        usa = predict.resolve_team("USA")
        united_states = predict.resolve_team("United States")
        self.assertEqual(usa.player_code, united_states.player_code)
        self.assertEqual(usa.season_name, united_states.season_name)

    def test_prediction_returns_probabilities_and_set_score(self) -> None:
        result = predict.predict_match("USA", "Poland")
        self.assertIn(result["winner"], {"USA", "Poland"})
        self.assertAlmostEqual(
            sum(result["probabilities"].values()),
            1.0,
            places=10,
        )
        self.assertIn(result["set_score"]["score"], {"3-0", "3-1", "3-2"})

    def test_invalid_teams_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown team"):
            predict.predict_match("Atlantis", "Poland")
        with self.assertRaisesRegex(ValueError, "different teams"):
            predict.predict_match("USA", "United States")


if __name__ == "__main__":
    unittest.main()

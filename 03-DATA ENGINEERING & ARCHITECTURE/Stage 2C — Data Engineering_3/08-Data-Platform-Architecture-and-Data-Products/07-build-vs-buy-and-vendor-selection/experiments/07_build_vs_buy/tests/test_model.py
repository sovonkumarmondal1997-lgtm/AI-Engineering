import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
import model


class TCOModelTests(unittest.TestCase):
    def test_weights_sum_to_100_and_scores_in_range(self):
        weights = model.SCORECARD["weights"]
        self.assertEqual(sum(weights.values()), 100)
        for scores in model.SCORECARD["candidate_scores"].values():
            self.assertEqual(set(scores), set(weights))
            self.assertTrue(all(type(x) is int and 1 <= x <= 5 for x in scores.values()))

    def test_tco_horizons_include_initial_migration_training_and_exit_once(self):
        c = model.ASSUMPTIONS["candidates"]["managed_saas"]
        rate = model.ASSUMPTIONS["fully_loaded_engineering_hourly_rate"]
        one = model.tco(c, 1, 1, rate)
        three = model.tco(c, 3, 1, rate)
        self.assertEqual(one["initial_implementation"], c["initial_implementation_hours"] * rate)
        self.assertEqual(one["migration"], c["one_time_migration_hours"] * rate)
        self.assertEqual(one["one_time_training"], c["one_time_training_hours"] * rate)
        self.assertEqual(one["terminal_exit"], c["terminal_exit_hours"] * rate)
        self.assertAlmostEqual(three["tco_including_exit"] - one["tco_including_exit"], 2 * one["annual_recurring_total"])

    def test_annual_recurring_includes_egress_and_training_refresh(self):
        c = model.ASSUMPTIONS["candidates"]["managed_saas"]
        rate = model.ASSUMPTIONS["fully_loaded_engineering_hourly_rate"]
        recurring = model.annual_recurring(c, 1, rate)
        self.assertEqual(recurring["egress"], c["annual_data_movement_egress_at_1x"])
        expected_labour = sum(c[k] for k in (
            "annual_maintenance_operations_hours", "annual_on_call_hours",
            "annual_upgrade_hours", "annual_training_refresh_hours",
        )) * rate
        self.assertEqual(recurring["labour"], expected_labour)

    def test_higher_usage_increases_cost_under_linear_assumption(self):
        c = model.ASSUMPTIONS["candidates"]["managed_saas"]
        rate = model.ASSUMPTIONS["fully_loaded_engineering_hourly_rate"]
        costs = [model.tco(c, 3, x, rate)["tco_including_exit"] for x in (1, 5, 10)]
        self.assertLess(costs[0], costs[1])
        self.assertLess(costs[1], costs[2])

    def test_score_is_weighted_average(self):
        weights = {"a": 70, "b": 30}
        scores = {"a": 5, "b": 1}
        self.assertAlmostEqual(model.weighted_score(weights, scores), 3.8)

    def test_score_rejects_non_100_weights_and_non_integer_scores(self):
        with self.assertRaises(ValueError):
            model.weighted_score({"a": 50, "b": 30}, {"a": 5, "b": 1})
        with self.assertRaises(ValueError):
            model.weighted_score({"a": 100}, {"a": 4.5})

    def test_candidates_not_decision_eligible_before_hard_gates(self):
        rows = model.generate_score_rows()
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row["hard_gate_status"] == "NOT_ASSESSED" for row in rows))
        self.assertTrue(all(row["decision_eligible"] == "NO—HARD GATES NOT ASSESSED" for row in rows))

    def test_each_candidate_has_a_hypothesis_rationale(self):
        self.assertEqual(set(model.SCORECARD["candidate_rationale"]), set(model.SCORECARD["candidate_scores"]))
        self.assertTrue(all(reason.strip() for reason in model.SCORECARD["candidate_rationale"].values()))

    def test_golden_tco_outputs_match_lesson_tables(self):
        rate = model.ASSUMPTIONS["fully_loaded_engineering_hourly_rate"]
        managed = model.ASSUMPTIONS["candidates"]["managed_saas"]
        self.assertEqual(model.tco(managed, 1, 1, rate)["tco_including_exit"], 239000)
        self.assertEqual(model.tco(managed, 3, 1, rate)["tco_including_exit"], 532000)
        self.assertEqual(model.tco(managed, 3, 10, rate)["tco_including_exit"], 1828000)

    def test_golden_score_outputs_match_lesson_table(self):
        rows = {row["candidate"]: row for row in model.generate_score_rows()}
        self.assertEqual(rows["fivetran_managed"]["weighted_score_1_to_5"], 3.71)
        self.assertEqual(rows["airbyte_self_managed"]["weighted_score_1_to_5"], 3.2)
        self.assertEqual(rows["custom_dlt"]["weighted_score_1_to_5"], 2.87)

    def test_csv_rows_cover_all_scenarios(self):
        rows = model.generate_tco_rows()
        self.assertEqual(len(rows), 3 * 2 * 3)
        self.assertEqual(len(model.generate_score_rows()), 3)


if __name__ == "__main__":
    unittest.main()

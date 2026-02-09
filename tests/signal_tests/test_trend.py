import pandas as pd
import pytest

from scaffold.bitstomach.signals import Trend
from scaffold.utils.namespace._PSDO import PSDO


def message() -> dict:
    return {
        "Performance_data": [
            [
                "subject",
                "measure",
                "period.start",
                "measureScore.rate",
                "measureScore.denominator",
                "peer_average_comparator",
                "peer_75th_percentile_benchmark",
                "peer_90th_percentile_benchmark",
                "MPOG_goal",
            ],
            [1, "BP01", "2022-12-01", 19, 19, 83.0, 100.0, 100.0, 90.0],
            [1, "BP01", "2023-01-01", 46, 46, 83.0, 100.0, 100.0, 90.0],
            [1, "BP01", "2023-02-01", 58, 58, 83.3, 100.0, 100.0, 90.0],
            [1, "BP01", "2023-03-01", 68, 68, 83.6, 100.0, 100.0, 90.0],
            [1, "BP01", "2023-04-01", 49, 49, 84.7, 100.0, 100.0, 90.0],
            [1, "BP01", "2023-05-01", 96, 96, 84.5, 100.0, 100.0, 90.0],
            [1, "BP01", "2023-06-01", 91, 91, 84.8, 100.0, 100.0, 90.0],
            [1, "BP01", "2023-07-01", 74, 74, 84.6, 100.0, 100.0, 90.0],
            [1, "BP01", "2023-08-01", 97.62, 42, 84.9, 100.0, 100.0, 90.0],
        ]
    }


def perf(message: dict) -> pd.DataFrame:
    perf_data = message["Performance_data"]

    perf = pd.DataFrame(columns=perf_data[0], data=perf_data[1:])

    perf["valid"] = perf["measureScore.denominator"] >= 10
    perf["passed_change"] = perf["measureScore.rate"].diff()
    perf["period.start"] = pd.to_datetime(perf["period.start"])
    perf["pos_trend"] = (
        perf["measureScore.rate"]
        .rolling(window=3)
        .apply(lambda x: (x.is_monotonic_increasing and x.is_unique))[2:]
        .astype(bool)
    )
    perf.worse = perf["passed_change"].iat[-1] < 0
    perf.better = perf["passed_change"].iat[-1] >= 0

    return perf


@pytest.fixture
def signal_data():
    return 0.045


detection_test_set = [
    ([0.77, 0.88, 0.99], 0.11, "simple positive trend"),
    ([0.99, 0.88, 0.77], -0.11, "simple negative trend"),
    ([0.88, 0.88, 0.88], 0.0, "no trend"),
    ([0.77, 0.77, 0.99], 0.11, "partial positive trend"),
    ([0.77, 0.99, 0.99], 0.0, "partial positive trend"),
    ([0.77, 0.99, 0.88], 0.0, "non-monotonic, last month negative"),
    ([0.88, 0.77, 0.88], 0.0, "non-monotonic, last month positive"),
]


@pytest.mark.parametrize("perf_level, expected, condition", detection_test_set)
def test_trend__detect(perf_level: list, expected: float, condition: str):
    perf = pd.DataFrame({"measureScore.rate": perf_level})
    slope = Trend._detect(perf)

    assert slope == pytest.approx(expected), condition + " failed"


mods_test_set = [
    (0.11, round(abs(0.22), 4), "simple negative trend"),
    (-0.111111111111, round(abs(0.22222222222), 4), "simple negative trend"),
    (0.0, 0.0, "no trend"),
]


@pytest.mark.parametrize("slope, moderator, condition", mods_test_set)
def test_trend_moderators(slope: float, moderator: float, condition):
    signal = Trend._resource(slope,PSDO.desired_increase)
    mods = Trend.moderators([signal])[0]

    assert str(mods["trend_size"]) == str(moderator), condition + " failed"

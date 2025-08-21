import json

import pandas as pd
import pytest
from rdflib import Graph
from rdflib.resource import Resource

from scaffold import context
from scaffold.bitstomach.signals import Achievement
from scaffold.bitstomach.signals._comparison import Comparison
from scaffold.utils.namespace import PSDO, SLOWMO
from scaffold.utils.settings import settings

comparators = [
    {
        "@id": "http://purl.obolibrary.org/obo/PSDO_0000094",
        "@type": ["http://purl.obolibrary.org/obo/PSDO_0000093"],
    },
    {
        "@id": "http://purl.obolibrary.org/obo/PSDO_0000126",
        "@type": [
            "http://purl.obolibrary.org/obo/PSDO_0000093",
            "http://purl.obolibrary.org/obo/PSDO_0000095",
        ],
    },
    {
        "@id": "http://purl.obolibrary.org/obo/PSDO_0000128",
        "@type": [
            "http://purl.obolibrary.org/obo/PSDO_0000093",
            "http://purl.obolibrary.org/obo/PSDO_0000095",
        ],
    },
    {
        "@id": "http://purl.obolibrary.org/obo/PSDO_0000129",
        "@type": [
            "http://purl.obolibrary.org/obo/PSDO_0000093",
            "http://purl.obolibrary.org/obo/PSDO_0000095",
        ],
    },
]
jsonld_str = json.dumps(comparators)

context.subject_graph = Graph().parse(data=jsonld_str, format="json-ld")


@pytest.fixture(autouse=True)
def reset_global():
    yield
    settings.meas_period = 1


@pytest.fixture
def perf_data() -> pd.DataFrame:
    performance_data = [
        [
            "valid",
            "subject",
            "measure",
            "period.start",
            "measureScore.rate",
            "measureScore.denominator",
        ],
        [True, 157, "BP01", "2022-08-01", 0.85, 100.0],
        [True, 157, "BP01", "2022-09-01", 0.86, 100.0],
        [True, 157, "BP01", "2022-10-01", 0.97, 100.0],
    ]
    df = pd.DataFrame(performance_data[1:], columns=performance_data[0])
    df.attrs["performance_month"] = "2022-10-01"

    return df


@pytest.fixture
def perf_data_quarterly() -> pd.DataFrame:
    performance_data = [
        [
            "valid",
            "subject",
            "measure",
            "period.start",
            "measureScore.rate",
            "measureScore.denominator",
        ],
        [True, 157, "BP01", "2022-04-01", 0.85, 100.0],
        [True, 157, "BP01", "2022-07-01", 0.86, 100.0],
        [True, 157, "BP01", "2022-10-01", 0.97, 100.0],
    ]
    df = pd.DataFrame(performance_data[1:], columns=performance_data[0])
    df.attrs["performance_month"] = "2022-10-01"

    return df


@pytest.fixture
def comparator_data() -> pd.DataFrame:
    comparator_data = [
        [
            "measure",
            "period.start",
            "measureScore.rate",
            "group.code",
        ],
        ["BP01", "2022-08-01", 85.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP01", "2022-08-01", 88.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["BP01", "2022-08-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP01", "2022-08-01", 99.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["BP01", "2022-09-01", 85.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP01", "2022-09-01", 89.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["BP01", "2022-09-01", 91.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP01", "2022-09-01", 100.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["BP01", "2022-10-01", 80.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP01", "2022-10-01", 85.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["BP01", "2022-10-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP01", "2022-10-01", 95.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
    ]
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])

    return comparator_df


@pytest.fixture
def comparator_data_quarterly() -> pd.DataFrame:
    comparator_data = [
        [
            "measure",
            "period.start",
            "measureScore.rate",
            "group.code",
        ],
        ["BP01", "2022-04-01", 85.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP01", "2022-04-01", 88.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["BP01", "2022-04-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP01", "2022-04-01", 99.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["BP01", "2022-07-01", 85.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP01", "2022-07-01", 89.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["BP01", "2022-07-01", 91.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP01", "2022-07-01", 100.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["BP01", "2022-10-01", 80.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP01", "2022-10-01", 85.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["BP01", "2022-10-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP01", "2022-10-01", 95.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
    ]
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])

    return comparator_df


def test_signal_properties(perf_data, comparator_data):
    signals = Achievement.detect(perf_data, comparator_data)
    signal = None
    for s in signals:
        if (
            str(Comparison.comparator_type(s))
            == "http://purl.obolibrary.org/obo/PSDO_0000128"
        ):
            signal = s

    assert isinstance(signal, Resource)

    slope = signal.value(SLOWMO.PerformanceTrendSlope).value
    assert slope == pytest.approx(0.06)

    gap = signal.value(SLOWMO.PerformanceGapSize).value
    assert gap == pytest.approx(0.12)

    gap = signal.value(SLOWMO.PriorPerformanceGapSize).value
    assert gap == pytest.approx(-0.03)


def test_signal_properties_quarterly(perf_data_quarterly, comparator_data_quarterly):
    settings.meas_period = 3
    signals = Achievement.detect(perf_data_quarterly, comparator_data_quarterly)
    signal = None
    for s in signals:
        if (
            str(Comparison.comparator_type(s))
            == "http://purl.obolibrary.org/obo/PSDO_0000128"
        ):
            signal = s

    assert isinstance(signal, Resource)

    slope = signal.value(SLOWMO.PerformanceTrendSlope).value
    assert slope == pytest.approx(0.06)

    gap = signal.value(SLOWMO.PerformanceGapSize).value
    assert gap == pytest.approx(0.12)

    gap = signal.value(SLOWMO.PriorPerformanceGapSize).value
    assert gap == pytest.approx(-0.03)


perf_level_test_set = [
    (
        [0.67, 0.79, 0.97],
        [80.0, 85.0, 90.0, 95.0],
        {
            PSDO.peer_90th_percentile_benchmark,
            PSDO.peer_75th_percentile_benchmark,
            PSDO.peer_average_comparator,
            PSDO.goal_comparator_content,
        },
        "achievement all benchmarks",
    ),
    (
        [0.67, 0.95, 0.99],
        [80.0, 96.0, 98.0, 97.0],
        {
            PSDO.peer_90th_percentile_benchmark,
            PSDO.peer_75th_percentile_benchmark,
            PSDO.goal_comparator_content,
        },
        "achievement no peer_average_comparator",
    ),
    (
        [0.67, 0.96, 0.97],
        [80.0, 95.0, 96.5, 95.0],
        {
            PSDO.peer_90th_percentile_benchmark,
        },
        "last month negative gap for 90 percentile",
    ),
    (
        [0.67, 0.98, 0.97],
        [80.0, 95.0, 96.5, 95.0],
        set(),
        "no trend",
    ),
]

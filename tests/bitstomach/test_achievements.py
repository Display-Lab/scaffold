import json
from typing import List

import pandas as pd
import pytest
from rdflib import RDF, BNode, Graph, Literal
from rdflib.resource import Resource

from scaffold import context, startup
from scaffold.bitstomach.signals import Achievement
from scaffold.bitstomach.signals._comparison import Comparison
from scaffold.utils.namespace import PSDO, SLOWMO


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

    g = Graph()
    g.add((BNode("BP01"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("BP01"),PSDO.has_desired_direction, Literal(str(PSDO.desired_increasing_measure))))
    startup.base_graph = g

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
        ["BP01", "2022-08-01", 0.85, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP01", "2022-08-01", 0.88, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["BP01", "2022-08-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP01", "2022-08-01", 0.99, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["BP01", "2022-09-01", 0.85, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP01", "2022-09-01", 0.89, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["BP01", "2022-09-01", 0.91, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP01", "2022-09-01", 1.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["BP01", "2022-10-01", 0.80, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP01", "2022-10-01", 0.85, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["BP01", "2022-10-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP01", "2022-10-01", 0.95, "http://purl.obolibrary.org/obo/PSDO_0000094"],
    ]
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])

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
    return comparator_df


def test_achievement_is_rdf_type():
    g: Graph = Graph()
    mi = g.resource(BNode())
    mi.add(RDF.type, PSDO.achievement_content)

    assert Achievement.is_rdf_type_of(mi)


def test_disposition():
    g: Graph = Graph()

    # Hand create an Achievement with dispositions
    mi: Resource = g.resource(BNode())
    mi.add(RDF.type, PSDO.achievement_content)
    mi.add(RDF.type, PSDO.performance_gap_content)
    mi.add(RDF.type, PSDO.performance_trend_content)

    c = mi.graph.resource(BNode())  # Comparator
    c.add(RDF.type, PSDO.goal_comparator_content)
    mi[SLOWMO.RegardingComparator] = c

    dispositions = Achievement.disposition(mi)
    assert len(dispositions)
    assert g.resource(PSDO.achievement_content) in dispositions


def test_detect_handles_empty_datframe():
    with pytest.raises(ValueError):
        Achievement.detect(pd.DataFrame(), pd.DataFrame())


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


perf_level_test_set = [
    (
        [0.67, 0.79, 0.97],
        [0.80, 0.85, 0.90, 0.95],
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
        [0.80, 0.96, 0.98, 0.97],
        {
            PSDO.peer_90th_percentile_benchmark,
            PSDO.peer_75th_percentile_benchmark,
            PSDO.goal_comparator_content,
        },
        "achievement no peer_average_comparator",
    ),
    (
        [0.67, 0.96, 0.97],
        [0.80, 0.95, 0.965, 0.95],
        {
            PSDO.peer_90th_percentile_benchmark,
        },
        "last month negative gap for 90 percentile",
    ),
    (
        [0.67, 0.98, 0.97],
        [0.80, 0.95, 0.965, 0.95],
        set(),
        "no trend",
    ),
]


@pytest.mark.parametrize(
    "perf_level, comparator_values, types, condition", perf_level_test_set
)
def test_detect_signals(
    perf_level, comparator_values, types, condition, perf_data, comparator_data
):
    perf_data2 = perf_data.assign(**{"measureScore.rate": perf_level})

    # perf_data2.iloc[:, -4:] = comparator_values
    comparator_data["measureScore.rate"] = comparator_values * 3
    signals = Achievement.detect(perf_data2, comparator_data)

    comparators = {
        s.value(SLOWMO.RegardingComparator / RDF.type).identifier for s in signals
    }

    assert comparators == types, condition + " failed"


def test_detect(perf_data, comparator_data):
    g: Graph = Graph()
    comparator = g.resource(BNode())
    comparator[RDF.type] = PSDO.peer_90th_percentile_benchmark
    streap_length = Achievement._detect(perf_data, comparator, comparator_data)
    assert streap_length == 2

    new_row_perf = pd.DataFrame(
        {
            "period.start": "2022-07-01",
            "measureScore.rate": [0.81],
        }
    )
    new_row_comp = pd.DataFrame(
        {
            "period.start": "2022-07-01",
            "measureScore.rate": [0.9],
            "group.code": "http://purl.obolibrary.org/obo/PSDO_0000129",
        }
    )
    perf_data = pd.concat([new_row_perf, perf_data], ignore_index=True)
    comparator_data = pd.concat([new_row_comp, comparator_data], ignore_index=True)
    streap_length = Achievement._detect(perf_data, comparator, comparator_data)
    assert streap_length == 3

    new_row_perf = pd.DataFrame(
        {
            "period.start": "2022-06-01",
            "measureScore.rate": [0.91],
        }
    )

    new_row_comp = pd.DataFrame(
        {
            "period.start": "2022-06-01",
            "measureScore.rate": [0.90],
            "group.code": "http://purl.obolibrary.org/obo/PSDO_0000129",
        }
    )
    perf_data = pd.concat([new_row_perf, perf_data], ignore_index=True)
    comparator_data = pd.concat([new_row_comp, comparator_data], ignore_index=True)
    streap_length = Achievement._detect(perf_data, comparator, comparator_data)
    assert streap_length == 3
    pass


def test_only_current_month_no_achievement(perf_data, comparator_data):
    assert [] == Achievement.detect(
        perf_data[-2:], comparator_data
    )  # Prior month but no trend
    assert [] == Achievement.detect(
        perf_data[-1:], comparator_data
    )  # only current month
    assert [] != Achievement.detect(perf_data[:], comparator_data)  # three months


def test_moderators_return_dictionary():
    assert isinstance(Achievement.moderators([]), List)


def test_moderators():
    gap = 0.02
    prior_gap = -0.03
    slope = 0.1
    graph = Graph()
    r = graph.resource(BNode())
    # add achievement types
    r.add(RDF.type, PSDO.performance_gap_content)
    r.add(RDF.type, PSDO.performance_trend_content)
    r.add(RDF.type, PSDO.achievement_content)

    # add achievement properites
    r.add(SLOWMO.PerformanceGapSize, Literal(gap))
    r.add(SLOWMO.PerformanceTrendSlope, Literal(slope))
    r.add(SLOWMO.PriorPerformanceGapSize, Literal(prior_gap))
    r.add(SLOWMO.StreakLength, Literal(3))
    r.add(SLOWMO.RegardingMeasure, BNode("PONV05"))

    # Add the comparator
    c = graph.resource(BNode())
    c.set(RDF.type, PSDO.peer_90th_percentile_benchmark)
    c.set(RDF.value, Literal(95.0))
    r.add(SLOWMO.RegardingComparator, c)

    moderators = Achievement.moderators([r])

    moderator = [
        moderator
        for moderator in moderators
        if moderator["comparator_type"] == PSDO.peer_90th_percentile_benchmark
    ][0]

    assert moderator["comparison_size"] == abs(gap)
    assert moderator["trend_size"] == abs(slope) * 2
    assert moderator["prior_comparison_size"] == abs(prior_gap)

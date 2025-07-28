import json
from typing import List

import pandas as pd
import pytest
from rdflib import RDF, BNode, Graph, Literal
from rdflib.resource import Resource

from scaffold import context
from scaffold.bitstomach.signals import Loss
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
            "http://purl.obolibrary.org/obo/PSDO_0000126",
            "http://purl.obolibrary.org/obo/PSDO_0000128",
            "http://purl.obolibrary.org/obo/PSDO_0000129",
            "http://purl.obolibrary.org/obo/PSDO_0000094",
        ],
        [True, 157, "BP01", "2022-08-01", 0.97, 100.0, 85.0, 88.0, 90.0, 95.0],
        [True, 157, "BP01", "2022-09-01", 0.96, 100.0, 85.0, 89.0, 91.0, 95.0],
        [True, 157, "BP01", "2022-10-01", 0.94, 100.0, 80.0, 85.0, 90.0, 95.0],
    ]
    df = pd.DataFrame(performance_data[1:], columns=performance_data[0])
    df.attrs["performance_month"] = "2022-10-01"

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
    return df


def test_loss_is_rdf_type():
    g: Graph = Graph()
    mi = g.resource(BNode())
    mi.add(RDF.type, PSDO.loss_content)

    assert Loss.is_rdf_type_of(mi)


def test_disposition():
    g: Graph = Graph()

    # Hand create a Loss with dispositions
    mi: Resource = g.resource(BNode())
    mi.add(RDF.type, PSDO.loss_content)
    mi.add(RDF.type, PSDO.performance_gap_content)
    mi.add(RDF.type, PSDO.performance_trend_content)

    c = mi.graph.resource(BNode())  # Comparator
    c.add(RDF.type, PSDO.goal_comparator_content)
    mi[SLOWMO.RegardingComparator] = c

    dispositions = Loss.disposition(mi)
    assert len(dispositions)
    assert g.resource(PSDO.loss_content) in dispositions


def test_detect_handles_empty_datframe():
    with pytest.raises(ValueError):
        Loss.detect(pd.DataFrame())


def test_signal_properties(perf_data):
    signals = Loss.detect(perf_data)
    assert isinstance(signals[0], Resource)

    slope = signals[0].value(SLOWMO.PerformanceTrendSlope).value
    assert slope == pytest.approx(-0.015)

    gap = signals[0].value(SLOWMO.PerformanceGapSize).value
    assert gap == pytest.approx(-0.01)

    gap = signals[0].value(SLOWMO.PriorPerformanceGapSize).value
    assert gap == pytest.approx(0.01)


perf_level_test_set = [
    (
        [0.97, 0.96, 0.67],
        [80.0, 85.0, 90.0, 95.0],
        {
            PSDO.peer_average_comparator,
            PSDO.peer_75th_percentile_benchmark,
            PSDO.peer_90th_percentile_benchmark,
            PSDO.goal_comparator_content,
        },
        "loss all benchmarks",
    ),
    (
        [0.99, 0.98, 0.67],
        [95.0, 96.0, 99.0, 97.0],
        {
            PSDO.peer_average_comparator,
            PSDO.peer_75th_percentile_benchmark,
            PSDO.goal_comparator_content,
        },
        "loss no peer_90th_percentile_benchmark",
    ),
    (
        [0.97, 0.90, 0.67],
        [80.0, 94.0, 96.5, 95.0],
        {
            PSDO.peer_average_comparator,
        },
        "last month positive gap for peer_average_comparator",
    ),
    (
        [0.97, 0.95, 0.81],
        [80.0, 94.0, 96.5, 95.0],
        {
            PSDO.peer_75th_percentile_benchmark,
            PSDO.goal_comparator_content,
        },
        "last month positive gap for peer_average_comparator",
    ),
    (
        [0.67, 0.98, 0.97],
        [80.0, 94.0, 96.5, 95.0],
        set(),
        "no trend",
    ),
]


@pytest.mark.parametrize(
    "perf_level, comparator_values, types, condition", perf_level_test_set
)
def test_detect_signal(perf_level, comparator_values, types, condition, perf_data):
    perf_data2 = perf_data.assign(**{"measureScore.rate": perf_level})

    perf_data2.iloc[:, -4:] = comparator_values

    signals = Loss.detect(perf_data2)

    comparators = {
        s.value(SLOWMO.RegardingComparator / RDF.type).identifier for s in signals
    }

    assert comparators == types, condition + " failed"


def test_detect(perf_data):
    g: Graph = Graph()
    comparator = g.resource(BNode())
    comparator[RDF.type] = PSDO.goal_comparator_content
    streap_length = Loss._detect(perf_data, comparator)
    assert streap_length == 2

    new_row = pd.DataFrame(
        {
            "measureScore.rate": [0.98],
            "http://purl.obolibrary.org/obo/PSDO_0000094": 95.0,
        }
    )
    perf_data = pd.concat([new_row, perf_data], ignore_index=True)
    streap_length = Loss._detect(perf_data, comparator)
    assert streap_length == 3

    new_row = pd.DataFrame(
        {
            "measureScore.rate": [0.94],
            "http://purl.obolibrary.org/obo/PSDO_0000094": 95.0,
        }
    )
    perf_data = pd.concat([new_row, perf_data], ignore_index=True)
    streap_length = Loss._detect(perf_data, comparator)
    assert streap_length == 3
    pass


def test_only_current_month_no_loss(perf_data):
    assert [] == Loss.detect(perf_data[-2:])  # Prior month but no trend
    assert [] == Loss.detect(perf_data[-1:])  # only current month
    assert [] != Loss.detect(perf_data[:])  # three months


def test_moderators_return_dictionary():
    assert isinstance(Loss.moderators([]), List)


def test_moderators():
    gap = -0.02
    prior_gap = 0.03
    slope = -0.1
    graph = Graph()
    r = graph.resource(BNode())
    # add loss types
    r.add(RDF.type, PSDO.performance_gap_content)
    r.add(RDF.type, PSDO.performance_trend_content)
    r.add(RDF.type, PSDO.loss_content)

    # add loss properites
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

    moderators = Loss.moderators([r])

    moderator = [
        moderator
        for moderator in moderators
        if moderator["comparator_type"] == PSDO.peer_90th_percentile_benchmark
    ][0]

    assert moderator["comparison_size"] == abs(gap)
    assert moderator["trend_size"] == abs(slope) * 2
    assert moderator["prior_comparison_size"] == abs(prior_gap)

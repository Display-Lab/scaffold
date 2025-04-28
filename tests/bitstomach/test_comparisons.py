from typing import List, Tuple

import pandas as pd
import pytest
from rdflib import RDF, BNode, Graph, Literal
from rdflib.resource import Resource

from scaffold.bitstomach.signals import Comparison
from scaffold.utils.namespace import PSDO, SLOWMO


@pytest.fixture
def perf_info() -> Tuple[Graph, Resource]:
    g = Graph()
    r = g.resource(BNode("performance_content"))
    r.set(RDF.type, PSDO.performance_content)
    return g, r


@pytest.fixture
def perf_data() -> pd.DataFrame:
    performance_data = [
        [
            "valid",
            "staff_number",
            "measure",
            "month",
            "passed_rate",
            "passed_count",
            "flagged_count",
            "denominator",
            "peer_average_comparator",
            "peer_75th_percentile_benchmark",
            "peer_90th_percentile_benchmark",
            "goal_comparator_content",
        ],
        [True, 157, "BP01", "2022-08-01", 0.85, 85.0, 0, 100.0, 84.0, 88.0, 90.0, 99.0],
        [
            True,
            157,
            "BP01",
            "2022-09-01",
            0.90,
            90.0,
            0,
            100.0,
            85.0,
            89.0,
            91.0,
            100.0,
        ],
    ]
    return pd.DataFrame(performance_data[1:], columns=performance_data[0])


def test_comp_annotation_creates_minimal_subgraph(perf_data):
    comparison = Comparison.detect(perf_data)
    # logger.info(annotation_graph.serialize(format="json-ld"))

    assert isinstance(comparison, List)
    assert isinstance(comparison[0], Resource)
    assert 4 == len(comparison)
    assert 1 == len(
        set(comparison[0].graph.subjects(RDF.type, PSDO.performance_gap_content))
    )


def test_multiple_signals_from_single_detector(perf_info, perf_data):
    perf_graph, perf_content = perf_info

    signals = Comparison.detect(perf_data)

    assert 4 == len(signals)

    for s in signals:
        perf_content.add(PSDO.motivating_information, s.identifier)
        perf_graph += s.graph

    assert 33 == len(perf_graph)


def test_multiple_gap_values(perf_data):
    signal = Comparison()

    signals = signal.detect(perf_data)

    assert 4 == len(signals)

    expected_gap_sizes = [0.05, 0.01, -0.01, -0.1]

    for index, signal in enumerate(signals):
        v = signal.value(SLOWMO.PerformanceGapSize).value
        assert pytest.approx(v) == expected_gap_sizes[index]


def test_comparator_node(perf_data):
    signal = Comparison()

    signals = signal.detect(perf_data)

    expected_comparator_values = [0.85, 0.89, 0.91, 1.0]

    for index, signal in enumerate(signals):
        assert Literal(expected_comparator_values[index]) == signal.value(
            SLOWMO.RegardingComparator / RDF.value
        )


def test_empty_performance_content_returns_value_error():
    mi = Comparison()
    with pytest.raises(ValueError):
        mi.detect(pd.DataFrame([[]]))


def test_moderators_return_dictionary():
    assert isinstance(Comparison.moderators([]), List)


def test_moderators_return_dictionary1():
    gap = 23
    graph = Graph()
    r = graph.resource(BNode())
    r.add(RDF.type, PSDO.performance_gap_content)
    r.add(SLOWMO.PerformanceGapSize, Literal(gap))
    r.add(
        RDF.type,
        PSDO.positive_performance_gap_content
        if gap >= 0
        else PSDO.negative_performance_gap_content,
    )
    r.add(SLOWMO.RegardingMeasure, BNode("PONV05"))

    # Add the comparator
    c = graph.resource(BNode())
    c.set(RDF.type, PSDO.peer_90th_percentile_benchmark)
    c.set(RDF.value, Literal(95.0))

    r.add(SLOWMO.RegardingComparator, c)

    moderators = Comparison.moderators([r])

    moderator = [
        moderator
        for moderator in moderators
        if moderator["comparator_type"] == PSDO.peer_90th_percentile_benchmark
    ][0]

    assert moderator["comparison_size"] == 23


def test_comparison_has_super_type(perf_data):
    signal = Comparison()

    signals = signal.detect(perf_data)

    s = signals[0]
    assert s.graph.resource(PSDO.motivating_information) in s[RDF.type]
    assert s.graph.resource(PSDO.performance_gap_content) in s[RDF.type]
    assert s.graph.resource(PSDO.positive_performance_gap_content) in s[RDF.type]

    assert s.graph.resource(PSDO.social_comparator_content) not in s[RDF.type]


def test_can_get_dispositions(perf_data, perf_info):
    g, perf_content = perf_info

    # given
    comparator = g.resource(PSDO.peer_average_comparator)
    comparator.add(RDF.type, PSDO.social_comparator_content)

    signal = Comparison()
    signals = signal.detect(perf_data)

    s = signals[0]  # positive performance gap to peer average

    perf_content.add(PSDO.motivating_information, s)
    g += s.graph
    #
    matching_types = Comparison.disposition(g.resource(s.identifier))

    assert g.resource(PSDO.motivating_information) in matching_types
    assert g.resource(PSDO.performance_gap_content) in matching_types
    assert g.resource(PSDO.positive_performance_gap_content) in matching_types

    assert g.resource(PSDO.peer_average_comparator) in matching_types

    assert g.resource(PSDO.social_comparator_content) in matching_types


def test_detect1(perf_data):
    gaps: dict = Comparison._detect(perf_data[-1:])

    assert gaps["peer_90th_percentile_benchmark"][0] == pytest.approx(-0.01)

import json
from typing import List, Tuple

import pandas as pd
import pytest
from rdflib import RDF, BNode, Graph, Literal
from rdflib.resource import Resource

from scaffold import startup
from scaffold import context
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
            "subject",
            "measure",
            "period.start",
            "measureScore.rate",
            "measureScore.denominator",
        ],
        [True, 157, "BP01", "2022-08-01", 0.85, 100.0],
        [True, 157, "BP01", "2022-09-01", 0.90, 100.0],
        [True, 157, "BP02", "2022-08-01", 0.15, 100.0],
        [True, 157, "BP02", "2022-09-01", 0.14, 100.0],
    ]
    
    g = Graph()
    g.add((BNode("BP01"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("BP01"), PSDO.has_desired_direction, Literal(str(PSDO.desired_increasing_measure))))
    g.add((BNode("BP02"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("BP02"), PSDO.has_desired_direction, Literal(str(PSDO.desired_decreasing_measure))))
    startup.base_graph = g


    return pd.DataFrame(performance_data[1:], columns=performance_data[0])


@pytest.fixture
def comparator_data() -> pd.DataFrame:
    comparator_data = [
        [
            "measure",
            "period.start",
            "measureScore.rate",
            "group.code",
        ],
        ["BP01", "2022-08-01", 0.84, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP01", "2022-08-01", 0.88, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["BP01", "2022-08-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP01", "2022-08-01", 0.99, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["BP01", "2022-09-01", 0.85, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP01", "2022-09-01", 0.89, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["BP01", "2022-09-01", 0.91, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP01", "2022-09-01", 1.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["BP02", "2022-08-01", 0.16, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP02", "2022-08-01", 0.105, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP02", "2022-08-01", 0.10, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["BP02", "2022-09-01", 0.16, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["BP02", "2022-09-01", 0.105, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["BP02", "2022-09-01", 0.10, "http://purl.obolibrary.org/obo/PSDO_0000094"],
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





def test_comp_annotation_creates_minimal_subgraph(perf_data, comparator_data):
    BP01_perf_data = perf_data [perf_data["measure"] == "BP01"]
    BP01_comp_data = comparator_data [comparator_data["measure"] == "BP01"]
    
    comparison = Comparison.detect(BP01_perf_data, BP01_comp_data)

    assert isinstance(comparison, List)
    assert isinstance(comparison[0], Resource)
    assert 4 == len(comparison)
    assert 1 == len(
        set(comparison[0].graph.subjects(RDF.type, PSDO.performance_gap_content))
    )
    
    BP02_perf_data = perf_data [perf_data["measure"] == "BP02"]
    BP02_comp_data = comparator_data [comparator_data["measure"] == "BP02"]
    comparison = Comparison.detect(BP02_perf_data, BP02_comp_data)
    assert isinstance(comparison, List)
    assert isinstance(comparison[0], Resource)
    assert 3 == len(comparison)
    assert 1 == len(
        set(comparison[0].graph.subjects(RDF.type, PSDO.performance_gap_content))
    )


def test_multiple_signals_from_single_detector(perf_info, perf_data, comparator_data):
    perf_graph, perf_content = perf_info

    BP01_perf_data = perf_data [perf_data["measure"] == "BP01"]
    BP01_comp_data = comparator_data [comparator_data["measure"] == "BP01"]
    signals = Comparison.detect(BP01_perf_data, BP01_comp_data)

    assert 4 == len(signals)

    for s in signals:
        perf_content.add(PSDO.motivating_information, s.identifier)
        perf_graph += s.graph

    assert 33 == len(perf_graph)
    
    perf_graph, perf_content = perf_info
    BP02_perf_data = perf_data [perf_data["measure"] == "BP02"]
    BP02_comp_data = comparator_data [comparator_data["measure"] == "BP02"]

    signals = Comparison.detect(BP02_perf_data, BP02_comp_data)

    assert 3 == len(signals)

    for s in signals:
        perf_content.add(PSDO.motivating_information, s.identifier)
        perf_graph += s.graph

    assert 57 == len(perf_graph)


def test_multiple_gap_values(perf_data, comparator_data):
    signal = Comparison()

    BP01_perf_data = perf_data [perf_data["measure"] == "BP01"]
    BP01_comp_data = comparator_data [comparator_data["measure"] == "BP01"]

    signals = signal.detect(BP01_perf_data, BP01_comp_data)

    assert 4 == len(signals)

    expected_gap_sizes = [-0.1, 0.05, 0.01, -0.01]

    for index, signal in enumerate(signals):
        v = signal.value(SLOWMO.PerformanceGapSize).value
        assert pytest.approx(v) == expected_gap_sizes[index]
        
    
    signal = Comparison()    
    BP02_perf_data = perf_data [perf_data["measure"] == "BP02"]
    BP02_comp_data = comparator_data [comparator_data["measure"] == "BP02"]
    signals = signal.detect(BP02_perf_data, BP02_comp_data)

    assert 3 == len(signals)

    expected_gap_sizes = [0.04, -0.02,0.035]

    for index, signal in enumerate(signals):
        v = signal.value(SLOWMO.PerformanceGapSize).value
        assert pytest.approx(v) == expected_gap_sizes[index]


def test_comparator_node(perf_data, comparator_data):
    signal = Comparison()
    
    
    BP01_perf_data = perf_data [perf_data["measure"] == "BP01"]
    BP01_comp_data = comparator_data [comparator_data["measure"] == "BP01"]

    signals = signal.detect(BP01_perf_data, BP01_comp_data)

    expected_comparator_values = [1.0, 0.85, 0.89, 0.91]

    for index, signal in enumerate(signals):
        assert Literal(expected_comparator_values[index]) == signal.value(
            SLOWMO.RegardingComparator / RDF.value
        )
    
        signal = Comparison()
    
    
    BP02_perf_data = perf_data [perf_data["measure"] == "BP02"]
    BP02_comp_data = comparator_data [comparator_data["measure"] == "BP02"]

    signals = signal.detect(BP02_perf_data, BP02_comp_data)

    expected_comparator_values = [0.10, 0.16, 0.105]

    for index, signal in enumerate(signals):
        assert Literal(expected_comparator_values[index]) == signal.value(
            SLOWMO.RegardingComparator / RDF.value
        )


def test_empty_performance_content_returns_value_error():
    mi = Comparison()
    with pytest.raises(ValueError):
        mi.detect(pd.DataFrame([[]]), pd.DataFrame([[]]))


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


def test_comparison_has_super_type(perf_data, comparator_data):
    signal = Comparison()
    BP01_perf_data = perf_data [perf_data["measure"] == "BP01"]
    BP01_comp_data = comparator_data [comparator_data["measure"] == "BP01"]

    signals = signal.detect(BP01_perf_data, BP01_comp_data)

    s = signals[1]
    assert s.graph.resource(PSDO.motivating_information) in s[RDF.type]
    assert s.graph.resource(PSDO.performance_gap_content) in s[RDF.type]
    assert s.graph.resource(PSDO.positive_performance_gap_content) in s[RDF.type]

    assert s.graph.resource(PSDO.social_comparator_content) not in s[RDF.type]


def test_can_get_dispositions(perf_data, perf_info, comparator_data):
    g, perf_content = perf_info

    # given
    comparator = g.resource(PSDO.peer_average_comparator)
    comparator.add(RDF.type, PSDO.social_comparator_content)

    signal = Comparison()
    BP01_perf_data = perf_data [perf_data["measure"] == "BP01"]
    BP01_comp_data = comparator_data [comparator_data["measure"] == "BP01"]
    signals = signal.detect(BP01_perf_data, BP01_comp_data)

    s = signals[1]  # positive performance gap to peer average

    perf_content.add(PSDO.motivating_information, s)
    g += s.graph
    #
    matching_types = Comparison.disposition(g.resource(s.identifier))

    assert g.resource(PSDO.motivating_information) in matching_types
    assert g.resource(PSDO.performance_gap_content) in matching_types
    assert g.resource(PSDO.positive_performance_gap_content) in matching_types

    assert g.resource(PSDO.peer_average_comparator) in matching_types

    assert g.resource(PSDO.social_comparator_content) in matching_types


def test_detect1(perf_data, comparator_data):
    BP01_perf_data = perf_data [perf_data["measure"] == "BP01"]
    BP01_comp_data = comparator_data [comparator_data["measure"] == "BP01"]
    gaps: dict = Comparison._detect(BP01_perf_data[-1:], BP01_comp_data)

    assert gaps["http://purl.obolibrary.org/obo/PSDO_0000129"][0] == pytest.approx(
        -0.01
    )

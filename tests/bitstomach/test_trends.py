from typing import List
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from rdflib import RDF, BNode, Graph, Literal, URIRef
from rdflib.resource import Resource

from scaffold import startup
from scaffold.bitstomach.signals import Comparison, Trend
from scaffold.utils import PSDO, SLOWMO
@pytest.fixture
def setup_base_graph():
    g = Graph()
    g.add((BNode("BP01"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("BP01"),PSDO.has_desired_direction, Literal(str(PSDO.desired_increase))))
    g.add((BNode("BP02"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("BP02"),PSDO.has_desired_direction, Literal(str(PSDO.desired_decrease))))
    startup.base_graph = g

## Trend resource
def test_empty_perf_data_raises_value_error():
    with pytest.raises(ValueError):
        Trend().detect(pd.DataFrame())


def test_no_trend_returns_none(setup_base_graph):
    df = pd.DataFrame(
            {
                "measure":["BP01","BP01","BP01","BP02","BP02","BP02"],
                "measureScore.rate": [90, 90, 90,0.10, 0.11, 0.08],
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01","2023-11-01", "2023-12-01", "2024-01-01"],
                "valid": [True, True, True, True, True, True],
            },
        )
    
    mi = Trend.detect(
        df[df["measure"]=="BP01"]
    )
    assert mi == []

    mi = Trend.detect(
        df[df["measure"]=="BP02"]
    )
    assert mi == []

## Signal detection tests
def test_trend_is_detected():
    slope = Trend._detect(
        pd.DataFrame(columns=["measureScore.rate"], data=[[90], [91], [92]]), PSDO.desired_increase
    )
    assert slope == 1

    slope = Trend._detect(
        pd.DataFrame(columns=["measureScore.rate"], data=[[90], [92], [94]]), PSDO.desired_increase
    )
    assert slope == 2

    slope = Trend._detect(
        pd.DataFrame(columns=["measureScore.rate"], data=[[90], [92], [90], [92], [94]]), PSDO.desired_increase
    )
    assert slope == 2
    
    slope = Trend._detect(
        pd.DataFrame(columns=["measureScore.rate"], data=[[0.14], [0.12], [0.10]]), PSDO.desired_decrease
    )
    assert pytest.approx(slope) == 0.02

    slope = Trend._detect(
        pd.DataFrame(columns=["measureScore.rate"], data=[[0.10], [0.15], [0.20]]) , PSDO.desired_decrease
    )
    assert pytest.approx(slope) == -0.05

    slope = Trend._detect(
        pd.DataFrame(columns=["measureScore.rate"], data=[[0.10], [0.15], [0.10], [0.15], [0.20]]), PSDO.desired_decrease
    )
    assert pytest.approx(slope) == -0.05


def test_trend_as_resource():
    df = pd.DataFrame(
            {
                "measure":["BP01","BP01","BP01","BP02","BP02","BP02"],
                "measureScore.rate": [90, 91, 92, 0.14, 0.12, 0.10],
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01", "2023-11-01", "2023-12-01", "2024-01-01"],
                "valid": [True, True, True, True, True, True],
            },
        )
    signal = Trend.detect(
        df[df["measure"]=="BP01"], PSDO.desired_increase
    ).pop()

    assert isinstance(signal, Resource)

    assert Trend.is_rdf_type_of(signal)
    # assert signal.value(RDF.type).identifier == PSDO.performance_trend_content
    assert signal.value(SLOWMO.PerformanceTrendSlope) == Literal(1.0)
    
    assert signal.value(SLOWMO.PerformanceTrendSlope) == Literal(1.0)

    signal = Trend.detect(
        df[df["measure"]=="BP02"], PSDO.desired_decrease
    ).pop()

    assert isinstance(signal, Resource)

    assert Trend.is_rdf_type_of(signal)
    # assert signal.value(RDF.type).identifier == PSDO.performance_trend_content
    assert pytest.approx(signal.value(SLOWMO.PerformanceTrendSlope).value) == 0.02
    

def test_to_moderators_returns_dictionary():
    assert isinstance(Trend.moderators([]), List)


def test_to_moderators_return_dictionary1():
    r = Graph().resource(BNode())
    r.add(RDF.type, PSDO.performance_trend_content)
    slope = 2.0
    r.add(SLOWMO.PerformanceTrendSlope, Literal(slope))
    r.add(RDF.type, PSDO.performance_trend_content)
    r.add(RDF.type, PSDO.positive_performance_trend_content)

    r.add(SLOWMO.RegardingMeasure, BNode("PONV05"))

    mods = Trend.moderators([r])[0]
    assert pytest.approx(slope * 2) == mods["trend_size"]

    assert PSDO.performance_trend_content in mods["type"]
    assert PSDO.positive_performance_trend_content in mods["type"]


def test_resource_selects_pos_or_neg():
    r = Trend._resource(3.0)
    types = [t.identifier for t in list(r[RDF.type])]
    assert PSDO.positive_performance_trend_content in types
    assert PSDO.negative_performance_trend_content not in types

    r = Trend._resource(-1.0)
    types = [t.identifier for t in list(r[RDF.type])]
    assert PSDO.positive_performance_trend_content not in types
    assert PSDO.negative_performance_trend_content in types

    r = Trend._resource(0.0)
    types = [t.identifier for t in list(r[RDF.type])]
    assert PSDO.positive_performance_trend_content not in types
    assert PSDO.negative_performance_trend_content not in types
    
    r = Trend._resource(3.0)
    types = [t.identifier for t in list(r[RDF.type])]
    assert PSDO.negative_performance_trend_content not in types
    assert PSDO.positive_performance_trend_content in types

    r = Trend._resource(-1.0)
    types = [t.identifier for t in list(r[RDF.type])]
    assert PSDO.negative_performance_trend_content in types
    assert PSDO.positive_performance_trend_content not in types

    r = Trend._resource(0.0)
    types = [t.identifier for t in list(r[RDF.type])]
    assert PSDO.negative_performance_trend_content not in types
    assert PSDO.positive_performance_trend_content not in types


def test_select_ignores_signals_of_a_different_type():
    comparator_data = [
        [
            "period.start",
            "measureScore.rate",
            "group.code",
        ],
        ["2023-11-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["2023-11-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["2023-11-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["2023-11-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
    ]
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])
    r1 = Comparison().detect(
        pd.DataFrame(
            columns=["measure","period.start", "valid", "measureScore.rate"],
            data=[["BP01","2023-11-01", True, 0.80]],
        ),
        comparator_df,
    )

    r2 = Trend.detect(
        pd.DataFrame(
            {
                "measure":"BP01",
                "measureScore.rate": [89, 90, 91],
                "valid": True,
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
            },
        )
    )

    mi = r1 + r2  # four comparisons and one trend

    selected_mi = Trend.select(mi)
    assert len(selected_mi) == 1
    assert PSDO.performance_trend_content in [
        t.identifier for t in selected_mi[0][RDF.type]
    ]

    selected_mi = Trend.select(r1)
    assert len(selected_mi) == 0

    selected_mi = Trend.select([])
    assert len(selected_mi) == 0

    selected_mi = Trend.select(r2)
    assert len(selected_mi) == 1
    assert selected_mi == r2

    Trend.signal_type

    comparator_data = [
        [
            "period.start",
            "measureScore.rate",
            "group.code",
        ],
        ["2023-11-01", 0.12, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["2023-11-01", 0.12, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["2023-11-01", 0.12, "http://purl.obolibrary.org/obo/PSDO_0000094"],
    ]
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])
    r1 = Comparison().detect(
        pd.DataFrame(
            columns=["measure","period.start", "valid", "measureScore.rate"],
            data=[["BP02","2023-11-01", True, 0.11]],
        ),
        comparator_df,
    )

    r2 = Trend.detect(
        pd.DataFrame(
            {
                "measure":"BP02",
                "measureScore.rate": [0.14, 0.12, 0.10],
                "valid": True,
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
            },
        )
    )

    mi = r1 + r2  # four comparisons and one trend

    selected_mi = Trend.select(mi)
    assert len(selected_mi) == 1
    assert PSDO.performance_trend_content in [
        t.identifier for t in selected_mi[0][RDF.type]
    ]

    selected_mi = Trend.select(r1)
    assert len(selected_mi) == 0

    selected_mi = Trend.select([])
    assert len(selected_mi) == 0

    selected_mi = Trend.select(r2)
    assert len(selected_mi) == 1
    assert selected_mi == r2
def test_trend_identity():
    r1 = Trend.detect(
        pd.DataFrame(
            {
                "measure":"BP01",
                "measureScore.rate": [89, 90, 91],
                "valid": True,
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
            },
        )
    )
    r2 = Trend.detect(
        pd.DataFrame(
            {
                "measure":"BP01",
                "measureScore.rate": [89, 90, 91],
                "valid": True,
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
            },
        )
    )

    assert r1 is not r2

    r1a = Trend.select(r1)

    assert r1.pop() is r1a.pop()


# @pytest.mark.skip("boo")
@patch.object(Trend, "_detect")
def test_partial_mock(mock_detect: Mock):
    mock_detect.return_value = 42.0

    signal = Trend.detect(
        pd.DataFrame(
            {
                "measure":"BP01",
                "measureScore.rate": [89, 90, 91],
                "valid": True,
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
            },  # slope 1.0
        )
    )

    assert signal[0].value(SLOWMO.PerformanceTrendSlope) == Literal(42.0)


@patch.object(Trend, "_detect")
def test_partial_mock_with_patch_decorator(mock_detect: Mock):
    class TypeMatcher:
        def __init__(self, expected_type):
            self.expected_type = expected_type

        def __eq__(self, other):
            return isinstance(other, self.expected_type)

    mock_detect.return_value = 42.0
    
    g = Graph()
    g.add((BNode("BP01"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("BP01"),PSDO.has_desired_direction, Literal(str(PSDO.desired_increase))))
    g.add((BNode("BP02"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("BP02"),PSDO.has_desired_direction, Literal(str(PSDO.desired_decrease))))
    startup.base_graph = g

    signal = Trend.detect(
        pd.DataFrame(
            {
                "measure":"BP01",
                "measureScore.rate": [89, 90, 91],
                "valid": True,
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
            },  # slope 1.0
        )
    )

    mock_detect.assert_called_once_with(TypeMatcher(pd.DataFrame),TypeMatcher(URIRef))

    assert signal[0].value(SLOWMO.PerformanceTrendSlope) == Literal(42.0)


def test_partial_mock_using_with():
    with patch.object(Trend, "_detect", return_value=42.0):
        signal = Trend.detect(
            pd.DataFrame(
                {
                    "measure":"BP01",
                    "measureScore.rate": [89, 90, 91],
                    "valid": True,
                    "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
                },  # slope 1.0
            )
        )

    assert signal[0].value(SLOWMO.PerformanceTrendSlope) == Literal(42.0)

    # TODO: Try some https://mockito-python.readthedocs.io

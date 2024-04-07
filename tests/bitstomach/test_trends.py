from typing import List
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from rdflib import RDF, BNode, Graph, Literal
from rdflib.resource import Resource

from bitstomach.signals import Comparison, Trend
from utils import PSDO, SLOWMO


## Trend resource
def test_empty_perf_data_raises_value_error():
    with pytest.raises(ValueError):
        Trend().detect(pd.DataFrame())


def test_no_trend_returns_none():
    mi = Trend.detect(
        pd.DataFrame(
            {"passed_rate": [90, 90, 90]},
        )
    )
    assert mi is None


## Signal detection tests
def test_trend_is_detected():
    slope = Trend._detect(
        pd.DataFrame(columns=["passed_rate"], data=[[90], [91], [92]])
    )
    assert slope == 1

    slope = Trend._detect(
        pd.DataFrame(columns=["passed_rate"], data=[[90], [92], [94]])
    )
    assert slope == 2

    slope = Trend._detect(
        pd.DataFrame(columns=["passed_rate"], data=[[90], [92], [90], [92], [94]])
    )
    assert slope == 2


def test_trend_as_resource():
    signal = Trend.detect(
        pd.DataFrame(columns=["passed_rate"], data=[[90], [91], [92]])
    ).pop()

    assert isinstance(signal, Resource)

    assert Trend.is_rdf_type_of(signal)
    # assert signal.value(RDF.type).identifier == PSDO.performance_trend_content
    assert signal.value(SLOWMO.PerformanceTrendSlope) == Literal(1.0)


def test_to_moderators_returns_dictionary():
    assert isinstance(Trend.moderators([]), List)


def test_to_moderators_return_dictionary1():
    r = Graph().resource(BNode())
    r.add(RDF.type, PSDO.performance_trend_content)
    r.add(SLOWMO.PerformanceTrendSlope, Literal(2.0))
    r.add(RDF.type, PSDO.performance_trend_content)
    r.add(RDF.type, PSDO.positive_performance_trend_content)

    r.add(SLOWMO.RegardingMeasure, BNode("PONV05"))

    trend = Trend.moderators([r])[0]
    assert pytest.approx(2) == trend["trend_size"]

    assert PSDO.performance_trend_content in trend["type"]
    assert PSDO.positive_performance_trend_content in trend["type"]


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


def test_select():
    r1 = Comparison().detect(
        pd.DataFrame(
            columns=[
                "measure",
                "passed_rate",
                "peer_average_comparator",
                "peer_75th_percentile_benchmark",
                "peer_90th_percentile_benchmark",
                "goal_comparator_content",
            ],
            data=[["PONV05", 80, 90, 90, 90, 90]],
        )
    )

    r2 = Trend.detect(
        pd.DataFrame(
            {"passed_rate": [89, 90, 91]},
        )
    )

    mi = r1 + r2

    assert len(mi) == 5

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


def test_trend_identity():
    r1 = Trend.detect(
        pd.DataFrame(
            {"passed_rate": [89, 90, 91]},
        )
    )
    r2 = Trend.detect(
        pd.DataFrame(
            {"passed_rate": [89, 90, 91]},
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
            {"passed_rate": [89, 90, 91]},  # slope 1.0
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

    signal = Trend.detect(
        pd.DataFrame(
            {"passed_rate": [89, 90, 91]},  # slope 1.0
        )
    )

    mock_detect.assert_called_once_with(TypeMatcher(pd.DataFrame))

    assert signal[0].value(SLOWMO.PerformanceTrendSlope) == Literal(42.0)


def test_partial_mock_using_with():
    with patch.object(Trend, "_detect", return_value=42.0):
        signal = Trend.detect(
            pd.DataFrame(
                {"passed_rate": [89, 90, 91]},  # slope 1.0
            )
        )

    assert signal[0].value(SLOWMO.PerformanceTrendSlope) == Literal(42.0)

    # TODO: Try some https://mockito-python.readthedocs.io

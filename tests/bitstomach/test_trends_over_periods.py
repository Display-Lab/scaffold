import pandas as pd
import pytest
from rdflib import RDF, BNode, Graph, Literal
from rdflib.resource import Resource

from scaffold import startup
from scaffold.bitstomach.signals import Trend
from scaffold.utils import SLOWMO
from scaffold.utils.namespace._PSDO import PSDO
from scaffold.utils.settings import settings

g = Graph()
g.add((BNode("BP01"), RDF.type, PSDO.performance_measure_content))
g.add((BNode("BP01"), PSDO.has_desired_direction, Literal(str(PSDO.desired_increasing_measure))))
startup.base_graph = g

@pytest.fixture(autouse=True)
def reset_global():
    yield
    settings.meas_period = 1


def test_no_trend_returns_none():
    mi = Trend.detect(
        pd.DataFrame(
            {
                "measure":"BP01",
                "measureScore.rate": [90, 90, 90],
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
                "valid": True,
            },
        )
    )
    assert mi == []

    mi = Trend.detect(
        pd.DataFrame(
            {
                "measure":"BP01",
                "measureScore.rate": [90, 90, 90],
                "period.start": ["2024-01-01", "2024-04-01", "2024-05-01"],
                "valid": True,
            },
        )
    )
    assert mi == []


## Signal detection tests
def test_trend_is_detected():
    slope = Trend._detect(
        pd.DataFrame(columns=["measureScore.rate"], data=[[90], [91], [92]])
    )
    assert slope == 1

    slope = Trend._detect(
        pd.DataFrame(columns=["measureScore.rate"], data=[[90], [92], [94]])
    )
    assert slope == 2

    slope = Trend._detect(
        pd.DataFrame(columns=["measureScore.rate"], data=[[90], [92], [90], [92], [94]])
    )
    assert slope == 2


def test_trend_as_resource():
    signal = Trend.detect(
        pd.DataFrame(
            {
                "measure":"BP01",
                "measureScore.rate": [90, 91, 92],
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
                "valid": True,
            },
        )
    ).pop()

    assert isinstance(signal, Resource)

    assert Trend.is_rdf_type_of(signal)
    # assert signal.value(RDF.type).identifier == PSDO.performance_trend_content
    assert signal.value(SLOWMO.PerformanceTrendSlope) == Literal(1.0)
    settings.meas_period = 3
    signal = Trend.detect(
        pd.DataFrame(
            {
                "measure":"BP01",
                "measureScore.rate": [90, 91, 92],
                "period.start": ["2024-01-01", "2024-04-01", "2024-07-01"],
                "valid": True,
            },
        )
    ).pop()

    assert isinstance(signal, Resource)

    assert Trend.is_rdf_type_of(signal)
    # assert signal.value(RDF.type).identifier == PSDO.performance_trend_content
    assert signal.value(SLOWMO.PerformanceTrendSlope) == Literal(1.0)

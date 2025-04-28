import pytest
from rdflib import RDF, BNode, Graph, Literal

from scaffold.esteemer import utils
from scaffold.utils.namespace import SLOWMO


@pytest.fixture
def graph():
    graph = Graph()
    candidate1 = graph.resource(BNode("candidate1"))
    candidate1[RDF.type] = SLOWMO.Candidate
    candidate1[SLOWMO.RegardingMeasure] = BNode("PONV05")
    candidate1[SLOWMO.AcceptableBy] = Literal("improving")

    candidate2 = graph.resource(BNode("candidate2"))
    candidate2[RDF.type] = SLOWMO.Candidate
    candidate2[SLOWMO.RegardingMeasure] = BNode("SUS02")
    candidate2[SLOWMO.AcceptableBy] = Literal("worsening")

    candidate3 = graph.resource(BNode("candidate3"))
    candidate3[RDF.type] = SLOWMO.Candidate
    candidate3[SLOWMO.RegardingMeasure] = BNode("PONV05")

    candidate4 = graph.resource(BNode("candidate4"))
    candidate4[RDF.type] = SLOWMO.Candidate
    candidate4[SLOWMO.RegardingMeasure] = BNode("SUS02")

    return graph


def test_candidates_returns_the_one_acceptable_for_measure(graph):
    measure_candidates = utils.candidates(
        graph, BNode("PONV05"), True
    )  # only one acceptable candidate

    assert len(measure_candidates) == 1

    assert measure_candidates[0].value(SLOWMO.RegardingMeasure).identifier == BNode(
        "PONV05"
    )


def test_candidates_returns_all_acceptable(graph):
    acceptable_candidates = utils.candidates(graph, None, True)

    assert len(acceptable_candidates) == 2

    assert acceptable_candidates[0].value(SLOWMO.RegardingMeasure).identifier in [
        BNode("PONV05"),
        BNode("SUS02"),
    ]


def test_candidates_all(graph):
    candidates = utils.candidates(graph, None, False)

    assert len(candidates) == 4
    assert candidates[0].value(SLOWMO.RegardingMeasure).identifier in [
        BNode("PONV05"),
        BNode("SUS02"),
    ]


def test_candidates_empty_or_no_match(graph):
    candidates = utils.candidates(graph, measure=BNode("nope"))

    assert len(candidates) == 0

    candidates = utils.candidates(Graph())

    assert len(candidates) == 0

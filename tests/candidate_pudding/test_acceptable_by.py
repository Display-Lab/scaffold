import pytest
from rdflib import RDF, XSD, BNode, Graph, Literal, URIRef

from scaffold.bitstomach.signals import Trend
from scaffold.candidate_pudding import candidate_pudding
from scaffold.utils.namespace import IAO, PSDO, SLOWMO

IMPROVING_TEMPLATE = URIRef(
    "https://repo.metadatacenter.org/template-instances/0ae1872f-5593-4891-8713-7d5e815c0b00"
)
CPO_has_preconditions = URIRef(
    "http://purl.bioontology.org/ontology/SNOMEDCT/has_precondition"
)


@pytest.fixture
def graph():
    graph = Graph()

    measure = graph.resource(BNode("PONV05"))
    measure[RDF.type] = PSDO.performance_measure_content

    template = graph.resource(IMPROVING_TEMPLATE)
    template[RDF.type] = candidate_pudding.PERFORMANCE_SUMMARY_DISPLAY_TEMPLATE
    template[
        URIRef(
            "https://schema.metadatacenter.org/properties/6b9dfdf9-9c8a-4d85-8684-a24bee4b85a8"
        )
    ] = Literal(
        "Your performance is improving this month for the measure [measure name]. Your performance was [recipient performance level]."
    )
    template.add(IAO.is_about, PSDO.positive_performance_trend_set)
    template.add(
        URIRef("http://schema.org/name"),
        Literal("Performance Improving", datatype=XSD.string),
    )
    template[
        URIRef(
            "https://schema.metadatacenter.org/properties/5b4f16a9-feb7-4724-8741-2739d8808760"
        )
    ] = Literal("Line chart")
    template[URIRef("http://purl.obolibrary.org/obo/cpo_0000056")] = URIRef(
        "https://repo.metadatacenter.org/template-instances/0b160448-c376-476d-b4a9-5e8a5496eaf0"
    )

    performance_content = graph.resource(BNode("performance_content"))
    performance_content.set(RDF.type, PSDO.performance_content)
    signal = Trend._resource(2.0, PSDO.desired_increasing_measure)
    signal.add(SLOWMO.RegardingMeasure, measure)
    performance_content.add(PSDO.motivating_information, signal)
    graph += signal.graph

    causal_pathway = graph.resource(
        URIRef(
            "https://repo.metadatacenter.org/template-instances/0b160448-c376-476d-b4a9-5e8a5496eaf0"
        )
    )
    causal_pathway[URIRef("http://schema.org/name")] = Literal(
        "improving", datatype=XSD.string
    )
    causal_pathway.add(CPO_has_preconditions, PSDO.positive_performance_trend_content)
    causal_pathway.add(CPO_has_preconditions, PSDO.positive_performance_trend_set)

    return graph


def test_create_candidate(graph):
    # given
    measure = graph.resource(BNode("PONV05"))
    template = graph.resource(IMPROVING_TEMPLATE)

    # when
    candidate = candidate_pudding.create_candidate(measure, template)

    # then
    assert candidate.value(SLOWMO.RegardingMeasure) == measure
    assert candidate.value(SLOWMO.AncestorTemplate) == template


def test_accaptable_by(graph):
    # given
    measure = graph.resource(BNode("PONV05"))
    template = graph.resource(IMPROVING_TEMPLATE)
    candidate = candidate_pudding.create_candidate(measure, template)

    # when
    candidate = candidate_pudding.acceptable_by(candidate)

    # then
    assert candidate.value(SLOWMO.AcceptableBy).value == Literal("improving").value

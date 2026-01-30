import pytest
from rdflib import RDF, XSD, BNode, Graph, Literal, URIRef
from rdflib.resource import Resource

from scaffold.bitstomach.signals import Comparison, Trend
from scaffold.candidate_pudding import candidate_pudding
from scaffold.utils.namespace import IAO, PSDO, RO, SLOWMO


@pytest.fixture
def graph():
    graph = Graph()

    measure = graph.resource(BNode("PONV05"))
    measure[RDF.type] = PSDO.performance_measure_content

    template = graph.resource(
        URIRef(
            "https://repo.metadatacenter.org/template-instances/9e71ec9e-26f3-442a-8278-569bcd58e708"
        )
    )
    template[RDF.type] = candidate_pudding.PERFORMANCE_SUMMARY_DISPLAY_TEMPLATE
    template[PSDO.has_desired_direction] = Literal(PSDO.desired_increasing_measure)
    template[
        URIRef(
            "https://schema.metadatacenter.org/properties/6b9dfdf9-9c8a-4d85-8684-a24bee4b85a8"
        )
    ] = Literal(
        "You may have an opportunity to improve for the measure [measure name]. Your performance was [recipient performance level], below the top 10% peer benchmark, which was [comparator performance level] this month."
    )
    template[URIRef("http://purl.obolibrary.org/obo/cpo_0000056")] = URIRef(
        "https://repo.metadatacenter.org/template-instances/f4006042-5750-4f6c-a039-fe0a88466464"
    )
    template.add(IAO.is_about, PSDO.negative_performance_gap_set)
    template.add(IAO.is_about, PSDO.peer_90th_percentile_benchmark)
    template.add(
        URIRef("http://schema.org/name"),
        Literal("Opportunity to Improve Top 10 Peer Benchmark", datatype=XSD.string),
    )
    template[
        URIRef(
            "https://schema.metadatacenter.org/properties/5b4f16a9-feb7-4724-8741-2739d8808760"
        )
    ] = Literal("Line chart")

    comparator = graph.resource(PSDO.peer_90th_percentile_benchmark)
    comparator[RDF.type] = PSDO.comparator_content

    performance_content = graph.resource(BNode("performance_content"))
    performance_content.set(RDF.type, PSDO.performance_content)
    signal = Comparison._resource(
        -0.04, "http://purl.obolibrary.org/obo/PSDO_0000129", 0.94,PSDO.desired_increasing_measure
    )
    signal.add(SLOWMO.RegardingMeasure, measure)
    performance_content.add(PSDO.motivating_information, signal)
    graph += signal.graph

    causal_pathway = graph.resource(
        URIRef(
            "https://repo.metadatacenter.org/template-instances/f4006042-5750-4f6c-a039-fe0a88466464"
        )
    )
    causal_pathway[URIRef("http://schema.org/name")] = Literal(
        "social worse", datatype=XSD.string
    )

    return graph


def test_create_candidate(graph):
    # given
    measure = graph.resource(BNode("PONV05"))
    template = graph.resource(
        URIRef(
            "https://repo.metadatacenter.org/template-instances/9e71ec9e-26f3-442a-8278-569bcd58e708"
        )
    )
    

    # when
    candidate = candidate_pudding.create_candidate(measure, template)

    # then
    assert (
        candidate
        and isinstance(candidate, Resource)
        and isinstance(candidate.identifier, BNode)
    )
    assert candidate.value(RDF.type).identifier == SLOWMO.Candidate
    assert candidate.value(SLOWMO.RegardingMeasure) == measure
    assert candidate.value(SLOWMO.AncestorTemplate) == template


def test_add_convenoience_properties(graph):
    # given
    measure = graph.resource(BNode("PONV05"))
    template = graph.resource(
        URIRef(
            "https://repo.metadatacenter.org/template-instances/9e71ec9e-26f3-442a-8278-569bcd58e708"
        )
    )
    candidate = candidate_pudding.create_candidate(measure, template)

    assert candidate.value(SLOWMO.name) == Literal(
        "Opportunity to Improve Top 10 Peer Benchmark", datatype=XSD.string
    )
    assert candidate.value(URIRef("psdo:PerformanceSummaryTextualEntity")) == Literal(
        "You may have an opportunity to improve for the measure [measure name]. Your performance was [recipient performance level], below the top 10% peer benchmark, which was [comparator performance level] this month."
    )
    assert (
        candidate.value(SLOWMO.RegardingComparator).identifier
        == PSDO.peer_90th_percentile_benchmark
    )


def test_add_motivating_information(graph):
    # given
    measure = graph.resource(BNode("PONV05"))
    template = graph.resource(
        URIRef(
            "https://repo.metadatacenter.org/template-instances/9e71ec9e-26f3-442a-8278-569bcd58e708"
        )
    )
    candidate = candidate_pudding.create_candidate(measure, template)

    # when
    candidate = candidate_pudding.add_motivating_information(candidate)

    assert len(list(candidate[PSDO.motivating_information])) > 0
    assert (
        candidate.value(PSDO.motivating_information / SLOWMO.RegardingMeasure)
        == measure
    )
    disposition_count = len(list(candidate[RO.has_disposition]))
    assert disposition_count > 0

    candidate = candidate_pudding.add_motivating_information(candidate)
    assert disposition_count == len(list(candidate[RO.has_disposition]))

    signal = Trend._resource(-0.05,PSDO.desired_increasing_measure)
    signal.add(SLOWMO.RegardingMeasure, measure)
    graph.resource(BNode("performance_content")).add(
        PSDO.motivating_information, signal
    )
    graph += signal.graph

    candidate = candidate_pudding.add_motivating_information(candidate)
    assert 7 == len(list(candidate[RO.has_disposition]))

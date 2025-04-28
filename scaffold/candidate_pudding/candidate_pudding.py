from typing import Optional

from rdflib import RDF, BNode, Graph, Literal, URIRef
from rdflib.resource import Resource

from scaffold.bitstomach.signals import Signal
from scaffold.utils.namespace import CPO, IAO, PSDO, RO, SCHEMA, SLOWMO

PERFORMANCE_SUMMARY_DISPLAY_TEMPLATE = URIRef(
    "http://data.bioontology.org/ontologies/PSDO/classes/http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000002"
)
CPO_HAS_PRECONDITIONS = URIRef(
    "http://purl.bioontology.org/ontology/SNOMEDCT/has_precondition"
)

DEFAULT_DISPLAY = URIRef(
    "https://schema.metadatacenter.org/properties/5b4f16a9-feb7-4724-8741-2739d8808760"
)


def create_candidate(measure: Resource, template: Resource) -> Optional[Resource]:
    g: Graph = measure.graph

    if not template.value(CPO.has_causal_pathway):
        return None

    candidate = g.resource(BNode())
    candidate[RDF.type] = SLOWMO.Candidate
    candidate[SLOWMO.RegardingMeasure] = measure
    candidate[SLOWMO.AncestorTemplate] = template
    # TODO: Add candidate[SLOWMO.CausalPathway] = causal_pathway, to make it easier for down stream code

    if not add_motivating_information(candidate):
        g.remove((candidate.identifier, None, None))
        return None

    add_convenience_properties(candidate)

    return candidate


def add_motivating_information(candidate: Resource):
    performance_content = candidate.graph.resource(BNode("performance_content"))
    measure = candidate.value(SLOWMO.RegardingMeasure)
    motivating_informations = [
        motivating_info
        for motivating_info in performance_content[PSDO.motivating_information]
        if motivating_info.value(SLOWMO.RegardingMeasure) == measure
    ]

    if not motivating_informations:
        return None

    roles = list(candidate[SLOWMO.AncestorTemplate / IAO.is_about])  #

    for motivating_information in motivating_informations:
        signal: Signal = Signal.for_type(motivating_information)  #
        if not signal:
            continue
        if not signal.exclude(motivating_information, roles):  #
            candidate.add(PSDO.motivating_information, motivating_information)
            for disposition in signal.disposition(motivating_information):
                candidate.add(RO.has_disposition, disposition)

    return candidate


def acceptable_by(candidate: Resource):
    pathway = candidate.value(SLOWMO.AncestorTemplate / CPO.has_causal_pathway)

    roles = list(candidate[SLOWMO.AncestorTemplate / IAO.is_about])

    mi_dispositions = list(candidate[RO.has_disposition])

    pre_conditions = set(pathway[CPO_HAS_PRECONDITIONS])

    dispositions = roles + mi_dispositions

    if pre_conditions.issubset(dispositions):
        candidate[SLOWMO.AcceptableBy] = pathway.value(SCHEMA.name)

    return candidate


def add_convenience_properties(candidate: Resource):
    candidate[SLOWMO.name] = candidate.value(
        SLOWMO.AncestorTemplate / URIRef("http://schema.org/name")
    )

    candidate[URIRef("psdo:PerformanceSummaryTextualEntity")] = candidate.value(
        SLOWMO.AncestorTemplate
        / URIRef(
            "https://schema.metadatacenter.org/properties/6b9dfdf9-9c8a-4d85-8684-a24bee4b85a8"
        )
    )

    comparator = next(
        (
            ttype
            for ttype in candidate[SLOWMO.AncestorTemplate / IAO.is_about]
            if ttype[RDF.type : PSDO.comparator_content]
        ),
        None,
    )

    candidate[SLOWMO.RegardingComparator] = comparator or Literal(None)
    candidate[SLOWMO.Display] = candidate.value(
        SLOWMO.AncestorTemplate / DEFAULT_DISPLAY
    )
    return candidate


def create_candidates(graph: Graph):
    # measures = graph[: RDF.type : PSDO.performance_measure_content]
    # How do we get the measures for all MI?
    measures: set[BNode] = set(
        graph.objects(None, PSDO.motivating_information / SLOWMO.RegardingMeasure)
    )
    for measure in measures:
        measure_resource = graph.resource(measure)
        for template in graph[: RDF.type : PERFORMANCE_SUMMARY_DISPLAY_TEMPLATE]:
            template_resource = graph.resource(template)
            candidate = create_candidate(measure_resource, template_resource)
            if not candidate:
                continue
            candidate = acceptable_by(candidate)

import json

import pytest
from rdflib import RDF, BNode, Graph, Literal, URIRef

from src import context, startup
from src.bitstomach.signals import Comparison
from src.utils.namespace import PSDO, SLOWMO

JSONLD_ID_KEY = "@id"
JSONLD_TYPE_KEY = "@type"
PSDO_COMPARATOR_TYPE = "http://purl.obolibrary.org/obo/PSDO_0000093"
PSDO_PEER_GROUP_TYPE = "http://purl.obolibrary.org/obo/PSDO_0000095"


@pytest.fixture
def template_a():
    return "https://repo.metadatacenter.org/template-instances/9e71ec9e-26f3-442a-8278-569bcd58e708"


@pytest.fixture
def mpm():
    return {
        "Social Worse": {
            "comparison_size": 0.5,
            "message_recency": 0.9,
            "message_recurrence": 0.5,
            "measure_recency": 0.5,
            "coachiness": 1.0,
        },
        "Social Better": {
            "comparison_size": 0.5,
            "message_recency": 0.9,
            "message_recurrence": 0.9,
            "measure_recency": 0.5,
            "coachiness": 0.0,
            "history": 0.7,
        },
        "Improving": {
            "trend_size": 0.8,
            "message_recency": 0.9,
            "message_recurrence": 0.9,
            "measure_recency": 1.0,
            "coachiness": 0.5,
        },
        "Worsening": {
            "trend_size": 0.8,
            "message_recency": 0.9,
            "message_recurrence": 0.5,
            "measure_recency": 1.0,
            "coachiness": 1.0,
        },
        "Goal Gain": {
            "comparison_size": 0.5,
            "trend_size": 0.8,
            "achievement_recency": 0.5,
            "message_recency": 0.9,
            "message_recurrence": 0.9,
            "measure_recency": 0.5,
            "coachiness": 0.5,
        },
        "Goal Loss": {
            "comparison_size": 0.5,
            "trend_size": 0.8,
            "loss_recency": 0.5,
            "message_recency": 0.9,
            "message_recurrence": 0.5,
            "measure_recency": 0.5,
            "coachiness": 1.0,
        },
    }


@pytest.fixture
def comparators():
    return [
        {
            JSONLD_ID_KEY: "http://purl.obolibrary.org/obo/PSDO_0000094",
            JSONLD_TYPE_KEY: [PSDO_COMPARATOR_TYPE],
        },
        {
            JSONLD_ID_KEY: "http://purl.obolibrary.org/obo/PSDO_0000126",
            JSONLD_TYPE_KEY: [
                PSDO_COMPARATOR_TYPE,
                PSDO_PEER_GROUP_TYPE,
            ],
        },
        {
            JSONLD_ID_KEY: "http://purl.obolibrary.org/obo/PSDO_0000128",
            JSONLD_TYPE_KEY: [
                PSDO_COMPARATOR_TYPE,
                PSDO_PEER_GROUP_TYPE,
            ],
        },
        {
            JSONLD_ID_KEY: "http://purl.obolibrary.org/obo/PSDO_0000129",
            JSONLD_TYPE_KEY: [
                PSDO_COMPARATOR_TYPE,
                PSDO_PEER_GROUP_TYPE,
            ],
        },
    ]


@pytest.fixture(autouse=True)
def setup_subject_graph(comparators):
    jsonld_str = json.dumps(comparators)
    context.subject_graph = Graph().parse(data=jsonld_str, format="json-ld")


@pytest.fixture
def set_desired_increase_graph():
    def _set(measure="PONV05"):
        g = Graph()
        g.add((BNode(measure), RDF.type, PSDO.performance_measure_content))
        g.add(
            (
                BNode(measure),
                PSDO.has_desired_direction,
                Literal(str(PSDO.desired_increase)),
            )
        )
        startup.base_graph = g

    return _set


@pytest.fixture
def build_comparison_candidate(template_a):
    def _build(performance_df, comparator_df):
        graph = Graph()

        candidate_resource = graph.resource(BNode())
        candidate_resource[SLOWMO.RegardingComparator] = (
            PSDO.peer_90th_percentile_benchmark
        )
        candidate_resource[SLOWMO.AcceptableBy] = Literal("Social Better")
        candidate_resource[SLOWMO.AncestorTemplate] = URIRef(template_a)
        candidate_resource[SLOWMO.RegardingMeasure] = BNode("PONV05")

        motivating_informations = Comparison.detect(performance_df, comparator_df)

        performance_content = graph.resource(BNode("performance_content"))
        for signal in motivating_informations:
            candidate_resource.add(PSDO.motivating_information, signal)
            signal[SLOWMO.RegardingMeasure] = BNode("PONV05")
            performance_content.add(PSDO.motivating_information, signal.identifier)
            graph += signal.graph

        return candidate_resource

    return _build
from datetime import datetime
import json

import pandas as pd
import pytest
from rdflib import RDF, XSD, BNode, Graph, Literal, URIRef

from scaffold import context
from scaffold.bitstomach.bitstomach import prepare
from scaffold.bitstomach.signals import Achievement, Comparison, Loss, Trend
from scaffold.esteemer import esteemer
from scaffold.esteemer.signals._history import History
from scaffold.utils.namespace import PSDO, SLOWMO

TEMPLATE_A = "https://repo.metadatacenter.org/template-instances/9e71ec9e-26f3-442a-8278-569bcd58e708"
MPM = {
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
    "improving": {
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


@pytest.fixture
def history():
    return {
        "2023-04-01": {
            "message_template": TEMPLATE_A,
            "acceptable_by": "Social better",
            "measure": "PONV05",
        },
        "2023-05-01": {
            "message_template": "different template B",
            "acceptable_by": "Social Worse",
            "measure": "PONV05",
        },
        "2023-06-01": {
            "message_template": TEMPLATE_A,
            "acceptable_by": "Social Better",
            "measure": "PONV05",
        },
        "2023-07-01": {
            "message_template": "different template A",
            "acceptable_by": "Social Better",
            "measure": "PONV05",
        },
    }


@pytest.fixture
def performance_data_frame():
    performance_data = [
        [
            "subject",
            "measure",
            "period.start",
            "measureScore.rate",
            "measureScore.denominator",
        ],
        [157, "PONV05", "2023-06-01", 0.93, 100],
        [157, "PONV05", "2023-07-01", 0.94, 100],
        [157, "PONV05", "2023-08-01", 0.95, 100],
    ]

    performance_df = pd.DataFrame(performance_data[1:], columns=performance_data[0])
    context.performance_month = "2023-08-01"
    context.subject = 157
    context.performance_df = performance_df
    perf_df = prepare()
    return perf_df


@pytest.fixture
def comparator_data_frame():
    comparator_data = [
        [
            "measure",
            "period.start",
            "measureScore.rate",
            "group.code",
        ],
        ["PONV05", "2023-06-01", 84.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["PONV05", "2023-06-01", 88.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["PONV05", "2023-06-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["PONV05", "2023-06-01", 99.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["PONV05", "2023-07-01", 84.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["PONV05", "2023-07-01", 88.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["PONV05", "2023-07-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["PONV05", "2023-07-01", 99.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["PONV05", "2023-08-01", 84.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["PONV05", "2023-08-01", 88.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["PONV05", "2023-08-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["PONV05", "2023-08-01", 99.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
    ]
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])
    return comparator_df


@pytest.fixture
def candidate_resource(performance_data_frame, comparator_data_frame):
    graph = Graph()

    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.RegardingComparator] = PSDO.peer_90th_percentile_benchmark
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Social Better")
    candidate_resource[SLOWMO.AncestorTemplate] = URIRef(TEMPLATE_A)
    candidate_resource[SLOWMO.RegardingMeasure] = BNode("PONV05")

    motivating_informations = Comparison.detect(
        performance_data_frame, comparator_data_frame
    )

    performance_content = graph.resource(BNode("performance_content"))
    for s in motivating_informations:
        candidate_resource.add(PSDO.motivating_information, s)
        s[SLOWMO.RegardingMeasure] = BNode("PONV05")
        performance_content.add(PSDO.motivating_information, s.identifier)
        graph += s.graph

    return candidate_resource

def test_history_with_two_recurrances(candidate_resource, history):
    score = esteemer.score_history(candidate_resource, history, MPM["Social Better"])

    assert score == pytest.approx(0.586589)
    
    signal = History.detect(
        history,
        {
            datetime.fromisoformat("2023-08-01"): {
                "message_template": TEMPLATE_A,
                "acceptable_by": "Social better",
                "measure": "PONV05",
            }
        },
    )[0]

    assert signal.value(URIRef("message_recurrence")) == Literal(
        2, datatype=XSD.integer
    )
    
    assert signal.value(URIRef("message_recency")) == Literal(
        2, datatype=XSD.integer
    )

    assert signal.value(URIRef("measure_recurrence")) == Literal(
        4, datatype=XSD.integer
    )
    
    assert signal.value(URIRef("measure_recency")) == Literal(
        1, datatype=XSD.integer
    )


@pytest.fixture
def history_periodic():
    return {
        "2023-01-01": {
            "message_template": TEMPLATE_A,
            "acceptable_by": "Social better",
            "measure": "PONV05",
        },
        "2023-04-01": {
            "message_template": "different template B",
            "acceptable_by": "Social Worse",
            "measure": "PONV05",
        },
        "2023-07-01": {
            "message_template": TEMPLATE_A,
            "acceptable_by": "Social Better",
            "measure": "PONV05",
        },
        "2023-10-01": {
            "message_template": "different template A",
            "acceptable_by": "Social Better",
            "measure": "PONV05",
        },
    }


@pytest.fixture
def performance_data_frame_periodic():
    performance_data = [
        [
            "subject",
            "measure",
            "period.start",
            "measureScore.rate",
            "measureScore.denominator",
        ],
        [157, "PONV05", "2023-07-01", 0.93, 100],
        [157, "PONV05", "2023-10-01", 0.94, 100],
        [157, "PONV05", "2024-01-01", 0.95, 100],
    ]

    performance_df = pd.DataFrame(performance_data[1:], columns=performance_data[0])
    context.performance_month = "2024-01-01"
    context.subject = 157
    context.performance_df = performance_df
    perf_df = prepare()
    return perf_df


@pytest.fixture
def comparator_data_frame_periodic():
    comparator_data = [
        [
            "measure",
            "period.start",
            "measureScore.rate",
            "group.code",
        ],
        ["PONV05", "2023-07-01", 84.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["PONV05", "2023-07-01", 88.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["PONV05", "2023-07-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["PONV05", "2023-07-01", 99.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["PONV05", "2023-10-01", 84.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["PONV05", "2023-10-01", 88.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["PONV05", "2023-10-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["PONV05", "2023-10-01", 99.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["PONV05", "2024-01-01", 84.0, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["PONV05", "2024-01-01", 88.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["PONV05", "2024-01-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["PONV05", "2024-01-01", 99.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
    ]
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])
    return comparator_df


@pytest.fixture
def candidate_resource_periodic(performance_data_frame_periodic, comparator_data_frame_periodic):
    graph = Graph()

    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.RegardingComparator] = PSDO.peer_90th_percentile_benchmark
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Social Better")
    candidate_resource[SLOWMO.AncestorTemplate] = URIRef(TEMPLATE_A)
    candidate_resource[SLOWMO.RegardingMeasure] = BNode("PONV05")

    motivating_informations = Comparison.detect(
        performance_data_frame_periodic, comparator_data_frame_periodic
    )

    performance_content = graph.resource(BNode("performance_content"))
    for s in motivating_informations:
        candidate_resource.add(PSDO.motivating_information, s)
        s[SLOWMO.RegardingMeasure] = BNode("PONV05")
        performance_content.add(PSDO.motivating_information, s.identifier)
        graph += s.graph

    return candidate_resource

def test_history_with_two_recurrances_periodic(candidate_resource_periodic, history_periodic):
    score = esteemer.score_history(candidate_resource_periodic, history_periodic, MPM["Social Better"])

    assert score == pytest.approx(0.70325174)
    
    signal = History.detect(
        history_periodic,
        {
            datetime.fromisoformat("2024-01-01"): {
                "message_template": TEMPLATE_A,
                "acceptable_by": "Social better",
                "measure": "PONV05",
            }
        },
    )[0]

    assert signal.value(URIRef("message_recurrence")) == Literal(
        2, datatype=XSD.integer
    )
    
    assert signal.value(URIRef("message_recency")) == Literal(
        6, datatype=XSD.integer
    )

    assert signal.value(URIRef("measure_recurrence")) == Literal(
        4, datatype=XSD.integer
    )
    
    assert signal.value(URIRef("measure_recency")) == Literal(
        3, datatype=XSD.integer
    )
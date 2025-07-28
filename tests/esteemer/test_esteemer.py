import json

import pandas as pd
import pytest
from rdflib import RDF, BNode, Graph, Literal, URIRef

from scaffold import context
from scaffold.bitstomach.bitstomach import prepare
from scaffold.bitstomach.signals import Achievement, Comparison, Loss, Trend
from scaffold.esteemer import esteemer
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
            "http://purl.obolibrary.org/obo/PSDO_0000126",
            "http://purl.obolibrary.org/obo/PSDO_0000128",
            "http://purl.obolibrary.org/obo/PSDO_0000129",
            "http://purl.obolibrary.org/obo/PSDO_0000094",
        ],
        [157, "PONV05", "2023-06-01", 0.93, 100, 84.0, 88.0, 90.0, 99.0],
        [157, "PONV05", "2023-07-01", 0.94, 100, 84.0, 88.0, 90.0, 99.0],
        [157, "PONV05", "2023-08-01", 0.95, 100, 84.0, 88.0, 90.0, 99.0],
    ]

    performance_df = pd.DataFrame(performance_data[1:], columns=performance_data[0])
    context.performance_month = "2023-08-01"
    context.subject = 157
    context.performance_df = performance_df
    perf_df = prepare()
    return perf_df


@pytest.fixture
def candidate_resource(performance_data_frame):
    graph = Graph()

    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.RegardingComparator] = PSDO.peer_90th_percentile_benchmark
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Social Better")
    candidate_resource[SLOWMO.AncestorTemplate] = URIRef(TEMPLATE_A)
    candidate_resource[SLOWMO.RegardingMeasure] = BNode("PONV05")

    motivating_informations = Comparison.detect(performance_data_frame)

    performance_content = graph.resource(BNode("performance_content"))
    for s in motivating_informations:
        candidate_resource.add(PSDO.motivating_information, s)
        s[SLOWMO.RegardingMeasure] = BNode("PONV05")
        performance_content.add(PSDO.motivating_information, s.identifier)
        graph += s.graph

    return candidate_resource


def test_score(candidate_resource):
    context.preferences_dict = context.set_preferences({})
    context.performance_month = "2023-08-01"
    esteemer.score(candidate_resource, MPM)
    assert candidate_resource.value(SLOWMO.Score).value == pytest.approx(2.05)


def test_calculate_preference_score(candidate_resource):
    assert esteemer.score_preferences(candidate_resource, {}) == 0


def test_select_candidate():
    graph = Graph()
    candidate1 = graph.resource(BNode("candidate1"))
    candidate2 = graph.resource(BNode("candidate2"))

    candidate1[SLOWMO.Score] = Literal(0.2)
    candidate2[SLOWMO.Score] = Literal(0.1)
    candidate1[URIRef("coachiness_score")] = Literal(1.00)
    candidate2[URIRef("coachiness_score")] = Literal(1.00)
    candidate1[SLOWMO.AcceptableBy] = Literal(True)
    candidate2[SLOWMO.AcceptableBy] = Literal(True)
    candidate1[RDF.type] = SLOWMO.Candidate
    candidate2[RDF.type] = SLOWMO.Candidate
    candidate1[SLOWMO.AcceptableBy] = Literal("Social Worse")
    candidate1[SLOWMO.AcceptableBy] = Literal("improving")

    # get graph that has candidates scored by esteemer
    selected_candidate = esteemer.select_candidate(graph)
    assert str(selected_candidate) in ["candidate1", "candidate2"]
    assert str(selected_candidate) == "candidate1"

    candidate3 = graph.resource(BNode("candidate3"))
    candidate3[SLOWMO.Score] = Literal(0.2)
    candidate3[SLOWMO.AcceptableBy] = Literal("Social Worse")
    selected_candidate = esteemer.select_candidate(graph)
    assert str(selected_candidate) in ["candidate1", "candidate3"]
    assert graph.resource(selected_candidate).value(SLOWMO.Score) == Literal(0.2)


def test_get_trend_info():
    candidate_resource = Trend._resource(0.0034)
    mods = Trend.moderators([candidate_resource])[0]
    assert mods["trend_size"] == pytest.approx(0.0068)
    assert Trend.signal_type in mods["type"]


# History scoring tests


def test_no_history_signal_is_score_0(candidate_resource):
    assert esteemer.score_history(candidate_resource, {}, {}) == 1.0

    assert esteemer.score_history(candidate_resource, None, {}) == 1.0


def test_history_with_two_recurrances(candidate_resource, history):
    score = esteemer.score_history(candidate_resource, history, MPM["Social Better"])

    assert score == pytest.approx(0.586589)


def test_social_better_score(performance_data_frame):
    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.RegardingComparator] = PSDO.peer_90th_percentile_benchmark
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Social Better")

    motivating_informations = Comparison.detect(performance_data_frame)
    score = esteemer.score_better(
        candidate_resource, motivating_informations, MPM["Social Better"]
    )
    assert score == pytest.approx(0.05)


def test_social_worse_score():
    data_frame = pd.DataFrame(
        {
            "measureScore.rate": [0.92, 0.91, 0.88],
            "valid": [True, True, True],
            "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
        },
        columns=[
            "period.start",
            "valid",
            "measureScore.rate",
            "http://purl.obolibrary.org/obo/PSDO_0000126",
            "http://purl.obolibrary.org/obo/PSDO_0000128",
            "http://purl.obolibrary.org/obo/PSDO_0000129",
            "http://purl.obolibrary.org/obo/PSDO_0000094",
        ],
    )
    data_frame[data_frame.columns[-4:]] = [90.0, 92.0, 94.0, 90.0]

    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.RegardingComparator] = PSDO.peer_average_comparator
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Social Worse")

    motivating_informations = Comparison.detect(data_frame)
    score = esteemer.score_worse(
        candidate_resource, motivating_informations, MPM["Social Worse"]
    )
    assert score == pytest.approx(0.02)


def test_improving_score():
    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.AcceptableBy] = Literal("improving")

    motivating_informations = Trend.detect(
        pd.DataFrame(
            {
                "measureScore.rate": [0.89, 0.90, 0.91],
                "valid": True,
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
            },  # slope 1.0
        )
    )
    score = esteemer.score_improving(
        candidate_resource, motivating_informations, MPM["improving"]
    )
    assert score == pytest.approx(0.02)


def test_worsening_score():
    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Worsening")

    motivating_informations = Trend.detect(
        pd.DataFrame(
            {
                "measureScore.rate": [0.91, 0.90, 0.89],
                "valid": True,
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
            },  # slope 1.0
        )
    )
    score = esteemer.score_worsening(
        candidate_resource, motivating_informations, MPM["Worsening"]
    )
    assert score == pytest.approx(0.02)


def test_goal_gain_score():
    data_frame = pd.DataFrame(
        {
            "measureScore.rate": [0.88, 0.89, 0.91],
            "valid": [True, True, True],
            "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
        },
        columns=[
            "period.start",
            "valid",
            "measureScore.rate",
            "http://purl.obolibrary.org/obo/PSDO_0000126",
            "http://purl.obolibrary.org/obo/PSDO_0000128",
            "http://purl.obolibrary.org/obo/PSDO_0000129",
            "http://purl.obolibrary.org/obo/PSDO_0000094",
        ],
    )

    data_frame[data_frame.columns[-4:]] = [90.0, 92.0, 94.0, 90.0]
    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Goal Gain")
    candidate_resource[SLOWMO.RegardingComparator] = PSDO.goal_comparator_content

    motivating_informations = Achievement.detect(data_frame)
    score = esteemer.score_gain(
        candidate_resource, motivating_informations, MPM["Goal Gain"]
    )
    assert score == pytest.approx(0.062407407407407404)


def test_goal_loss_score():
    data_frame = pd.DataFrame(
        {
            "measureScore.rate": [0.92, 0.91, 0.88],
            "valid": [True, True, True],
            "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
        },
        columns=[
            "period.start",
            "valid",
            "measureScore.rate",
            "http://purl.obolibrary.org/obo/PSDO_0000126",
            "http://purl.obolibrary.org/obo/PSDO_0000128",
            "http://purl.obolibrary.org/obo/PSDO_0000129",
            "http://purl.obolibrary.org/obo/PSDO_0000094",
        ],
    )
    data_frame[data_frame.columns[-4:]] = [90.0, 92.0, 94.0, 90.0]

    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Goal Loss")
    candidate_resource[SLOWMO.RegardingComparator] = PSDO.goal_comparator_content

    motivating_informations = Loss.detect(data_frame)
    score = esteemer.score_loss(
        candidate_resource, motivating_informations, MPM["Goal Loss"]
    )
    assert score == pytest.approx(0.0696296)

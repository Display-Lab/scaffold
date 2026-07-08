from unittest.mock import patch

import pandas as pd
import pytest
from rdflib import RDF, BNode, Graph, Literal, URIRef

from src import context, startup
from src.bitstomach.bitstomach import prepare
from src.bitstomach.signals import Achievement, Comparison, Loss, Trend
from src.esteemer.mpm_candidate_selector import MPM_candidate_selector
from src.utils.namespace import PSDO, SLOWMO


@pytest.fixture
def history(template_a):
    return {
        "2023-04-01": {
            "message_template": template_a,
            "acceptable_by": "Social better",
            "measure": "PONV05",
        },
        "2023-05-01": {
            "message_template": "different template B",
            "acceptable_by": "Social Worse",
            "measure": "PONV05",
        },
        "2023-06-01": {
            "message_template": template_a,
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
def performance_data_frame(set_desired_increase_graph):
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
    context.subject = 157
    context.performance_df = performance_df
    context.performance_month = "2023-08-01"
    perf_df = prepare()

    set_desired_increase_graph("PONV05")

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
        ["PONV05", "2023-06-01", 0.84, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["PONV05", "2023-06-01", 0.88, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["PONV05", "2023-06-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["PONV05", "2023-06-01", 0.99, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["PONV05", "2023-07-01", 0.84, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["PONV05", "2023-07-01", 0.88, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["PONV05", "2023-07-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["PONV05", "2023-07-01", 0.99, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["PONV05", "2023-08-01", 0.84, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["PONV05", "2023-08-01", 0.88, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["PONV05", "2023-08-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["PONV05", "2023-08-01", 0.99, "http://purl.obolibrary.org/obo/PSDO_0000094"],
    ]
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])
    return comparator_df


@pytest.fixture
def candidate_resource(
    performance_data_frame, comparator_data_frame, build_comparison_candidate
):
    return build_comparison_candidate(performance_data_frame, comparator_data_frame)


@pytest.fixture(autouse=True)
def patched_dependencies(history, mpm):
    with (
        patch.object(MPM_candidate_selector, "_load_mpm_from_env", return_value=mpm),
        patch.object(MPM_candidate_selector, "_load_history", return_value=history),
        patch.object(
            MPM_candidate_selector, "_load_preferences", return_value=({}, {})
        ),
    ):
        yield


def test_score(candidate_resource):
    context.subject = 157
    context.performance_month = "2023-08-01"
    MPM_candidate_selector(context)._score(candidate_resource)
    assert candidate_resource.value(SLOWMO.Score).value == pytest.approx(2.05)


def test_calculate_preference_score(candidate_resource):
    context.subject = 157
    context.performance_month = ""
    assert (
        MPM_candidate_selector(context)._score_preferences(candidate_resource, {}) == 0
    )


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
    candidate1[SLOWMO.AcceptableBy] = Literal("Improving")

    with patch.object(MPM_candidate_selector, "_score", return_value=None):
        with patch.object(context, "subject_graph", graph):
            context.subject = 157
            context.performance_month = ""
            selected_candidate = MPM_candidate_selector(context).select_candidate()
            assert str(selected_candidate.identifier) in ["candidate1", "candidate2"]
            assert str(selected_candidate.identifier) == "candidate1"

            candidate3 = graph.resource(BNode("candidate3"))
            candidate3[SLOWMO.Score] = Literal(0.2)
            candidate3[SLOWMO.AcceptableBy] = Literal("Social Worse")
            selected_candidate = MPM_candidate_selector(context).select_candidate()
            assert str(selected_candidate.identifier) in ["candidate1", "candidate3"]
            assert graph.resource(selected_candidate.identifier).value(
                SLOWMO.Score
            ) == Literal(0.2)


def test_get_trend_info():
    candidate_resource = Trend._resource(0.0034)
    mods = Trend.moderators([candidate_resource])[0]
    assert mods["trend_size"] == pytest.approx(0.0068)
    assert Trend.signal_type in mods["type"]


# History scoring tests


def test_no_history_signal_is_score_0(candidate_resource):
    context.subject = 157
    context.performance_month = "2023-08-01"
    assert (
        MPM_candidate_selector(context)._score_history(candidate_resource, {}, {})
        == 1.0
    )
    assert (
        MPM_candidate_selector(context)._score_history(candidate_resource, None, {})
        == 1.0
    )


def test_history_with_two_recurrances(candidate_resource, history, mpm):
    context.subject = 157
    context.performance_month = "2023-08-01"
    score = MPM_candidate_selector(context)._score_history(
        candidate_resource, history, mpm["Social Better"]
    )
    assert score == pytest.approx(0.586589)


def test_social_better_score(performance_data_frame, comparator_data_frame, mpm):
    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.RegardingComparator] = PSDO.peer_90th_percentile_benchmark
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Social Better")

    motivating_informations = Comparison.detect(
        performance_data_frame, comparator_data_frame
    )
    context.subject = 157
    context.performance_month = ""

    score = MPM_candidate_selector(context)._score_better(
        candidate_resource, motivating_informations, mpm["Social Better"]
    )
    assert score == pytest.approx(0.05)

@pytest.fixture
def comparator_data():
    comparator_data = [
        [
            "period.start",
            "measureScore.rate",
            "group.code",
        ],
        ["2023-11-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["2023-11-01", 0.92, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["2023-11-01", 0.94, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["2023-11-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["2023-12-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["2023-12-01", 0.92, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["2023-12-01", 0.94, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["2023-12-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["2024-01-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["2024-01-01", 0.92, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["2024-01-01", 0.94, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["2024-01-01", 0.90, "http://purl.obolibrary.org/obo/PSDO_0000094"],
    ]
    return comparator_data

def test_social_worse_score(comparator_data, set_desired_increase_graph, mpm):
    data_frame = pd.DataFrame(
        {
            "subject": [157, 157, 157],
            "measure": ["PONV05", "PONV05", "PONV05"],
            "measureScore.rate": [0.92, 0.91, 0.88],
            "valid": [True, True, True],
            "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
        },
        columns=[
            "subject",
            "measure",
            "period.start",
            "valid",
            "measureScore.rate",
            "http://purl.obolibrary.org/obo/PSDO_0000126",
            "http://purl.obolibrary.org/obo/PSDO_0000128",
            "http://purl.obolibrary.org/obo/PSDO_0000129",
            "http://purl.obolibrary.org/obo/PSDO_0000094",
        ],
    )
    
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])

    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.RegardingComparator] = PSDO.peer_average_comparator
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Social Worse")

    set_desired_increase_graph("PONV05")

    motivating_informations = Comparison.detect(data_frame, comparator_df)
    context.subject = 157
    context.performance_month = ""
    score = MPM_candidate_selector(context)._score_worse(
        candidate_resource, motivating_informations, mpm["Social Worse"]
    )
    assert score == pytest.approx(0.02)


def test_improving_score(set_desired_increase_graph, mpm):
    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Improving")

    set_desired_increase_graph("PONV05")

    motivating_informations = Trend.detect(
        pd.DataFrame(
            {
                "measure": "PONV05",
                "measureScore.rate": [0.89, 0.90, 0.91],
                "valid": True,
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
            },  # slope 1.0
        )
    )
    context.subject = 157
    context.performance_month = ""
    score = MPM_candidate_selector(context)._score_improving(
        candidate_resource, motivating_informations, mpm["Improving"]
    )
    assert score == pytest.approx(0.02)


def test_worsening_score(set_desired_increase_graph, mpm):
    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Worsening")

    set_desired_increase_graph("PONV05")

    motivating_informations = Trend.detect(
        pd.DataFrame(
            {
                "measure": "PONV05",
                "measureScore.rate": [0.91, 0.90, 0.89],
                "valid": True,
                "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
            },  # slope 1.0
        )
    )
    context.subject = 157
    context.performance_month = ""
    score = MPM_candidate_selector(context)._score_worsening(
        candidate_resource, motivating_informations, mpm["Worsening"]
    )
    assert score == pytest.approx(0.02)


def test_goal_gain_score(comparator_data, set_desired_increase_graph, mpm):
    data_frame = pd.DataFrame(
        {
            "measure": ["PONV05", "PONV05", "PONV05"],
            "measureScore.rate": [0.88, 0.89, 0.91],
            "valid": [True, True, True],
            "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
        },
        columns=["measure", "period.start", "valid", "measureScore.rate"],
    )

    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])
    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Goal Gain")
    candidate_resource[SLOWMO.RegardingComparator] = PSDO.goal_comparator_content

    set_desired_increase_graph("PONV05")

    motivating_informations = Achievement.detect(data_frame, comparator_df)
    context.subject = 157
    context.performance_month = ""
    score = MPM_candidate_selector(context)._score_gain(
        candidate_resource, motivating_informations, mpm["Goal Gain"]
    )
    assert score == pytest.approx(0.062407407407407404)


def test_goal_loss_score(comparator_data, set_desired_increase_graph, mpm):
    data_frame = pd.DataFrame(
        {
            "measure": ["PONV05", "PONV05", "PONV05"],
            "measureScore.rate": [0.92, 0.91, 0.88],
            "valid": [True, True, True],
            "period.start": ["2023-11-01", "2023-12-01", "2024-01-01"],
        },
        columns=["measure", "period.start", "valid", "measureScore.rate"],
    )
    
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])

    graph = Graph()
    candidate_resource = graph.resource(BNode())
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Goal Loss")
    candidate_resource[SLOWMO.RegardingComparator] = PSDO.goal_comparator_content

    set_desired_increase_graph("PONV05")

    motivating_informations = Loss.detect(data_frame, comparator_df)
    context.subject = 157
    context.performance_month = ""
    score = MPM_candidate_selector(context)._score_loss(
        candidate_resource, motivating_informations, mpm["Goal Loss"]
    )
    assert score == pytest.approx(0.0696296)

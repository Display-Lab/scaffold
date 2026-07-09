from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest
from rdflib import XSD, Literal, URIRef

from src import context
from src.bitstomach.bitstomach import prepare
from src.esteemer.mpm_candidate_selector import MPM_candidate_selector
from src.esteemer.signals._history import History
from src.utils.namespace import PSDO

PEER_AVERAGE_URI = str(PSDO.peer_average_comparator)
PEER_75TH_URI = str(PSDO.peer_75th_percentile_benchmark)
PEER_90TH_URI = str(PSDO.peer_90th_percentile_benchmark)
GOAL_COMPARATOR_URI = str(PSDO.goal_comparator_content)

@pytest.fixture
def history_periodic(template_a):
    return {
        "2023-01-01": {
            "message_template": template_a,
            "acceptable_by": "Social better",
            "measure": "PONV05",
        },
        "2023-04-01": {
            "message_template": "different template B",
            "acceptable_by": "Social Worse",
            "measure": "PONV05",
        },
        "2023-07-01": {
            "message_template": template_a,
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
def performance_data_frame_periodic(set_desired_increase_graph):
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
    context.subject = 157
    context.performance_df = performance_df
    context.performance_month = "2024-01-01"
    set_desired_increase_graph("PONV05")
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
        ["PONV05", "2023-07-01", 84.0, PEER_AVERAGE_URI],
        ["PONV05", "2023-07-01", 88.0, PEER_75TH_URI],
        ["PONV05", "2023-07-01", 90.0, PEER_90TH_URI],
        ["PONV05", "2023-07-01", 99.0, GOAL_COMPARATOR_URI],
        ["PONV05", "2023-10-01", 84.0, PEER_AVERAGE_URI],
        ["PONV05", "2023-10-01", 88.0, PEER_75TH_URI],
        ["PONV05", "2023-10-01", 90.0, PEER_90TH_URI],
        ["PONV05", "2023-10-01", 99.0, GOAL_COMPARATOR_URI],
        ["PONV05", "2024-01-01", 84.0, PEER_AVERAGE_URI],
        ["PONV05", "2024-01-01", 88.0, PEER_75TH_URI],
        ["PONV05", "2024-01-01", 90.0, PEER_90TH_URI],
        ["PONV05", "2024-01-01", 99.0, GOAL_COMPARATOR_URI],
    ]
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])
    return comparator_df


@pytest.fixture
def candidate_resource_periodic(
    performance_data_frame_periodic,
    comparator_data_frame_periodic,
    build_comparison_candidate,
):
    return build_comparison_candidate(
        performance_data_frame_periodic, comparator_data_frame_periodic
    )


def test_history_with_two_recurrances_periodic(
    candidate_resource_periodic, history_periodic, mpm, template_a
):
    with (
        patch.object(MPM_candidate_selector, "_load_mpm_from_env", return_value=mpm),
        patch.object(MPM_candidate_selector, "_load_history", return_value=history_periodic),
        patch.object(
            MPM_candidate_selector, "_load_preferences", return_value=({}, {})
        ),
    ):
        context.subject = 157
        context.performance_month = "2024-01-01"
        score = MPM_candidate_selector(context)._score_history(
            candidate_resource_periodic, history_periodic, mpm["Social Better"]
        )

    assert score == pytest.approx(0.70325174)

    signal = History.detect(
        history_periodic,
        {
            datetime.fromisoformat("2024-01-01"): {
                "message_template": template_a,
                "acceptable_by": "Social better",
                "measure": "PONV05",
            }
        },
    )[0]

    assert signal.value(URIRef("message_recurrence")) == Literal(
        2, datatype=XSD.integer
    )

    assert signal.value(URIRef("message_recency")) == Literal(6, datatype=XSD.integer)

    assert signal.value(URIRef("measure_recurrence")) == Literal(
        4, datatype=XSD.integer
    )

    assert signal.value(URIRef("measure_recency")) == Literal(3, datatype=XSD.integer)

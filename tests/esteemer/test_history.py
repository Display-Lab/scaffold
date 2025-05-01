from datetime import datetime
from typing import List

import pytest
from rdflib import RDF, XSD, BNode, Graph, Literal, URIRef

from scaffold.esteemer.signals import History
from scaffold.utils import SLOWMO

TEMPLATE_A = "https://repo.metadatacenter.org/template-instances/9e71ec9e-26f3-442a-8278-569bcd58e708"


@pytest.fixture
def history():
    return {
        "2023-06-01": {
            "message_template": "https://repo.metadatacenter.org/template-instances/1f257d98-f6b0-44f6-92c8-1a194954f33f",
            "acceptable_by": "Social better",
            "measure": "PONV05",
        },
        "2023-07-01": {
            "message_template": "different template B",
            "acceptable_by": "Social worse",
            "measure": "PONV05",
        },
        "2023-08-01": {
            "message_template": "https://repo.metadatacenter.org/template-instances/1f257d98-f6b0-44f6-92c8-1a194954f33f",
            "acceptable_by": "Social better",
            "measure": "PONV05",
        },
        "2023-09-01": {
            "message_template": "different template A",
            "acceptable_by": "Social better",
            "measure": "PONV05",
        },
    }


def test_history_detect_returns_list():
    message_history = {}

    signals = History.detect(message_history, {})
    assert not signals


def test_history_detect_signal(history):
    signal = History.detect(
        history,
        {
            datetime.fromisoformat("2024-01-01"): {
                "message_template": "https://repo.metadatacenter.org/template-instances/1f257d98-f6b0-44f6-92c8-1a194954f33f",
                "acceptable_by": "Social better",
                "measure": "PONV05",
            }
        },
    )[0]

    assert signal.value(URIRef("message_recurrence")) == Literal(
        2, datatype=XSD.integer
    )


def test_moderators_no_resources_return_empty_list():
    mods = History.moderators([])

    assert isinstance(mods, List)
    assert len(mods) == 0


def test_single_resource_returns_single_moderator():
    signal = Graph().resource(BNode())
    signal.add(URIRef("message_recurrence"), Literal(4))
    signal.add(URIRef("message_recency"), Literal(4))
    signal.add(URIRef("measure_recurrence"), Literal(4))
    signal.add(URIRef("measure_recency"), Literal(4))

    signal.add(RDF.type, History.signal_type)
    mods = History.moderators([signal])

    assert isinstance(mods, List)
    assert isinstance(mods[0], dict)
    assert len(mods) == 1

    assert mods[0]["message_recurrence"] == pytest.approx(round(4 / 12, 4))


# Supplementary methods


def test_to_element():
    candidate_resource = Graph().resource(BNode())
    candidate_resource[SLOWMO.AncestorTemplate] = URIRef(TEMPLATE_A)
    candidate_resource[SLOWMO.AcceptableBy] = Literal("Social Worse")
    candidate_resource[SLOWMO.RegardingMeasure] = BNode("PONV05")

    current_hist: dict = History.to_element(candidate_resource)

    assert current_hist
    assert current_hist["acceptable_by"] == "Social Worse"
    assert current_hist["message_template"] == TEMPLATE_A

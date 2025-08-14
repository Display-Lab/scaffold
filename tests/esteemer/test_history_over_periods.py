from datetime import datetime

import pytest
from rdflib import XSD, Literal, URIRef

from scaffold.esteemer.signals import History

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


@pytest.fixture
def history_periodic():
    return {
        "2023-01-01": {
            "message_template": "https://repo.metadatacenter.org/template-instances/1f257d98-f6b0-44f6-92c8-1a194954f33f",
            "acceptable_by": "Social better",
            "measure": "PONV05",
        },
        "2023-04-01": {
            "message_template": "different template B",
            "acceptable_by": "Social worse",
            "measure": "PONV05",
        },
        "2023-07-01": {
            "message_template": "https://repo.metadatacenter.org/template-instances/1f257d98-f6b0-44f6-92c8-1a194954f33f",
            "acceptable_by": "Social better",
            "measure": "PONV05",
        },
        "2023-10-01": {
            "message_template": "different template A",
            "acceptable_by": "Social better",
            "measure": "PONV05",
        },
    }


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

    assert signal.value(URIRef("message_recency")) == Literal(5, datatype=XSD.integer)

    assert signal.value(URIRef("measure_recurrence")) == Literal(
        4, datatype=XSD.integer
    )

    assert signal.value(URIRef("measure_recency")) == Literal(4, datatype=XSD.integer)


def test_history_detect_signal_periodic_data(history_periodic):
    signal = History.detect(
        history_periodic,
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

    assert signal.value(URIRef("message_recency")) == Literal(6, datatype=XSD.integer)

    assert signal.value(URIRef("measure_recurrence")) == Literal(
        4, datatype=XSD.integer
    )

    assert signal.value(URIRef("measure_recency")) == Literal(3, datatype=XSD.integer)

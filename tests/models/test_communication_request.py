import pytest

from src.models import CommunicationRequest


def test_to_json_returns_minimal_communication_request():
    request = CommunicationRequest(identifier="communication-request-1")

    assert request.to_json() == {
        "resourceType": "CommunicationRequest",
        "id": "communication-request-1",
        "status": "active",
    }


def test_add_about_and_payload_methods_mutate_and_return_request():
    request = CommunicationRequest(
        identifier="communication-request-1",
        subject_reference="Practitioner/practitioner-1",
        authored_on="2026-09-15T12:00:00",
    )

    assert request.add_about("Measure/measure-1", "Example measure") is request
    assert request.add_about("#parameters-1") is request
    assert request.add_text_payload("Your performance message...") is request
    assert request.add_attachment_payload(
        content_type="image/png",
        data="base64-image",
    ) is request
    assert request.add_attachment_payload(
        content_type="text/csv; charset=utf-8",
        data="base64-csv",
        title="Performance history",
    ) is request

    assert request.to_json() == {
        "resourceType": "CommunicationRequest",
        "id": "communication-request-1",
        "status": "active",
        "subject": {"reference": "Practitioner/practitioner-1"},
        "authoredOn": "2026-09-15T12:00:00",
        "about": [
            {"reference": "Measure/measure-1", "display": "Example measure"},
            {"reference": "#parameters-1"},
        ],
        "payload": [
            {"contentString": "Your performance message..."},
            {
                "contentAttachment": {
                    "contentType": "image/png",
                    "data": "base64-image",
                }
            },
            {
                "contentAttachment": {
                    "contentType": "text/csv; charset=utf-8",
                    "data": "base64-csv",
                    "title": "Performance history",
                }
            },
        ],
    }


def test_add_attachment_payload_supports_url():
    request = CommunicationRequest(identifier="communication-request-1")

    request.add_attachment_payload(
        content_type="text/csv",
        url="Binary/performance-history",
    )

    assert request.to_json()["payload"] == [
        {
            "contentAttachment": {
                "contentType": "text/csv",
                "url": "Binary/performance-history",
            }
        }
    ]


def test_add_attachment_payload_requires_data_or_url():
    request = CommunicationRequest(identifier="communication-request-1")

    with pytest.raises(ValueError, match="requires data or url"):
        request.add_attachment_payload(content_type="text/csv")


def test_add_contained_accepts_complete_fhir_resource_and_copies_it():
    request = CommunicationRequest(identifier="communication-request-1")
    parameters = {
        "resourceType": "Parameters",
        "id": "parameters-1",
        "parameter": [{"name": "performance-month", "valueDate": "2025-01-01"}],
    }

    assert request.add_contained(parameters) is request
    parameters["parameter"] = []

    assert request.to_json()["contained"] == [
        {
            "resourceType": "Parameters",
            "id": "parameters-1",
            "parameter": [
                {"name": "performance-month", "valueDate": "2025-01-01"}
            ],
        }
    ]


def test_add_parameters_builds_contained_parameters_resource_and_copies_values():
    request = CommunicationRequest(identifier="communication-request-1")
    parameters = [
        {"name": "performance-month", "valueDate": "2025-01-01"},
        {"name": "selected-comparator", "valueString": "Peer Top 10%"},
    ]

    assert request.add_parameters("parameters-1", parameters) is request
    parameters.clear()

    assert request.to_json()["contained"] == [
        {
            "resourceType": "Parameters",
            "id": "parameters-1",
            "parameter": [
                {"name": "performance-month", "valueDate": "2025-01-01"},
                {
                    "name": "selected-comparator",
                    "valueString": "Peer Top 10%",
                },
            ],
        }
    ]


@pytest.mark.parametrize(
    "resource, message",
    [
        ({"id": "parameters-1"}, "requires resourceType"),
        ({"resourceType": "Parameters"}, "requires id"),
    ],
)
def test_add_contained_requires_resource_type_and_id(resource, message):
    request = CommunicationRequest(identifier="communication-request-1")

    with pytest.raises(ValueError, match=message):
        request.add_contained(resource)


def test_add_contained_rejects_duplicate_ids():
    request = CommunicationRequest(identifier="communication-request-1")
    resource = {"resourceType": "Parameters", "id": "parameters-1"}
    request.add_contained(resource)

    with pytest.raises(ValueError, match="already exists"):
        request.add_contained(resource)


def test_to_json_returns_copies_of_mutable_values():
    request = CommunicationRequest(identifier="communication-request-1")
    request.add_text_payload("Message")

    serialized = request.to_json()
    serialized["payload"].append({"contentString": "Changed"})

    assert request.to_json()["payload"] == [{"contentString": "Message"}]
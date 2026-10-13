from src.models import Measure


def test_measure_to_json_returns_fhir_measure_resource():
    measure = Measure(
        identifier="Physician-language-01",
        name="Physician-language-01",
        title="Physician informed using clear language",
        measure_type="process",
        improvement_notation="increase",
    )

    assert measure.to_json() == {
        "resourceType": "Measure",
        "id": "Physician-language-01",
        "identifier": [{"value": "Physician-language-01"}],
        "name": "Physician-language-01",
        "title": "Physician informed using clear language",
        "status": "active",
        "type": [{"text": "process"}],
        "improvementNotation": {"text": "increase"},
    }
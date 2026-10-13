import pandas as pd

from src.models import MeasureReport


def test_bundle_entries_from_dataframe_creates_one_entry_per_performance_row():
    dataframe = pd.DataFrame(
        [
            {
                "identifier": "row-1",
                "measure": "Clean-Rating-01",
                "subject": "practitioner-1",
                "period.start": "2025-01-01",
                "period.end": "2025-01-31",
                "measureScore.rate": 0.94,
                "measureScore.denominator": 586,
            },
            {
                "identifier": "row-2",
                "measure": "Care-Rating-01",
                "subject": "practitioner-1",
                "period.start": "2025-01-01",
                "period.end": "2025-01-31",
                "measureScore.rate": 0.84,
                "measureScore.denominator": 512,
            },
        ]
    )

    entries = MeasureReport.bundle_entries_from_dataframe(dataframe)

    assert len(entries) == 2
    assert entries[0]["fullUrl"] == "urn:uuid:measure-report-row-1"
    assert entries[0]["resource"] == {
        "resourceType": "MeasureReport",
        "id": "measure-report-row-1",
        "status": "complete",
        "type": "individual",
        "measure": "urn:uuid:measure-Clean-Rating-01",
        "subject": {"reference": "Practitioner/practitioner-1"},
        "period": {
            "start": "2025-01-01",
            "end": "2025-01-31",
        },
        "group": [
            {
                "measureScore": {"value": 0.94},
                "population": [
                    {
                        "code": {"text": "denominator"},
                        "count": 586,
                    }
                ],
            }
        ],
    }


def test_bundle_entries_from_dataframe_supports_comparator_rows_with_default_group():
    dataframe = pd.DataFrame(
        [
            {
                "identifier": "cmp-1",
                "measure": "Clean-Rating-01",
                "period.start": pd.Timestamp("2025-01-01"),
                "period.end": pd.Timestamp("2025-01-31"),
                "measureScore.rate": 1.0,
                "measureScore.denominator": None,
                "group.subject": "Network-A",
            }
        ]
    )

    entries = MeasureReport.bundle_entries_from_dataframe(
        dataframe=dataframe,
        report_type="summary",
        id_prefix="comparator-measure-report",
        subject_column="group.subject",
        subject_resource_type="Organization",
    )

    assert entries == [
        {
            "fullUrl": "urn:uuid:comparator-measure-report-cmp-1",
            "resource": {
                "resourceType": "MeasureReport",
                "id": "comparator-measure-report-cmp-1",
                "status": "complete",
                "type": "summary",
                "measure": "urn:uuid:measure-Clean-Rating-01",
                "subject": {"reference": "Organization/Network-A"},
                "period": {
                    "start": "2025-01-01",
                    "end": "2025-01-31",
                },
                "group": [
                    {
                        "measureScore": {"value": 1.0},
                    }
                ],
            },
        }
    ]
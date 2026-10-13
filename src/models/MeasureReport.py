from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

import pandas as pd


@dataclass(frozen=True)
class MeasureReport:
    identifier: str
    measure: str
    period_start: str
    period_end: str
    measure_score_rate: float
    report_type: str = "individual"
    subject_reference: str | None = None
    group: list[dict[str, object]] | None = None
    extension: list[dict[str, object]] | None = None

    def to_json(self) -> dict[str, object]:
        resource: dict[str, object] = {
            "resourceType": "MeasureReport",
            "id": self.identifier,
            "status": "complete",
            "type": self.report_type,
            "measure": f"urn:uuid:measure-{self.measure}",
            "period": {
                "start": self.period_start,
                "end": self.period_end,
            },
            "group": self.group
            if self.group is not None
            else [{"measureScore": {"value": self.measure_score_rate}}],
        }

        if self.subject_reference is not None:
            resource["subject"] = {"reference": self.subject_reference}

        if self.extension:
            resource["extension"] = self.extension

        return resource

    @staticmethod
    def bundle_entries_from_dataframe(
        dataframe: pd.DataFrame,
        report_type: str = "individual",
        id_prefix: str = "measure-report",
        subject_column: str = "subject",
        subject_resource_type: str = "Practitioner",
    ) -> list[dict[str, object]]:
        """
        Create FHIR Bundle entries for MeasureReport resources from rows in a dataframe.

        Each row is treated as a single MeasureReport.
        """
        entries: list[dict[str, object]] = []
        
        if len(dataframe) == 0:
                raise ValueError("Expected at least 1 row, found 0")

        for idx, row in dataframe.reset_index(drop=True).iterrows():
            row_identifier = str(row.get("identifier") or idx)
            report_id = f"{id_prefix}-{row_identifier}"

            group = MeasureReport._default_group(row)

            subject_reference = None
            if subject_column in row and pd.notna(row[subject_column]):
                subject_reference = f"{subject_resource_type}/{row[subject_column]}"

            report = MeasureReport(
                identifier=report_id,
                measure=str(row["measure"]),
                period_start=MeasureReport._to_date_string(row["period.start"]),
                period_end=MeasureReport._to_date_string(row["period.end"]),
                measure_score_rate=float(row["measureScore.rate"]),
                report_type=report_type,
                subject_reference=subject_reference,
                group=[group],
            )

            entries.append(
                {
                    "fullUrl": f"urn:uuid:{report_id}",
                    "resource": report.to_json(),
                }
            )

        return entries

    @staticmethod
    def _default_group(row: pd.Series) -> dict[str, object]:
        group: dict[str, object] = {
            "measureScore": {"value": float(row["measureScore.rate"])}
        }

        if "measureScore.denominator" in row and pd.notna(row["measureScore.denominator"]):
            group["population"] = [
                {
                    "code": {"text": "denominator"},
                    "count": int(row["measureScore.denominator"]),
                }
            ]

        return group

    @staticmethod
    def _to_date_string(value: object) -> str:
        if isinstance(value, pd.Timestamp):
            return value.date().isoformat()
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        return str(value)
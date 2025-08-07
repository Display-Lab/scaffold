import json
import os
import re
import uuid
from pathlib import Path

import pandas as pd

# Path to the directory containing input files
os.environ.pop("INPUT_DIR", None)
INPUT_DIR = os.environ.setdefault(
    "INPUT_DIR",
    "/home/faridsei/dev/code/scaffold/bulk-up/random_performance_data/data_with_h",
)

output_dir = Path("random_performance_data/data_with_h_new_format")
output_dir.mkdir(exist_ok=True)


def extract_number(filename):
    # Extract numeric part from filename
    match = re.search(r"_(\d+)", filename)
    if match:
        return int(match.group(1))
    else:
        return float("inf")  # Return infinity if no numeric part found


def main():
    performance_rows = []
    preferences_rows = []
    history_rows = []
    columns = None
    input_files = sorted(
        [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")], key=extract_number
    )
    df_providers = pd.DataFrame(
        columns=["Provider_Number", "Institution", "Professional_Role"]
    )

    for filename in input_files:
        with open(os.path.join(INPUT_DIR, filename), "r") as file:
            data = json.load(file)
            performance_data = data["Performance_data"]
            if columns is None:
                columns = performance_data[0]
            for row in performance_data[1:]:
                performance_rows.append(row)

            preferences_rows.append([performance_data[1][0], data["Preferences"]])

            history_data = data["History"]

            history_rows.extend(
                [
                    [performance_data[1][0], key, value]
                    for key, value in history_data.items()
                ]
            )
            if data["institution_id"]:
                df_providers.loc[len(df_providers)] = [
                    performance_data[1][0],
                    data["institution_id"],
                    "resident",
                ]

    performance_data_df = pd.DataFrame(performance_rows, columns=columns)
    performance_data_df["identifier"] = [
        str(uuid.uuid4()) for _ in range(len(performance_data_df))
    ]

    performance_data_df.rename(
        columns={
            "staff_number": "subject",
            "month": "period.start",
            "denominator": "measureScore.denominator",
        },
        inplace=True,
    )

    performance_data_df["measureScore.rate"] = (
        performance_data_df["passed_count"]
        / performance_data_df["measureScore.denominator"]
    )

    performance_data_df["period.end"] = performance_data_df["period.start"]

    performance_data_df["period.end"] = pd.to_datetime(
        performance_data_df["period.start"]
    )
    performance_data_df["period.end"] = performance_data_df[
        "period.end"
    ] + pd.offsets.MonthEnd(0)
    performance_data_df["period.end"] = performance_data_df["period.end"].dt.strftime(
        "%Y-%m-%d"
    )
    performance_data_df["measureScore.range"] = None

    performance_data_df = performance_data_df.merge(
        df_providers[["Provider_Number", "Institution", "Professional_Role"]],
        left_on="subject",
        right_on="Provider_Number",
        how="left",
    )
    comparator_df = performance_data_df[
        [
            "measure",
            "period.start",
            "period.end",
            "peer_average_comparator",
            "peer_75th_percentile_benchmark",
            "peer_90th_percentile_benchmark",
            "MPOG_goal",
            "Institution",
            "Professional_Role",
        ]
    ]

    subject_data_df = performance_data_df[
        ["subject", "Institution", "Professional_Role"]
    ].drop_duplicates()
    subject_data_df["type"] = "Practitioner"

    subject_data_df.rename(
        columns={
            "subject": "PractitionerRole.practitioner",
            "Institution": "PractitionerRole.organization",
            "Professional_Role": "PractitionerRole.code",
        },
        inplace=True,
    )

    performance_data_df = performance_data_df[
        [
            "identifier",
            "measure",
            "subject",
            "period.start",
            "period.end",
            "measureScore.rate",
            "measureScore.denominator",
            "measureScore.range",
        ]
    ]

    preferences_data_df = pd.DataFrame(
        preferences_rows, columns=["subject", "preferences.json"]
    )
    preferences_data_df = preferences_data_df[
        preferences_data_df["preferences.json"] != {}
    ]

    history_data_df = pd.DataFrame(
        history_rows, columns=["subject", "period.start", "history.json"]
    )
    history_data_df["period.end"] = history_data_df["period.start"]
    history_data_df["period.end"] = pd.to_datetime(history_data_df["period.start"])
    history_data_df["period.end"] = history_data_df["period.end"] + pd.offsets.MonthEnd(
        0
    )
    history_data_df["period.end"] = history_data_df["period.end"].dt.strftime(
        "%Y-%m-%d"
    )
    history_data_df = history_data_df[
        ["subject", "period.start", "period.end", "history.json"]
    ]

    comparator_df = comparator_df.drop_duplicates()
    comparator_df = comparator_df.melt(
        id_vars=[
            "measure",
            "period.start",
            "period.end",
            "Institution",
            "Professional_Role",
        ],
        value_vars=[
            "peer_average_comparator",
            "peer_75th_percentile_benchmark",
            "peer_90th_percentile_benchmark",
            "MPOG_goal",
        ],
        var_name="group.code",  # new column for the original column names
        value_name="measureScore.rate",  # new column for the values
    )
    comparator_df.rename(
        columns={
            "Institution": "group.subject",
            "Professional_Role": "PractitionerRole.code",
        },
        inplace=True,
    )
    comparator_df["identifier"] = [str(uuid.uuid4()) for _ in range(len(comparator_df))]
    comparator_df = comparator_df[
        [
            "identifier",
            "measure",
            "period.start",
            "measureScore.rate",
            "period.end",
            "group.subject",
            "group.code",
            "PractitionerRole.code",
        ]
    ]

    type_mapping = {
        "peer_average_comparator": "http://purl.obolibrary.org/obo/PSDO_0000126",
        "peer_75th_percentile_benchmark": "http://purl.obolibrary.org/obo/PSDO_0000128",
        "peer_90th_percentile_benchmark": "http://purl.obolibrary.org/obo/PSDO_0000129",
        "MPOG_goal": "http://purl.obolibrary.org/obo/PSDO_0000094",
    }

    comparator_df["group.code"] = comparator_df["group.code"].replace(type_mapping)

    for filename in input_files:
        with open(os.path.join(INPUT_DIR, filename), "r") as file:
            data = json.load(file)
            subject = data["Performance_data"][1][0]

            data_with_new_format = {
                "message_instance_id": f"{str(uuid.uuid4())}",
                "performance_month": data["performance_month"],
                "subject": subject,
                "PractitionerRole": [
                    [
                        "PractitionerRole.practitioner",
                        "PractitionerRole.organization",
                        "PractitionerRole.code",
                        "type",
                    ],
                    [subject, data["institution_id"], "resident", "Practitioner"],
                ],
                "performance_measurer_report": [performance_data_df.columns.tolist()]
                + performance_data_df[
                    performance_data_df["subject"] == subject
                ].values.tolist(),
                "comparator_measurer_report": [comparator_df.columns.tolist()]
                + comparator_df[
                    comparator_df["group.subject"] == data["institution_id"]
                ].values.tolist(),
                "History": data["History"],
                "Preferences": data["Preferences"],
                "debug": "no",
            }

            file_name = f"Provider_{str(subject)}.json"
            file_path = output_dir / file_name

            # Write JSON file
            with open(file_path, "w") as f:
                json.dump(data_with_new_format, f, indent=2)


if __name__ == "__main__":
    main()

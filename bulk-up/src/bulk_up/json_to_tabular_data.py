import json
import os
import re
import uuid

import pandas as pd

# Path to the directory containing input files
INPUT_DIR = os.environ.setdefault("INPUT_DIR", "/home/faridsei/dev/test/MPOG/2024-09_h")


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

    performance_data_df = pd.DataFrame(performance_rows, columns=columns)
    performance_data_df["identifier"] = [
        str(uuid.uuid4()) for _ in range(len(performance_data_df))
    ]

    performance_data_df.rename(
        columns={
            "staff_number": "subject",
            "month": "period.start",
            "denominator": "measureScore[x].denominator",
        },
        inplace=True,
    )

    performance_data_df["measureScore[x].rate"] = (
        performance_data_df["passed_count"]
        / performance_data_df["measureScore[x].denominator"]
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
    performance_data_df["measureScore[x].range"] = None
    performance_data_df = performance_data_df[
        [
            "identifier",
            "measure",
            "subject",
            "period.start",
            "period.end",
            "measureScore[x].rate",
            "measureScore[x].denominator",
            "measureScore[x].range",
        ]
    ]

    subject_data_df = performance_data_df[["subject"]].drop_duplicates()
    subject_data_df["type"] = "Practitioner"
    subject_data_df["PractitionerRole.code"] = ""
    subject_data_df["PractitionerRole.organization"] = ""

    preferences_data_df = pd.DataFrame(
        preferences_rows, columns=["subject", "preferences.json"]
    )

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

    subject_data_df.rename(
        columns={
            "subject": "PractitionerRole.practitioner"
        },
        inplace=True,
    )

    performance_data_df.to_csv("PerformanceData.csv", index=False)
    subject_data_df.to_csv("PractitionerRole.csv", index=False)
    preferences_data_df.to_csv("Preference.csv", index=False)
    history_data_df.to_csv("MessageHistory.csv", index=False)
    
    # with pd.ExcelWriter("output.xlsx", engine="openpyxl") as writer:
    #     performance_data_df.to_excel(writer, sheet_name="performance data", index=False)
    #     subject_data_df.to_excel(writer, sheet_name="PractitionerRole", index=False)
    #     preferences_data_df.to_excel(writer, sheet_name="preference data", index=False)
    #     history_data_df.to_excel(writer, sheet_name="message history data", index=False)


if __name__ == "__main__":
    main()

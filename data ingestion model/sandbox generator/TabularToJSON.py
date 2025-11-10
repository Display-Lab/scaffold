import argparse
import ast
import copy
import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

from utils import message_template

start = time.time()

parser = argparse.ArgumentParser(
    description="Create JSON input message from tabular data."
)
parser.add_argument(
    "--path",
    type=str,
    default="/home/faridsei/dev/code/scaffold/data ingestion model/sandbox examples/",
    help="Output path",
)
parser.add_argument(
    "--performance_month", type=str, default="2025-01-01", help="Performance month"
)

args = parser.parse_args()
output_dir = Path(args.path)

new_folder = output_dir / "JSON Messages"
new_folder.mkdir(exist_ok=True)

performance_data_df = pd.read_csv(
    output_dir / "PerformanceMeasureReport.csv",
    parse_dates=["period.start", "period.end"],
)
practitioner_data_df = pd.read_csv(output_dir / "PractitionerRole.csv")
comparator_data_df = pd.read_csv(
    output_dir / "ComparatorMeasureReport.csv",
    parse_dates=["period.start", "period.end"],
)
history = pd.read_csv(output_dir / "MessageHistory.csv")
preferences = pd.read_csv(output_dir / "Preference.csv")
config = json.load(open(os.path.join(args.path, "config.json")))
performance_date = datetime.strptime(args.performance_month, "%Y-%m-%d")

for subject in performance_data_df["subject"].drop_duplicates():
    performance_df = performance_data_df[
        performance_data_df["subject"] == subject
    ].reset_index(drop=True)
    performance_df["period.start"] = pd.to_datetime(
        performance_df["period.start"]
    ).dt.strftime("%Y-%m-%d")
    performance_df["period.end"] = pd.to_datetime(
        performance_df["period.end"]
    ).dt.strftime("%Y-%m-%d")

    practitioner_role = practitioner_data_df[
        practitioner_data_df["PractitionerRole.identifier"] == subject
    ].copy()
    org_id = practitioner_role.iloc[0]["PractitionerRole.organization"]
    role = practitioner_role.iloc[0]["PractitionerRole.code"]
    comparator_df = comparator_data_df.copy().reset_index(drop=True)
    comparator_df["period.start"] = pd.to_datetime(
        comparator_df["period.start"]
    ).dt.strftime("%Y-%m-%d")
    comparator_df["period.end"] = pd.to_datetime(
        comparator_df["period.end"]
    ).dt.strftime("%Y-%m-%d")
    if "group.subject" in config["ComparatorMergeColumns"]:
        comparator_df = comparator_df[
            comparator_df["group.subject"] == org_id
        ].reset_index(drop=True)
    if "PractitionerRole.code" in config["ComparatorMergeColumns"]:
        comparator_df = comparator_df[
            comparator_df["PractitionerRole.code"] == role
        ].reset_index(drop=True)

    try:
        preferences_dict = preferences.loc[subject, "preferences.json"]
    except Exception:
        preferences_dict = {}

    try:
        history_data = history[history["subject"] == subject].copy()
        history_data["history.json"] = history_data["history.json"].apply(
            ast.literal_eval
        )
        history_dict = history_data.set_index("period.start")["history.json"].to_dict()
    except Exception:
        history_dict = {}

    message = copy.deepcopy(message_template)
    message["message_instance_id"] = str(uuid.uuid4())
    message["performance_month"] = args.performance_month
    message["subject"] = subject
    message["PractitionerRole"].extend(practitioner_role.fillna("").values.tolist())
    message["performance_measure_report"].extend(performance_df.values.tolist())
    message["comparator_measure_report"].extend(
        comparator_df.fillna("").values.tolist()
    )
    message["Preferences"] = preferences_dict
    message["History"] = history_dict
    json_file = new_folder / ("input_" + subject + ".json")

    # Write JSON to file
    with json_file.open("w") as f:
        json.dump(message, f, indent=2)

end = time.time()
print(f"Elapsed time to generate PractitionerRole: {end - start:.2f} seconds")

import csv
import re
from pathlib import Path

import orjson


def extract_number(filename):
    match = re.search(r"_(\d+)", str(filename))
    if match:
        return int(match.group(1))
    else:
        return float("inf")  # Return infinity if no numeric part found


file_path = Path("/home/faridsei/dev/test/2024-06-24/2024-05-01/")
input_files = sorted(file_path.glob("*.json"), key=extract_number)
with open("performance_data.csv", "w", newline="") as file:
    writer = csv.writer(file)
    for index, input_file in enumerate(input_files):
        input_data = orjson.loads(input_file.read_bytes())
        if index == 0:
            writer.writerows(input_data["Performance_data"])
        else:
            writer.writerows(input_data["Performance_data"][1:])


fieldnames = [
    "staff_number",
    "Social gain",
    "Social stayed better",
    "Worsening",
    "Improving",
    "Social loss",
    "Social stayed worse",
    "Social better",
    "Social worse",
    "Social approach",
    "Goal gain",
    "Goal approach",
    "Display_Format",
]
with open("preferences.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for index, input_file in enumerate(input_files):
        input_data = orjson.loads(input_file.read_bytes())
        if input_data["Preferences"].get("Utilities", {}).get("Message_Format", {}):
            preferences = {"staff_number": input_data["Performance_data"][1][0]}
            preferences.update(
                input_data["Preferences"].get("Utilities", {}).get("Message_Format", {})
            )
            preferences["Display_Format"] = next(
                (
                    k
                    for k, v in input_data["Preferences"]
                    .get("Utilities", {})
                    .get("Display_Format", {})
                    .items()
                    if v == 1
                ),
                None,
            )
            writer.writerows([preferences])

all_keys = set(["staff_number"])
for input_file in input_files:
    input_data = orjson.loads(input_file.read_bytes())
    all_keys.update(input_data["History"].keys())
with open("history.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=all_keys)
    writer.writeheader()
    for index, input_file in enumerate(input_files):
        input_data = orjson.loads(input_file.read_bytes())
        if input_data["History"]:
            history = {"staff_number": input_data["Performance_data"][1][0]}
            history.update(input_data["History"])
            writer.writerows([history])

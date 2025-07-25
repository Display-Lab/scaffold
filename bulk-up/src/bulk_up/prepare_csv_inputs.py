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


file_path = Path("/home/faridsei/dev/code/scaffold/bulk-up/random_performance_data/")
input_files = sorted(file_path.glob("*.json"), key=extract_number)
with open("performance_data.csv", "w", newline="") as file:
    writer = csv.writer(file)
    for index, input_file in enumerate(input_files):
        input_data = orjson.loads(input_file.read_bytes())
        if index == 0:
            writer.writerows(input_data["Performance_data"])
        else:
            writer.writerows(input_data["Performance_data"][1:])


with open("preferences.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["staff_number", "preferences"])
    writer.writeheader()
    for index, input_file in enumerate(input_files):
        input_data = orjson.loads(input_file.read_bytes())
        preferences = {
            "staff_number": input_data["Performance_data"][1][0],
            "preferences": orjson.dumps(input_data["Preferences"]).decode(),
        }

        writer.writerows([preferences])

all_keys = set(["staff_number", "month", "history"])
for input_file in input_files:
    input_data = orjson.loads(input_file.read_bytes())
with open("history.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=all_keys)
    writer.writeheader()
    for index, input_file in enumerate(input_files):
        input_data = orjson.loads(input_file.read_bytes())
        for key, value in input_data["History"].items():
            history = {
                "staff_number": input_data["Performance_data"][1][0],
                "month": key,
                "history": orjson.dumps(value).decode(),
            }
            writer.writerows([history])

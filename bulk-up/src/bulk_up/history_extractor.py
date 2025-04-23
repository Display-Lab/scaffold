import json
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

# Path to the directory containing input files
INPUT_DIR = os.environ.setdefault("INPUT_DIR", "")
WORKERS = int(os.environ.setdefault("WORKERS", "1"))
OUTPUT = os.environ.get("OUTPUT", "history_output.csv")

history_df: pd.DataFrame = pd.DataFrame()
lock = threading.Lock()


def add_history(filename):
    global history_df
    print(f"processing {filename}", end="\r")
    try:
        with open(os.path.join(INPUT_DIR, filename), "r") as file:
            data = None
            try:
                data = json.load(file)
            except Exception as e:
                print(f"file: {filename} failed. {e}")
                return

            performance_data = data["Performance_data"][1:]
            passed_rate = {}
            for row in performance_data:
                if row[1] not in passed_rate:
                    passed_rate[row[1]] = {}
                if int(row[5])!=0:
                    passed_rate[row[1]][row[2]] = int(row[3]) / int(row[5])
                else:
                    passed_rate[row[1]][row[2]]=0

            with lock:
                for key, value in data["History"].items():
                    history_dict: dict = {
                        "staff_number": data["Performance_data"][1][0],
                        "month": key,
                        "passed_rate": passed_rate[value["measure"]][key],
                        "selected message": value["message_template_name"],
                        "selected measure": value["measure"],
                        "causal_pathway": value["acceptable_by"][0],
                    }
                    history_df = pd.concat(
                        [history_df, pd.DataFrame([history_dict])], ignore_index=True
                    )

    except Exception as e:
        print(f"Error processing {filename}: {e}")


def extract_number(filename):
    # Extract numeric part from filename
    match = re.search(r"_(\d+)", filename)
    if match:
        return int(match.group(1))
    else:
        return float("inf")  # Return infinity if no numeric part found


def main():
    global count

    input_files = sorted(
        [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")], key=extract_number
    )

    with ThreadPoolExecutor(WORKERS) as executor:
        executor.map(add_history, input_files)

    if OUTPUT:
        history_df.to_csv(OUTPUT, index=False)


if __name__ == "__main__":
    main()

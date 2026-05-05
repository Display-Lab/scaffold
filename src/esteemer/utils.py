import os
import csv
import requests
from io import StringIO

def load_mpm_from_env() -> dict:
    mpm_dict = {}
    mpm_path: str = os.getenv("mpm")
    if mpm_path is None:
        raise ValueError("Environment variable 'mpm' must be set to the MPM file path or URL.")
    if mpm_path.startswith("http"):
        response = requests.get(mpm_path)
        response.raise_for_status()
        csv_content = StringIO(response.text)
        file = csv_content
    else:
        file = open(mpm_path, mode="r")

    reader = csv.DictReader(file)
    for row in reader:
        outer_key = row.pop("causal_pathway")
        mpm_dict[outer_key] = {
            k: (float(v) if v != "" else None) for k, v in row.items()
        }

    if not mpm_path.startswith("http"):
        file.close()

    return mpm_dict


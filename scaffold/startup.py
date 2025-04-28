import csv
import json
from io import StringIO

import requests
from rdflib import Graph
from requests_file import FileAdapter

from scaffold.utils.graph_operations import manifest_to_graph
from scaffold.utils.settings import settings

mpm: dict = {}
default_preferences: dict = {}
base_graph: Graph = Graph()

# Set up request session as se, config to handle file URIs with FileAdapter
se = requests.Session()
se.mount("file://", FileAdapter())


def startup():
    try:
        global base_graph, mpm, default_preferences

        mpm = load_mpm()

        preferences_text = se.get(settings.preferences).text
        default_preferences = json.loads(preferences_text)

        base_graph = manifest_to_graph(settings.manifest)

    except Exception as e:
        print("Startup aborted, see traceback:")
        raise e


def set_preferences(req_info):
    preferences_utilities = req_info.get("Preferences", {}).get("Utilities", {})
    input_preferences: dict = preferences_utilities.get("Message_Format", {})
    individual_preferences: dict = {}
    for key in input_preferences:
        individual_preferences[key.lower()] = float(input_preferences[key])

    preferences: dict = default_preferences.copy()
    preferences.update(individual_preferences)

    min_value = min(preferences.values())
    max_value = max(preferences.values())

    for key in preferences:
        preferences[key] = (preferences[key] - min_value) / (max_value - min_value)

    display_format = None
    for key, value in preferences_utilities.get("Display_Format", {}).items():
        if value == 1 and key != "System-generated":
            display_format = key.lower()

    return {"Message_Format": preferences, "Display_Format": display_format}


### read csv file to a dictionary
def load_mpm() -> dict:
    mpm_dict = {}

    if settings.mpm.startswith("http"):
        response = requests.get(settings.mpm)
        response.raise_for_status()
        csv_content = StringIO(response.text)
        file = csv_content
    else:
        file = open(settings.mpm, mode="r")

    reader = csv.DictReader(file)
    for row in reader:
        outer_key = row.pop("causal_pathway")
        mpm_dict[outer_key] = {
            k: (float(v) if v != "" else None) for k, v in row.items()
        }

    if not settings.mpm.startswith("http"):
        file.close()

    return mpm_dict

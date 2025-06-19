import csv
import json
import pathlib
from io import StringIO

import matplotlib
import pandas as pd
import requests
from loguru import logger
from rdflib import Graph
from requests_file import FileAdapter

from scaffold.utils.graph_operations import manifest_to_graph
from scaffold.utils.settings import settings
from scaffold.utils.utils import set_logger

set_logger()

matplotlib.use("Agg")
mpm: dict = {}
default_preferences: dict = {}
base_graph: Graph = Graph()
preferences: pd.DataFrame = pd.DataFrame(
    columns=["staff_number", "preferences"], index=["staff_number"]
)
history: pd.DataFrame = pd.DataFrame(
    columns=["staff_number", "month", "history"], index=["staff_number"]
)
performance_data = pd.DataFrame()

# Set up request session as se, config to handle file URIs with FileAdapter
se = requests.Session()
se.mount("file://", FileAdapter())


def startup(performance_data_path: pathlib.Path = None):
    ## Log of instance configuration
    logger.debug("Startup configuration for this instance:")
    for attribute in dir(settings):
        if not attribute.startswith("__"):
            value = getattr(settings, attribute)
            logger.debug(f"{attribute}:\t{value}")

    try:
        global \
            base_graph, \
            mpm, \
            default_preferences, \
            preferences, \
            history, \
            performance_data

        mpm = load_mpm()

        default_preferences_text = se.get(settings.default_preferences).text
        default_preferences_original_dict = json.loads(default_preferences_text)
        default_preferences = {
            k.lower(): v for k, v in default_preferences_original_dict.items()
        }

        base_graph = manifest_to_graph(settings.manifest)

        if settings.preferences != "None":
            preferences = pd.read_csv(
                settings.preferences, converters={"preferences": json.loads}
            )
            preferences.set_index("staff_number", inplace=True, drop=False)
        if settings.history != "None":
            history = pd.read_csv(
                settings.history,
                converters={"history": json.loads},
                dtype={"month": str},
            )
            history.set_index("staff_number", inplace=True, drop=False)

        if performance_data_path:
            performance_data = pd.read_csv(performance_data_path, parse_dates=["month"])

    except Exception as e:
        print("Startup aborted, see traceback:")
        raise e


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

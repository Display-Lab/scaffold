import csv
import json
from io import StringIO

import matplotlib
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

# Set up request session as se, config to handle file URIs with FileAdapter
se = requests.Session()
se.mount("file://", FileAdapter())


def startup():
    ## Log of instance configuration
    logger.debug("Startup configuration for this instance:")
    for attribute in dir(settings):
        if not attribute.startswith("__"):
            value = getattr(settings, attribute)
            logger.debug(f"{attribute}:\t{value}")

    try:
        global base_graph, mpm, default_preferences

        mpm = load_mpm()

        default_preferences_text = se.get(settings.default_preferences).text
        default_preferences = json.loads(default_preferences_text)

        base_graph = manifest_to_graph(settings.manifest)

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

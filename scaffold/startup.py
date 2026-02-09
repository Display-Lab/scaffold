import csv
import json
import os
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
config: dict = {}
base_graph: Graph = Graph()
preferences: pd.DataFrame = pd.DataFrame(
    columns=["subject", "preference.json"], index=["subject"]
)
history: pd.DataFrame = pd.DataFrame(
    columns=["subject", "period.start", "period.end", "history.json"], index=["subject"]
)
# performance_data = pd.DataFrame()
performance_measure_report = pd.DataFrame()
practitioner_role = pd.DataFrame()
comparator_measure_report = pd.DataFrame()

performance_month = ""

# Set up request session as se, config to handle file URIs with FileAdapter
se = requests.Session()
se.mount("file://", FileAdapter())


def startup(performance_data_path: pathlib.Path = None, performance_m: str = ""):
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
            performance_measure_report, \
            comparator_measure_report, \
            practitioner_role, \
            performance_month, \
            config

        mpm = load_mpm()

        default_preferences_text = se.get(settings.default_preferences).text
        default_preferences_original_dict = json.loads(default_preferences_text)
        default_preferences = {
            k.lower(): v for k, v in default_preferences_original_dict.items()
        }

        base_graph = manifest_to_graph(settings.manifest)

        if performance_data_path:
            performance_measure_report = pd.read_csv(
                os.path.join(performance_data_path, "PerformanceMeasureReport.csv"),
                parse_dates=["period.start", "period.end"],
                dtype={"subject": str}                
            )
            
            # force the column to numeric and drop bad rows
            performance_measure_report["measureScore.rate"] = pd.to_numeric(
                performance_measure_report["measureScore.rate"],
                errors="coerce"
            )
            performance_measure_report = performance_measure_report.dropna(
                subset=["measureScore.rate"]
            )
            
            comparator_measure_report = pd.read_csv(
                os.path.join(performance_data_path, "ComparatorMeasureReport.csv"),
                parse_dates=["period.start", "period.end"],
            )
            practitioner_role = pd.read_csv(
                os.path.join(performance_data_path, "PractitionerRole.csv"),
                dtype={"PractitionerRole.identifier": str},
            )
            config = json.load(open(os.path.join(performance_data_path, "config.json")))

            if settings.use_preferences:
                preferences_file = os.path.join(performance_data_path, "Preference.csv")
                if os.path.exists(preferences_file):
                    preferences = pd.read_csv(
                        preferences_file, converters={"preferences": json.loads}
                    )
                    preferences.set_index("subject", inplace=True, drop=False)
            if settings.use_history:
                history_file = os.path.join(performance_data_path, "MessageHistory.csv")
                if os.path.exists(history_file):
                    history = pd.read_csv(
                        history_file,
                        converters={"history": json.loads},
                        dtype={"period.start": str},
                    )
                    history.set_index("subject", inplace=True, drop=False)

        if settings.performance_month:
            performance_month = settings.settings.performance_month

        if performance_m:
            performance_month = performance_m

    except Exception as e:
        print("Startup aborted:", e)
        exit(0)


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

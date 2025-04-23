import json
import os
import sys

import pandas as pd
from rdflib import RDF, RDFS, Graph, URIRef

module_path = ".."  # run this script from the bulk-up folder. This will add the directory above (which is precision-feedback-pipeline/) to system path to be able to import pipeline modules
sys.path.append(module_path)
from bitstomach.bitstomach import prepare
from bitstomach.signals._achievement import Achievement
from bitstomach.signals._approach import Approach
from bitstomach.signals._comparison import Comparison
from bitstomach.signals._loss import Loss
from bitstomach.signals._trend import Trend
from utils.graph_operations import manifest_to_graph
from utils.namespace._IAO import IAO
from utils.namespace._PSDO import PSDO
from utils.namespace._SLOWMO import SLOWMO

INPUT_DIR = os.environ.get(
    "INPUT_DIR",
    "/home/faridsei/dev/test/Precision Feedback Message Log 2024-08-20.xlsx",
)
KNOWLEDGE_BASE_LOCAL_MANIFEST = os.environ.get(
    "KNOWLEDGE_BASE_LOCAL_MANIFEST",
    "file:///home/faridsei/dev/code/knowledge-base/mpog_local_manifest.yaml",
)
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output.xlsx")
SHEET_NAME = "Sheet1"  # Change this to the name of the sheet in your .xlsx file

df = pd.read_excel(INPUT_DIR, sheet_name=SHEET_NAME, engine="openpyxl")
response_df: pd.DataFrame = pd.DataFrame()

graph: Graph = manifest_to_graph(
    KNOWLEDGE_BASE_LOCAL_MANIFEST
)

is_about_to_columns: dict = {
    PSDO.achievement_set: "represented set",
    PSDO.loss_set: "represented set",
    PSDO.approach_set: "represented set",
    PSDO.peer_average_comparator: "comparator content",
    PSDO.peer_75th_percentile_benchmark: "comparator content",
    PSDO.peer_90th_percentile_benchmark: "comparator content",
    PSDO.goal_comparator_content: "comparator content",
    PSDO.social_comparator_element: "comparative element",
    PSDO.goal_comparator_element: "comparative element",
    PSDO.negative_performance_trend_set: "performance trend set",
    PSDO.positive_performance_trend_set: "performance trend set",
    PSDO.negative_performance_gap_set: "performance gap set",
    PSDO.positive_performance_gap_set: "performance gap set",
}

comparator_name_to_iri: dict = {
    "peer 90th percentile benchmark": PSDO.peer_90th_percentile_benchmark,
    "peer 75th percentile benchmark": PSDO.peer_75th_percentile_benchmark,
    "peer average comparator": PSDO.peer_average_comparator,
    "goal comparator content": PSDO.goal_comparator_content,
}


def generate_response(output_message, input_message):
    selected_candidate = output_message.get("selected_candidate", None)
    global response_df
    response_dict: dict = {
        "Performance Month": input_message.get("performance_month", None),
        "Message instance ID": input_message.get("message_instance_id", None),
        "Recipient ID": output_message.get("staff_number", None),
        "Message template ID": selected_candidate["message_template_id"],
        "Message template name": selected_candidate.get(
            "message_template_name", "missing"
        ),
        "represented set": "",
        "performance gap set": "",
        "performance trend set": "",
        "comparative element": "",
        "comparator content": "",
        "causal_pathway": selected_candidate["acceptable_by"],
        "measure": selected_candidate["measure"],
    }

    is_about_set = set(
        graph.objects(URIRef(selected_candidate["message_template_id"]), IAO.is_about)
    )

    if {
        PSDO.negative_performance_gap_set,
        PSDO.positive_performance_gap_set,
    } & is_about_set:
        response_dict["represented set"] = "performance gap set"

    if {
        PSDO.negative_performance_trend_set,
        PSDO.positive_performance_trend_set,
    } & is_about_set:
        response_dict["represented set"] = "performance trend set"

    for is_about in is_about_set:
        if is_about in is_about_to_columns:
            column_name = is_about_to_columns[is_about]
            response_dict[column_name] = graph.value(is_about, RDFS.label).value

    return pd.DataFrame(response_dict)


def add_signal_properties(row, output_message, input_message):
    performance_df = prepare(input_message)
    performance_df = performance_df[
        performance_df["measure"] == output_message["selected_candidate"]["measure"]
    ].tail(12)

    represented_set = row["represented set"][0]
    if represented_set == "performance gap set":
        comparison = Comparison.detect(performance_df)
        comparator = comparator_name_to_iri[row["comparator content"][0]]
        for signal in comparison:
            if (
                signal.value(SLOWMO.RegardingComparator / RDF.type).identifier
                == comparator
            ):
                row["PerformanceGapSize"] = signal.value(
                    SLOWMO.PerformanceGapSize
                ).value
    elif represented_set == "performance trend set":
        signal = Trend.detect(performance_df)[0]
        row["PerformanceTrendSlope"] = signal.value(SLOWMO.PerformanceTrendSlope).value
    elif represented_set in {"achievement set", "loss set", "approach set"}:
        signal_class = {
            "achievement set": Achievement,
            "loss set": Loss,
            "approach set": Approach,
        }.get(represented_set)
        signals = signal_class.detect(performance_df)
        comparator = comparator_name_to_iri[row["comparator content"][0]]
        for signal in signals:
            if (
                signal.value(SLOWMO.RegardingComparator / RDF.type).identifier
                == comparator
            ):
                row["PerformanceGapSize"] = signal.value(
                    SLOWMO.PerformanceGapSize
                ).value
                row["PerformanceTrendSlope"] = signal.value(
                    SLOWMO.PerformanceTrendSlope
                ).value
                row["PriorPerformanceGapSize"] = signal.value(
                    SLOWMO.PriorPerformanceGapSize
                ).value
                row["StreakLength"] = signal.value(SLOWMO.StreakLength).value
    return row


total_messages = len(df["Output_Message"])
for index, message in enumerate(df["Output_Message"]):
    if pd.isnull(message):
        continue

    message_parts = message.split(',"image":')
    if len(message_parts) > 1:
        output_message = json.loads(message_parts[0] + "}}")
    else:
        output_message = json.loads(message)

    input_message = json.loads(df.at[index, "Input_Message"].replace("_x000D_", ""))

    new_row = generate_response(output_message, input_message)
    add_signal_properties(new_row, output_message, input_message)

    response_df = pd.concat([response_df, new_row], ignore_index=True)

    percentage_complete = ((index + 1) / total_messages) * 100
    print(f"\rProgress: {percentage_complete:.2f}% complete", end="")
response_df.to_excel(OUTPUT_DIR, index=False)

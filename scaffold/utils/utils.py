import re
import sys

import pandas as pd
from loguru import logger

from scaffold import context
from scaffold.utils.settings import settings

candidate_df: pd.DataFrame = pd.DataFrame()
response_df: pd.DataFrame = pd.DataFrame()


def analyse_responses():
    global response_df

    r2 = (
        response_df.groupby("causal_pathway")["staff_number"]
        .agg(count=("count"))
        .reset_index()
    )

    r2["%  "] = round(r2["count"] / r2["count"].sum() * 100, 1)

    print(f"\n {r2} \n")


def analyse_candidates(OUTPUT):
    global candidate_df

    if OUTPUT:
        candidate_df.to_csv(OUTPUT, index=False)

    candidate_df.rename(columns={"acceptable_by": "causal_pathway"}, inplace=True)
    candidate_df["score"] = candidate_df["score"].astype(float)
    candidate_df.rename(columns={"name": "message"}, inplace=True)

    # causal pathways
    causal_pathway_report = build_table("causal_pathway")
    print(causal_pathway_report, "\n")

    # messages
    message_report = build_table("message")
    print(message_report, "\n")

    # measures
    measure_report = build_table("measure")
    print(measure_report, "\n")


def build_table(grouping_column):
    report_table = (
        candidate_df.groupby(grouping_column)["selected"]
        .agg(acceptable=("count"), selected=("sum"))
        .reset_index()
    )
    scores = round(
        candidate_df.groupby(grouping_column)["score"]
        .agg(acceptable_score=("mean"))
        .reset_index(),
        2,
    )
    report_table = pd.merge(report_table, scores, on=grouping_column, how="left")

    report_table["% acceptable"] = round(
        report_table["acceptable"] / report_table["acceptable"].sum() * 100, 1
    )
    report_table["% selected"] = round(
        report_table["selected"] / report_table["selected"].sum() * 100, 1
    )
    report_table["% of acceptable selected"] = round(
        report_table["selected"] / report_table["acceptable"] * 100, 1
    )
    selected_scores = round(
        candidate_df[candidate_df["selected"]]
        .groupby(grouping_column)["score"]
        .agg(selected_score=("mean"))
        .reset_index(),
        2,
    )
    report_table = pd.merge(
        report_table, selected_scores, on=grouping_column, how="left"
    )

    report_table = report_table[
        [
            grouping_column,
            "acceptable",
            "% acceptable",
            "acceptable_score",
            "selected",
            "% selected",
            "selected_score",
            "% of acceptable selected",
        ]
    ]

    return report_table


def add_candidates(response_data: dict):
    global candidate_df
    data = response_data.get("candidates", None)
    if data:
        candidates = pd.DataFrame(data[1:], columns=data[0])
        candidates["performance_month"] = context.performance_month
        candidate_df = pd.concat([candidate_df, candidates], ignore_index=True)


def add_response(response_data):
    global response_df
    selected_candidate = response_data.get("selected_candidate", None)

    response_dict: dict = {
        "staff_number": [response_data.get("staff_number", None)],
        "causal_pathway": selected_candidate["acceptable_by"]
        if selected_candidate
        else [None],
    }
    response_df = pd.concat(
        [response_df, pd.DataFrame(response_dict)], ignore_index=True
    )
    print(response_dict, end="\r")


def extract_number(filename):
    # Extract numeric part from filename
    match = re.search(r"_(\d+)", str(filename))
    if match:
        return int(match.group(1))
    else:
        return float("inf")  # Return infinity if no numeric part found


def set_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="{level}|  {message}",
        level=settings.log_level,
    )
    logger.at_least = (
        lambda lvl: logger.level(lvl).no >= logger.level(settings.log_level).no
    )

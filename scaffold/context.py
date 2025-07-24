import ast

import pandas as pd
from rdflib import Graph

from scaffold import startup

preferences_dict = {}
history_dict = {}
subject = 0
performance_month = ""
performance_df: pd.DataFrame
subject_graph = Graph()


def from_req(req_info):
    global \
        preferences_dict, \
        history_dict, \
        subject, \
        performance_month, \
        performance_df, \
        subject_graph

    try:
        performance_df = pd.DataFrame(
            req_info["Performance_data"][1:], columns=req_info["Performance_data"][0]
        )
    except Exception:
        pass

    performance_month = startup.performance_month
    if req_info["performance_month"]:
        performance_month = req_info["performance_month"]
    if not performance_month:
        performance_month = performance_df["period.start"].max()

    subject = int(performance_df.at[0, "staff_number"])

    preferences_dict = {}
    try:
        preferences_dict = set_preferences(req_info.get("Preferences", {}))
    except Exception:
        preferences_dict = set_preferences({})

    history_dict = {}
    try:
        history_dict = req_info.get("History", {})
    except Exception:
        pass

    subject_graph = Graph()
    subject_graph += startup.base_graph


def from_global(subject_num):
    global \
        preferences_dict, \
        history_dict, \
        subject, \
        performance_month, \
        performance_df, \
        subject_graph

    subject = int(subject_num)

    try:
        performance_df = startup.performance_measure_report[
            startup.performance_measure_report["subject"] == subject
        ].reset_index(drop=True)

        # prepare performance data
        performance_enriched = performance_df.merge(
            startup.practitioner_role,
            how="left",
            left_on="subject",
            right_on="PractitionerRole.practitioner",
        )

        pivoted_comparator = startup.comparator_measure_report.pivot_table(
            index=["period.start", "measure", "group.subject", "PractitionerRole.code"],
            columns="group.code",
            values="measureScore.rate",
        ).reset_index()

        final_df = performance_enriched.merge(
            pivoted_comparator,
            how="left",
            left_on=[
                "period.start",
                "measure",
                "PractitionerRole.organization",
                "PractitionerRole.code",
            ],
            right_on=[
                "period.start",
                "measure",
                "group.subject",
                "PractitionerRole.code",
            ],
        ).drop(columns=["group.subject"])

        performance_df = final_df.copy()
    except Exception:
        pass

    performance_month = startup.performance_month
    if not performance_month:
        performance_month = performance_df["period.start"].max()

    preferences_dict = {}
    try:
        p = startup.preferences.loc[subject, "preferences.json"]
        preferences_dict = set_preferences(p)
    except Exception:
        preferences_dict = set_preferences({})

    history_dict = {}
    try:
        history_data = startup.history[startup.history["subject"] == subject].copy()
        history_data["history.json"] = history_data["history.json"].apply(
            ast.literal_eval
        )
        history_dict = history_data.set_index("period.start")["history.json"].to_dict()
    except Exception:
        pass

    subject_graph = Graph()
    subject_graph += startup.base_graph


def get_preferences():
    global preferences_dict
    return preferences_dict


def get_history():
    global history_dict
    return history_dict


def set_preferences(req_info):
    preferences_utilities = req_info.get("Utilities", {})
    input_preferences: dict = preferences_utilities.get("Message_Format", {})
    individual_preferences: dict = {}
    for key in input_preferences:
        individual_preferences[key.lower()] = float(input_preferences[key])

    preferences: dict = startup.default_preferences.copy()
    preferences.update(individual_preferences)

    if preferences:
        min_value = min(preferences.values())
        max_value = max(preferences.values())

        for key in preferences:
            preferences[key] = (preferences[key] - min_value) / (max_value - min_value)

    display_format = None
    for key, value in preferences_utilities.get("Display_Format", {}).items():
        if value == 1 and key != "System-generated":
            display_format = key.lower()  # display formats are hardcoded with lower case in pictoralist so lower() is used to keep it the same

    return {"Message_Format": preferences, "Display_Format": display_format}

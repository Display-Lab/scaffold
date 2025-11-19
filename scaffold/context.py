import ast

import pandas as pd
from rdflib import Graph

from scaffold import startup

preferences_dict = {}
history_dict = {}
subject = "0"
performance_month = ""
performance_df: pd.DataFrame
comparator_df: pd.DataFrame
subject_graph = Graph()
practitioner_role = pd.DataFrame()


def from_req(req_info):
    global \
        preferences_dict, \
        history_dict, \
        subject, \
        performance_month, \
        performance_df, \
        subject_graph, \
        comparator_df, \
        practitioner_role

    try:
        performance_df = pd.DataFrame(req_info["performance_measure_report"])
        
        comparator_df = pd.DataFrame(req_info["comparator_measure_report"])

        practitioner_role = pd.DataFrame(req_info["PractitionerRole"])
    except Exception:
        pass

    performance_month = startup.performance_month
    if req_info["performance_month"]:
        performance_month = req_info["performance_month"]
    if not performance_month:
        performance_month = performance_df["period.start"].max()

    subject = req_info["subject"] #int(req_info["subject"])

    preferences_dict = {}
    try:
        preferences_dict = set_preferences(req_info.get("Preferences", {}))
    except Exception:
        preferences_dict = set_preferences({})

    history_dict = {}
    try:
        history_list = req_info.get("History", {})
        history_dict = {
            item["period.start"]: {k: v for k, v in item.items() if k != "period.end" and k != "period.start"}
            for item in history_list
        }
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
        subject_graph, \
        comparator_df, \
        practitioner_role

    subject = subject_num #int(subject_num)

    try:
        performance_df = startup.performance_measure_report[
            startup.performance_measure_report["subject"] == subject
        ].reset_index(drop=True)
        practitioner_role = startup.practitioner_role[
            startup.practitioner_role["PractitionerRole.identifier"] == subject
        ].copy()
        org_id = practitioner_role.iloc[0]["PractitionerRole.organization"]
        role = practitioner_role.iloc[0]["PractitionerRole.code"]
        comparator_df = startup.comparator_measure_report.copy().reset_index(drop=True)
        if "group.subject" in startup.config["ComparatorMergeColumns"]:
            comparator_df = comparator_df[
                comparator_df["group.subject"] == org_id            
            ].reset_index(drop=True)
        if "PractitionerRole.code" in startup.config["ComparatorMergeColumns"]:    
            comparator_df = comparator_df[
               comparator_df["PractitionerRole.code"] == role
            ].reset_index(drop=True)        
    except Exception:
        pass

    performance_month = startup.performance_month
    if not performance_month:
        performance_month = performance_df["period.start"].max()

    preferences_dict = {}
    try:
        p = ast.literal_eval(startup.preferences.loc[subject, "preferences.json"])
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
        if max_value != min_value:
            for key in preferences:
                preferences[key] = (preferences[key] - min_value) / (max_value - min_value)

    display_format = None
    for key, value in preferences_utilities.get("Display_Format", {}).items():
        if value == 1 and key != "System-generated":
            display_format = key.lower()  # display formats are hardcoded with lower case in pictoralist so lower() is used to keep it the same

    return {"Message_Format": preferences, "Display_Format": display_format}

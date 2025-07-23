import pandas as pd
from rdflib import Graph

from scaffold import startup

preferences_dict = {}
history_dict = {}
staff_number = 0
performance_month = ""
performance_df: pd.DataFrame
subject_graph = Graph()


def from_req(req_info):
    global \
        preferences_dict, \
        history_dict, \
        staff_number, \
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
        performance_month = performance_df["month"].max()

    staff_number = int(performance_df.at[0, "staff_number"])

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


def from_global(staff_num):
    global \
        preferences_dict, \
        history_dict, \
        staff_number, \
        performance_month, \
        performance_df, \
        subject_graph

    staff_number = int(staff_num)

    try:
        performance_df = startup.performance_measure_report[
            startup.performance_measure_report["subject"] == staff_number
        ].reset_index(drop=True)
        
        # first simple attempt to read and prepare tabular data
        performance_df["staff_number"] = performance_df["subject"]
        performance_df["month"] = performance_df["period.start"]
        performance_df["denominator"] = performance_df["measureScore.denominator"]
        performance_df["passed_count"] = performance_df["measureScore.rate"] * performance_df["measureScore.denominator"]
        performance_df["flagged_count"] = performance_df["denominator"] - performance_df["passed_count"]
        performance_enriched = performance_df.merge(
            startup.practitioner_role,
            how='left',
            left_on='staff_number',
            right_on='PractitionerRole.practitioner'
        )
        
        group_code_map = {
            "http://purl.obolibrary.org/obo/PSDO_0000126": "peer_average_comparator",
            "http://purl.obolibrary.org/obo/PSDO_0000128": "peer_75th_percentile_benchmark",
            "http://purl.obolibrary.org/obo/PSDO_0000129": "peer_90th_percentile_benchmark",
            "http://purl.obolibrary.org/obo/PSDO_0000094": "MPOG_goal"
        }
        comparator_measure_report = startup.comparator_measure_report.copy()
        comparator_measure_report["group_code_label"] = comparator_measure_report["group.code"].map(group_code_map)
        pivoted_comparator = comparator_measure_report.pivot_table(
        index=["period.start", "measure", "group.subject", "PractitionerRole.code"],
            columns="group_code_label",
            values="measureScore.rate"
        ).reset_index()
        
        final_df = performance_enriched.merge(
            pivoted_comparator,
            how="left",
            left_on=["period.start", "measure", "PractitionerRole.organization", "PractitionerRole.code"],
            right_on=["period.start", "measure", "group.subject", "PractitionerRole.code"]
        ).drop(columns=["group.subject"])
        
        performance_df = final_df[["staff_number", "measure", "month", "passed_count", "flagged_count", "denominator", "peer_average_comparator", "peer_75th_percentile_benchmark", "peer_90th_percentile_benchmark", "MPOG_goal"]]
        startup.history["month"] = startup.history["period.start"]
        startup.history["staff_number"] = startup.history["subject"]
        startup.preferences["staff_number"] = startup.preferences["subject"]
        startup.preferences["preferences"] = startup.preferences["preferences.json"]
    except Exception:
        pass

    performance_month = startup.performance_month
    if not performance_month:
        performance_month = performance_df["month"].max()

    preferences_dict = {}
    try:
        p = startup.preferences.loc[staff_number, "preferences"]
        preferences_dict = set_preferences(p)
    except Exception:
        preferences_dict = set_preferences({})

    history_dict = {}
    try:
        staff_data = startup.history[startup.history["staff_number"] == staff_number]
        history_dict = staff_data.set_index("month")["history"].to_dict()
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

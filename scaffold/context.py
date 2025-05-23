import json

import numpy as np
import pandas as pd

from scaffold import startup
from scaffold.utils.settings import settings

preferences: pd.DataFrame = pd.DataFrame()
history: pd.DataFrame = pd.DataFrame()


def init():
    try:
        global preferences, history

        if settings.preferences is not None:
            preferences = pd.read_csv(settings.preferences)
        if settings.history is not None:
            history = pd.read_csv(settings.history, converters={"history": json.loads})

    except Exception as e:
        print("context init aborted, see traceback:")
        raise e


def update(req_info):
    try:
        global preferences, history
        staff_number = req_info["Performance_data"][1][0]

        preferences_dict = req_info.get("Preferences", {}).get("Utilities", {})
        if preferences_dict:
            new_row = {"staff_number": staff_number} | preferences_dict[
                "Message_Format"
            ]
            display_format = next(
                (
                    k
                    for k, v in preferences_dict.get("Display_Format", {}).items()
                    if v == 1
                ),
                "None",
            )
            new_row["Display_Format"] = display_format

            if preferences.empty:
                preferences = pd.DataFrame([new_row])
            elif not (preferences["staff_number"] == staff_number).any():
                preferences = pd.concat(
                    [preferences, pd.DataFrame([new_row])], ignore_index=True
                )

        history_dict: dict = req_info.get("History", {})

        if history.empty:
            history = pd.DataFrame(columns=["staff_number", "month", "history"])

        for key, value in history_dict.items():
            if (
                history.empty
                or history[
                    (history["staff_number"] == staff_number)
                    & (history["month"] == key)
                ].empty
            ):
                new_row = pd.DataFrame(
                    [{"staff_number": staff_number, "month": key, "history": value}]
                )
                history = pd.concat([history, pd.DataFrame(new_row)], ignore_index=True)
    except Exception as e:
        print("context update aborted, see traceback:")
        raise e


def get_preferences(staff_number):
    global preferences
    if preferences.empty:
        return set_preferences({})

    preferences_row = preferences[preferences["staff_number"] == staff_number]
    provider_preferences = {}
    if not preferences_row.empty:
        provider_preferences = {
            "Preferences": {"Utilities": {"Message_Format": {}, "Display_Format": {}}}
        }

        # We'll just use the first row of the CSV
        row = preferences_row.iloc[0]

        for key in preferences_row.columns:
            value = row[key]
            if key == "staff_number":
                continue  # skip or store if you need it
            elif key == "Display_Format":
                # Example: "Bar chart, Line chart"
                provider_preferences["Preferences"]["Utilities"]["Display_Format"] = {
                    "Bar chart": 0,
                    "Line chart": 0,
                    "Text-only": 0,
                    "System-generated": "0",
                }
                provider_preferences["Preferences"]["Utilities"]["Display_Format"][
                    value
                ] = 1
            else:
                if isinstance(value, (np.float64, np.int64)):
                    value = value.item()
                provider_preferences["Preferences"]["Utilities"]["Message_Format"][
                    key
                ] = value
    return set_preferences(provider_preferences)


def get_history(staff_number):
    global history

    if history.empty:
        return {}
    history_rows = history[history["staff_number"] == staff_number]
    if history_rows.empty:
        return {}

    provider_history = {}
    for index, row in history_rows.iterrows():
        history_item = row["history"]  # ast.literal_eval(row["history"])
        month = row["month"]
        provider_history[month] = history_item

    return provider_history


def set_preferences(req_info):
    preferences_utilities = req_info.get("Preferences", {}).get("Utilities", {})
    input_preferences: dict = preferences_utilities.get("Message_Format", {})
    individual_preferences: dict = {}
    for key in input_preferences:
        individual_preferences[key] = float(input_preferences[key])

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

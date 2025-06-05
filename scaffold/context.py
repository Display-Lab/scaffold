import pandas as pd

from scaffold import startup

preferences_dict = {}
history_dict = {}


def update(req_info):
    global preferences_dict, history_dict

    if not req_info:
        history_dict = {}
        preferences_dict = {}
        return

    try:
        preferences_dict = set_preferences(req_info.get("Preferences", {}))
        history_dict = req_info.get("History", {})
    except Exception as e:
        print("context update aborted, see traceback:")
        raise e


def get_preferences(staff_number):
    global preferences_dict

    if preferences_dict:
        return preferences_dict
    try:
        p = startup.preferences.loc[staff_number, "preferences"]
        if isinstance(p, pd.Series):
            p = p.iloc[0]
        return set_preferences(p)
    except Exception:
        return set_preferences({})


def get_history(staff_number):
    global history_dict

    if history_dict:
        return history_dict
    try:
        staff_data = startup.history[startup.history["staff_number"] == staff_number]
        history_dict = staff_data.set_index("month")["history"].to_dict()
    except Exception:
        pass

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

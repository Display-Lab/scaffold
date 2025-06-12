from scaffold import startup

preferences_dict = {}
history_dict = {}
staff_number = 0
performance_month = ""

def create(req_info, staff_num, perf_month):
    global preferences_dict, history_dict, staff_number
    staff_number=staff_num
    history_dict = {}
    preferences_dict = {}
    performance_month=perf_month
    try:
        if req_info.get("Preferences", {}):
            preferences_dict = set_preferences(req_info.get("Preferences", {}))
        else:
            p = startup.preferences.loc[staff_number, "preferences"]
            preferences_dict = set_preferences(p)
    except Exception:
        return set_preferences({})

    try:
        if req_info.get("History", {}):
            history_dict = req_info.get("History", {})
        else:
            staff_data = startup.history[
                startup.history["staff_number"] == staff_number
            ]
            history_dict = staff_data.set_index("month")["history"].to_dict()
    except Exception:
        pass


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

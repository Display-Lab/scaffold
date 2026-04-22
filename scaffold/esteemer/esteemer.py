import ast
import json
import os
from abc import ABC, abstractmethod

import pandas as pd
import requests
from rdflib import Graph
from rdflib.resource import Resource
from requests_file import FileAdapter
from dotenv import load_dotenv



class Esteemer(ABC):
    _instances = {}
    preferences: pd.DataFrame = pd.DataFrame(
        columns=["subject", "preference.json"], index=["subject"]
    )
    history: pd.DataFrame = pd.DataFrame(
        columns=["subject", "period.start", "period.end", "history.json"],
        index=["subject"],
    )
    default_preferences = {}
    _env_loaded = False

    @abstractmethod
    def score(self, candidate: Resource):
        pass

    @abstractmethod
    def select_candidate(self, performer_graph: Graph):
        pass

    @classmethod
    def load_history(cls):
        if cls.history is None:
            history_file = os.environ.get("history")
            if os.path.exists(history_file):
                cls.history = pd.read_csv(
                    history_file,
                    converters={"history.json": json.loads},
                    dtype={"period.start": str},
                )
                cls.history.set_index("subject", inplace=True, drop=False)

    @classmethod
    def load_preferences(cls):
        if cls.preferences is None:
            preferences_file = os.environ.get("preferences")
            if os.path.exists(preferences_file):
                cls.preferences = pd.read_csv(
                    preferences_file, converters={"preferences": json.loads}
                )
                cls.preferences.set_index("subject", inplace=True, drop=False)
        if not cls.default_preferences:
            default_preferences_file = os.environ.get("default_preferences")
            se = requests.Session()
            se.mount("file://", FileAdapter())
            default_preferences_text = se.get(default_preferences_file).text
            default_preferences_original_dict = json.loads(default_preferences_text)
            cls.default_preferences = {
                k.lower(): v for k, v in default_preferences_original_dict.items()
            }
            
    @classmethod
    def _ensure_env_loaded(cls):
        if not cls._env_loaded:
            load_dotenv(os.environ.get("ENV_PATH"))
            cls._env_loaded = True

    def __new__(cls, *args, **kwargs):
        cls._ensure_env_loaded()
        
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls.load_history()
            cls.load_preferences()
            cls._instances[cls] = instance
        return cls._instances[cls]

    def __init__(self, performance_month: str, subject: str):
        self.performance_month = performance_month
        self.subject = subject

    def get_history(self, subject):
        history_dict = {}
        try:
            history_data = self.history[self.history["subject"] == subject].copy()
            history_data["history.json"] = history_data["history.json"].apply(
                ast.literal_eval
            )
            history_dict = history_data.set_index("period.start")[
                "history.json"
            ].to_dict()
        except Exception:
            pass
        return history_dict

    def get_preferences(self, subject):
        preferences_dict = {}
        try:
            p = ast.literal_eval(self.preferences.loc[subject, "preferences.json"])
            preferences_dict = self._apply_default_preferences(p)
        except Exception:
            preferences_dict = self._apply_default_preferences({})
        return preferences_dict

    def _apply_default_preferences(self, req_info):
        preferences_utilities = req_info.get("Utilities", {})
        input_preferences: dict = preferences_utilities.get("Message_Format", {})
        individual_preferences: dict = {}
        for key in input_preferences:
            individual_preferences[key.lower()] = float(input_preferences[key])

        preferences: dict = self.default_preferences.copy()
        preferences.update(individual_preferences)

        if preferences:
            min_value = min(preferences.values())
            max_value = max(preferences.values())
            if max_value != min_value:
                for key in preferences:
                    preferences[key] = (preferences[key] - min_value) / (
                        max_value - min_value
                    )

        display_format = None
        for key, value in preferences_utilities.get("Display_Format", {}).items():
            if value == 1 and key != "System-generated":
                display_format = key.lower()  # display formats are hardcoded with lower case in pictoralist so lower() is used to keep it the same

        return {"Message_Format": preferences, "Display_Format": display_format}

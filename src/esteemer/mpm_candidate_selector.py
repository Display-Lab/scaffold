import ast
import csv
import json
import os
import random
from datetime import datetime
from io import StringIO
from typing import List

import pandas as pd
import requests
from rdflib import XSD, Graph, Literal, URIRef
from rdflib.resource import Resource
from requests_file import FileAdapter

from src.bitstomach.signals import (
    Achievement,
    Approach,
    Comparison,
    Loss,
    Signal,
    Trend,
)
from src.esteemer.esteemer import Esteemer
from src.esteemer.signals import History
from src.utils import utils
from src.utils.namespace import PSDO, SLOWMO
from src.utils.settings import settings


class MPM_candidate_selector(Esteemer):
    def _initialize(self):
        self.preferences, self.default_preferences = self._load_preferences()
        self.history = self._load_history()
        self.mpm = self._load_mpm_from_env()
        
    def version(self) -> str:
        return "1.0.0"
    
    def _score(self, candidate: Resource) -> Resource:
        """
        Calculates score for a candidate.
        """
        # Get subject from candidate
        history = self._get_history(self.subject)
        preferences = self._get_preferences(self.subject)["Message_Format"]

        CAUSAL_PATHWAY = {
            "Social Better": {
                "score": self._score_better,
                "rules": self._rule_social_highest,
            },
            "Social Worse": {"score": self._score_worse, "rules": self._null_rule},
            "Improving": {"score": self._score_improving, "rules": self._null_rule},
            "Worsening": {"score": self._score_worsening, "rules": self._null_rule},
            "Goal Gain": {"score": self._score_gain, "rules": self._null_rule},
            "Goal Loss": {"score": self._score_loss, "rules": self._null_rule},
            "Social Gain": {
                "score": self._score_gain,
                "rules": self._rule_social_highest,
            },
            "Social Loss": {
                "score": self._score_loss,
                "rules": self._rule_social_lowest,
            },
            "Goal Worse": {"score": self._score_worse, "rules": self._null_rule},
            "Goal Better": {
                "score": self._score_better,
                "rules": self._rule_social_highest,
            },
            "Goal Approach": {"score": self._score_approach, "rules": self._null_rule},
            "Social Approach": {
                "score": self._score_approach,
                "rules": self._rule_social_lowest,
            },
        }

        causal_pathway = candidate.value(SLOWMO.AcceptableBy).value
        motivating_informations = list(candidate[PSDO.motivating_information])
        rules = CAUSAL_PATHWAY[causal_pathway]["rules"]
        score_mi = CAUSAL_PATHWAY[causal_pathway]["score"]

        if not rules(candidate):
            return None

        if settings.use_mi:
            mi_score = score_mi(
                candidate, motivating_informations, self.mpm[causal_pathway]
            )
        else:
            mi_score = 0.0

        candidate[URIRef("motivating_score")] = Literal(mi_score, datatype=XSD.double)

        history_score = self._score_history(
            candidate, history, self.mpm[causal_pathway]
        )
        candidate[URIRef("history_score")] = Literal(history_score, datatype=XSD.double)

        preference_score = self._score_preferences(candidate, preferences)
        candidate[URIRef("preference_score")] = Literal(
            preference_score, datatype=XSD.double
        )

        coachiness_score = self.mpm[causal_pathway]["coachiness"]
        candidate[URIRef("coachiness_score")] = Literal(
            coachiness_score, datatype=XSD.double
        )

        final_calculated_score = self._final_score(
            mi_score, history_score, preference_score
        )
        candidate[SLOWMO.Score] = Literal(final_calculated_score, datatype=XSD.double)
        return candidate

    def select_candidate(self) -> Resource:
        """
        Scores candidates, applies business rules, and selects the best candidate.
        """
        candidates = utils.candidates(
            self.subject_graph, filter_acceptable=True, measure=None
        )
        for candidate in candidates:
            self._score(candidate)
        selected_candidate = self._select(candidates)
        selected_candidate[SLOWMO.Selected] = Literal(True)
        return selected_candidate

    # Internal methods
    def _final_score(self, m, h, p):
        score = m * 1 + h * 2 + p * 1.3
        return round(score, 2)

    def _score_better(
        self, candidate: Resource, motivating_informations: List[Resource], mpm: dict
    ) -> float:
        moderators = self._comparator_moderators(
            candidate, motivating_informations, Comparison
        )
        return moderators["comparison_size"]

    def _null_rule(self, candidate):
        return True

    def _rule_social_highest(self, candidate: Resource):
        causal_pathway = candidate.value(SLOWMO.AcceptableBy).value
        if candidate[SLOWMO.RegardingComparator : PSDO.peer_average_comparator]:
            candidates = utils.candidates(
                candidate.graph,
                candidate.value(SLOWMO.RegardingMeasure).identifier,
                filter_acceptable=True,
            )
            return not any(
                (
                    candid[
                        SLOWMO.RegardingComparator : PSDO.peer_90th_percentile_benchmark
                    ]
                    or candid[
                        SLOWMO.RegardingComparator : PSDO.peer_75th_percentile_benchmark
                    ]
                )
                and candid.value(SLOWMO.AcceptableBy).value == causal_pathway
                for candid in candidates
            )
        if candidate[SLOWMO.RegardingComparator : PSDO.peer_75th_percentile_benchmark]:
            candidates = utils.candidates(
                candidate.graph,
                candidate.value(SLOWMO.RegardingMeasure).identifier,
                filter_acceptable=True,
            )
            return not any(
                candid[SLOWMO.RegardingComparator : PSDO.peer_90th_percentile_benchmark]
                and candid.value(SLOWMO.AcceptableBy).value == causal_pathway
                for candid in candidates
            )
        return True

    def _rule_social_lowest(self, candidate: Resource):
        causal_pathway = candidate.value(SLOWMO.AcceptableBy).value
        if candidate[SLOWMO.RegardingComparator : PSDO.peer_90th_percentile_benchmark]:
            candidates = utils.candidates(
                candidate.graph,
                candidate.value(SLOWMO.RegardingMeasure).identifier,
                filter_acceptable=True,
            )
            return not any(
                (
                    candid[SLOWMO.RegardingComparator : PSDO.peer_average_comparator]
                    or candid[
                        SLOWMO.RegardingComparator : PSDO.peer_75th_percentile_benchmark
                    ]
                )
                and candid.value(SLOWMO.AcceptableBy).value == causal_pathway
                for candid in candidates
            )
        if candidate[SLOWMO.RegardingComparator : PSDO.peer_75th_percentile_benchmark]:
            candidates = utils.candidates(
                candidate.graph,
                candidate.value(SLOWMO.RegardingMeasure).identifier,
                filter_acceptable=True,
            )
            return not any(
                candid[SLOWMO.RegardingComparator : PSDO.peer_average_comparator]
                and candid.value(SLOWMO.AcceptableBy).value == causal_pathway
                for candid in candidates
            )
        return True

    def _score_worse(
        self, candidate: Resource, motivating_informations: List[Resource], mpm: dict
    ) -> float:
        moderators = self._comparator_moderators(
            candidate, motivating_informations, Comparison
        )
        return moderators["comparison_size"]

    def _score_improving(
        self, candidate: Resource, motivating_informations: List[Resource], mpm: dict
    ) -> float:
        moderators = Trend.moderators(motivating_informations)[0]
        return moderators["trend_size"]

    def _score_worsening(
        self, candidate: Resource, motivating_informations: List[Resource], mpm: dict
    ) -> float:
        moderators = Trend.moderators(motivating_informations)[0]
        return moderators["trend_size"]

    def _score_approach(
        self, candidate: Resource, motivating_informations: List[Resource], mpm: dict
    ) -> float:
        moderators = self._comparator_moderators(
            candidate, motivating_informations, Approach
        )
        return (
            moderators["comparison_size"] * mpm["comparison_size"]
            + moderators["trend_size"] * mpm["trend_size"]
            + moderators["achievement_recency"] * mpm["achievement_recency"]
        ) / (mpm["comparison_size"] + mpm["trend_size"] + mpm["achievement_recency"])

    def _score_gain(
        self, candidate: Resource, motivating_informations: List[Resource], mpm: dict
    ) -> float:
        moderators = self._comparator_moderators(
            candidate, motivating_informations, Achievement
        )
        return (
            moderators["comparison_size"] * mpm["comparison_size"]
            + moderators["trend_size"] * mpm["trend_size"]
            + moderators["achievement_recency"] * mpm["achievement_recency"]
        ) / (mpm["comparison_size"] + mpm["trend_size"] + mpm["achievement_recency"])

    def _score_loss(
        self, candidate: Resource, motivating_informations: List[Resource], mpm: dict
    ) -> float:
        moderators = self._comparator_moderators(
            candidate, motivating_informations, Loss
        )
        return (
            moderators["comparison_size"] * mpm["comparison_size"]
            + moderators["trend_size"] * mpm["trend_size"]
            + moderators["loss_recency"] * mpm["loss_recency"]
        ) / (mpm["comparison_size"] + mpm["trend_size"] + mpm["loss_recency"])

    def _comparator_moderators(
        self, candidate, motivating_informations, signal: Signal
    ):
        comparator = candidate.value(SLOWMO.RegardingComparator)
        if str(comparator) == "None":
            raise ValueError(
                "A candidate is created using a message template which is regarding a comparator that is not defined in the Knowledge Base."
            )
        comparator_type = comparator.identifier
        moderators = signal.moderators(motivating_informations)
        scoring_detail = [
            moderator
            for moderator in moderators
            if moderator["comparator_type"] == comparator_type
        ][0]
        return scoring_detail

    def _score_history(self, candidate: Resource, history, mpm: dict) -> float:
        if not history or not settings.use_history:
            return 1.0
        g: Graph = candidate.graph
        history.pop(self.performance_month, None)
        signals = History.detect(
            history,
            {
                datetime.fromisoformat(self.performance_month): History.to_element(
                    candidate
                )
            },
        )
        if not signals:
            return 1.0
        mod = History.moderators(signals)[0]
        history_moderator = (
            mod["message_recurrence"] * mpm["message_recurrence"]
            + mod["message_recency"] * mpm["message_recency"]
            + mod["measure_recency"] * mpm["measure_recency"]
        ) / (
            mpm["message_recurrence"] + mpm["message_recency"] + mpm["measure_recency"]
        )
        return 1 - history_moderator * mpm["history"]

    def _score_preferences(
        self, candidate_resource: Resource, preferences: dict
    ) -> float:
        if not settings.use_preferences:
            return 0.0
        return preferences.get(
            str(candidate_resource.value(SLOWMO.AcceptableBy).value).lower(), 0.0
        )

    def _select(self, candidates: List[Resource]) -> Resource:
        candidates = [
            candidate
            for candidate in candidates
            if (candidate.value(URIRef("coachiness_score")) is not None)
        ]
        if settings.use_coachiness:
            highest_coachiness_candidates = self._candidates_from_coachiness_category(
                candidates, category=1.0
            )
            if not highest_coachiness_candidates:
                highest_coachiness_candidates = (
                    self._candidates_from_coachiness_category(candidates, category=0.5)
                )
            if highest_coachiness_candidates:
                candidates = highest_coachiness_candidates
        max_score = max(
            [candidate.value(SLOWMO.Score).value for candidate in candidates],
            default=None,
        )
        candidates_with_max_score = [
            (candidate)
            for candidate in candidates
            if candidate.value(SLOWMO.Score).value == max_score
        ]
        selected_candidate = random.choice(candidates_with_max_score)
        return selected_candidate

    def _candidates_from_coachiness_category(self, candidates, category):
        return [
            candidate
            for candidate in candidates
            if (candidate.value(URIRef("coachiness_score")).value == category)
        ]

    def _load_mpm_from_env(self) -> dict:
        mpm_dict = {}
        mpm_path: str = os.getenv("mpm")
        if mpm_path is None:
            raise ValueError(
                "Environment variable 'mpm' must be set to the MPM file path or URL."
            )
        if mpm_path.startswith("http"):
            response = requests.get(mpm_path)
            response.raise_for_status()
            csv_content = StringIO(response.text)
            file = csv_content
        else:
            file = open(mpm_path, mode="r")

        reader = csv.DictReader(file)
        for row in reader:
            outer_key = row.pop("causal_pathway")
            mpm_dict[outer_key] = {
                k: (float(v) if v != "" else None) for k, v in row.items()
            }

        if not mpm_path.startswith("http"):
            file.close()

        return mpm_dict

    def _load_history(self):
        history: pd.DataFrame = pd.DataFrame(
            columns=["subject", "period.start", "period.end", "history.json"],
            index=["subject"],
        )
        history_file = os.environ.get("history")
        if os.path.exists(history_file):
            history = pd.read_csv(
                history_file,
                converters={"history": json.loads},
                dtype={"period.start": str},
            )
            history.set_index("subject", inplace=True, drop=False)
        return history

    def _load_preferences(self):
        preferences: pd.DataFrame = pd.DataFrame(
            columns=["subject", "preference.json"], index=["subject"]
        )
        preferences_file = os.environ.get("preferences")
        if os.path.exists(preferences_file):
            preferences = pd.read_csv(
                preferences_file, converters={"preferences": json.loads}
            )
            preferences.set_index("subject", inplace=True, drop=False)

        default_preferences_file = os.environ.get("default_preferences")
        se = requests.Session()
        se.mount("file://", FileAdapter())
        default_preferences_text = se.get(default_preferences_file).text
        default_preferences_original_dict = json.loads(default_preferences_text)
        default_preferences = {
            k.lower(): v for k, v in default_preferences_original_dict.items()
        }
        return preferences, default_preferences

    def _get_history(self, subject):
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
        
        history_dict_from_request = {}
        try:
            history_list = self.req_info.get("History", {})
            history_dict_from_request = {
                item["period.start"]: {k: v for k, v in item.items() if k != "period.end" and k != "period.start"}
                for item in history_list
            }
        except Exception:
            pass
        
        for key, value in history_dict_from_request.items():
            if key not in history_dict:
                history_dict[key] = value
        return history_dict

    def _get_preferences(self, subject):
        preferences_dict = {}
        try:
            if self.req_info:
                p = self.req_info.get("Preferences", {})
            else: 
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

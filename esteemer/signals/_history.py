from datetime import datetime
from typing import List, Optional, Tuple

from dateutil.relativedelta import relativedelta
from rdflib import XSD, Literal, URIRef
from rdflib.resource import Resource

from bitstomach.signals import Signal
from utils.namespace import SLOWMO


class History(Signal):
    # TODO: Allow an array of types
    signal_type = SLOWMO.MessageRecurrance

    @staticmethod
    def detect(message_history: dict, current_month: dict) -> Optional[List[Resource]]:
        if not message_history:
            return None

        message_recurrence, message_recency, measure_recurrence, measure_recency = (
            History._detect(message_history, current_month)
        )

        return [
            History._resource(
                message_recurrence, message_recency, measure_recurrence, measure_recency
            )
        ]

    @classmethod
    def _resource(
        cls,
        message_recurrence: int,
        message_recency: int,
        measure_recurrence: int,
        measure_recency: int,
    ) -> Resource:
        base = super()._resource()

        base[URIRef("message_recurrence")] = Literal(
            message_recurrence, datatype=XSD.integer
        )

        base[URIRef("message_recency")] = Literal(message_recency, datatype=XSD.integer)

        base[URIRef("measure_recurrence")] = Literal(
            measure_recurrence, datatype=XSD.integer
        )

        base[URIRef("measure_recency")] = Literal(measure_recency, datatype=XSD.integer)
        return base

    @classmethod
    def moderators(cls, signals: List[Resource]) -> List[dict]:
        mods = []

        for signal in super().select(signals):
            history_dict = {}
            message_recency = signal.value(URIRef("message_recency")).value
            measure_recency = signal.value(URIRef("measure_recency")).value

            history_dict["message_recurrence"] = round(
                1 - (signal.value(URIRef("message_recurrence")).value / 12), 4
            )
            history_dict["message_recency"] = round(
                (message_recency / 12) if message_recency else 1.0, 4
            )
            history_dict["measure_recurrence"] = round(
                1 - (signal.value(URIRef("measure_recurrence")).value / 12), 4
            )
            history_dict["measure_recency"] = round(
                measure_recency / 12 if measure_recency else 1.0, 4
            )
            mods.append(history_dict)

        return mods

    @staticmethod
    def _detect(
        history: dict, current_month_dict: dict
    ) -> Tuple[float, float, float, float]:
        message_count = 0
        message_recency = 0
        measure_count = 0
        measure_recency = 0

        current_month, history_element = list(current_month_dict.items())[0]
        message_template = history_element["message_template"]
        measure = history_element["measure"]
        most_recent_message = None
        most_recent_measure = None
        for key, value in history.items():
            month = datetime.fromisoformat(key)
            if history[key]["message_template"] == message_template:
                message_count += 1
                most_recent_message = month

            if history[key]["measure"] == measure:
                measure_count += 1
                most_recent_measure = month

        difference = relativedelta(current_month, most_recent_message)
        message_recency = difference.years * 12 + difference.months

        difference = relativedelta(current_month, most_recent_measure)
        measure_recency = difference.years * 12 + difference.months

        return message_count, message_recency, measure_count, measure_recency

    @staticmethod
    def to_element(candidate: Resource):
        element = {}
        element["message_template"] = str(
            candidate.value(SLOWMO.AncestorTemplate).identifier
        )
        element["acceptable_by"] = candidate.value(SLOWMO.AcceptableBy).value
        element["measure"] = str(candidate.value(SLOWMO.RegardingMeasure).identifier)

        return element

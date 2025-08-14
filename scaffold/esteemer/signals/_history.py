from datetime import datetime
from typing import List, Optional, Tuple

from dateutil.relativedelta import relativedelta
from rdflib import XSD, Literal, URIRef
from rdflib.resource import Resource

from scaffold.bitstomach.signals import Signal
from scaffold.utils.namespace import SLOWMO


class History(Signal):
    """
    See the documentation for prioritization_algorithms in the the knowledge base
    """

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
                (signal.value(URIRef("message_recurrence")).value / 12), 4
            )
            history_dict["message_recency"] = round(
                1 - (message_recency / 12) if message_recency else 0.0, 4
            )
            history_dict["measure_recurrence"] = round(
                (signal.value(URIRef("measure_recurrence")).value / 12), 4
            )
            history_dict["measure_recency"] = round(
                1 - (measure_recency / 12) if measure_recency else 0.0, 4
            )
            mods.append(history_dict)

        return mods

    @staticmethod
    def _detect(
        history: dict, current: dict
    ) -> Tuple[float, float, float, float]:
        message_recurrence = 0
        message_recency = 0
        measure_recurrence = 0
        measure_recency = 0

        current_period, current_message = list(current.items())[0]
        current_message_template = current_message["message_template"]
        current_measure = current_message["measure"]
        most_recent_message_dt = None
        most_recent_measure_dt = None
        for period, message in history.items():
            period_dt = datetime.fromisoformat(period)
            if message["message_template"] == current_message_template:
                message_recurrence += 1
                most_recent_message_dt = period_dt

            if message["measure"] == current_measure:
                measure_recurrence += 1
                most_recent_measure_dt = period_dt

        difference = relativedelta(current_period, most_recent_message_dt)
        message_recency = difference.years * 12 + difference.months

        difference = relativedelta(current_period, most_recent_measure_dt)
        measure_recency = difference.years * 12 + difference.months

        return message_recurrence, message_recency, measure_recurrence, measure_recency

    @staticmethod
    def to_element(candidate: Resource):
        element = {}
        element["message_template"] = str(
            candidate.value(SLOWMO.AncestorTemplate).identifier
        )
        element["acceptable_by"] = candidate.value(SLOWMO.AcceptableBy).value
        element["measure"] = str(candidate.value(SLOWMO.RegardingMeasure).identifier)

        return element

from typing import List, Optional, Union

import pandas as pd
from rdflib import RDF, BNode, Literal, URIRef
from rdflib.resource import Resource

from scaffold import context
from scaffold.bitstomach.signals import Signal
from scaffold.utils.namespace import PSDO, SLOWMO


class Comparison(Signal):
    signal_type = PSDO.performance_gap_content

    @staticmethod
    def detect(
        perf_data: pd.DataFrame, tiered_comparators: bool = True
    ) -> Optional[List[Resource]]:
        """
        Detects comparison signals against a pre-defined list of comparators using performance levels in performance content.
        The signal is calculated as a simple difference. It returns a list of resources representing each signal detected.

        Parameters:
        - perf_content (DataFrame): The performance content.

        Returns:
        - List[Resource]: The list of signal resources.
        """

        if perf_data.empty:
            raise ValueError

        if not perf_data[-1:]["valid"].item():
            return []

        resources = []

        gaps = Comparison._detect(perf_data)

        for key, value in gaps.items():
            r = Comparison._resource(value[0], key, value[1])
            resources.append(r)

        return resources

    @classmethod
    def _resource(
        cls, gap: float, comparator_iri: str, comparator_value: float
    ) -> Resource:
        """
        adds the performance gap size, types it as positive or negative and adds the comparator to the subgraph
        """
        base = super()._resource()

        # Add the signal node and value
        base.add(SLOWMO.PerformanceGapSize, Literal(gap))
        base.add(
            RDF.type,
            PSDO.positive_performance_gap_content
            if gap >= 0
            else PSDO.negative_performance_gap_content,
        )

        # Add the comparator
        c = base.graph.resource(BNode())
        c.set(RDF.type, URIRef(comparator_iri))
        c.set(RDF.value, Literal(comparator_value))

        base.add(SLOWMO.RegardingComparator, c)

        return base

    @staticmethod
    def _detect(perf_data: pd.DataFrame) -> dict:
        """Calculate gap from levels and comparators"""

        gaps: dict = {}
        for comparator in context.subject_graph.subjects(
            RDF.type, PSDO.comparator_content
        ):
            comparator_iri = str(comparator)
            comparator_value = perf_data[-1:][comparator_iri] / 100
            gap = perf_data[-1:]["measureScore.rate"] - comparator_value
            gaps[comparator_iri] = (gap.item(), comparator_value.item())

        return gaps

    @classmethod
    def moderators(cls, motivating_informations: List[Resource]) -> List[dict]:
        """
        extracts comparison moderators (comparison_size and comparator_type) from a suplied list of motivating information
        """
        mods = []

        for signal in super().select(motivating_informations):
            motivating_info_dict = super().moderators(signal)
            motivating_info_dict["comparison_size"] = round(
                abs(signal.value(SLOWMO.PerformanceGapSize).value), 4
            )
            motivating_info_dict["comparator_type"] = signal.value(
                SLOWMO.RegardingComparator / RDF.type
            ).identifier

            mods.append(motivating_info_dict)

        return mods

    @classmethod
    def disposition(cls, mi: Resource) -> Union[List[Resource] | None]:
        if not super().select([mi]):
            return None

        disposition = super().disposition(mi)

        # extras
        comparator_type = mi.value(SLOWMO.RegardingComparator / RDF.type)

        disposition.append(comparator_type)

        disposition += list(comparator_type[RDF.type])
        TypeError
        return disposition

    @classmethod
    def exclude(cls, mi, message_roles: List[Resource]) -> bool:
        comparator_type = mi.value(SLOWMO.RegardingComparator / RDF.type)
        if comparator_type in message_roles:
            return False
        else:
            return True

    @staticmethod
    def comparator_type(mi: Resource) -> URIRef:
        return mi.value(SLOWMO.RegardingComparator / RDF.type).identifier

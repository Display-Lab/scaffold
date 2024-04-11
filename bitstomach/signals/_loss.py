from typing import List, Optional

import pandas as pd
from rdflib import RDF
from rdflib.resource import Resource

from bitstomach.signals import Comparison, Signal, Trend
from utils.namespace import PSDO, SLOWMO


class Loss(Signal):
    signal_type = PSDO.loss_content

    @staticmethod
    def detect(perf_data: pd.DataFrame) -> Optional[List[Resource]]:
        if perf_data.empty:
            raise ValueError

        trend_signals = Trend.detect(perf_data)
        if (
            not trend_signals
            or not trend_signals[0][RDF.type : PSDO.negative_performance_trend_content]
        ):
            return []

        negative_comparison_signals = [
            s
            for s in Comparison.detect(perf_data)
            if s[RDF.type : PSDO.negative_performance_gap_content]
        ]

        positive_prior_month_comparisons = [
            s
            for s in Comparison.detect(perf_data.iloc[:-1])
            if s[RDF.type : PSDO.positive_performance_gap_content]
        ]

        loss_signals = []

        for comparison_signal in negative_comparison_signals:
            previous_comparison_signal = next(
                (
                    comparison
                    for comparison in positive_prior_month_comparisons
                    if (
                        Comparison.comparator_type(comparison)
                        == Comparison.comparator_type(comparison_signal)
                    )
                ),
                None,
            )

            if not previous_comparison_signal:
                continue

            mi = Loss._resource(
                trend_signals[0], comparison_signal, previous_comparison_signal
            )

            loss_signals.append(mi)
        return loss_signals

    @classmethod
    def _resource(
        cls,
        trend_signal: Resource,
        comparison_signal: Resource,
        previous_comparison_signal: Resource,
    ) -> Resource:
        # create and type the Achievmente
        mi = super()._resource()
        mi.add(RDF.type, Comparison.signal_type)
        mi.add(RDF.type, Trend.signal_type)

        # set signal properties
        mi[SLOWMO.PerformanceTrendSlope] = trend_signal.value(
            SLOWMO.PerformanceTrendSlope
        )
        mi[SLOWMO.PerformanceGapSize] = comparison_signal.value(
            SLOWMO.PerformanceGapSize
        )
        mi[SLOWMO.PriorPerformanceGapSize] = previous_comparison_signal.value(
            SLOWMO.PerformanceGapSize
        )

        # add comparator (Achievments are a Comparison)
        comparator = comparison_signal.value(SLOWMO.RegardingComparator)

        mi[SLOWMO.RegardingComparator] = comparator

        g = mi.graph
        g += comparison_signal.graph.triples((comparator.identifier, None, None))

        return mi

    @classmethod
    def disposition(cls, mi: Resource) -> List[Resource]:
        dispos = super().disposition(mi)
        dispos += Comparison.disposition(mi)
        dispos += Trend.disposition(mi)

        return dispos

    @classmethod
    def moderators(cls, motivating_informations: List[Resource]) -> List[dict]:
        """
        extracts loss moderators (trend_slope, gap_size, comparator_type and prior_gap_size) from a suplied list of motivating information
        """
        mods = []

        for signal in super().select(motivating_informations):
            motivating_info_dict = super().moderators(signal)

            motivating_info_dict["gap_size"] = round(
                abs(signal.value(SLOWMO.PerformanceGapSize).value), 4
            )
            motivating_info_dict["comparator_type"] = signal.value(
                SLOWMO.RegardingComparator / RDF.type
            ).identifier
            motivating_info_dict["trend_size"] = round(
                abs(signal.value(SLOWMO.PerformanceTrendSlope).value), 4
            )
            motivating_info_dict["prior_gap_size"] = round(
                abs(signal.value(SLOWMO.PriorPerformanceGapSize).value), 4
            )

            mods.append(motivating_info_dict)

        return mods

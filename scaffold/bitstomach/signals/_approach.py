from typing import List, Optional

import numpy as np
import pandas as pd
from rdflib import RDF, Literal
from rdflib.resource import Resource

from scaffold.bitstomach.signals import Comparison, Signal, Trend
from scaffold.utils.namespace import PSDO, SLOWMO


class Approach(Signal):
    signal_type = PSDO.approach_content

    @staticmethod
    def detect(perf_data: pd.DataFrame) -> Optional[List[Resource]]:
        if perf_data.empty:
            raise ValueError

        trend_signals = Trend.detect(perf_data)
        if (
            not trend_signals
            or not trend_signals[0][RDF.type : PSDO.positive_performance_trend_content]
        ):
            return []

        negative_comparison_signals = [
            s
            for s in Comparison.detect(perf_data)
            if s[RDF.type : PSDO.negative_performance_gap_content]
        ]

        negative_prior_month_comparisons = [
            s
            for s in Comparison.detect(perf_data.iloc[:-1], tiered_comparators=False)
            if s[RDF.type : PSDO.negative_performance_gap_content]
        ]

        approach_signals = []

        for comparison_signal in negative_comparison_signals:
            previous_comparison_signal = next(
                (
                    comparison
                    for comparison in negative_prior_month_comparisons
                    if (
                        Comparison.comparator_type(comparison)
                        == Comparison.comparator_type(comparison_signal)
                    )
                ),
                None,
            )

            if not previous_comparison_signal:
                continue

            streak_length = Approach._detect(
                perf_data, comparison_signal.value(SLOWMO.RegardingComparator)
            )

            mi = Approach._resource(
                trend_signals[0],
                comparison_signal,
                previous_comparison_signal,
                streak_length,
            )

            approach_signals.append(mi)
        return approach_signals

    @classmethod
    def _resource(
        cls,
        trend_signal: Resource,
        comparison_signal: Resource,
        previous_comparison_signal: Resource,
        streak_length: int,
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
        mi[SLOWMO.StreakLength] = Literal(streak_length)

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
        extracts approach moderators (trend_slope, comparison_size, comparator_type and prior_comparison_size) from a suplied list of motivating information
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
            motivating_info_dict["trend_size"] = round(
                abs(signal.value(SLOWMO.PerformanceTrendSlope).value * 2), 4
            )
            motivating_info_dict["prior_comparison_size"] = round(
                abs(signal.value(SLOWMO.PriorPerformanceGapSize).value), 4
            )
            motivating_info_dict["achievement_recency"] = (
                signal.value(SLOWMO.StreakLength).value / 12
            )

            mods.append(motivating_info_dict)

        return mods

    @staticmethod
    def _detect(perf_data: pd.DataFrame, comparator: Resource) -> float:
        """
        calculates the number of consecutive negative gaps prior to this months negative gap.
        """

        comparator_id = comparator.value(RDF.type).identifier

        gaps = (
            perf_data["measureScore.rate"] - perf_data[str(comparator_id)] / 100
        )

        # find the number of consecutive negative gaps
        diff_reversed = gaps.values[:-1][::-1]
        end_negative_gaps_index = np.argmax(diff_reversed >= 0)
        if end_negative_gaps_index == 0:
            consecutive_negative_gaps = len(diff_reversed)
        else:
            consecutive_negative_gaps = end_negative_gaps_index

        return consecutive_negative_gaps

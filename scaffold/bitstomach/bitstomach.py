import pandas as pd
from rdflib import RDF, BNode, Graph, Literal

from scaffold.bitstomach.signals import SIGNALS
from scaffold.utils import settings
from scaffold.utils.namespace import PSDO, SLOWMO


def extract_signals(perf_df: pd.DataFrame) -> Graph:
    """
    Prepares performance data, loops through measures and calls each signal detect method,
    adds the measure to the signal and adds each signal to the graph as motivating information
    """
    # create the graph
    g = Graph()
    r = g.resource(BNode("performance_content"))
    r.set(RDF.type, PSDO.performance_content)
    r.set(SLOWMO.PerformanceMonth, Literal(perf_df.attrs["performance_month"]))
    if perf_df.empty:
        return g

    for measure in perf_df.attrs["valid_measures"]:
        measure_df = perf_df[perf_df["measure"] == measure].tail(12)
        for signal_type in SIGNALS:
            signals = signal_type.detect(measure_df)
            if not signals:
                continue

            for s in signals:
                s.add(SLOWMO.RegardingMeasure, BNode(measure))
                r.add(PSDO.motivating_information, s.identifier)
                g += s.graph
    return g


def prepare(req_info):
    if settings.settings.performance_month:
        req_info["performance_month"] = settings.settings.performance_month
    performance_data = req_info["Performance_data"]
    performance_df = pd.DataFrame(performance_data[1:], columns=performance_data[0])

    performance_df.attrs["staff_number"] = int(performance_df.at[0, "staff_number"])

    performance_df["goal_comparator_content"] = performance_df["MPOG_goal"]

    performance_df.attrs["performance_month"] = req_info.get(
        "performance_month", performance_df["month"].max()
    )

    performance_df = performance_df[
        performance_df["month"] <= performance_df.attrs["performance_month"]
    ]

    performance_df["valid"] = performance_df["denominator"] >= 10

    performance_df["passed_rate"] = (
        performance_df["passed_count"] / performance_df["denominator"]
    )

    performance_df.attrs["measures"] = performance_df["measure"].unique()

    performance_df.attrs["valid_measures"] = performance_df[
        (
            (performance_df["month"] == performance_df.attrs["performance_month"])
            & performance_df["valid"]
        )
    ]["measure"]

    return performance_df

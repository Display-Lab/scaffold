import pandas as pd
from rdflib import RDF, BNode, Graph

from scaffold import context, startup
from scaffold.bitstomach.signals import SIGNALS
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
    if perf_df.empty:
        return g

    process_measures = set(
        startup.base_graph[: RDF.type : PSDO.process_measure]
    )
    
    for measure in perf_df.attrs["valid_measures"]:
        measure_df = (
            perf_df[perf_df["measure"] == measure].tail(12).sort_values("period.start")
        )
        if BNode(measure) in process_measures:
            measure_type = PSDO.process_measure
        else:
            measure_type = PSDO.outcome_measure
        
        comparator_df = context.comparator_df[
            context.comparator_df["measure"] == measure
        ].sort_values("period.start")
        for signal_type in SIGNALS:
            if signal_type.measure_type != measure_type:
                continue
            signals = signal_type.detect(measure_df, comparator_df)
            if not signals:
                continue

            for s in signals:
                s.add(SLOWMO.RegardingMeasure, BNode(measure))
                r.add(PSDO.motivating_information, s.identifier)
                g += s.graph
    return g


def prepare():
    performance_df = context.performance_df

    performance_df = performance_df[
        performance_df["period.start"] <= context.performance_month
    ].copy()

    performance_df["valid"] = performance_df["measureScore.denominator"] >= 10

    performance_df.attrs["valid_measures"] = performance_df[
        (
            (performance_df["period.start"] == context.performance_month)
            & performance_df["valid"]
        )
    ]["measure"]

    measures = set(startup.base_graph[: RDF.type : PSDO.performance_measure_content])

    performance_df.attrs["valid_measures"] = [
        m for m in performance_df.attrs["valid_measures"] if BNode(m) in measures
    ]

    return performance_df

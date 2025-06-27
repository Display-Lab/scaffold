import pandas as pd
from rdflib import RDF, BNode, Graph

from scaffold import context, startup
from scaffold.bitstomach import bitstomach
from scaffold.utils.namespace import PSDO

COLUMNS = [
    "staff_number",
    "measure",
    "month",
    "passed_count",
    "flagged_count",
    "denominator",
    "peer_average_comparator",
    "peer_75th_percentile_benchmark",
    "peer_90th_percentile_benchmark",
    "MPOG_goal",
]


def test_extract_signals_return_a_graph():
    df = pd.DataFrame()
    df.attrs["performance_month"] = "2024-01-01"
    g = bitstomach.extract_signals(df)

    assert isinstance(g, Graph)

    assert g.value(None, RDF.type, PSDO.performance_content)


def test_returns_performance_content_with_multiple_elements():
    perf_data = [
        COLUMNS,
        [157, "SUS04", "2022-10-01", 29, 0, 29, 81.7, 100.0, 100.0, 90.0],
        [157, "SUS04", "2022-11-01", 29, 0, 29, 81.7, 100.0, 100.0, 90.0],
        [157, "PONV05", "2022-11-01", 40, 0, 40, 82.4, 100.0, 100.0, 90.0],
    ]
    performance_df = pd.DataFrame(perf_data[1:], columns=COLUMNS)
    context.performance_month = "2022-11-01"
    context.staff_number = 157
    context.performance_df = performance_df
    
    g = Graph()
    g.add((BNode("PONV05"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("SUS04"), RDF.type, PSDO.performance_measure_content))
    startup.base_graph = g
    
    perf_df = bitstomach.prepare()

    g = bitstomach.extract_signals(perf_df)
    r = g.resource(BNode("performance_content"))
    mi = set(r[PSDO.motivating_information])

    assert len(mi) == 8

    assert g.value(None, RDF.type, PSDO.performance_gap_content)


def test_fix_up_marks_low_count_as_invalid():
    perf_data = [
        COLUMNS,
        [157, "SUS04", "2022-11-01", 29, 0, 29, 81.7, 100.0, 100.0, 90.0],
        [157, "PONV05", "2022-11-01", 40, 0, 4, 82.4, 100.0, 100.0, 90.0],
        [157, "BP01", "2022-10-01", 40, 0, 40, 82.4, 100.0, 100.0, 90.0],
        [157, "BP02", "2022-10-01", 29, 0, 2, 81.7, 100.0, 100.0, 90.0],
    ]
    performance_df = pd.DataFrame(perf_data[1:], columns=COLUMNS)
    context.performance_month = "2022-11-01"
    context.staff_number = 157
    context.performance_df = performance_df
    
    g = Graph()
    g.add((BNode("PONV05"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("SUS04"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("BP01"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("BP02"), RDF.type, PSDO.performance_measure_content))
    startup.base_graph = g
    
    perf_df = bitstomach.prepare()

    assert "SUS04" in perf_df.attrs["valid_measures"]
    assert "PONV05" not in perf_df.attrs["valid_measures"]
    assert "BP01" not in perf_df.attrs["valid_measures"]
    assert "BP02" not in perf_df.attrs["valid_measures"]

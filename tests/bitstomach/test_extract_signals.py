import json


import pandas as pd
from rdflib import RDF, BNode, Graph, Literal

from scaffold import context, startup
from scaffold.bitstomach import bitstomach
from scaffold.utils.namespace import PSDO
import pytest

COLUMNS = [
    "subject",
    "measure",
    "period.start",
    "measureScore.rate",
    "measureScore.denominator",
]





@pytest.fixture
def prep_base_graph() :
    g = Graph()
    g.add((BNode("PONV05"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("PONV05"), PSDO.has_desired_direction, Literal(str(PSDO.desired_increasing_measure))))
    g.add((BNode("SUS04"), RDF.type, PSDO.performance_measure_content))
    g.add((BNode("SUS04"), PSDO.has_desired_direction, Literal(str(PSDO.desired_increasing_measure))))
    startup.base_graph = g
    
    comparators = [
        {
            "@id": "http://purl.obolibrary.org/obo/PSDO_0000094",
            "@type": ["http://purl.obolibrary.org/obo/PSDO_0000093"],
        },
        {
            "@id": "http://purl.obolibrary.org/obo/PSDO_0000126",
            "@type": [
                "http://purl.obolibrary.org/obo/PSDO_0000093",
                "http://purl.obolibrary.org/obo/PSDO_0000095",
            ],
        },
        {
            "@id": "http://purl.obolibrary.org/obo/PSDO_0000128",
            "@type": [
                "http://purl.obolibrary.org/obo/PSDO_0000093",
                "http://purl.obolibrary.org/obo/PSDO_0000095",
            ],
        },
        {
            "@id": "http://purl.obolibrary.org/obo/PSDO_0000129",
            "@type": [
                "http://purl.obolibrary.org/obo/PSDO_0000093",
                "http://purl.obolibrary.org/obo/PSDO_0000095",
            ],
        },
    ]
    jsonld_str = json.dumps(comparators)

    context.subject_graph = Graph().parse(data=jsonld_str, format="json-ld")

def test_extract_signals_return_a_graph():
    df = pd.DataFrame()
    df.attrs["performance_month"] = "2024-01-01"
    g = bitstomach.extract_signals(df)

    assert isinstance(g, Graph)

    assert g.value(None, RDF.type, PSDO.performance_content)


def test_returns_performance_content_with_multiple_elements(prep_base_graph):
    perf_data = [
        COLUMNS,
        [157, "SUS04", "2022-10-01", 1, 100],
        [157, "SUS04", "2022-11-01", 1, 100],
        [157, "PONV05", "2022-11-01", 1, 100],
    ]
    performance_df = pd.DataFrame(perf_data[1:], columns=COLUMNS)

    comparator_data = [
        [
            "measure",
            "period.start",
            "measureScore.rate",
            "group.code",
        ],
        ["SUS04", "2022-10-01", 81.7, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["SUS04", "2022-10-01", 100.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["SUS04", "2022-10-01", 100.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["SUS04", "2022-10-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["SUS04", "2022-11-01", 81.7, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["SUS04", "2022-11-01", 100.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["SUS04", "2022-11-01", 100.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["SUS04", "2022-11-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
        ["PONV05", "2022-11-01", 82.4, "http://purl.obolibrary.org/obo/PSDO_0000126"],
        ["PONV05", "2022-11-01", 100.0, "http://purl.obolibrary.org/obo/PSDO_0000128"],
        ["PONV05", "2022-11-01", 100.0, "http://purl.obolibrary.org/obo/PSDO_0000129"],
        ["PONV05", "2022-11-01", 90.0, "http://purl.obolibrary.org/obo/PSDO_0000094"],
    ]
    comparator_df = pd.DataFrame(comparator_data[1:], columns=comparator_data[0])
    context.comparator_df = comparator_df
    context.performance_month = "2022-11-01"
    context.subject = 157
    context.performance_df = performance_df

    perf_df = bitstomach.prepare()

    g = bitstomach.extract_signals(perf_df)
    r = g.resource(BNode("performance_content"))
    mi = set(r[PSDO.motivating_information])

    assert len(mi) == 8

    assert g.value(None, RDF.type, PSDO.performance_gap_content)


def test_fix_up_marks_low_count_as_invalid():
    perf_data = [
        COLUMNS,
        [157, "SUS04", "2022-11-01", 1, 29],
        [157, "PONV05", "2022-11-01", 1, 4],
        [157, "BP01", "2022-10-01", 1, 40],
        [157, "BP02", "2022-10-01", 1, 2],
    ]
    performance_df = pd.DataFrame(perf_data[1:], columns=COLUMNS)
    context.performance_month = "2022-11-01"
    context.subject = 157
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

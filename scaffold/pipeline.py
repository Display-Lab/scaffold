import os

import pandas as pd
import psutil
from fastapi import HTTPException
from loguru import logger
from rdflib import RDF, BNode, Graph, Literal, URIRef

from scaffold import startup
from scaffold.bitstomach import bitstomach
from scaffold.candidate_pudding import candidate_pudding
from scaffold.esteemer import esteemer, utils
from scaffold.pictoralist.pictoralist import Pictoralist
from scaffold.utils.namespace import PSDO, SLOWMO
from scaffold.utils.settings import settings
from scaffold.utils.utils import set_logger

set_logger()


def pipeline(performance_df: pd.DataFrame, staff_number, performance_month):
    performance_df, performance_month = bitstomach.prepare(
        performance_df, staff_number, performance_month
    )

    measures = set(startup.base_graph[: RDF.type : PSDO.performance_measure_content])

    performance_df.attrs["valid_measures"] = [
        m for m in performance_df.attrs["valid_measures"] if BNode(m) in measures
    ]

    cool_new_super_graph = Graph()
    cool_new_super_graph += startup.base_graph
    cool_new_super_graph.add(
        (
            BNode("p1"),
            URIRef("http://example.com/slowmo#IsAboutPerformer"),
            Literal(int(performance_df.attrs["staff_number"])),
        )
    )
    # BitStomach
    logger.debug("Calling BitStomach from main...")

    g: Graph = bitstomach.extract_signals(performance_df)

    performance_content = g.resource(BNode("performance_content"))
    if len(list(performance_content[PSDO.motivating_information])) == 0:
        cool_new_super_graph.close()
        detail = {
            "message": "Insufficient significant data found for providing feedback, process aborted.",
            "staff_number": performance_df.attrs["staff_number"],
        }
        raise HTTPException(
            status_code=400,
            detail=detail,
            headers={"400-Error": "Invalid Input Error"},
        )

    cool_new_super_graph += g

    # candidate_pudding
    logger.debug("Calling candidate_pudding from main...")
    candidate_pudding.create_candidates(cool_new_super_graph)

    # #Esteemer
    logger.debug("Calling Esteemer from main...")

    measures: set[BNode] = set(
        cool_new_super_graph.objects(
            None, PSDO.motivating_information / SLOWMO.RegardingMeasure
        )
    )

    for measure in measures:
        candidates = utils.candidates(
            cool_new_super_graph, filter_acceptable=True, measure=measure
        )
        for candidate in candidates:
            esteemer.score(candidate, startup.mpm, performance_month)
    selected_candidate = esteemer.select_candidate(cool_new_super_graph)
    preferences = esteemer.get_preferences(performance_df.attrs["staff_number"])

    if preferences["Display_Format"]:
        cool_new_super_graph.resource(selected_candidate)[SLOWMO.Display] = Literal(
            preferences["Display_Format"]
        )

    selected_message = utils.render(cool_new_super_graph, selected_candidate)

    ### Pictoralist 2, now on the Nintendo DS: ###
    logger.debug("Calling Pictoralist from main...")
    if selected_message["message_text"] != "No message selected":
        ## Initialize and run message and display generation:
        pc = Pictoralist(
            performance_df,
            selected_message,
            settings,
        )
        pc.prep_data_for_graphing()  # Setup dataframe of one measure, cleaned for graphing
        pc.fill_missing_months()  # Fill holes in dataframe where they exist
        pc.set_timeframe()  # Ensure no less than three months being graphed
        pc.finalize_text()  # Finalize text message and labels
        pc.graph_controller()  # Select and run graphing based on display type

        full_selected_message = pc.prepare_selected_message()
    else:
        full_selected_message = selected_message

    response = {}
    # if settings.log_level == "INFO":
    if logger.at_least("INFO"):
        # Get memory usage information
        mem_info = psutil.Process(os.getpid()).memory_info()

        response["memory (RSS in MB)"] = {
            "memory_info.rss": mem_info.rss / 1024 / 1024,
        }

        response["candidates"] = utils.candidates_records(cool_new_super_graph)

    response.update(full_selected_message)

    return response

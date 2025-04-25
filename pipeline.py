import os

import psutil
from fastapi import HTTPException
from loguru import logger
from rdflib import RDF, BNode, Graph, Literal, URIRef

import startup
from bitstomach import bitstomach
from candidate_pudding import candidate_pudding
from esteemer import esteemer, utils
from pictoralist.pictoralist import Pictoralist
from utils.namespace import PSDO, SLOWMO
from utils.settings import settings


def pipeline(req_info):
    if settings.performance_month:
        req_info["performance_month"] = settings.performance_month

    preferences = startup.set_preferences(req_info)

    cool_new_super_graph = Graph()
    cool_new_super_graph += startup.base_graph

    # BitStomach
    logger.debug("Calling BitStomach from main...")

    performance_data_df = bitstomach.prepare(req_info)
    # TODO: find a place for measures to live...mabe move these two line into prepare or make a measurees class
    measures = set(cool_new_super_graph[: RDF.type : PSDO.performance_measure_content])

    performance_data_df.attrs["valid_measures"] = [
        m for m in performance_data_df.attrs["valid_measures"] if BNode(m) in measures
    ]
    g: Graph = bitstomach.extract_signals(performance_data_df)

    performance_content = g.resource(BNode("performance_content"))
    if len(list(performance_content[PSDO.motivating_information])) == 0:
        cool_new_super_graph.close()
        detail = {
            "message": "Insufficient significant data found for providing feedback, process aborted.",
            "message_instance_id": req_info["message_instance_id"],
            "staff_number": performance_data_df.attrs["staff_number"],
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
    history: dict = req_info.get("History", {})
    history = {
        key: value
        for key, value in history.items()
        if key < performance_data_df.attrs["performance_month"]
    }

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
            esteemer.score(
                candidate, history, preferences["Message_Format"], startup.mpm
            )
    selected_candidate = esteemer.select_candidate(cool_new_super_graph)
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
            performance_data_df,
            req_info["Performance_data"],
            selected_message,
            settings,
            req_info["message_instance_id"],
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

        cool_new_super_graph.add(
            (
                BNode("p1"),
                URIRef("http://example.com/slowmo#IsAboutPerformer"),
                Literal(int(performance_data_df["staff_number"].iloc[0])),
            )
        )
        response["candidates"] = utils.candidates_records(cool_new_super_graph)

    response.update(full_selected_message)

    return response

import os

import psutil
from fastapi import HTTPException
from loguru import logger
from rdflib import BNode, Graph, Literal

from scaffold import context, startup
from scaffold.bitstomach import bitstomach
from scaffold.candidate_pudding import candidate_pudding
from scaffold.esteemer import esteemer, utils
from scaffold.pictoralist.pictoralist import Pictoralist
from scaffold.utils.namespace import PSDO, SLOWMO
from scaffold.utils.settings import settings
from scaffold.utils.utils import set_logger

set_logger()


def pipeline():
    performance_df = bitstomach.prepare()

    # BitStomach
    logger.debug("Calling BitStomach from main...")

    g: Graph = bitstomach.extract_signals(performance_df)

    performance_content = g.resource(BNode("performance_content"))
    if len(list(performance_content[PSDO.motivating_information])) == 0:
        context.subject_graph.close()
        detail = {
            "message": "Insufficient significant data found for providing feedback, process aborted.",
            "subject": context.subject,
        }
        raise HTTPException(
            status_code=400,
            detail=detail,
            headers={"400-Error": "Invalid Input Error"},
        )

    context.subject_graph += g

    # candidate_pudding
    logger.debug("Calling candidate_pudding from main...")
    candidate_pudding.create_candidates()

    # #Esteemer
    logger.debug("Calling Esteemer from main...")

    measures: set[BNode] = set(
        context.subject_graph.objects(
            None, PSDO.motivating_information / SLOWMO.RegardingMeasure
        )
    )

    for measure in measures:
        candidates = utils.candidates(
            context.subject_graph, filter_acceptable=True, measure=measure
        )
        for candidate in candidates:
            esteemer.score(candidate, startup.mpm)
    selected_candidate = esteemer.select_candidate(context.subject_graph)
    preferences = esteemer.get_preferences()

    if preferences["Display_Format"]:
        context.subject_graph.resource(selected_candidate)[SLOWMO.Display] = Literal(
            preferences["Display_Format"]
        )

    selected_message = utils.render(context.subject_graph, selected_candidate)

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

        response["candidates"] = utils.candidates_records(context.subject_graph)

    response.update(full_selected_message)

    return response

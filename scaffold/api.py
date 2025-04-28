import os
import sys
import webbrowser
from pathlib import Path

import matplotlib
import psutil
from fastapi import FastAPI, Request
from loguru import logger
from rdflib import (  # , ConjunctiveGraph, Namespace, URIRef, RDFS, Literal
    Graph,
)

from scaffold.pipeline import pipeline
from scaffold.startup import startup
from scaffold.utils.settings import settings

matplotlib.use("Agg")


logger.info(
    f"Initial system memory: {psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024}"
)

### Logging module setup (using loguru module)
logger.remove()
logger.add(
    sys.stdout, colorize=True, format="{level}|  {message}", level=settings.log_level
)
logger.at_least = (
    lambda lvl: logger.level(lvl).no >= logger.level(settings.log_level).no
)

## Log of instance configuration
logger.debug("Startup configuration for this instance:")
for attribute in dir(settings):
    if not attribute.startswith("__"):
        value = getattr(settings, attribute)
        logger.debug(f"{attribute}:\t{value}")


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    startup()


@app.get("/")
async def root():
    return {"Hello": "Universe"}


@app.get("/info")
async def info():
    return settings


@app.get("/template/")
async def template():
    github_link = "https://raw.githubusercontent.com/Display-Lab/precision-feedback-pipeline/main/input_message.json"
    return webbrowser.open(github_link)


@app.post("/createprecisionfeedback/")
async def createprecisionfeedback(info: Request):
    req_info = await info.json()

    return pipeline(req_info)


def debug_output_if_set(graph: Graph, file_location):
    if settings.outputs is True and logger.at_least("DEBUG"):
        file_path = Path(file_location)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        graph.serialize(destination=file_path, format="json-ld", indent=2)

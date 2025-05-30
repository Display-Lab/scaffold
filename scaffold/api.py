import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

from scaffold import context
from scaffold.bitstomach.bitstomach import prepare
from scaffold.pipeline import pipeline
from scaffold.startup import startup
from scaffold.utils.settings import settings
from scaffold.utils.utils import get_performance_month

app = FastAPI()


startup()


@app.get("/")
async def root():
    return {"Hello": "Universe"}


@app.get("/info")
async def info():
    return settings


@app.get("/template/")
async def template():
    github_link = "https://raw.githubusercontent.com/Display-Lab/scaffold/refs/heads/main/tests/test_cases/input_message.json"
    return RedirectResponse(url=github_link)


@app.post("/createprecisionfeedback/")
async def createprecisionfeedback(info: Request):
    req_info = await info.json()
    context.update(req_info)

    performance_month = get_performance_month(req_info)
    performance_df = prepare(
        performance_month,
        pd.DataFrame(
            req_info["Performance_data"][1:], columns=req_info["Performance_data"][0]
        ),
    )
    try:
        full_message = pipeline(performance_df)
        full_message["message_instance_id"] = req_info["message_instance_id"]
        full_message["performance_data"] = req_info["Performance_data"]
    except HTTPException as e:
        e.detail["message_instance_id"] = req_info["message_instance_id"]
        raise e

    return full_message

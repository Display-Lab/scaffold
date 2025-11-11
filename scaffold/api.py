from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

from scaffold import context
from scaffold.pipeline import pipeline
from scaffold.startup import startup
from scaffold.utils.settings import settings

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

    try:
        context.from_req(req_info)

        full_message = pipeline()
        full_message["message_instance_id"] = req_info["@id"]
        full_message["performance_measure_report"] = req_info[
            "performance_measure_report"
        ]
        full_message["comparator_measure_report"] = req_info[
            "comparator_measure_report"
        ]
    except HTTPException as e:
        e.detail["message_instance_id"] = req_info["@id"]
        raise e

    return full_message

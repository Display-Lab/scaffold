from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

from scaffold.bitstomach.bitstomach import prepare
from scaffold.pipeline import pipeline
from scaffold.startup import set_preferences, startup
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
    preferences = set_preferences(req_info)
    history: dict = req_info.get("History", {})
    performance_df = prepare(req_info)
    try:
        full_message = pipeline(preferences, history, performance_df)
        full_message["message_instance_id"] = req_info["message_instance_id"]
        full_message["performance_data"] = req_info["Performance_data"]
    except HTTPException as e:        
        e.detail["message_instance_id"] = req_info["message_instance_id"]
        raise e
        
    return full_message

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

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

    return pipeline(req_info)

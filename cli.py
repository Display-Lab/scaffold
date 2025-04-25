import os

os.environ["ENV_PATH"] = "/home/faridsei/dev/code/dev.env"
os.environ["log_level"] = "DEBUG"
import json
import sys
from typing import Annotated

from loguru import logger
from typer import Argument, Typer

from pipeline import pipeline as process_pipeline
from startup import startup
from utils.settings import settings

logger.remove()
logger.add(
    sys.stdout, colorize=True, format="{level}|  {message}", level=settings.log_level
)
logger.at_least = (
    lambda lvl: logger.level(lvl).no >= logger.level(settings.log_level).no
)
cli = Typer(no_args_is_help=True)

startup()


@cli.command()
def pipeline(
    file_path: Annotated[str, Argument(help="Path to input data in JSON format")],
) -> None:
    with open(file_path, "r") as file:
        input = json.load(file)

    result = process_pipeline(input)
    result["message_generated_datetime"] = str(result["message_generated_datetime"])
    directory = os.path.join(os.path.dirname(file_path), "messages")
    filename = os.path.basename(file_path)
    name_without_ext, _ = os.path.splitext(filename)
    new_filename = f"{name_without_ext} - message for {input['performance_month']}.json"
    output_path = os.path.join(directory, new_filename)
    os.makedirs(directory, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)


# @cli.command()
# def web():
#     uvicorn.run("butter_cup.api:app", reload=True, use_colors=True)

if __name__ == "__main__":
    import sys

    sys.argv = [
        "pipeline.py",
        "/home/faridsei/dev/test/2024-06-24/2024-05-01/Provider_1.json",
    ]

    cli()

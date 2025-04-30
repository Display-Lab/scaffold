import os
import pathlib
from typing import Annotated

import orjson
import uvicorn
from loguru import logger
from typer import Argument, Typer

from scaffold.pipeline import pipeline
from scaffold.startup import startup

cli = Typer(no_args_is_help=True)

startup()


@cli.command()
def single(
    file_path: Annotated[
        pathlib.Path, Argument(help="Path to input data in JSON format")
    ],
) -> None:
    input = orjson.loads(file_path.read_bytes())
    result = pipeline(input)

    directory = file_path.parent / "messages"
    os.makedirs(directory, exist_ok=True)

    new_filename = f"{file_path.stem} - message for {input['performance_month']}.json"

    output_path = directory / new_filename

    output_path.write_bytes(orjson.dumps(result, option=orjson.OPT_INDENT_2))

    logger.info(f"Message created at {output_path}")


@cli.command()
def web():
    uvicorn.run("scaffold.api:app", reload=False, use_colors=True)


if __name__ == "__main__":
    cli()

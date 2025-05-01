import os
import pathlib
from typing import Annotated

import orjson
import typer
import uvicorn
from loguru import logger
from typer import Argument, Typer

from scaffold.pipeline import pipeline
from scaffold.startup import startup

cli = Typer(no_args_is_help=True)


@cli.command()
def single(
    file_path: Annotated[
        pathlib.Path, Argument(help="Path to input data in JSON format")
    ],
) -> None:
    startup()

    input = orjson.loads(file_path.read_bytes())
    result = pipeline(input)

    directory = file_path.parent / "messages"
    os.makedirs(directory, exist_ok=True)

    new_filename = f"{file_path.stem} - message for {input['performance_month']}.json"

    output_path = directory / new_filename

    output_path.write_bytes(orjson.dumps(result, option=orjson.OPT_INDENT_2))

    logger.info(f"Message created at {output_path}")


@cli.command()
def batch(
    file_path: Annotated[
        pathlib.Path,
        Argument(help="Path to a JSON file or a directory containing JSON files"),
    ],
    max_files: Annotated[
        int, typer.Option("--max-files", help="Maximum number of files to process")
    ] = None,
    count_only: Annotated[
        bool,
        typer.Option(
            "--count-only",
            help="Only simulate processing; count successes and failures",
        ),
    ] = False,
) -> None:
    startup()

    if file_path.is_file() and file_path.suffix == ".json":
        input_files = [file_path]
    elif file_path.is_dir():
        input_files = sorted(file_path.glob("*.json"))
    else:
        logger.error(
            f"Invalid input: {file_path} is neither a .json file nor a directory containing .json files."
        )
        raise SystemExit(1)

    if max_files is not None:
        input_files = input_files[:max_files]

    success_count = 0
    failure_count = 0

    for input_file in input_files:
        try:
            input_data = orjson.loads(input_file.read_bytes())
            result = pipeline(input_data)

            if not count_only:
                directory = input_file.parent / "messages"
                os.makedirs(directory, exist_ok=True)

                performance_month = input_data.get("performance_month", "unknown_month")
                new_filename = (
                    f"{input_file.stem} - message for {performance_month}.json"
                )
                output_path = directory / new_filename

                output_path.write_bytes(
                    orjson.dumps(result, option=orjson.OPT_INDENT_2)
                )
                logger.info(f"Message created at {output_path}")
            else:
                logger.info(f"✔ Would process: {input_file}")

            success_count += 1
        except Exception as e:
            logger.error(f"✘ Failed to process {input_file}: {e}")
            failure_count += 1

    logger.info(f"Total files scanned: {len(input_files)}")
    logger.info(f"Successful: {success_count}, Failed: {failure_count}")


@cli.command()
def web():
    uvicorn.run("scaffold.api:app", reload=False, use_colors=True)


if __name__ == "__main__":
    cli()

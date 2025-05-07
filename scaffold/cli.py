import os
import pathlib
import subprocess
from typing import Annotated

import orjson
import pandas as pd
import typer
from loguru import logger

from scaffold.bitstomach.bitstomach import prepare_performance_df
from scaffold.pipeline import pipeline, run_pipeline
from scaffold.startup import set_preferences, startup
from scaffold.utils.utils import (
    add_candidates,
    add_response,
    analyse_candidates,
    analyse_responses,
    extract_number,
)

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def batch(
    file_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to a JSON file or a directory containing JSON files"),
    ],
    max_files: Annotated[
        int, typer.Option("--max-files", help="Maximum number of files to process")
    ] = None,
    stats_only: Annotated[
        bool,
        typer.Option(
            "--stats-only",
            help="Only simulate processing; count successes and failures and additional stats",
        ),
    ] = False,
) -> None:
    startup()

    if file_path.is_file() and file_path.suffix == ".json":
        input_files = [file_path]
    elif file_path.is_dir():
        input_files = sorted(file_path.glob("*.json"), key=extract_number)
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

            response_data = run_pipeline(input_data)

            if not stats_only:
                directory = input_file.parent / "messages"
                os.makedirs(directory, exist_ok=True)

                performance_month = input_data.get("performance_month", "unknown_month")
                new_filename = (
                    f"{input_file.stem} - message for {performance_month}.json"
                )
                output_path = directory / new_filename

                output_path.write_bytes(
                    orjson.dumps(response_data, option=orjson.OPT_INDENT_2)
                )
                logger.info(f"Message created at {output_path}")
            else:
                logger.info(f"✔ Would process: {input_file}")

            success_count += 1
        except Exception as e:
            logger.error(f"✘ Failed to process {input_file}: {e}")
            failure_count += 1
            response_data = e.detail

        add_response(response_data)
        if not stats_only:
            add_candidates(response_data, input_data["performance_month"])

    logger.info(f"Total files scanned: {len(input_files)}")
    logger.info(f"Successful: {success_count}, Failed: {failure_count}")
    analyse_responses()
    if not stats_only:
        analyse_candidates(file_path / "messages" / "candidates.csv")

@cli.command()
def batch_csv(
    file_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to a JSON file or a directory containing JSON files"),
    ]):
    startup()
    
    all_performance_data = pd.read_csv(file_path,parse_dates=["month"])
    
    
    success_count = 0
    failure_count = 0
    for provider_id in all_performance_data["staff_number"].unique().tolist():
        try:
            preferences=set_preferences({})
            performance_df = prepare_performance_df("2024-05-01",all_performance_data[all_performance_data["staff_number"] == provider_id].reset_index(drop=True))
            result = pipeline(preferences,{},performance_df)
            print(result)
            success_count += 1
        except Exception as e:
            failure_count += 1

    logger.info(f"Successful: {success_count}, Failed: {failure_count}")   
    
    
@cli.command()
def web(workers: int = 5):
    # uvicorn.run(["scaffold.api:app","--workers", str(workers)], reload=False, use_colors=True)
    subprocess.run([
        "uvicorn",
        "scaffold.api:app",
        "--workers", str(workers),
        "--use-colors"
    ])

if __name__ == "__main__":
    cli()

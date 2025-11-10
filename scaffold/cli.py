import os
import pathlib
import subprocess
from typing import Annotated

import orjson
import typer
from fastapi import HTTPException
from loguru import logger

from scaffold import context, startup
from scaffold.pipeline import pipeline
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
    startup.startup()

    if file_path.is_file() and file_path.suffix == ".json":
        input_files = [file_path]
    elif file_path.is_dir():
        input_files = sorted(file_path.glob("*.json"), key=extract_number)
    else:
        logger.error(
            f"Invalid input: {file_path} is neither a .json file nor a directory containing .json files."
        )
        raise SystemExit(1)

    success_count = 0
    failure_count = 0

    for input_file in input_files[:max_files]:
        try:
            input_data = orjson.loads(input_file.read_bytes())

            try:
                context.from_req(input_data)

                full_message = pipeline()
                full_message["message_instance_id"] = input_data["message_instance_id"]
                full_message["performance_measure_report"] = input_data[
                    "performance_measure_report"
                ]
                full_message["comparator_measure_report"] = input_data[
                    "comparator_measure_report"
                ]
            except HTTPException as e:
                e.detail["message_instance_id"] = input_data["message_instance_id"]
                raise e

            if not stats_only:
                directory = input_file.parent / "messages"
                os.makedirs(directory, exist_ok=True)

                new_filename = (
                    f"{input_file.stem} - message for {context.performance_month}.json"
                )
                output_path = directory / new_filename

                output_path.write_bytes(
                    orjson.dumps(full_message, option=orjson.OPT_INDENT_2)
                )
                logger.info(f"Message created at {output_path}")
            else:
                logger.info(f"✔ Would process: {input_file}")

            success_count += 1
        except Exception as e:
            logger.error(f"✘ Failed to process {input_file}: {e}")
            failure_count += 1
            full_message = e.detail

        add_response(full_message)
        if not stats_only:
            add_candidates(full_message)

    logger.info(f"Total files scanned: {len(input_files[:max_files])}")
    logger.info(f"Successful: {success_count}, Failed: {failure_count}")
    analyse_responses()
    if not stats_only:
        analyse_candidates(file_path / "messages" / "candidates.csv")


@cli.command()
def batch_csv(
    performance_data_path: Annotated[
        pathlib.Path,
        typer.Argument(
            help="Path to a the folder containing ingestion CSV files for Performance Measure Report, Comparator Measure Report and Practitioner Role"
        ),
    ],
    max_files: Annotated[
        int, typer.Option("--max-files", help="Maximum number of files to process")
    ] = None,
    performance_month: Annotated[
        str, typer.Option("--performance-month", help="Performance month")
    ] = None,
    stats_only: Annotated[
        bool,
        typer.Option(
            "--stats-only",
            help="Only simulate processing; count successes and failures and additional stats",
        ),
    ] = False,
):
    startup.startup(
        performance_data_path=performance_data_path, performance_m=performance_month
    )

    success_count = 0
    failure_count = 0
    for subject in (
        startup.performance_measure_report["subject"].drop_duplicates().head(max_files)
    ):
        try:
            context.from_global(subject)
            try:
                full_message = pipeline()
                # full_message["message_instance_id"] = input_data["message_instance_id"]
                full_message["performance_data"] = context.performance_month
            except Exception as e:
                # e.detail["message_instance_id"] = input_data["message_instance_id"]
                raise e
            if not stats_only:
                directory = performance_data_path.parent / "messages"
                os.makedirs(directory, exist_ok=True)

                new_filename = (
                    f"Provider_{subject} - message for {context.performance_month}.json"
                )
                output_path = directory / new_filename

                output_path.write_bytes(
                    orjson.dumps(full_message, option=orjson.OPT_INDENT_2)
                )
                logger.info(f"Message created at {output_path}")
            else:
                logger.info(f"✔ Would process: Provider_{subject}")

            success_count += 1

        except Exception as e:
            logger.error(f"✘ Failed to process Provider_{subject}: {e}")
            failure_count += 1
            full_message = e.detail

        add_response(full_message)
        if not stats_only:
            add_candidates(full_message)

    logger.info(f"Successful: {success_count}, Failed: {failure_count}")
    analyse_responses()
    if not stats_only:
        analyse_candidates(performance_data_path.parent / "messages" / "candidates.csv")


@cli.command()
def web(workers: int = 5):
    subprocess.run(
        ["uvicorn", "scaffold.api:app", "--workers", str(workers), "--use-colors"]
    )


if __name__ == "__main__":
    cli()

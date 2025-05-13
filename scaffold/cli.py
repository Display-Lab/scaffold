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
    get_history,
    get_preferences,
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
    performance_data_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to a CSV file containing performance data"),
    ],
    preferences_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to a CSV file containing the preferences"),
    ],
    history_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to a CSV file containing the history"),
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
    startup()

    all_performance_data = pd.read_csv(performance_data_path, parse_dates=["month"])
    all_preferences = pd.read_csv(preferences_path)
    all_hostory = pd.read_csv(history_path)

    if max_files is not None:
        first_n_staff = (
            all_performance_data["staff_number"].drop_duplicates().head(max_files)
        )
        performance_data = all_performance_data[
            all_performance_data["staff_number"].isin(first_n_staff)
        ].reset_index(drop=True)
        # performance_data = all_performance_data[all_performance_data['staff_number'].isin(set(range(1, max_files + 1)))].reset_index(drop=True)
    success_count = 0
    failure_count = 0
    for provider_id in performance_data["staff_number"].unique().tolist():
        try:
            preferences = set_preferences(
                get_preferences(
                    all_preferences[all_preferences["staff_number"] == provider_id]
                )
            )
            history = get_history(
                all_hostory[all_hostory["staff_number"] == provider_id]
            )

            performance_df = prepare_performance_df(
                performance_month,
                performance_data[
                    performance_data["staff_number"] == provider_id
                ].reset_index(drop=True),
            )
            result = pipeline(preferences, history, performance_df)
            if not stats_only:
                directory = performance_data_path.parent / "messages"
                os.makedirs(directory, exist_ok=True)

                performance_month = performance_month
                new_filename = (
                    f"Provider_{provider_id} - message for {performance_month}.json"
                )
                output_path = directory / new_filename

                output_path.write_bytes(
                    orjson.dumps(result, option=orjson.OPT_INDENT_2)
                )
                logger.info(f"Message created at {output_path}")
            else:
                logger.info(f"✔ Would process: Provider_{provider_id}")

            success_count += 1

        except Exception as e:
            logger.error(f"✘ Failed to process Provider_{provider_id}: {e}")
            failure_count += 1
            result = e.detail

        add_response(result)
        if not stats_only:
            add_candidates(result, performance_month)

    logger.info(f"Successful: {success_count}, Failed: {failure_count}")
    analyse_responses()
    if not stats_only:
        analyse_candidates(performance_data_path.parent / "messages" / "candidates.csv")


@cli.command()
def web(workers: int = 5):
    # uvicorn.run(["scaffold.api:app","--workers", str(workers)], reload=False, use_colors=True)
    subprocess.run(
        ["uvicorn", "scaffold.api:app", "--workers", str(workers), "--use-colors"]
    )


if __name__ == "__main__":
    cli()

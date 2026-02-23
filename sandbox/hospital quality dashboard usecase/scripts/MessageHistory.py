import argparse
import os
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

# os.environ["ENV_PATH"] = "...." # set this if you are debugging this script 
from scaffold import context, startup
from scaffold import pipeline as p

start = time.time()

parser = argparse.ArgumentParser(
    description="PerformanceMeasureReport generator for PractitionerRole."
)
parser.add_argument("--path", type=str, default="../data/tabular inputs", help="Output path")

args = parser.parse_args()
output_dir = Path(args.path)
performance_data_df = pd.read_csv(output_dir / "PerformanceMeasureReport.csv")
months = (
    performance_data_df[["period.start", "period.end"]]
    .drop_duplicates()
    .sort_values("period.start")
    .values.tolist()
)
print(output_dir)

startup.startup(performance_data_path=output_dir)
for subject in performance_data_df["subject"].drop_duplicates():
    print(f"Generating history for {subject}")
    for month in months:
        if month[0] == months[-1][0]:
            continue
        startup.performance_month = month[0]
        context.from_global(subject)
        full_message = p.pipeline()
        startup.history.loc[len(startup.history)] = [
            subject,
            month[0],
            month[1],
            str(
                {
                    "message_template": full_message["selected_candidate"][
                        "message_template_id"
                    ],
                    "message_template_name": full_message["selected_candidate"][
                        "message_template_name"
                    ],
                    "message_generated_datetime": datetime.now().strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    ),
                    "measure": full_message["selected_candidate"]["measure"],
                    "acceptable_by": [
                        str(full_message["selected_candidate"]["acceptable_by"][0])
                    ],
                }
            ),
        ]

startup.history.to_csv(output_dir / "MessageHistory.csv", index=False)


end = time.time()
print(f"Elapsed time: {end - start:.2f} seconds")

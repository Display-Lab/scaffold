import argparse
import random
import time
import uuid
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from utils import calculate_mean_and_stds, generate_months, measures



start = time.time()

parser = argparse.ArgumentParser(
    description="PerformanceMeasureReport generator for PractitionerRole."
)
parser.add_argument("--path", type=str, default="sandbox_data", help="Output path")
parser.add_argument(
    "--performance_month", type=str, default="2025-01-01", help="Performance month"
)
parser.add_argument("--num_month", type=int, default=12, help="Number of months")

args = parser.parse_args()
output_dir = Path(args.path)
practitioner_data_df = pd.read_csv(output_dir / "PractitionerRole.csv")
performance_date = datetime.strptime(args.performance_month, "%Y-%m-%d")


performance_rows = []

months = generate_months(performance_date, args.num_month)
means, stds = calculate_mean_and_stds(measures, args.num_month)

random_matrix = np.random.normal(
    loc=means[:, :, None],
    scale=stds[:, :, None],
    size=(len(means), args.num_month, len(practitioner_data_df)),
)
random_matrix = np.clip(random_matrix, 0, 100)
random_matrix = np.round(random_matrix / 100, 2)


for organization_index, organization in practitioner_data_df[
    "PractitionerRole.identifier"
].items():
    for measure_index, measure in enumerate(measures):
        for month_index, month in enumerate(months):
            rate = random_matrix[measure_index, month_index, organization_index]
            denominator = random.randint(50, 5000)
            performance_rows.append(
                [
                    f"{str(uuid.uuid4())}",
                    measure,
                    organization,
                    month[0],
                    month[1][0],
                    rate,
                    denominator,
                    0,
                ]
            )

performance_data_columns = [
    "identifier",
    "measure",
    "subject",
    "period.start",
    "period.end",
    "measureScore.rate",
    "measureScore.denominator",
    "measureScore.range",
]

performance_data_df = pd.DataFrame(performance_rows, columns=performance_data_columns)
performance_data_df.to_csv(output_dir / "PerformanceMeasureReport.csv", index=False)


end = time.time()
print(f"Elapsed time to generate PractitionerRole: {end - start:.2f} seconds")

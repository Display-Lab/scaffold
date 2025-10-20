import argparse
import time
from pathlib import Path

import pandas as pd
from utils import generate_preferences

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

preferences_rows = []
for organization_index, organization in practitioner_data_df[
    "PractitionerRole.identifier"
].items():
    preferences = generate_preferences(0.035)
    if preferences:
        preferences_rows.append(
            ["hospital " + str(organization), preferences]
        )


preferences_data_columns = [
    "subject",
    "preferences.json",
]
preferences_data_df = pd.DataFrame(preferences_rows, columns=preferences_data_columns)
preferences_data_df.to_csv(output_dir / "Preference.csv", index=False)

end = time.time()
print(f"Elapsed time to generate PractitionerRole: {end - start:.2f} seconds")

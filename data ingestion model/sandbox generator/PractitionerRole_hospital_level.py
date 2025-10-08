import argparse
import time
from pathlib import Path

import pandas as pd

start = time.time()

parser = argparse.ArgumentParser(description="PractitionerRole generator for hospital level data.")
parser.add_argument("--num_orgs", type=int, default=100, help="Number of organizations")
parser.add_argument("--path", type=str, default="sandbox_data", help="Output path")

args = parser.parse_args()

organizations = list(range(1, args.num_orgs + 1))
start = time.time()

practitioner_rows = []
for organization_index, organization in enumerate(organizations):
    practitioner_rows.append(
        [
            "hospital " + str(organization),
            "Network-Hospital-A",
            " ",
            "Hospital",
        ]
    )

practitioner_data_columns = [
    "PractitionerRole.practitioner",
    "PractitionerRole.organization",
    "PractitionerRole.code",
    "type",
]
practitioner_data_df = pd.DataFrame(
    practitioner_rows, columns=practitioner_data_columns
)

output_dir = Path(args.path)
output_dir.mkdir(exist_ok=True)
practitioner_data_df.to_csv(output_dir / "PractitionerRole.csv", index=False)

end = time.time()
print(f"Elapsed time to generate PractitionerRole: {end - start:.2f} seconds")
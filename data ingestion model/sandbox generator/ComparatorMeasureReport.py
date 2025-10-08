import argparse
import time
import uuid
from pathlib import Path

import pandas as pd
from utils import measures, peer_average, top_10_percent_mean

start = time.time()

parser = argparse.ArgumentParser(
    description="PerformanceMeasureReport generator for PractitionerRole."
)
parser.add_argument("--path", type=str, default="sandbox_data", help="Output path")

args = parser.parse_args()
output_dir = Path(args.path)
performance_data_df = pd.read_csv(output_dir / "PerformanceMeasureReport.csv")
practitioner_data_df = pd.read_csv(output_dir / "PractitionerRole.csv")

months = (
    performance_data_df[["period.start", "period.end"]]
    .drop_duplicates()
    .sort_values("period.start")
    .values.tolist()
)

comparator_rows = []
for measure_index, measure in enumerate(measures):
    for month_index, month in enumerate(months):
        comparator_rows.append(
            [
                f"{str(uuid.uuid4())}",
                measure,
                month[0],
                month[1],
                measures[measure]["target"],
                "Network-Hospital-A",
                "http://purl.obolibrary.org/obo/PSDO_0000094",
                " ",
            ]
        )

comparator_data_columns = [
    "identifier",
    "measure",
    "period.start",
    "period.end",
    "measureScore.rate",
    "group.subject",
    "group.code",
    "PractitionerRole.code",
]
comparator_data_df = pd.DataFrame(comparator_rows, columns=comparator_data_columns)

practitioner_subset = practitioner_data_df[
    [
        "PractitionerRole.practitioner",
        "PractitionerRole.organization",
        "PractitionerRole.code",
    ]
]

merged_df = performance_data_df.merge(
    practitioner_subset,
    how="left",  # keeps all rows from performance_data_df
    left_on="subject",
    right_on="PractitionerRole.practitioner",
)

merged_df = merged_df.drop(columns=["PractitionerRole.practitioner"])

group_cols = [
    "measure",
    "period.start",
    "period.end",
    "PractitionerRole.organization",
    "PractitionerRole.code",
]

top_10_df = (
    merged_df.groupby(group_cols)["measureScore.rate"]
    .apply(top_10_percent_mean)
    .reset_index()
)
top_10_df["group.code"] = "http://purl.obolibrary.org/obo/PSDO_0000129"

peer_avg_df = (
    merged_df.groupby(group_cols)["measureScore.rate"].apply(peer_average).reset_index()
)
peer_avg_df["group.code"] = "http://purl.obolibrary.org/obo/PSDO_0000126"

peer_and_topten_df = pd.concat([top_10_df, peer_avg_df], ignore_index=True)

peer_and_topten_df = peer_and_topten_df.rename(
    columns={
        "measureScore.rate": "measureScore.rate",
        "PractitionerRole.organization": "group.subject",
        "PractitionerRole.code": "PractitionerRole.code",
    }
)

peer_and_topten_df["identifier"] = [
    str(uuid.uuid4()) for _ in range(len(peer_and_topten_df))
]

peer_and_topten_df = peer_and_topten_df[
    [
        "identifier",
        "measure",
        "period.start",
        "period.end",
        "measureScore.rate",
        "group.subject",
        "group.code",
        "PractitionerRole.code",
    ]
]

comparator_data_df = pd.concat(
    [comparator_data_df, peer_and_topten_df], ignore_index=True
)

comparator_data_df.to_csv(output_dir / "ComparatorMeasureReport.csv", index=False)

end = time.time()
print(f"Elapsed time to generate PractitionerRole: {end - start:.2f} seconds")
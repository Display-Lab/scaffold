import argparse
import json
import os
import time
import uuid
from pathlib import Path

import pandas as pd
from utils import measures, peer_average, top_10_percent_mean

def top10_stats(group):
    """Compute top 10% stats within each group."""
    # 90th percentile cutoff for rate
    cutoff = group["measureScore.rate"].quantile(0.9)

    # filter top 10% rows
    top10 = group[group["measureScore.rate"] >= cutoff]

    # compute desired values
    top10_rate_mean = top10["measureScore.rate"].mean()
    top10_denom_sum = top10["measureScore.denominator"].sum()

    # return one-row DataFrame (so it can be concatenated easily)
    return pd.Series({
        "measureScore.rate": top10_rate_mean,
        "measureScore.denominator": top10_denom_sum,
    })

def peer_everage_stats(group):
    """Compute  peer (overall) averages per group."""
   
    peer_rate_mean = group["measureScore.rate"].mean()
    peer_denom_sum = group["measureScore.denominator"].sum()

    # Return as one row
    return pd.Series({       
        "measureScore.rate": peer_rate_mean,
        "measureScore.denominator": peer_denom_sum,
    })
    
start = time.time()

parser = argparse.ArgumentParser(
    description="PerformanceMeasureReport generator for PractitionerRole."
)
parser.add_argument("--path", type=str, default="/home/faridsei/dev/code/scaffold/new_data", help="Output path")

args = parser.parse_args()
output_dir = Path(args.path)
performance_data_df = pd.read_csv(output_dir / "PerformanceMeasureReport.csv")
practitioner_data_df = pd.read_csv(output_dir / "PractitionerRole.csv")
config = json.load(open(os.path.join(args.path, "config.json")))
if "group.subject" not in config["ComparatorMergeColumns"]: 
    practitioner_data_df["PractitionerRole.organization"] = "Network-A"
    
months = (
    performance_data_df[["period.start", "period.end"]]
    .drop_duplicates()
    .sort_values("period.start")
    .values.tolist()
)

organizations = practitioner_data_df["PractitionerRole.organization"].drop_duplicates().values.tolist()

comparator_rows = []
for measure_index, measure in enumerate(measures):
    for month_index, month in enumerate(months):
        for organization in organizations:
            comparator_rows.append(
                [
                    f"{str(uuid.uuid4())}",
                    measure,
                    month[0],
                    month[1],
                    measures[measure]["target"]/100,
                    "",
                    organization,
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
    "measureScore.denominator",
    "group.subject",
    "group.code",
    "PractitionerRole.code",
]
comparator_data_df = pd.DataFrame(comparator_rows, columns=comparator_data_columns)

practitioner_subset = practitioner_data_df[
    [
        "PractitionerRole.identifier",
        "PractitionerRole.organization",
        "PractitionerRole.code",
    ]
]

merged_df = performance_data_df.merge(
    practitioner_subset,
    how="left",  # keeps all rows from performance_data_df
    left_on="subject",
    right_on="PractitionerRole.identifier",
)

merged_df = merged_df.drop(columns=["PractitionerRole.identifier"])

group_cols = [
    "measure",
    "period.start",
    "period.end",
    "PractitionerRole.organization",
    "PractitionerRole.code",
]

# top_10_df = (
#     merged_df.groupby(group_cols)["measureScore.rate"]
#     .apply(top_10_percent_mean)
#     .reset_index()
# )
top_10_df = (
    merged_df.groupby(group_cols, group_keys=False)
      .apply(top10_stats)
      .reset_index()
)

top_10_df["group.code"] = "http://purl.obolibrary.org/obo/PSDO_0000129"

# peer_avg_df = (
#     merged_df.groupby(group_cols)["measureScore.rate"].apply(peer_average).reset_index()
# )
# peer_avg_df["group.code"] = "http://purl.obolibrary.org/obo/PSDO_0000126"
peer_avg_df = (
    merged_df.groupby(group_cols, group_keys=False)
      .apply(peer_everage_stats)
      .reset_index()
)

peer_avg_df["group.code"] = "http://purl.obolibrary.org/obo/PSDO_0000126"

peer_and_topten_df = pd.concat([top_10_df, peer_avg_df], ignore_index=True)





peer_and_topten_df = peer_and_topten_df.rename(
    columns={
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
        "measureScore.denominator",
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
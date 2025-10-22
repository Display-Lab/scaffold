# This script should be executed having SCAFFOLD as the current directory because it uses the scaffold package.

import os
import random
import time
import uuid
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta


# from scipy.stats import truncnorm

os.environ["ENV_PATH"] = "/home/faridsei/dev/code/dev.env"
from scaffold import context, pipeline as p, startup


global_staff_number = 0
import numpy as np

def find_precap_mean(target_mean, cv=0.15, cap=100.0, tol=0.01, n=500_000, seed=42):
    np.random.seed(seed)
    lo, hi = target_mean, 150.0  # start search from target to high
    for _ in range(50):
        mid = (lo + hi)/2
        sigma = mid * cv
        x = np.random.normal(mid, sigma, n)
        x = np.clip(x, None, cap)
        post_mean = x.mean()
        if abs(post_mean - target_mean) < tol:
            return mid
        if post_mean < target_mean:
            lo = mid
        else:
            hi = mid
    return mid

measures = {
    "Transfer-01": {"mean": 53.8, "target": 73.0},
    "Hand-01": {"mean": find_precap_mean(94), "target": 95.0},
    "Provider-Rating-01": {"mean": find_precap_mean(90.6), "target": 90.9},
    "Care-Rating-01": {"mean": find_precap_mean(92.3), "target": 92.3},
    "Clean-Rating-01": {"mean": 83.9, "target": 86.7},
    "Quiet-Rating-01": {"mean": 73.2, "target": 75.6},
    "Patient-Concern-01": {"mean": find_precap_mean(95.3), "target": 95.5},
    "Discharge-01": {"mean": 82.7, "target": 83.3},
    "Nurse-informed-01": {"mean": find_precap_mean(89.4), "target": 90.0},
    "Nurse-language-01": {"mean": find_precap_mean(93.2), "target": 93.8},
    "Physician-language-01": {"mean": find_precap_mean(89.7), "target": 90.0},
    "Physician-informed-01": {"mean": 84.8, "target": 86.1},
}

Roles = ["resident", "attending", "CRNA"]
performance_rows = []
practitioner_rows = []
preferences_rows = []

def calculate_mean_and_stds(measures, num_months=12, COEF_VARIATION=0.15):
    means = np.empty((0, num_months), dtype=float)
    for name, measure in measures.items():
        base_mean = measure["mean"]
        growth_factors = np.linspace(1.0, 1.03, num_months)
        growth_factors /= growth_factors.mean()
        normalized = np.array(base_mean * growth_factors)
        means = np.append(means, [normalized.round(2).tolist()], axis=0)
    stds = means * COEF_VARIATION
    return means, stds


def input_parameters():
    performance_month = (
        input("Enter performance month [default=2025-01-01]:") or "2025-01-01"
    )
    performance_date = datetime.strptime(performance_month, "%Y-%m-%d")

    organizations = list(
        range(1, int(input("Enter number of organizations [default=120]:") or 119) + 1)
    )
    num_months = int(input("Enter number of month [default=12]:") or 12)

    output_dir = Path(
        input("Enter output folder path and name [default=sandbox_data]:")
        or "sandbox_data"
    )
    output_dir.mkdir(exist_ok=True)
    return performance_month, performance_date, organizations, num_months, output_dir


def generate_months(performance_date, num_months):
    months = [
        [(performance_date - relativedelta(months=i)).strftime("%Y-%m-%d"), ""]
        for i in reversed(range(0, num_months))
    ]
    for index, month in enumerate(months):
        end_date = pd.to_datetime(month)
        end_date = end_date + pd.offsets.MonthEnd(0)
        months[index][1] = end_date.strftime("%Y-%m-%d")
    return months

# def truncated_normal(mean, std, lower, upper, size):
#     a, b = (lower - mean) / std, (upper - mean) / std
#     samples = truncnorm.rvs(a, b, loc=mean, scale=std, size=size)
#     return np.round(samples, 2)

def top_10_percent_mean(series):
    n = max(int(len(series) * 0.1), 1)  # at least 1 value
    top_n = series.nlargest(n)
    return round(top_n.mean()*100, 2)

def peer_average(series):
    return round(series.mean()*100,2)

def generate_preferences(probability=1):
    if random.random() > probability:
        return {}

    def random_float(min_val, max_val, decimals=2):
        return round(random.uniform(min_val, max_val), decimals)

    # Randomly choose one of the display formats to be 1
    display_options = ["Bar chart", "Line chart", "Text-only", "System-generated"]
    selected_display = random.choice(display_options)
    display_format = {
        option: 1 if option == selected_display else 0 for option in display_options
    }

    preferences = {
        "Utilities": {
            "Message_Format": {
                "Social gain": str(random_float(0.01, 0.1)),
                "Social stayed better": str(random_float(-0.2, -0.05)),
                "Worsening": str(random_float(-0.2, -0.05)),
                "Improving": str(random_float(-0.2, -0.05)),
                "Social loss": str(random_float(0.5, 0.8)),
                "Social stayed worse": str(random_float(-0.7, -0.4)),
                "Social better": str(random_float(-1.4, -1.0)),
                "Social worse": str(random_float(0.3, 0.6)),
                "Social approach": str(random_float(0.8, 1.1)),
                "Goal gain": str(random_float(0.01, 0.08)),
                "Goal approach": str(random_float(0.8, 1.1)),
            },
            "Display_Format": display_format,
        }
    }

    return preferences

performance_month, performance_date, organizations, num_months, output_dir = input_parameters()
start = time.time()
months = generate_months(performance_date, num_months)
means, stds = calculate_mean_and_stds(measures, num_months)

random_matrix = np.random.normal(
    loc=means[:, :, None],
    scale=stds[:, :, None],
    size=(len(means), num_months, len(organizations)),
)
random_matrix = np.clip(random_matrix, 0, 100)
random_matrix = np.round(random_matrix/100, 2)
# random_matrix = truncated_normal(
#     mean=means[:, :, None],
#     std=stds[:, :, None],
#     lower=0,
#     upper=100,
#     size=(len(means), num_months, num_staff))

# generate performance data, practitioner role and preferences
for organization_index,organization in enumerate(organizations):
    practitioner_rows.append(
            [
                "hospital " + str(organization),
                "Network-Hospital-A",
                " ",
                "Hospital",
            ]
        )

    for measure_index, measure in enumerate(measures):
        for month_index, month in enumerate(months):
            rate = random_matrix[measure_index, month_index, organization_index]
            denominator = random.randint(50, 5000)
            performance_rows.append(
                [
                    f"{str(uuid.uuid4())}",
                    measure,
                    "hospital " + str(organization),
                    month[0],
                    month[1][0],
                    rate,
                    denominator,
                    0,
                ]
            )
            
    preferences_rows.append(["hospital " + str(organization),generate_preferences()])

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

practitioner_data_columns = [
    "PractitionerRole.practitioner",
    "PractitionerRole.organization",
    "PractitionerRole.code",
    "type",
]
practitioner_data_df = pd.DataFrame(
    practitioner_rows, columns=practitioner_data_columns
)

# performance_data_df = performance_data_df[
#     np.random.rand(len(performance_data_df)) > 0.1
# ]

performance_data_df.to_csv(output_dir / "PerformanceMeasureReport.csv", index=False)
practitioner_data_df.to_csv(output_dir / "PractitionerRole.csv", index=False)

preferences_data_columns = [
    "subject",
    "preferences.json",]
preferences_data_df = pd.DataFrame(
    preferences_rows, columns=preferences_data_columns
)
preferences_data_df.to_csv(output_dir / "Preference.csv", index=False)


# generate comparator data 
comparator_rows = []
for measure_index, measure in enumerate(measures):
    for month_index, month in enumerate(months):
            comparator_rows.append(
                    [
                        f"{str(uuid.uuid4())}",
                        measure,
                        month[0],
                        month[1][0],
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
comparator_data_df = pd.DataFrame(
    comparator_rows, columns=comparator_data_columns
)

practitioner_subset = practitioner_data_df[[
    "PractitionerRole.practitioner",
    "PractitionerRole.organization",
    "PractitionerRole.code"
]]

merged_df = performance_data_df.merge(
    practitioner_subset,
    how='left',  # keeps all rows from performance_data_df
    left_on='subject',
    right_on='PractitionerRole.practitioner'
)

merged_df = merged_df.drop(columns=['PractitionerRole.practitioner'])

group_cols = [
    "measure",
    "period.start",
    "period.end",
    "PractitionerRole.organization",
    "PractitionerRole.code"
]

top_10_df = (
    merged_df
    .groupby(group_cols)["measureScore.rate"]
    .apply(top_10_percent_mean)
    .reset_index()
)
top_10_df["group.code"] = "http://purl.obolibrary.org/obo/PSDO_0000129"

peer_avg_df = (
    merged_df
    .groupby(group_cols)["measureScore.rate"]
    .apply(peer_average)
    .reset_index()
)
peer_avg_df["group.code"] = "http://purl.obolibrary.org/obo/PSDO_0000126"

peer_and_topten_df = pd.concat([top_10_df, peer_avg_df], ignore_index=True)

peer_and_topten_df = peer_and_topten_df.rename(columns={
    "measureScore.rate": "measureScore.rate",
    "PractitionerRole.organization": "group.subject",
    "PractitionerRole.code": "PractitionerRole.code"
})

peer_and_topten_df["identifier"] = [str(uuid.uuid4()) for _ in range(len(peer_and_topten_df))]

peer_and_topten_df = peer_and_topten_df[[
    "identifier",
    "measure",
    "period.start",
    "period.end",
    "measureScore.rate",
    "group.subject",
    "group.code",
    "PractitionerRole.code"
]]

comparator_data_df = pd.concat([comparator_data_df, peer_and_topten_df], ignore_index=True)

comparator_data_df.to_csv(output_dir / "ComparatorMeasureReport.csv", index=False)

# generate history data
startup.startup(
        performance_data_path=output_dir, performance_m=performance_month
    )
for subject in (
        performance_data_df["subject"].drop_duplicates()
    ):
    print(f"Generating history for {subject}")
    for month in months:
        if month[0] == performance_month: 
            continue
        startup.performance_month=month[0]
        context.from_global(subject)
        full_message = p.pipeline()
        startup.history.loc[len(startup.history)] = [subject, month[0], month[1][0], str({"message_template":full_message["selected_candidate"]["message_template_id"],"message_template_name":full_message["selected_candidate"]["message_template_name"],"message_generated_datetime":datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),"measure":full_message["selected_candidate"]["measure"],"acceptable_by":[str(full_message["selected_candidate"]["acceptable_by"][0])]})]

startup.history.to_csv(output_dir / "MessageHistory.csv", index=False)


end = time.time()
print(f"Elapsed time: {end - start:.2f} seconds")

from datetime import datetime
import random


import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta


def find_precap_mean(target_mean, cv=0.15, cap=100.0, tol=0.01, n=500_000, seed=42):
    np.random.seed(seed)
    lo, hi = target_mean, 150.0  # start search from target to high
    for _ in range(50):
        mid = (lo + hi) / 2
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


def top_10_percent_mean(series):
    n = max(int(len(series) * 0.1), 1)  # at least 1 value
    top_n = series.nlargest(n)
    return round(top_n.mean(), 2)


def peer_average(series):
    return round(series.mean(), 2)


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


def input_parameters():
    performance_month = (
        input("Enter performance month [default=2025-01-01]:") or "2025-01-01"
    )
    performance_date = datetime.strptime(performance_month, "%Y-%m-%d")

    organizations = list(
        range(1, int(input("Enter number of organizations [default=120]:") or 119) + 1)
    )
    num_months = int(input("Enter number of month [default=12]:") or 12)

    return performance_month, performance_date, organizations, num_months


message_template = {
    "@context": {
        "dcterms": "http://purl.org/dc/terms/",
        "schema": "http://schema.org/",
        "scaffold": "http://displaylab.com/scaffold#",
        "psdo": "http://purl.obolibrary.org/obo/",
        "slowmo": "http://example.com/slowmo#",
        "message_template": {"@id": "psdo:PSDO_0000002"},
        "measure": {"@id": "psdo:PSDO_0000102"},
        "performance_summary_document": {"@id": "psdo:PSDO_0000098"},
        "performance_month": {"@id": "scaffold:performance_month"},
        "History": {"@id": "scaffold:History"},
        "Preferences": {"@id": "scaffold:Preferences"},
        "performance_measure_report": {"@id": "psdo:PSDO_0000107"},
        "comparator_measure_report": {"@id": "scaffold:comparator_measure_report"},
        "PractitionerRole": {"@id": "scaffold:PractitionerRole"},
        "subject": {"@id": "scaffold:subject"},
        "PractitionerRole.identifier": {"@id": "scaffold:PractitionerRole.identifier"},
        "PractitionerRole.practitioner": {
            "@id": "scaffold:PractitionerRole.practitioner"
        },
        "PractitionerRole.organization": {
            "@id": "scaffold:PractitionerRole.organization"
        },
        "PractitionerRole.code": {"@id": "scaffold:PractitionerRole.code"},
        "identifier": {"@id": "scaffold:identifier"},
        "period.start": {"@id": "scaffold:period.start"},
        "period.end": {"@id": "scaffold:period.end"},
        "measureScore.rate": {"@id": "scaffold:measureScore.rate"},
        "measureScore.denominator": {"@id": "scaffold:measureScore.denominator"},
        "measureScore.range": {"@id": "scaffold:measureScore.range"},
        "group.subject": {"@id": "scaffold:group.subject"},
        "group.code": {"@id": "scaffold:group.code"},
        "message_template_name": {"@id": "scaffold:message_template_name"},
        "message_generated_datetime": {"@id": "scaffold:message_generated_datetime:"},
        "acceptable_by": {"@id": "scaffold:acceptable_by"},
        "Utilities": {"@id": "scaffold:Utilities"},
        "Message_Format": {"@id": "scaffold:Message_Format"},
        "Display_Format": {"@id": "scaffold:Display_Format"},
        "Social gain": {"@id": "scaffold:Social_gain"},
        "Worsening": {"@id": "scaffold:Worsening"},
        "Bar chart": {"@id": "scaffold:Bar_chart"},
        "Line chart": {"@id": "scaffold:Line_chart"},
    },
    "@id": "",
    "performance_month": "2025-01-01",
    "@type": "performance_summary_document",
    "subject": "",
    "PractitionerRole": [],
    "performance_measure_report": [],
    "comparator_measure_report": [],
    "History": [],
    "Preferences": {},
}

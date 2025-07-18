import json
import random
import uuid
from datetime import datetime
from pathlib import Path

from dateutil.relativedelta import relativedelta

# Variables
performance_month = "2025-01-01"
performance_date = datetime.strptime(performance_month, "%Y-%m-%d")
measures = [
    "BP01",
    "BP02",
    "BP03",
    "BP04",
    "BP05",
    "BP06",
    "GLU01",
    "GLU02",
    "GLU03",
    "GLU04",
    "GLU05",
    "NMB01",
    "NMB02",
    "NMB03",
    "PAIN01",
    "PAIN02",
    "PONV01",
    "PONV04",
    "PONV05",
    "PUL01",
    "PUL02",
    "PUL03",
    "SMOK01",
    "SMOK02",
    "SMOK03",
    "SUS01",
    "SUS02",
    "SUS03",
    "SUS04",
    "SUS05",
    "TEMP01",
    "TEMP02",
    "TEMP03",
    "TOC01",
    "TOC02",
    "TOC03",
    "TRAN01",
]
institutions = list(range(1, 51))
num_months = 12
months = [
    (performance_date - relativedelta(months=i)).strftime("%Y-%m-%d")
    for i in reversed(range(0, num_months ))
]

# Output directory
output_dir = Path("random_performance_data")
output_dir.mkdir(exist_ok=True)

# generate comparator values


# Generate list of 6 months before performance_month


# Output dictionary
comparators = {}

for inst in institutions:
    comparators[inst] = {}
    for measure in measures:
        comparators[inst][measure] = {}
        for date in months:
            # Generate values with the correct constraints
            peer_average = round(random.uniform(55.0, 90.0), 1)
            peer_90th = round(random.uniform(90.1, 99.9), 1)
            peer_75th = round(random.uniform(peer_average + 0.1, peer_90th - 0.1), 1)

            # Safety check
            if peer_75th <= peer_average:
                peer_75th = round(peer_average + 0.5, 1)
            if peer_90th <= peer_75th:
                peer_90th = round(peer_75th + 0.5, 1)

            comparators[inst][measure][date] = {
                "peer_average_comparator": peer_average,
                "peer_75th_percentile_benchmark": peer_75th,
                "peer_90th_percentile_benchmark": peer_90th,
                "MPOG_goal": 90.0,
            }


# Counter to ensure global uniqueness
global_staff_counter = 1

for institution in institutions:
    num_staff = random.randint(5, 25)
    for staff_number in range(num_staff):
        staff_data = {
            "@context": {
                "@vocab": "http://schema.org/",
                "slowmo": "http://example.com/slowmo#",
                "csvw": "http://www.w3.org/ns/csvw#",
                "dc": "http://purl.org/dc/terms/",
                "psdo": "http://purl.obolibrary.org/obo/",
                "slowmo:Measure": "http://example.com/slowmo#Measure",
                "slowmo:IsAboutPerformer": "http://example.com/slowmo#IsAboutPerformer",
                "slowmo:ColumnUse": "http://example.com/slowmo#ColumnUse",
                "slowmo:IsAboutTemplate": "http://example.com/slowmo#IsAboutTemplate",
                "slowmo:spek": "http://example.com/slowmo#spek",
                "slowmo:IsAboutCausalPathway": "http://example.com/slowmo#IsAboutCausalPathway",
                "slowmo:IsAboutOrganization": "http://example.com/slowmo#IsAboutOrganization",
                "slowmo:IsAboutMeasure": "http://example.com/slowmo#IsAboutMeasure",
                "slowmo:InputTable": "http://example.com/slowmo#InputTable",
                "slowmo:WithComparator": "http://example.com/slowmo#WithComparator",
                "has_part": "http://purl.obolibrary.org/obo/bfo#BFO_0000051",
                "has_disposition": "http://purl.obolibrary.org/obo/RO_0000091",
            },
            "message_instance_id": f"{str(uuid.uuid4())}",
            "performance_month": performance_month,
            "staff_number": f"STAFF-{global_staff_counter:06}",  # e.g., STAFF-000001
            "institution_id": institution,
            "Performance_data": [
                [
                    "staff_number",
                    "measure",
                    "month",
                    "passed_count",
                    "flagged_count",
                    "denominator",
                    "peer_average_comparator",
                    "peer_75th_percentile_benchmark",
                    "peer_90th_percentile_benchmark",
                    "MPOG_goal",
                ],
            ],
            "History": {},
            "Preferences": {},
            "debug": "no",
        }

        for measure in comparators[institution]:
            for month in comparators[institution][measure]:
                # Get comparator values
                comparator_values = comparators[institution][measure][month]

                # Random denominator, passed ≥ 1
                denominator = random.randint(1, 40)
                passed_count = random.randint(1, denominator)
                flagged_count = denominator - passed_count

                # Build row
                row = [
                    staff_number,
                    measure,
                    month,
                    passed_count,
                    flagged_count,
                    denominator,
                    comparator_values["peer_average_comparator"],
                    comparator_values["peer_75th_percentile_benchmark"],
                    comparator_values["peer_90th_percentile_benchmark"],
                    comparator_values["MPOG_goal"],
                ]
                staff_data["Performance_data"].append(row)

        file_name = f"Provider_{global_staff_counter}.json"
        file_path = output_dir / file_name

        # Write JSON file
        with open(file_path, "w") as f:
            json.dump(staff_data, f, indent=2)

        global_staff_counter += 1

import json
import os

import pandas as pd
import uuid
import copy
from datetime import datetime
from dateutil.relativedelta import relativedelta

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "outputs")
INPUT_DIR = os.environ.get("INPUT_DIR", "/home/faridsei/dev/test/OBI/obi_cat2_dystocia_compliance.xlsx")
PERFORMANCE_MONTH = os.environ.get("PERFORMANCE_MONTH", None)
QUARTERLY_DATA=os.environ.get("QUARTERLY_DATA", False)
INPUT_TEMPLATE = {
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
    "has_disposition": "http://purl.obolibrary.org/obo/RO_0000091"
  },
  "message_instance_id": "",
  "performance_month":  "",
  "Performance_data": [
    [ "staff_number", "measure", "month", "passed_count", "flagged_count", "denominator", "peer_average_comparator", "peer_75th_percentile_benchmark", "peer_90th_percentile_benchmark", "MPOG_goal" ],
 
  ],
  "History": {
    
  },
  "Preferences": {}
}

measure_name_to_id={
    "Cat II Compliance - 12 month rolling average": "CATII12",
    "Cat II Compliance - Monthly": "CATII",
    "Dystocia Compliance - 12 month rolling average": "DC12",
    "Dystocia Compliance - Monthly": "DC"
    
}

sheet_name = "obi_cat2_dystocia_compliance" #"Sheet1"  # Change this to the name of the sheet in your .xlsx file
df = pd.read_excel(INPUT_DIR, sheet_name=sheet_name, engine="openpyxl")
df['Time interval'] = pd.to_datetime(df['Time interval']).dt.strftime('%Y-%m-%d')

unique_site_ids = df['site_id'].unique()
if not PERFORMANCE_MONTH:
  PERFORMANCE_MONTH = df['Time interval'].max()
site_id= None
for site_id in unique_site_ids:
    site_rows = df[df['site_id'] == site_id]
    input_file = copy.deepcopy(INPUT_TEMPLATE)
    measure = ""
    Numerator = 0
    Denominator = 0 
    for _, row in site_rows.iterrows():
        Numerator += row["Numerator"]
        Denominator += row["Denominator"]
        time_interval = row["Time interval"]
        if QUARTERLY_DATA:
          
          date1 = datetime.strptime(row["Time interval"], '%Y-%m-%d')
          date2 = datetime.strptime(PERFORMANCE_MONTH, '%Y-%m-%d')  
          year_diff = date2.year - date1.year
          month_diff = date2.month - date1.month

          # Total months difference
          total_months = year_diff * 12 + month_diff

          # Check if the difference is a multiple of 4 then just continue to the next row (added up the Numerators and Denominators and checked the measure to be the same)
          if total_months % 3 != 0:
            
            #make sure the quarter data is for the same measure
            if measure == "":
              measure = measure_name_to_id[row["Performance measure name"]]
            if measure != measure_name_to_id[row["Performance measure name"]]:
              raise ValueError("Sorry, wrong quarterly data issue for site "+ site_id + "meassure "+ measure + "date "+ row["Time interval"]) 
            continue            
          time_interval = (date2 - relativedelta(months=total_months / 3)).strftime('%Y-%m-%d')
        # if not row["Performance level (monthly rate)"]:
        #   continue
        # Format the row and write it to the file
        input_file["Performance_data"].append([int(site_id),measure_name_to_id[row["Performance measure name"]],time_interval,
                                               Numerator,Denominator-Numerator,Denominator,0,0,0,row["Target"]*100  ])
        input_file["message_instance_id"] = str(uuid.uuid4())
        input_file["performance_month"] = PERFORMANCE_MONTH
        
        measure =""
        Numerator = 0
        Denominator = 0

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file_name = f"Provider_{site_id}.json"
    file_path = os.path.join(OUTPUT_DIR, output_file_name)
    with open(file_path, "w") as file:
        json.dump(input_file, file, indent=4)


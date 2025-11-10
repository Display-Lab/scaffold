# SCAFFOLD [Data Ingestion Model](https://docs.google.com/spreadsheets/d/1qDjS2-a7F1El53jUx0fippL3m28pQilLcYNAv4pQkxI/edit?gid=1258033503#gid=1258033503)
We adopted several [FHIR standard](https://hl7.org/fhir/index.html)'s resources to model performance data ingestion for SCAFFOLD. The performance input data include:
- Provider information 
- Performance data
- Comparator data

SCAFFOLD can also input the `Message history` and `Preferences` which are optional and can be for prioritization of candidate messages.

The data was structured using FHIR resources to the extent possible. Since no suitable resources exist for history and preferences, those were represented using our own format.

## Performance Data Structure
### Provider information (`PractitionerRole`)
The [`PractitionerRole`](https://build.fhir.org/practitionerrole.html) resource is used to represent message recipients(individuals or organizations), their relationships and their roles. The input data include a table (PractitionerRole.csv) with the following columns:
- **[PractitionerRole.identifier](https://build.fhir.org/practitionerrole-definitions.html#PractitionerRole.identifier)**: Unique identifier for each row in the Practitiner table. This identifier links performance data, history and preferences to each recipient. In those datasets, PractitionerRole.identifier is referred to as subject.
- **[PractitionerRole.practitioner](https://build.fhir.org/practitionerrole-definitions.html#PractitionerRole.practitioner)**: Contains the practitioner identifier. If this column has a value, the row represents an individual practitioner otherwise it is aggregate data for a group for example a hospital.
- **[PractitionerRole.organization](https://build.fhir.org/practitionerrole-definitions.html#PractitionerRole.organization)**: Contains the identifier of the institution where the recipient serves. This field, together with `PractitionerRole.code` is used to identify the comparator data associated with each recipient. 

- **[PractitionerRole.code](https://build.fhir.org/practitionerrole-definitions.html#PractitionerRole.code)**: Contains the role of the recipient in the institution. Example values for this field could be `Resident`, `Attending` or `CRNA`.
- **type**: Indicates whether the performance data belong to an individual provider or to a group of providers. Accordingly, a `PractitionerRole` may represent either a single provider or a group. This field is not part of the FHIR `PractitionerRole` resource; in our model, it is introduced to classify `PractitionerRole` as either individual or group, allowing us to distinguish between the two types of performance data. Example values include `Practitioner` and `Organization`.
  
### Performance data (`MeasureReport`)
Performance data are modeled using the [`MeasureReport`](https://build.fhir.org/measurereport.html) resource, which represents the results of a measure evaluation. In SCAFFOLD, each row of performance data is modeled as a measure report. Accordingly, the input data include a table (PerformanceMeasureReport.csv) with the following columns:
- **[identifier](https://build.fhir.org/measurereport-definitions.html#MeasureReport.identifier)**: Uniquely identifies a specific performance data record.
- **[measure](https://build.fhir.org/measurereport-definitions.html#MeasureReport.measure)**: 	
A reference to the measure with which the performance record is associated.
- **[subject](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.subject)**: Contains the recipient's unique identifier.
- **[period.start](https://hl7.org/fhir/datatypes-definitions.html#Period.start)**: The start date of the period for which the performance record was collected.
- **[period.end](https://hl7.org/fhir/datatypes-definitions.html#Period.end)**: The end date of the period for which the performance record was collected.
- **[measureScore](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.group.measureScore_x_).rate**: The calculated success rate for the performance record.
- **[measureScore](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.group.measureScore_x_).denominator**: The total number of cases on which the performance record is based.
- **[measureScore](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.group.measureScore_x_).range**: Used for categorical values.

### Comparator data (`MeasureReport`):
Comparator data , which represent aggregated performance for a selected group of recipients, are modeled using the [`MeasureReport`](https://build.fhir.org/measurereport.html) resource. In SCAFFOLD, each row of comparator data is modeled as a measure report. Accordingly, the input data include a table (ComparatorMeasureReport.csv) with the following columns:
- **[identifier](https://build.fhir.org/measurereport-definitions.html#MeasureReport.identifier)**: Uniquely identifies a specific comparator data record.
- **[measure](https://build.fhir.org/measurereport-definitions.html#MeasureReport.measure)**: A reference to the measure with which the comparator record is associated.
- **[group.subject](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.subject)**: The identifier of the organization for which the comparator record is calculated. This column is equivalent to the `PractitionerRole.organization` column in the Provider Information data set.
- **[period.start](https://hl7.org/fhir/datatypes-definitions.html#Period.start)**: The start date of the period for which the comparator record was collected.
- **[period.end](https://hl7.org/fhir/datatypes-definitions.html#Period.end)**: The end date of the period for which the comparator record was collected.
- **[measureScore](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.group.measureScore_x_).rate**: The average calculated success rate for the performance records of the selected group of providers.
- **[measureScore](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.group.measureScore_x_).denominator**: The total number of cases on which the comparator record is based.
- **[group.code](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.group.code)**: Specifies the type of comparator represented in each comparator record. Example values for this field include `peer average`, `Peer Top 10%` or `Goal Value`. 
- **[PractitionerRole.code](https://build.fhir.org/practitionerrole-definitions.html#PractitionerRole.code)**: Indicates the role of the providers for whom the comparator record is calculated. Example values for this field include `Resident`, `Attending` or `CRNA`.

## Prioritization Data Structure

### Message history
Message history captures previously generated messages over defined time periods. SCAFFOLD's input data include a table (MessageHistory.csv) with the following columns:
- **subject**: The provider (practitioner) identifier, to whom the message history record belongs.
- **period.start**: The start date of the period for which the message was created.
- **period.end**: The end date of the period for which the message was created.	
- **history.json**: A JSON dictionary summarizing the generated message, with the following keys:
    - **message_template**: The identifier of the message template used to generate the message.
    - **message_template_name**: The name of the message template used to generate the message.
    - **message_generated_datetime**: The date and time the message was generated.
    - **measure**: The measure associated with the generated message.
    - **acceptable_by**: The causal pathway associated with the generated message.

### Preference
Preferences captures providers' choices, priorities, and settings for messages that are generated for them. SCAFFOLD's input data include a table (Preferences.csv) with the following columns:
- **subject**: The provider (practitioner) identifier, to whom the preferences record belongs.
- **preferences.json**: A JSON dictionary with preferences detail. Here is an example of preferences JSON which SCAFFOLD can currently use 
    ```json
    {
        "Utilities": {
            "Message_Format": {  
                "Social gain": "0.04", 
                "Social stayed better":"-0.08",
                "Worsening": "-0.1",  
                "Improving": "-0.11", 
                "Social loss": "0.69", 
                "Social stayed worse": "-0.54", 
                "Social better": "-1.23",
                "Social worse": "0.54", 
                "Social approach": "1.0",
                "Goal gain": "0.07", 
                "Goal approach": "1.1"
            }, 
            "Display_Format": {
                "Bar chart": 1, 
                "Line chart": 0, 
                "Text-only": 0, 
                "System-generated": 0
            }
        }
    }
    ```
## Data Generator 

### Generate Tabular data
First, create a folder for new data (i.e. `new_data`).
If the data is going to be generated for individual recipients, create a config.json inside the new data folder containing
```json
{
    "ComparatorMergeColumns":["group.subject", "PractitionerRole.code"]
}
```

for hospital level data use
```json
{
    "ComparatorMergeColumns":["PractitionerRole.code"]
}
```

Now you can run the scripts sequentially to generate data.

For example to generate hospital level data for 100 hospitals run the following commands:

```zsh
python data\ ingestion\ model/sandbox\ generator/PractitionerRole_hospital_level.py --num_orgs 100 --path new_data

python data\ ingestion\ model/sandbox\ generator/PerformanceMeasureReport.py --path new_data   

python data\ ingestion\ model/sandbox\ generator/ComparatorMeasureReport.py --path new_data

python data\ ingestion\ model/sandbox\ generator/Preference.py --path new_data 

ENV_PATH=/Path/to/your/environment/file/dev.env python data\ ingestion\ model/sandbox\ generator/MessageHistory.py --path new_data
```

This will start by creating the list of hospitals in PractitionerRole.csv file. Then will generate performance data in PerformanceMeasureReports.csv. Next step will create the comparator data in ComparatorMeasureReport.csv. Then the preferences will be added to preferences.csv. Final step will use SCAFFOLD to generate the history of messages generated by pipeline for the months before the performance month.

This process will start by creating a list of hospitals in the `PractitionerRole.csv` file. Next, performance data will be generated in `PerformanceMeasureReports.csv`. The following step will create comparator data in `ComparatorMeasureReport.csv`. Preferences will then be added to `preferences.csv`. Finally, SCAFFOLD will be used to generate the history of messages produced by the pipeline for the months preceding the performance month and store it in `MessageHistory.csv`.

### Convert Data To JSON-LD Inputs
You can use the script in TabularToJson.py to convert data in tabular format to json-ld input files. Use the following to run this script on a path where the tabular data with all the required files that follow the SCAFFOLD data ingestion model exists to generate json-ld inputs files

```
python data\ ingestion\ model/sandbox\ generator/TabularToJSON.py --path new_data --performance_month 2025-01-01
```

## Example Data
Sandbox hospital-level example data is generated for 100 hospitals and included in the sandbox examples folder. This folder includes both tabular data and json-ld input files for same hospitals. 


### Tabular data
Tabular input data includes:

#### Performance Data
- PractitionerRole.csv, which contains hospital definitions
- PerformanceMeaasureReport, which contains performance data for each hospital on 12 defined measures in sandbox knowledge base for 12 month.
- config.json, which is required to find the right comparator for each recipient
- ComparatorMeasureReport.csv, which contains the comparator data based on the entire network for each measure, for each month.

#### Prioritization Data
- Preferences.csv, which includes preferences for a small subgroup of recipients.
- MessageHistory.csv, which includes history of generated messages for 11 month before the performance month.

### JSON-LD Input files
The `JSON Messages` folder contains json-ld input files for the same data. Each file is created using the following template. See examples for more detail.

```json
{
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
    },
    "message_instance_id": "",
    "performance_month": "2025-01-01",
    "@type": "psdo:performance_summary_document",
    "subject": "",
    "PractitionerRole": [
        [
            "PractitionerRole.identifier",
            "PractitionerRole.practitioner",
            "PractitionerRole.organization",
            "PractitionerRole.code",
        ],
    ],
    "performance_measure_report": [
        [
            "identifier",
            "measure",
            "subject",
            "period.start",
            "period.end",
            "measureScore.rate",
            "measureScore.denominator",
            "measureScore.range",
        ],
    ],
    "comparator_measure_report": [
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
        ],
    ],
    "History": [],
    "Preferences": {},
}
```

## Run SCAFFOLD
To run SCAFFOLD on sandbox data you need to prepare the environment and install SCAFFOLD. For more detail, follow the `Quick start` section of the [main SCAFFOLD documentation page](../README.md). You can process JSON input files using `Run SCAFFOLD API` or `Run SCAFFOLD CLI with JSON inputs` sections. Use `Run SCAFFOLD CLI with CSV inputs` section to process tabular data.

## Expected Output
Here is an example of the output from SCAFFOLD after processing the sandbox example data:

Successful: 100, Failed: 0

| causal_pathway   | count | %    |
|-----------------|-------|------|
| Goal Approach    | 11    | 11.0 |
| Goal Gain        | 3     | 3.0  |
| Goal Loss        | 7     | 7.0  |
| Goal Worse       | 1     | 1.0  |
| Improving        | 14    | 14.0 |
| Social Approach  | 18    | 18.0 |
| Social Better    | 1     | 1.0  |
| Social Gain      | 6     | 6.0  |
| Social Loss      | 13    | 13.0 |
| Social Worse     | 16    | 16.0 |
| Worsening        | 10    | 10.0 |


| causal_pathway   | acceptable | % acceptable | acceptable_score | selected | % selected | selected_score | % of acceptable selected |
|-----------------|------------|--------------|-----------------|----------|------------|----------------|---------------------------|
| Goal Approach    | 36         | 1.0          | 2.78            | 11       | 11.0       | 2.90           | 30.6                      |
| Goal Gain        | 53         | 1.4          | 2.43            | 3        | 3.0        | 2.78           | 5.7                       |
| Goal Loss        | 129        | 3.5          | 2.32            | 7        | 7.0        | 2.89           | 5.4                       |
| Goal Worse       | 563        | 15.2         | 2.19            | 1        | 1.0        | 2.89           | 0.2                       |
| Improving        | 159        | 4.3          | 2.69            | 14       | 14.0       | 2.88           | 8.8                       |
| Social Approach  | 104        | 2.8          | 2.77            | 18       | 18.0       | 2.86           | 17.3                      |
| Social Better    | 352        | 9.5          | 2.30            | 1        | 1.0        | 2.65           | 0.3                       |
| Social Gain      | 137        | 3.7          | 2.41            | 6        | 6.0        | 2.94           | 4.4                       |
| Social Loss      | 229        | 6.2          | 2.37            | 13       | 13.0       | 2.93           | 5.7                       |
| Social Worse     | 1696       | 45.8         | 2.18            | 16       | 16.0       | 2.81           | 0.9                       |
| Worsening        | 246        | 6.6          | 2.63            | 10       | 10.0       | 2.83           | 4.1                       |


| message                                | acceptable | % acceptable | acceptable_score | selected | % selected | selected_score | % of acceptable selected |
|----------------------------------------|------------|--------------|-----------------|----------|------------|----------------|---------------------------|
| Achieved Peer Average                   | 61         | 1.6          | 2.38            | 1        | 1.0        | 2.78           | 1.6                       |
| Achieved Top 10 Peer Benchmark          | 76         | 2.1          | 2.42            | 5        | 5.0        | 2.98           | 6.6                       |
| Approach Goal                           | 36         | 1.0          | 2.78            | 11       | 11.0       | 2.90           | 30.6                      |
| Approach Peer Average                    | 21         | 0.6          | 2.76            | 0        | 0.0        | NaN            | 0.0                       |
| Approach Top 10 Peer Benchmark          | 83         | 2.2          | 2.77            | 18       | 18.0       | 2.86           | 21.7                      |
| Drop Below Goal                          | 129        | 3.5          | 2.32            | 7        | 7.0        | 2.89           | 5.4                       |
| Drop Below Peer Average                  | 136        | 3.7          | 2.34            | 4        | 4.0        | 2.94           | 2.9                       |
| Getting Worse                            | 246        | 6.6          | 2.63            | 10       | 10.0       | 2.83           | 4.1                       |
| No Longer Top Performer                  | 93         | 2.5          | 2.51            | 9        | 9.0        | 2.93           | 9.7                       |
| Not Top Performer                        | 848        | 22.9         | 2.18            | 7        | 7.0        | 2.76           | 0.8                       |
| Opportunity to Improve Goal              | 563        | 15.2         | 2.19            | 1        | 1.0        | 2.89           | 0.2                       |
| Opportunity to Improve Top 10 Peer Benchmark | 848   | 22.9         | 2.18            | 9        | 9.0        | 2.84           | 1.1                       |
| Performance Improving                    | 159        | 4.3          | 2.69            | 14       | 14.0       | 2.88           | 8.8                       |
| Reached Goal                             | 53         | 1.4          | 2.43            | 3        | 3.0        | 2.78           | 5.7                       |
| Top Performer                            | 352        | 9.5          | 2.30            | 1        | 1.0        | 2.65           | 0.3                       |


| measure               | acceptable | % acceptable | acceptable_score | selected | % selected | selected_score | % of acceptable selected |
|------------------------|-------------|---------------|------------------|-----------|-------------|----------------|---------------------------|
| Care-Rating-01         | 338         | 9.1           | 2.33             | 8         | 8.0         | 2.84           | 2.4                       |
| Clean-Rating-01        | 330         | 8.9           | 2.26             | 12        | 12.0        | 2.88           | 3.6                       |
| Discharge-01           | 299         | 8.1           | 2.25             | 10        | 10.0        | 2.85           | 3.3                       |
| Hand-01                | 287         | 7.7           | 2.34             | 5         | 5.0         | 2.88           | 1.7                       |
| Nurse-informed-01      | 270         | 7.3           | 2.33             | 6         | 6.0         | 2.86           | 2.2                       |
| Nurse-language-01      | 286         | 7.7           | 2.37             | 11        | 11.0        | 2.82           | 3.8                       |
| Patient-Concern-01     | 288         | 7.8           | 2.34             | 3         | 3.0         | 2.94           | 1.0                       |
| Physician-informed-01  | 295         | 8.0           | 2.23             | 9         | 9.0         | 2.85           | 3.1                       |
| Physician-language-01  | 299         | 8.1           | 2.28             | 5         | 5.0         | 2.92           | 1.7                       |
| Provider-Rating-01     | 264         | 7.1           | 2.31             | 6         | 6.0         | 2.87           | 2.3                       |
| Quiet-Rating-01        | 361         | 9.7           | 2.25             | 12        | 12.0        | 2.84           | 3.3                       |
| Transfer-01            | 387         | 10.4          | 2.22             | 13        | 13.0        | 2.92           | 3.4                       |

SCAFFOLD also creates a `messages` folder, which contains a summary of the generated candidates (`candidates.csv`) and a detailed JSON file for each generated message. Each JSON file includes information about the selected message, all created candidates with their scoring details, and any generated images.

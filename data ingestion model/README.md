# SCAFFOLD [Data Ingestion Model](https://docs.google.com/spreadsheets/d/1qDjS2-a7F1El53jUx0fippL3m28pQilLcYNAv4pQkxI/edit?gid=1258033503#gid=1258033503)
We adopted several [FHIR standard](https://hl7.org/fhir/index.html)'s resources to model data ingestion for SCAFFOLD. The input data include:
- Provider information 
- Performance data
- Comparator data
- Message history
- Preference

The data was structured using FHIR resources to the extent possible. Since no suitable resources exist for history and preferences, those were represented using our own format.

## Provider information (`PractitionerRole`)
The [`PractitionerRole`](https://build.fhir.org/practitionerrole.html) resource is used to represent providers, their relationship to organizations, and their roles. The input data include a table (PractitionerRole.csv) with the following columns:
- **[PractitionerRole.practitioner](https://build.fhir.org/practitionerrole-definitions.html#PractitionerRole.practitioner)**: Contains the provider (practitioner) identifier. This identifier links performance data, history and preferences to each provider. In those datasets, PractitionerRole.practitioner is refered to as subject.
- **[PractitionerRole.organization](https://build.fhir.org/practitionerrole-definitions.html#PractitionerRole.organization)**: Contains the identifier of the institution where the provider serves. This field, together with `PractitionerRole.code` is used to identify the comparator data associated with each provider. 

- **[PractitionerRole.code](https://build.fhir.org/practitionerrole-definitions.html#PractitionerRole.code)**: Contains the role of the provider in the institution. Example values for this field include `Resident`, `Attending` or `CRNA`.
- **type**: Indicates whether the performance data belong to an individual provider or to a group of providers. Accordingly, a `PractitionerRole` may represent either a single provider or a group. This field is not part of the FHIR `PractitionerRole` resource; in our model, it is introduced to classify `PractitionerRole` as either individual or group, allowing us to distinguish between the two types of performance data. Example values include `Practitioner` and `Organization`.
  
## Performance data (`MeasureReport`)
Performance data are modeled using the [`MeasureReport`](https://build.fhir.org/measurereport.html) resource, which represents the results of a measure evaluation. In SCAFFOLD, each row of performance data is modled as a measure report. Accordingly, the input data include a table (PerformanceMeasureReport.csv) with the following columns:
- **[identifier](https://build.fhir.org/measurereport-definitions.html#MeasureReport.identifier)**: Uniquely identifies a specific performance data record.
- **[measure](https://build.fhir.org/measurereport-definitions.html#MeasureReport.measure)**: 	
A reference to the measure with which the performance record is associated.
- **[subject](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.subject)**: Contains the provider (practitioner) identifier.
- **[period.start](https://hl7.org/fhir/datatypes-definitions.html#Period.start)**: The start date of the period for which the performance record was collected.
- **[period.end](https://hl7.org/fhir/datatypes-definitions.html#Period.end)**: The end date of the period for which the performance record was collected.
- **[measureScore](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.group.measureScore_x_).rate**: The calculated success rate for the performance record.
- **[measureScore](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.group.measureScore_x_).denominator**: The total number of cases on which the performance record is based.
- **[measureScore](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.group.measureScore_x_).range**: Used for categorical values.
## Comparator data (`MeasureReport`):
Comparator data , representing aggregated performance for a selected group of providers, are modeled using the [`MeasureReport`](https://build.fhir.org/measurereport.html) resource, which captures the results of a measure evaluation for either an individual or a group. In SCAFFOLD, each row of comparator data is modeled as a measure report. Accordingly, the input data include a table (ComparatorMeasureReport.csv) with the following columns:
- **[identifier](https://build.fhir.org/measurereport-definitions.html#MeasureReport.identifier)**: Uniquely identifies a specific comparator data record.
- **[measure](https://build.fhir.org/measurereport-definitions.html#MeasureReport.measure)**: A reference to the measure with which the comparator record is associated.
- **[subject](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.subject)**: The identifier of the institution for which the comparator record is calculated. This column is equivalent to the `PractitionerRole.organization` column in the Provider Information data set.
- **[period.start](https://hl7.org/fhir/datatypes-definitions.html#Period.start)**: The start date of the period for which the comparator record was collected.
- **[period.end](https://hl7.org/fhir/datatypes-definitions.html#Period.end)**: The end date of the period for which the comparator record was collected.
- **[measureScore](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.group.measureScore_x_).rate**: The average calculated success rate for the performance records of the selected group of providers.
- **[group.code](https://hl7.org/fhir/measurereport-definitions.html#MeasureReport.group.code)**: Specifies the type of comparator represented in each comparator record. Example values for this field include `peer average`, `Peer Top 10%` or `Goal Value`. 
- **[PractitionerRole.code](https://build.fhir.org/practitionerrole-definitions.html#PractitionerRole.code)**: Indicates the role of the providers for whom the comparator record is calculated. Example values for this field include `Resident`, `Attending` or `CRNA`.

## Message history
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

## Preference
Preferences captures providers' choices, priorities, and settings for messages that are generated for them. SCAFFOLD's input data include a table (Preferences.csv) with the following columns:
- **subject**: The provider (practitioner) identifier, to whom the preferences record belongs.
- **preferences.json**: A JSON dictionary with preferences detail. Here is an example of preferences JSON which SCAFFOLD can currently use 
    ```json
    {
        'Utilities': {
            'Message_Format': {  
                'Social gain': '0.04', 
                'Social stayed better':'-0.08',
                'Worsening': '-0.1',  
                'Improving': '-0.11', 
                'Social loss': '0.69', 
                'Social stayed worse': '-0.54', 
                'Social better': '-1.23',
                'Social worse': '0.54', 
                'Social approach': '1.0',
                'Goal gain': '0.07', 
                'Goal approach': '1.1'
            }, 
            'Display_Format': {
                'Bar chart': 1, 
                'Line chart': 0, 
                'Text-only': 0, 
                'System-generated': 0
            }
        }
    }
    ```


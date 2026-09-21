# SCAFFOLD

![](https://img.shields.io/badge/stable_version-v2.1-blue)

SCAFFOLD (Scalable Coaching and Appreciation Feedback For Optimal Learning and Decision-making) is a precision feedback system for healthcare organizations that can enhance feedback reports, emails, and dashboards with coaching and appreciation messages and visualizations. 

Some examples of messages SCAFFOLD can generate are "You reached the top performer benchmark", “You are not a top performer”, “You may have an opportunity to improve”, “Your team reached the goal”, and “Congratulations on the exceptionally high quality of care your team has provided”.

SCAFFOLD is implemented as a software pipeline that processes performance data to produce messages, and requires a knowledge base containing a collection of feedback message templates and prioritization algorithms, among other things. The [Precision Feedback Knowledge Base](https://github.com/Display-Lab/knowledge-base) contains examples of messages and algorithms that can be downloaded and customized for use with SCAFFOLD.

## System Architecture

<img width="1913" height="667" alt="scaffold_architecture" src="https://github.com/user-attachments/assets/5051b7bc-caa4-46ee-ac0a-f295d109124b" />

## Quick start

This is a Python software project and running SCAFFOLD requires some familiarity with [Python](https://www.python.org/downloads/) and virtual environments. This quick start gives directions using python's built in virtual environment tool [venv](https://docs.python.org/3/library/venv.html) and [Poetry](https://python-poetry.org/).

### Clone SCAFFOLD

```zsh
git clone https://github.com/Display-Lab/scaffold.git

cd scaffold
```

#### Setup a virtual environment, install SCAFFOLD and its dependencies
**Using `venv` and `pip`**
Create a virtual environment using python
```zsh
python --version # make sure you have python 3.12
python -m venv .venv
```

Then activate it.
##### For Windows do this next to activate the virtual environment

```zsh
.venv\Scripts\activate.bat
```

##### For Mac or Linux do this next to activate the virtual environment

```zsh
source .venv/bin/activate
```

##### Now complete the following two installs

```zsh
pip install .\scaffold-sdk  #depending on your OS you may need to use pip install ./scaffold-sdk 
pip install . # this will install scaffold 
```

**Alternative: Using [uv](https://docs.astral.sh/uv/getting-started/installation/) (for developers)**

```zsh
uv venv
.venv\Scripts\activate.bat # Windows
source .venv/bin/activate # Mac / Linux 
uv pip install -e .
uv pip install -e ".[dev]" #to install dev dependencies
```

#### Setup a knowledge base for SCAFFOLD

If you are using a knowledge base from a separate repository, clone it in a separate location. For sandbox usecases the corresponding knowledge bases are located in each usecase folder in the sandbox.


#### Prepare environment file

Create a copy of the `.env.local` file available at the root of SCAFFOLD and call it `.env.dev` and update it by changing `path/to/knowledge-base` to point to the local knowledge base that you just checked out. (Don't remove the `file://` for default_preferences and manifest.)

```properties
# .env.dev
default_preferences=file:///Users/bob/knowledge-base/preferences.json 
mpm=/Users/bob/knowledge-base/prioritization_algorithms/motivational_potential_model.csv
manifest=file:///Users/bob/knowledge-base/mpog_local_manifest.yaml
...
```
#### Running SCAFFOLD
To test if the pipeline is installed and available to use execute the following command

```zsh
pipeline --help
```

You should see the following commands are available:
- batch
- batch-csv
- web

Alternatively you can exexute

```zsh
python -m scaffold.cli --help
```

##### Run SCAFFOLD API 
Run SCAFFOLD API using 
```zsh
ENV_PATH=/user/.../.env.dev pipeline web
```

Once the API is running, you can use Postman or your favorite tool to send a request and review the results. If you have set up the knowledge base for the Sandbox Hospital Quality Dashboard usecase, below is an example `curl` request that sends an input message to be processed by the API:

```zsh
curl --data "@sandbox/hospital quality dashboard usecase/data/JSON inputs/input_0b4f8851-6f95-44a0-a771-44959993ea4b.json" http://localhost:8000/createprecisionfeedback/
```
##### Run SCAFFOLD CLI with JSON inputs
Use the following command to run the pipeline's `batch` command on some or all json input files in a folder

```zsh
ENV_PATH=/user/.../.env.dev pipeline batch '/path/to/input/folder/' --max-files 500
```
Use --max-files if you need to limit the number of files to process.

If you need to run the pipeline on a specific json input file use 

```zsh
ENV_PATH=/user/.../.env.dev pipeline batch '/path/to/input/file.json'
```

To run SCAFFOLD on the Sandbox Hospital Quality Dashboard Usecas, use the following command from the root of SCAFFOLD

```zsh
ENV_PATH=/user/.../.env.dev pipeline  batch 'sandbox/hospital quality dashboard usecase/data/JSON inputs' --max-files 10
```

##### Run SCAFFOLD CLI with CSV inputs
Use the following command to run the pipeline `batch-csv` command 
```zsh
ENV_PATH=/user/.../.env.dev pipeline batch-csv '/path/to/performance/data/folder' --performance-month 2025-01-01 --max-files 100
```

Use --performance-month to set the performance month for batch_csv command and optional --max-files to limit the cases to process for development.

To run SCAFFOLD on the Sandbox Hospital Quality Dashboard Usecase, use the following command from the root of SCAFFOLD

```zsh
ENV_PATH=/user/.../.env.dev pipeline  batch-csv 'sandbox/hospital quality dashboard usecase/data/tabular inputs' --performance-month 2025-01-01 --max-files 10
```

## Developer SDK imports

SCAFFOLD now exposes reusable developer-facing base classes through the `scaffold_sdk` package namespace.

Example:

```python
from scaffold_sdk import Esteemer
```

The SDK is split into a standalone distribution named `scaffold-sdk` in the `scaffold-sdk/` folder.

For local development from this repository, install the SDK first:

```zsh
pip install -e ./scaffold-sdk
pip install -e .
```

## External Esteemer plugin guide

For a complete guide to creating and using an external `scaffold.esteemer` plugin, see [src/esteemer/README.md](src/esteemer/README.md).

## Environment variables

### Knowledge base settings

Local file path or URL (see .env.remote for github URL formats). All are required.

#### mpm: Path to the mpm csv file

#### config: Path to the configuration
For now this config file contains the esteemer plugin name and version in a yaml file with a content like:

plugins:
  scaffold.esteemer:
    name: mpm_candidate_selector
    version: "1.0.0"

This configuration file specifies which candidate selection algorithm (plugin) SCAFFOLD should use. We recommend including this file in the knowledge base so that the selected configuration is preserved across knowledge base releases.

#### default_preferences: Path to the default preferences json file

#### manifest: Path to the manifest file that includes differend pieces of the base graph including (causal pathways, message templates, measures and comparators). See [manifest configuration](#manifest-configuration) for more detail

### Flags

#### display_window: Maximum number of month to be used to create visual displays (plots)

- default: 6

#### generate_image: If set to true and the display type is bar chart or line chart, then SCAFFOLD will generate the images and include them as part of the response

- default: True

#### log_level: Sets the log level

- default: `WARNING` (this is the production default)
- note: SCAFFOLD must be run with **`log_level=INFO`** in order to generate the candidate records in the output.

#### performance_month: If set, SCAFFOLD will override the performance month in the input requests

- default: None

#### meas_period_type: Defines the type of periods whather it is monthly or weekly

- default: monthly
- note: monthly and weekly are supported

#### meas_period_length: Defines the length of periods for the input data

- default: 1
- note: for example for a data that is collected quarterly this needs to be set to 3 meas_period_type should be set to monthly. For weekly data it should be set to 1 while meas_period_type is weekly. 

#### min_count: Defines the minumum counts to consider a performance rate valid

- default: 10
- note: performance data for a measure with a count less than the min_count will be removed before processing

### Scoring

These control the elements of the scoring algorithm.

#### use_coachiness: Switch to turn on and off coachiness

- default: True

#### use_history: Switch to turn on and off history

- default: True

#### use_mi: Switch to turn on and off motivating information

- default: True

#### use_preferences: Switch to turn on and off preferences

- default: True

### manifest configuration

The manifest file includes all different pieces that should be loaded to the base graph including causal pathways, message templates, measures and comparators. It is a yaml file which specifies a directory structure containing JSON files for all those different categories.

Each entry consists of a ***key*** which is a URL (file:// or https:// or relative, see [Uniform Resource Identifier (URI)](https://datatracker.ietf.org/doc/html/rfc3986)) and a ***value*** which is a file path relative to the url. See manifest examples in the [knowledge base](https://github.com/Display-Lab/knowledge-base).

If the key is a relative path, it must end with a '/'. In that case the key is going to be resolved towards the location of the manifest file by SCAFFOLD.

### examples

```zsh
 ENV_PATH=/user/.../.env.dev log_level=INFO use_preferences=True use_coachiness=True use_mi=True generate_image=False uvicorn api:app --workers=5
```


for windows:
```psh
$env:ENV_PATH=/user/.../.env.dev; $env:log_level="INFO"; $env:use_preferences="True"; $env:use_coachiness="True"; $env:use_mi="True"; $env:generate_image="False"; uvicorn api:app --workers=5
```

> :point_right: `uvicorn` can be run with multiple workers. This is useful when testing with a client that can send multiple requests.

## FHIR-aligned output model

SCAFFOLD now returns a single FHIR `CommunicationRequest` as the primary output model for generated feedback messages.

### Why this model

We selected a `CommunicationRequest`-first output for the following reasons:

- Clear intent: The pipeline's core result is a communication artifact (message + optional attachments), which maps directly to `CommunicationRequest`.
- Better interoperability: FHIR-native consumers can ingest a standard resource without custom wrappers.
- Simpler client parsing: Clients no longer need to navigate bundle entries to find the selected message.
- Preserved explainability: SCAFFOLD-specific metadata is still included using FHIR `extension` fields.
- Backward-friendly analytics: Candidate records can still be attached when `log_level=INFO`.

### Output shape at a glance

The response is a JSON object with:

- `resourceType: CommunicationRequest`
- Core identity and context: `id`, `status`, `subject`, `authoredOn`
- Measure context: `about`
- Message content and artifacts: `payload`
- SCAFFOLD metadata and signals: `extension`
- Optional debugging/analysis rows: `candidates` (when enabled)

### Design choices and logic

1. Chosen message as first-class resource
The selected candidate is represented as a single `CommunicationRequest`, because each run produces one final message for one subject and measure. If we decide to select multiple candidates in the future, it would be straightforward to switch from a single `CommunicationRequest` to a collection bundle containint multiple `CommunicationRequest` resources.

2. Domain metadata via extensions
Template details and causal pathway information are represented as nested extensions under `https://umich.edu/scaffold/`.
This keeps domain-specific fields explicit while staying FHIR-compatible.

3. Motivating signals in typed FHIR extensions
Signals such as performance gap size, trend slope, and streak length are emitted as typed extension values (`valueDecimal`, `valueInteger`) for predictable downstream parsing.

4. Portable context in attachments
The current performance measure reports and selected comparator measure report are attached as base64-encoded CSV payload attachments so clients can display or audit the exact evidence used in message generation.

5. Optional visual payload
When image generation is enabled, the feedback chart is included as a PNG attachment in `payload`.

### How to read the response

For most clients, this sequence works well:

1. Verify `resourceType == "CommunicationRequest"`.
2. Read practitioner ID from `subject.reference` (for example, `Practitioner/<id>`).
3. Read human-readable message from the first `payload` item with `contentString`.
4. Read measure info from `about[0]` (`display`, `identifier.value`).
5. Read SCAFFOLD metadata from nested extensions under `url == "https://umich.edu/scaffold/"`:
   - `template_name`
   - `template_id`
   - `display`
   - `acceptable_by`
   - `selected_comparator` (if present)
6. Read motivating signals from top-level extensions by URL:
   - `...#PerformanceGapSize`
   - `...#PerformanceTrendSlope`
   - `...#StreakLength`
7. Read optional attachment payloads (`image/png`, `text/csv`) as needed.

### Minimal example

```json
{
  "resourceType": "CommunicationRequest",
  "id": "communication-request-52e46856-...-Physician-language-01",
  "status": "active",
  "subject": {
    "reference": "Practitioner/52e46856-9a80-41cf-a74d-8cddd753ec56"
  },
  "about": [
    {
      "identifier": {
        "system": "urn:ietf:rfc:3986",
        "value": "Physician-language-01"
      },
      "type": "Measure",
      "display": "Physician informed using clear language"
    }
  ],
  "payload": [
    {
      "contentString": "Your performance is approaching the peer average this month..."
    },
    {
      "contentAttachment": {
        "contentType": "image/png",
        "data": "<base64>"
      }
    }
  ],
  "extension": [
    {
      "url": "https://umich.edu/scaffold/",
      "extension": [
        {"url": "template_name", "valueString": "Approach Peer Average"},
        {"url": "acceptable_by", "valueString": "Social Approach"}
      ]
    },
    {
      "url": "http://example.com/slowmo#PerformanceGapSize",
      "valueDecimal": -0.031
    }
  ]
}
```

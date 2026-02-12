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

```zsh
python --version # make sure you have python 3.12
python -m venv .venv
```

##### For Windows do this next to activate the virtual environment

```zsh
.venv\Scripts\activate.bat
```

##### For Mac or Linux do this next to activate the virtual environment

```zsh
source .venv/bin/activate
```

##### For Windows, Mac, and Linux, now complete the following two installs

```zsh
pip install . # this will install scaffold 
```

**Alternative: Using [Poetry](https://python-poetry.org/) (for developers)**

```zsh
poetry env use 3.12 # optional, but makes sure you have python 3.12 available
poetry install # creates a virtual environment and install dependencies
poetry shell # activates the enviroment
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

## Environment variables

### Knowledge base settings

Local file path or URL (see .env.remote for github URL formats). All are required.

#### mpm: Path to the mpm csv file

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

#### meas_period: Defines the length of periods in month for the input data

- default: 1
- note: for example for a data that is collected quarterly this needs to be set to 3

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

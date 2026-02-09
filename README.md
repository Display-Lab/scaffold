# SCAFFOLD

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

#### Setup a virtual environment and install dependencies

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
pip install -r requirements.txt # this will take a while, so go get a cup of coffee
pip install uvicorn # not installed by default (needed for running locally)
```

**Alternative: Using [Poetry](https://python-poetry.org/) (for developers)**

```zsh
poetry env use 3.12 # optional, but makes sure you have python 3.12 available
poetry install # creates a virtual environment and install dependencies
poetry shell # activates the enviroment
```

#### Setup a knowledge base for SCAFFOLD

If you are using a knowledge base from a separate repository, clone it in a separate location. For sandbox usecases the corresponding knowledge bases are located in each usecase folder in the sandbox.


#### Running SCAFFOLD

Change back to the root of scaffold

```zsh
cd scaffold
```

Create a copy of the `.env.local` file and call it `.env.dev` and update it by changing `path/to/knowledge-base` to point to the local knowledge base that you just checked out. (Don't remove the `file://` for default_preferences and manifest.)

```properties
# .env.dev
default_preferences=file:///Users/bob/knowledge-base/preferences.json 
mpm=/Users/bob/knowledge-base/prioritization_algorithms/motivational_potential_model.csv
manifest=file:///Users/bob/knowledge-base/mpog_local_manifest.yaml
...
```

##### Run SCAFFOLD API 
There are two different ways to run SCAFFOLD API:
1. Run SCAFFOLD API using uvicorn 
```zsh
ENV_PATH=.env.dev uvicorn scaffold.api:app
# Expect to see a server start message like this "INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"
```

You can use Postman or your favorite tool to send a message and check the results. There is a sample input message file located at `tests/test_cases/input_message.json`. Here is a sample `curl` request:

```zsh
curl --data "@tests/test_cases/input_message.json" http://localhost:8000/createprecisionfeedback/
```
2. Run SCAFFOLD API using CLI (`pipeline web` command )

```zsh
ENV_PATH=/user/.../.env.dev pipeline web
```
##### Run SCAFFOLD CLI with JSON inputs
First install the python app. Then use the following command to run the pipeline on one json input file

```zsh
ENV_PATH=/user/.../.env.dev pipeline batch '/path/to/input/file.json'
```

Use the following command to run the pipeline on some or all json input files in a folder

```zsh
ENV_PATH=/user/.../.env.dev pipeline batch '/path/to/input/folder/' --max-files 500
```
Use --max-files if you need to limit the number of files to process.

##### Run SCAFFOLD CLI with CSV inputs
First install the python app. Then create the `.env.dev` file as mentioned above. 

```properties
# .env.dev
default_preferences=file:///Users/bob/knowledge-base/preferences.json 
mpm=/Users/bob/knowledge-base/prioritization_algorithms/motivational_potential_model.csv
manifest=file:///Users/bob/knowledge-base/mpog_local_manifest.yaml
...
```
Then use the following command, from the root of SCAFFOLD repository, to run the pipeline passing the path to the folder that contains csv files

```zsh
ENV_PATH=/user/.../.env.dev python -m scaffold.cli batch-csv '/path/to/performance/data/folder' --performance-month 2025-01-01 --max-files 500
```

You can use the path to the local [sandbox example data folder](for hospital quality dashboard usecase use ./sandbox/hospital%20quality%20dashboard%20usecase/data/tabular%20inputs) to run the pipeline on the sandbox example data. You need to use 2025-01-01 for performance month if you are using the hospital quality dashboard usecase from the sandbox.

Alternatively, you can use pip to install the pipeline command and use it to run the pipeline. Use the following command in the root of repository to install SCAFFOLD

```zsh
pip install .
```

Then you can use the following command to run the pipeline
```zsh
ENV_PATH=/user/.../.env.dev pipeline batch-csv '/path/to/performance/data/folder' --performance-month 2025-01-01 --max-files 500
```

Alternatively, if you have poetry installed, you can run 
```zsh
poetry install
```

and then you should be able to use the following command to run the pipeline:

```zsh
ENV_PATH=/user/.../.env.dev pipeline batch_csv '/path/to/performance/data/folder' --performance-month 2025-01-01 --max-files 500
```
Use --performance-month to set the performance month for batch_csv command and optional --max-files to limit the cases to process for development.

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

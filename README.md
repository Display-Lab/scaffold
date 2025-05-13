# SCAFFOLD

SCAFFOLD (Scalable Coaching and Appreciation Feedback For Optimal Learning and Decision-making) is a precision feedback system, implemented as a software pipeline to enhance performance reporting systems and dashboards. The underlying model of precision feedback is captured in [this conceptual model](https://onlinelibrary.wiley.com/doi/full/10.1002/lrh2.10419).

Read through our [wiki pages](https://github.com/Display-Lab/scaffold/wiki) for more detail on testing. Please note that this wiki might not be completely up to date.

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
python --version # make sure you have python 3.11
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
poetry env use 3.11 # optional, but makes sure you have python 3.11 available
poetry install # creates a virtual environment and install dependencies
poetry shell # activates the enviroment
```

#### Setup a knowledge base for SCAFFOLD

Clone the knowledge base repository in a separate location

```zsh
cd ..
git clone https://github.com/Display-Lab/knowledge-base.git 
```

#### Running SCAFFOLD

Change back to the root of scaffold

```zsh
cd scaffold
```

Update the `.env.local` file and change `path/to/knowledge-base` to point to the local knowledge base that you just checked out. (Don't remove the `file://` for preferences and manifest.)

```properties
# .env.local
preferences=file:///Users/bob/knowledge-base/preferences.json 
mpm=/Users/bob/knowledge-base/prioritization_algorithms/motivational_potential_model.csv
manifest=file:///Users/bob/knowledge-base/mpog_local_manifest.yaml
...
```

Run SCAFFOLD API

```zsh
ENV_PATH=.env.local uvicorn scaffold.api:app
# Expect to see a server start message like this "INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"
```

You can use Postman or your favorite tool to send a message and check the results. There is a sample input message file located at `tests/test_cases/input_message.json`. Here is a sample `curl` request:

```zsh
curl --data "@tests/test_cases/input_message.json" http://localhost:8000/createprecisionfeedback/
```

Run SCAFFOLD CLI
First install the python app. Then use the following command to run the pipeline on one json input file

```zsh
ENV_PATH=/user/.../dev.env pipeline batch '/path/to/input/file.json'
```

Use the following command to run the pipeline on some or all json input files in a folder

```zsh
ENV_PATH=/user/.../dev.env pipeline batch '/path/to/input/folder/' --max-files 500
```
Use --max-files if you need to limit the number of files to process.

Use the following command to run the pipeline passing preformance_data, history and preferences as separate CSV files

```zsh
ENV_PATH=/user/.../dev.env pipeline batch_csv '/path/to/performance/data/file.csv' '/path/to/preferences/file.csv' '/path/to/history/file.csv' --performance-month {performance month i.e. 2024-05-01} --max-files 500
```
Use --performance-month to set the performance month for batch_csv command.

Use the following command to run the pipeline api

```zsh
ENV_PATH=/user/.../dev.env pipeline web
```

## Environment variables

### Knowledge base settings

Local file path or URL (see .env.remote for github URL formats). All are required.

#### mpm: Path to the mpm csv file

#### preferences: Path to the preferences json file

#### manifest: Path to the manifest file that includes differend pieces of the base graph including (causal pathways, message templates, measures and comparators). See [manifest configuration](#manifest-configuration) for more detail

### Flags

#### display_window: Maximum number of month to be used to create visual displays (plots)

- default: 6

#### generate_image: If set to true and the display type is bar chart or line chart, then SCAFFOLD will generate the images and include them as part of the response

- default: True

#### log_level: Sets the log level

- default: `WARNING` (this is the production defauslt)
- note: SCAFFOLD must be run with **`log_level=INFO`** in order to generate the candidate records in the output.

#### performance_month: If set, SCAFFOLD will override the performance month in the input requests

- default: None

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
 ENV_PATH=/user/.../dev.env log_level=INFO use_preferences=True use_coachiness=True use_mi=True generate_image=False uvicorn api:app --workers=5
```


for windows:
```psh
$env:ENV_PATH=/user/.../dev.env; $env:log_level="INFO"; $env:use_preferences="True"; $env:use_coachiness="True"; $env:use_mi="True"; $env:generate_image="False"; uvicorn api:app --workers=5
```

> :point_right: `uvicorn` can be run with multiple workers. This is useful when testing with a client that can send multiple requests.

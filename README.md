## Precision feedback pipeline

This is the pipeline service that implements the Precision Feedback Pipeline. The underlying model of precision feedback is captured in [this conceptual model](https://onlinelibrary.wiley.com/doi/full/10.1002/lrh2.10419).

Read through our [wiki pages](https://github.com/Display-Lab/precision-feedback-pipeline/wiki) for more detail on testing. Please note that this wiki might not be completely up to date.

### Quick start

Clone the precision feedback pipeline repo using

```zsh
git clone https://github.com/Display-Lab/precision-feedback-pipeline.git

cd precision-feedback-pipeline
```

Create a virtual enviromnent, install the dependencies, and use the virtual environment. This is a poetry project so running poetry install will do both. Poetry will look for a python 3.11+ version, so make sure you have it available. Once the reqirements are installed you can activate the enviroment with `poetry shell`

```zsh
poetry env use 3.11 # optional, but makes sure you have python 3.11 available
poetry install
poetry shell
```

Alternatively you can use `venv` and `pip`

```zsh
python --version # make sure you have python 3.11
python -m venv .venv
myenv\Scripts\activate.bat # on Windows 
# source myenv/bin/activate  # on Mac
pip install -r requirements.txt # use `poetry export --output requirements.txt` to generate the reqs file
```

clone the knowledge base repository in a separate location
```zsh
git clone https://github.com/Display-Lab/knowledge-base.git <path/to/knowledge_base>
```

Copy the .env.devexample file to a local location (i.e. <path/to/env_file/dev.env>), outside the repository, and update it's content based on the path to the local knowledge base.

Run the pipeline from the root of the precision feedback pipeline repository
```zsh
ENV_PATH=path/to/env_file/dev.env uvicorn main:app
```

## Environment variables

### Knowledge base settings
Local file path or URL (see .env.remote for github URL formats). All are required.

#### mpm: Path to the mpm csv file

#### preferences: Path to the preferences json file

#### manifest: Path to the manifest file that includes differend pieces of the base graph including (causal pathways, message templates, measures and comparators). See [manifest configuration](#manifest-configuration) for more detail.

### Flags

#### display_window: Maximum number of month to be used to create visual displays (plots)
- default: 6

#### generate_image: If set to true and the display type is bar chart or line chart, then the pipeline will generate the images and include them as part of the response
- default: True

#### log_level: Sets the log level
- default: `WARNING` (this is the production defauslt)
- note: The PFP must be run with **`log_level=INFO`** in order to generate the candidate records in the output. 


#### performance_month: If set, the pipeline will override the performance month in the input requests
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

If the key is a relative path, it must end with a '/'. In that case the key is going to be resolved towards the location of the manifest file by the pipeline.

### examples
```zsh
 ENV_PATH=/user/.../dev.env log_level=INFO use_preferences=True use_coachiness=True use_mi=True generate_image=False uvicorn main:app --workers=5
```

for windows:
```psh
$env:ENV_PATH=/user/.../dev.env; $env:log_level="INFO"; $env:use_preferences="True"; $env:use_coachiness="True"; $env:use_mi="True"; $env:generate_image="False"; uvicorn main:app --workers=5
```


> :point_right: `uvicorn` can be run with multiple workers. This is useful when testing with a client that can send multiple requests.


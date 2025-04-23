## Bulk request tooling for the precision feedback pipeline

This script loads input messages from a specified folder and sends them to a PFP endpoint. It captures candidate information (acceptable and selected) and store the candidate records in a dataframe for analysis. 

It currently produces a brief report of candidates grouped by causal pathways, messages, and measures. It reports on counts, percentages and average scores for these groups.

### Quick start

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

Start the PFP and run the script using:
```zsh
INPUT_DIR=~/dev/pf_inputs_bulk python src/bulk_up/req.py
```
> :warning: The PFP must be run with **`log_level=INFO`** in order to generate the candidate records in the output

The defaults behavior is to run 10 requests, using 1 worker, with `http://localhost:8000/createprecisionfeedback/`. No authentication is used

### Environment variables

#### ENDPOINT_URL: URL of the PFP create precision feedback endpoint
- default: `http://localhost:8000/createprecisionfeedback/` 
- Note please use the trailing '`/`' (backslash) to avoid redirects

#### INPUT_DIR: Path to the directory containing JSON files
- Required

#### START, END: Range of inputs to read and send (after sorting by provider number in filename; some may be missing)
- default: 0, 10
- maximum (END) is the number of input files in the INPUT_DIR
- minumum (START) is 0
- END > START

#### SAMPLE: Number of randomly sampled inputs from the range [START,END]
- default: 0 (do not sample, use all in range)
- maximum: SAMPLE <= END-START
- if SAMPLE >= END-START all inputs are selected and processed in provider number order

#### WORKERS: Number of simultaneous threads to use for sending requests
- default : 1
- note: The PFP can be configured to run multiple worker using `uvicorn ... --workers 10`. Suggest setting the number of workers the same for both client and server

#### OUTPUT: If specified writes the candidates to the file given
- default: None
- format: CSV

#### PROCESS_CANDIDATES: If set to True then processes candidates and print detailed report
- default: True
- note: If the PFP is not logging candidate detail you must skip candidate processing by setting this variable to False 

#### PERFORMANCE_MONTH: If set will override the performance month in input data
- default: None 

### Authentication (Google Cloud only)

If TARGET_AUDIENCE is set then the bulk requester will send Google cloud credentials to the PFP service. Both TARGET_AUDIENCE and SERVICE_ACCOUNT_KEY_PATH must be set. Both values can be obtained from deployment team.

#### SERVICE_ACCOUNT_KEY_PATH: Service account credentials (replace with your own)
- default: `~/service_account_key.json`

#### TARGET_AUDIENCE: intended service for a token
- Required (no default)

### examples
```zsh
ENDPOINT_URL="http://localhost:8000/createprecisionfeedback/" MAX_REQUESTS=10 INPUT_DIR=~/dev/pf_inputs_bulk WORKERS=10 python src/bulk_up/req.py 
```

```zsh
TARGET_AUDIENCE=123-xyz.apps.googleusercontent.com SERVICE_ACCOUNT_KEY_PATH=~/my-client-secret.json INPUT_DIR=~/pf_inputs_bulk ENDPOINT_URL="https://pfp.lab.app.med.umich.edu/createprecisionfeedback/" python src/bulk_up/req.py```
```

### Sample output (with preferences)

```
    status_code  count  response_time  pfp_time
0          200   8818          191.9     150.8
1          400   3946           57.3       NaN 

  causal_pathway  acceptable  % acceptable  acceptable_score  selected  % selected  selected_score
0      goal gain         577           1.0          0.528610       409        70.9        0.524729
1      goal loss         738           1.3          0.475710       484        65.6        0.483915
2      improving        3646           6.4          0.384189      1101        30.2        0.392016
3  social better       18814          33.0          0.267051      2325        12.4        0.268982
4    social gain        1976           3.5          0.504590       842        42.6        0.508364
5    social loss        1589           2.8          0.458295       918        57.8        0.459968
6   social worse       25432          44.6          0.183473      2730        10.7        0.258703
7      worsening        4231           7.4          0.089441         9         0.2        0.370852 

                                         message     %  total  selected  % selected
0                          Achieved Peer Average   0.7    374       302        80.7
1                 Achieved Top 10 Peer Benchmark   1.4    801       540        67.4
2                 Achieved Top 25 Peer Benchmark   1.4    801         0         0.0
3               Congratulations High Performance  16.5   9407      2325        24.7
4                                Drop Below Goal   1.3    738       484        65.6
5                        Drop Below Peer Average   0.9    506       262        51.8
6                                  Getting Worse   7.4   4231         9         0.2
7                                     In Top 25%  16.5   9407         0         0.0
8                        No Longer Top Performer   1.9   1083       656        60.6
9   Opportunity to Improve Top 10 Peer Benchmark  44.6  25432      2730        10.7
10                         Performance Improving   6.4   3646      1101        30.2
11                                  Reached Goal   1.0    577       409        70.9 

   measure     %  total  selected  % selected
0    ABX01   0.1     48         8        16.7
1     BP01   6.7   3806       622        16.3
2     BP02  10.1   5745      1087        18.9
3     BP03  12.7   7241      1191        16.4
4     BP06   1.3    733        57         7.8
5    GLU01   0.0      8         1        12.5
6    GLU03   0.0      6         0         0.0
7    GLU06   0.0      8         3        37.5
8    GLU08   0.0     22         1         4.5
9    GLU09   0.0      6         0         0.0
10   GLU10   0.0     16         0         0.0
11   GLU11   0.0      3         0         0.0
12   NMB01   6.7   3846       416        10.8
13   NMB02   7.3   4172       399         9.6
14   NMB04   0.2    139         0         0.0
15  PAIN01   0.2     89        18        20.2
16  PAIN02   4.0   2299       250        10.9
17  PONV01   0.7    425        40         9.4
18  PONV02   0.0     16         0         0.0
19  PONV04   0.2    101        19        18.8
20  PONV05   8.9   5076      1216        24.0
21   PUL01   4.8   2722       290        10.7
22   PUL02   3.0   1694       227        13.4
23  SMOK01   2.0   1132       156        13.8
24  SMOK02   0.9    525        65        12.4
25   SUS01   6.1   3470       362        10.4
26   SUS02   6.1   3486       884        25.4
27   SUS04   3.5   2002       328        16.4
28   SUS05   0.1     60         5         8.3
29   SUS07   1.0    570       164        28.8
30  TEMP01   5.1   2928       388        13.3
31  TEMP02   6.3   3619       492        13.6
32  TEMP04   0.1     65        16        24.6
33   TOC01   0.9    495        52        10.5
34   TOC02   0.7    422        60        14.2
35   TOC03   0.0      8         1        12.5 
```

## Additional scripts with examples on how to run them

### history.py
Generates history for input files in a given directory for CURRENT_MONTH going back for DURATION number of month.

```
INPUT_DIR=~/dev/inputs START=0 END=-1 CURRENT_MONTH=2024-04-01 DURATION=6 OUTPUT_DIR=~/dev/inputs_with_history WORKERS=5 python src/bulk_up/history.py
```

### log_to_reports.py
Extracts statistic report from a log file.

```
INPUT_DIR=~/dev/PrecisionFeedbackMessageLog2024-05-20.xlsx python src/bulk_up/log_to_reports.py
```

### log_to_inputs.py
Extracts input files from a log file.

```
INPUT_DIR=~/dev/PrecisionFeedbackMessageLog2024-05-20.xlsx OUTPUT_DIR=~/dev/inputs_2024-05-20/   python src/bulk_up/log_to_inputs.py
```

### log_to_data.py
Extracts analytical data from a log file. This script uses some of the PFP modules and therefore you need to run it from the bulk-up folder. This will let it add the directory above (which is precision-feedback-pipeline/) to system path to be able to import those pipeline modules. This script loads knowledge base to a graph from KNOWLEDGE_BASE_LOCAL_MANIFEST local variable so make sure the local knowledge base is fine.

```
INPUT_DIR=~/dev/PrecisionFeedbackMessageLog2024-05-20.xlsx OUTPUT_DIR=~/dev/AnalyticalData.xlsx KNOWLEDGE_BASE_LOCAL_MANIFEST=/path/to/knowledge-base/mpog_local_manifest.yaml  python src/bulk_up/log_to_data.py
```

### dataset_to_inputs.py
Extracts input files from a dataset file. Set QUARTERLY_DATA to True to create quarterly data instead of monthly data.

```
INPUT_DIR=~/dev/OBI_dataset.xlsx OUTPUT_DIR=~/dev/inputs/  python src/bulk_up/dataset_to_inputs.py
```

### history_extractor.py
Extracts history from a folder containing input files into a csv file.

```
INPUT_DIR=~/dev/inputs_2024-05-20/ WORKERS=5 OUTPUT=~/dev/history.csv python src/bulk_up/history_extractor.py
```

### stats.py
Currently calculates average and standard deviation of unique counts per provider for measures, messages and causal pathways. Use this as an example of one way to analyse messages from the pipeline. 

```
INPUT=~/dev/inputs_2024-05-20/history.csv python src/bulk_up/stats.py
```

```
cat ~/dev/inputs_2024-05-20/history.csv | python src/bulk_up/stats.py
```
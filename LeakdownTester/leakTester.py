import pandas as pd
import json
import requests
import time
import os
import argparse
import base64
import certifi
import google.auth.transport.requests
import requests
from google.auth import crypt
from google.oauth2 import service_account

global iniRow,finRow,numCol,reqNumber,target,useGit,showResp,saveResp,perfPath,pfp,audience,vers
vers = "1.3.0"

## Initialize argparse, define command-line arguments
parser = argparse.ArgumentParser(description="Leakdown Tester Script")
# Integer Args
parser.add_argument("--RI", type=int, default=0, help="First row of data to read from CSV.")
parser.add_argument("--RF", type=int, default=12, help="Last row of data to read from CSV.")
parser.add_argument("--C", type=int, default=10, help="Number of columns to read.")
parser.add_argument("--reqs", type=int, default=1, help="Number of post requests to send.")
# String Args
parser.add_argument("--target", choices=["local", "heroku", "cloud"], default="local", help="Target PFP environment: use 'local', 'heroku', or 'cloud'.")
parser.add_argument("--useGit", type=str, default=None, help="Address of GitHub input message file to send pipeline.")
parser.add_argument("--csv", type=str, default=None, help="Filepath to CSV file to read from.")
parser.add_argument("--servAcc", type=str, default=None, help="Filepath to the service account file to read from" )
# Logical Args
parser.add_argument("--respond", action="store_true", help="Logical flag to print API responses. Default = True; use '--respond' to see responses.")
parser.add_argument("--save", action="store_true", help="Logical flag to save API responses. Default = True; use '--save' to save outputs.")
parser.add_argument("--repoTest", action="store_true", help="Logical flag to test knowledgebase repo files.")

## Parse command-line arguments and pull in environmental variables
args = parser.parse_args()
iniRow =    args.RI         # Initial row read from CSV
finRow =    args.RF         # Final row read from CSV
numCol =    args.C          # Number of columns read
reqNumber = args.reqs       # Number of Requests sent
target =    args.target     # Flag: API endpoint target
useGit =    args.useGit     # Flag: GitHub JSON source
csvPath =   args.csv        # CSV file path (argument specified)
servAccPath = args.servAcc  # Service Account file path(argument specified)
showResp =  args.respond    # Flag: Print API response to console
saveResp =  args.save       # Flag: Save API response to file
repoTest =  args.repoTest   # Flag: Test knowledgebase repo files

perfPath =  os.environ.get("CSVPATH")
pfp =       os.environ.get("PFP")
audience = os.environ.get("TARGET_AUDIENCE")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#### Startup Functions ################################################
# Configure API endpoint from argument...
def set_target():
    global pfp
    # Local API target:
    if target == "local":
        pfp = "http://127.0.0.1:8000/createprecisionfeedback/"
    
    # Heroku API target:
    elif target == "heroku":
        pfp = "https://pfpapi.herokuapp.com/createprecisionfeedback/"
    
    # GCP API target (ft. token retrieval):
    elif target == "cloud":
        pfp = "https://pfp.test.app.med.umich.edu/createprecisionfeedback"
        oidc_token = service_account.IDTokenCredentials.from_service_account_file(
        servAccPath,
        target_audience=audience,
        )
    else:
        print("Warning: Target not declared. Continuing with local PFP target.")

# Handle JSON content pathing (& errors)...
def confirm_content():
    global perfPath
    # Override env var CSV filepath w/ arg
    if csvPath != None:
        perfPath = csvPath

    if perfPath == None and useGit == None:
        raise Exception("Please specify where to read JSON content from.")
    
    elif perfPath != None and useGit != None:
        print("\tINFO: JSON payloads specified by both GitHub link and filepath.")
        print("Continuing with GitHub payload...")


# Startup configuration setting readback...
def startup_checklist():
    if useGit != None:
        print(f"Reading JSON data from {useGit}...")
    elif perfPath != None and not repoTest:
        if csvPath == None:
            print("Using CSV data specified by environmental variable...")
        print(f"Reading data from {perfPath}...")
        print(f"Reading in data with dimensions {numCol} by {finRow - iniRow}...")
    elif repoTest:
            print("Running automated input_message tests...\n")
    print(f"Sending POST request(s) to {pfp}...\n")

#### Print Statements and Response Saving ################################
# Output relevant JSON keys from API response...
def text_back(postReturn):
    if "selected_candidate" in postReturn:
        selCan = postReturn["selected_candidate"]
        print("Selected Candidate Message Information:")
        print(f"Display: {selCan.get('display')}")
        print(f"Measure: {selCan.get('measure')}")
        print(f"Acceptable By: {selCan.get('acceptable_by')}")

    if "Message" in postReturn:
        messDat = postReturn["Message"]
        print(f"Text Message: {messDat.get('text_message')}")
        print(f"Comparison Value: {messDat.get('comparison_value')}\n\n")

# Save PFP API responses for review...
def log_return(postReturn, outputName):
    texName = outputName + ".json"
    imgName = outputName + ".png"
    with open(texName, "w") as file:
        json.dump(postReturn, file, indent=2)
        print(f"PFP response text saved to '{texName}'")
    with open(imgName, "wb") as imageFile:
        imageFile.write(base64.b64decode(postReturn["Message"]["image"]))
        print(f"Pictoralist image saved to '{imgName}'.\n\n")


# Handle API responses...
def handle_response(response, request_number):
    if response.status_code == 200:
        print("Message delivered in {:.3f} seconds.\n".format(response.elapsed.total_seconds()))
        api_return = json.loads(response.text)
        
        if showResp:
            text_back(api_return)

        if saveResp:
            resp_name = f"response_{request_number}"
            log_return(api_return, resp_name)
    else:
        if target == "cloud":
            raise Exception("Bad response from target API:\nStatus Code: {!r}\nHeaders: {!r}\n{!r}".format(
            response.status_code, response.headers, response.text))
        else:
            raise Exception("Bad response from target API:\nStatus Code: {!r}\n{!r}\n".format(
            response.status_code, response.text))


##### JSON Content Functions ########################################
# Fetch JSON content from GitHub... V9
def go_fetch(url):
    if "github.com" in url:
        url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob", "")
    header = {"Accept": "application/vnd.github.v3.raw"} # tell gitHub to send as raw, uncompressed
    bone = requests.get(url, headers=header)
    
    if bone.status_code == 200:
        try:
            jasonBone = json.dumps(json.loads(bone.text), indent=4) # reconstruct as JSON with indentation
            return jasonBone
        except json.JSONDecodeError as e:
            raise Exception("Failed parsing JSON content.")
    else:
        raise Exception(f"Failed to fetch JSON content from GitHub link: {url}")


# Read in CSV data from file...
def csv_trans_json(path):
    performance = pd.read_csv(path, header=None, usecols = range(numCol), nrows= finRow-iniRow)
    rowsRead, colsRead = performance.shape
    selectedRows = performance.iloc[iniRow : finRow]
    jsonedData = ""
    
    # Integrated dimension error catcher:
    if colsRead != numCol or rowsRead != finRow - iniRow:
        raise ValueError(f"Read error; expected {finRow - iniRow} rows and {numCol} columns. Actual data is {rowsRead} rows by {colsRead} columns.")

    # Integrated Dataframe to JSON conversion (V.15)
    for i, row in selectedRows.iterrows():
        current_line = json.dumps(row.to_list())
        jsonedData += current_line  # content addition
        if i < len(performance) - 1:
            jsonedData += ",\n\t"   # formatting
    return jsonedData


# Create JSON Payload (CSV data)...
def assemble_payload(warhead):
    missile = '''{
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
      "Performance_data":[
        ["staff_number","measure","month","passed_count","flagged_count","denominator","peer_average_comparator","peer_90th_percentile_benchmark","peer_75th_percentile_benchmark","MPOG_goal"],
        '''
    missile += warhead
    missile += '''
        ],
        "History":{
        },
        "Preferences":{
          "Utilities": {
          "Message_Format": 
            {
              "1": "0.0",
              "2": "0.1",
              "16": "7.5",
              "24": "9.4",
              "18": "11.3",
              "11": "13.2",
              "22": "15.1" ,
              "14": "22.6" ,
              "21": "62.3" ,
              "5":"0.2",
              "15":"4.0",
              "4":"0.9"
            },
          "Display_Format":
            {
              "short_sentence_with_no_chart": "0.0",
              "bar": "37.0",
              "line": "0.0"
            }
        }
      }
    }'''
    return missile

#### POST Functions ##################################################
# Send POST request to unprotected URLs...
def send_req(pfp, missile):
	headers1 = {"Content-Type": "application/json"}
	response = requests.post(pfp, data=missile, headers=headers1)
	return response

# Send POST to IAP protected URLs...
def make_iap_request(url, Fullmessage, method="POST", **kwargs):

    # Set the default timeout, if missing
    if "timeout" not in kwargs:
        kwargs["timeout"] = 90

    # Check if token valid, refresh expired token if not
    if oidc_token.valid != True:
        request = google.auth.transport.requests.Request()
        oidc_token.refresh(request)

    # Fetch the Identity-Aware Proxy-protected URL, including an
    # Authorization header containing "Bearer " followed by a
    # Google-issued OpenID Connect token for the service account.
    Fullmessage=json.loads(Fullmessage)
    resp = requests.post(
        url,
        headers={"Authorization": "Bearer {}".format(oidc_token.token)},
        json=Fullmessage,
    )
    return resp

# Automated full-repo test of knowledgebase input_message files...
def repo_test():
    hitlist = ["alice", "bob", "chikondi", "deepa", "eugene", "fahad", "gaile"]

    for request_number, persona in enumerate(hitlist, start=1):
        url = f"https://raw.githubusercontent.com/Display-Lab/knowledge-base/main/vignettes/personas/{persona}/input_message.json"

        try:
            json_content = go_fetch(url)
            response = send_req(pfp, json_content)
            print(f"Trying request {request_number} of {len(hitlist)}, Persona '{persona}':")
            handle_response(response, request_number)
        
        except Exception as e:
            print(f"Error processing message; {e}")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########### Main Script Body ################################
if __name__ == "__main__":
    print(f"\n\t\tWelcome to the Leakdown Tester, Version {vers}!")
    set_target()
    confirm_content()
    startup_checklist()

    try:
        # Call repo_test if requested
        if repoTest:
            repo_test()
            print("\n\t\tLeakdown Test complete.\n")
            exit(0)  # Exit the script

        # Retrieve GitHub JSON Payload if requested
        if useGit != None:
            fullMessage = go_fetch(useGit)    
        
        # Build JSON from CSV if requested / by default
        elif perfPath != None:
            perfJSON = csv_trans_json(perfPath)   # I/O from CSV dataframe
            fullMessage = assemble_payload(perfJSON)    # Make JSON payload
        else:
            print("Error: No content provided for POST request.")
            exit(1)

        # Send POST request(s)
        for i in range(reqNumber):
            print(f"Trying request {i + 1} of {reqNumber}:")
            
            if target == "heroku" or target == "local":
                sentPost = send_req(pfp, fullMessage)
                #print(sentPost)
            
            elif target == "cloud":
                sentPost = make_iap_request(pfp, fullMessage)
                #print(sentPost)
            
            # Check response(s)
            handle_response(sentPost, reqNumber)
        
        print("\t\tLeakdown Test complete.\n")

    except ValueError as e:
        print(f"Error: {e}")

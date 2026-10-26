# Causal Pathway Test Suite
This folder contains input_message files developed specifically such that each file tests the particular causal pathway that they are named for.

## Notes and additional details
- All cptest.json files use the staff_ID 7, corresponding to Gaile
- Performance data has been extensively altered relative to vignette-accurate input_message.json files found in the personas folder on this repo
- Measure names are mostly unchanged from input_message/vignette data
   - Exceptions: SUS02 and NMB-03-Peds
   - Changed to SUS04 to avoid tripping ongoing rdflib error bug and returning a 500 error from the API(s)

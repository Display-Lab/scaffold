# Performance JSON data
The following are templates for use in creating measure-associated JSON performance metadata to make **input_message.json files**.
This data is currently templated as twelve month blocks.
  - note: confirm twelve months of data sufficient for pipeline operations

### JSON data block (12 months)
Variables:
- `staffID` - ID # for personas: replace with number based on which persona you are working with.
- `MSR1` - Measure name (eg SUS04) - note that meausures have hypens removed in JSON data
- `passNumb` - count of successful events for each month. passNumb generally is 50, 85, or 95, based on persona specs, and with `denominator` set to 100 (as below)
- `flagNumb` - remainder of event sum, = 100-`passNumb`
- `p_avg` - peer average, needs to be set based on the vignette data
- `ninety` - 90th percentile benchmark
- `sevenFive` - 75th percentile benchmark
- `pogGoal` - MPOG goal values(measure dependent)

"Performance_data":[
    ["staff_number","measure","month","passed_count","flagged_count","denominator","peer_average_comparator","peer_90th_percentile_benchmark","peer_75th_percentile_benchmark", "MPOG_goal"],
    [staffID,"MSR1","2023-01-01",passNumb,flagNumb,100,p_avg,ninety,sevenFive,pogGoal],
    [staffID,"MSR1","2023-02-01",passNumb,flagNumb,100,p_avg,ninety,sevenFive,pogGoal],
    [staffID,"MSR1","2023-03-01",passNumb,flagNumb,100,p_avg,ninety,sevenFive,pogGoal],
    [staffID,"MSR1","2023-04-01",passNumb,flagNumb,100,p_avg,ninety,sevenFive,pogGoal],
    [staffID,"MSR1","2023-05-01",passNumb,flagNumb,100,p_avg,ninety,sevenFive,pogGoal],
    [staffID,"MSR1","2023-06-01",passNumb,flagNumb,100,p_avg,ninety,sevenFive,pogGoal],
    [staffID,"MSR1","2023-07-01",passNumb,flagNumb,100,p_avg,ninety,sevenFive,pogGoal],
    [staffID,"MSR1","2023-08-01",passNumb,flagNumb,100,p_avg,ninety,sevenFive,pogGoal],
    [staffID,"MSR1","2023-09-01",passNumb,flagNumb,100,p_avg,ninety,sevenFive,pogGoal],
    [staffID,"MSR1","2023-10-01",passNumb,flagNumb,100,p_avg,ninety,sevenFive,pogGoal],
    [staffID,"MSR1","2023-11-01",critPass,critFlag,100,p_avg,ninety,sevenFive,pogGoal],
    [staffID,"MSR1","2023-12-01",critPass,critFlag,100,p_avg,ninety,sevenFive,pogGoal],
  ],
  
  
When editing, copy paste into another text editor (sublime, notepad, whatever you use), then  `shft`+`ctrl`+`f` find/replace the variable with relevant data. Use `passNumb` and `flagNumb` to set the passed and flagged event counts, change the values for the benchmarks (including `pogGoal`), then edit the `critPass` and `critFlag` values based on the specifications in the [persona data sheet](https://docs.google.com/spreadsheets/d/1ZxtuEPI5EVfnO-YcvzGjbUSy3woixCsaz4slOCozVEU/edit#gid=0).

# Vignette Template Data
### Table 1: Typical Values and Benchmarks by Role (*Unused*)
 |Role|Performance Level|Peer Average|75th Percentile Benchmark|90th Percentile Benchmark|
|-----|-----------------|------------|------------------------|---------------|
|Attending|  90-94%|            90|             92|                96|
|Resident|   87-91%|            85|             88|                92|
|CRNA|       80-87%|            80|             85|                90|

## Attending Template Data
Associated personas: `Alice`   `Fahad`
### Six month block
|Month|Performance Level|Peer Average|75th Percentile Benchmark|90th Percentile Benchmark|MPOG Goal|
|-----|---------|---|---|---|---|
|Jul  |      90%| 90| 92| 96| 90|
|Aug  |      90%| 90| 92| 96| 90|
|Sept |      90%| 90| 92| 96| 90|
|Oct  |      90%| 90| 92| 96| 90|
|Nov  |***xx%***| 90| 92| 96| 90|
|Dec  |***xx%***| 90| 92| 96| 90|

## Resident Template Data
Associated personas: `Chikondi`  `Eugene`  `Gaile`
### Six month block
|Month|Performance Level|Peer Average|75th Percentile Benchmark|90th Percentile Benchmark|MPOG Goal|
|-----|---------|---|---|---|---|
|Jul  |      85%| 85| 88| 92| 90|
|Aug  |      85%| 85| 88| 92| 90|
|Sept |      85%| 85| 88| 92| 90|
|Oct  |      85%| 85| 88| 92| 90|
|Nov  |***xx%***| 85| 88| 92| 90|
|Dec  |***xx%***| 85| 88| 92| 90|

## CRNA Template Data
Associated personas: `Bob`   `Deepa`
### Six month block
|Month|Performance Level|Peer Average|75th Percentile Benchmark|90th Percentile Benchmark|MPOG Goal|
|-----|---------|---|---|---|---|
|Jul  |      80%| 80| 85| 90| 90|
|Aug  |      80%| 80| 85| 90| 90|
|Sept |      80%| 80| 85| 90| 90|
|Oct  |      80%| 80| 85| 90| 90|
|Nov  |***xx%***| 80| 85| 90| 90|
|Dec  |***xx%***| 80| 85| 90| 90|

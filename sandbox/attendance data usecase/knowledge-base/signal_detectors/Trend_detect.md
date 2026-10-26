# Trend Signal Detector
## Concept
The trend motivating information detector function compares the performance level of a feedback recipient for a specfic measure as it changes over time. The trend detector currently evaluates over a three month window, and detects monotonic and non-monotonic performance trend information. The signal detects when the performance level has a positive or negative slope over time, and extracts the magnitude of teh trend as motivating information to be used as a moderator.
## Example
Below are examples of performance data that leads to the detection of a trend signal.

|Month|Performance Level|Peer Average|75th Percentile Benchmark|90th Percentile Benchmark|MPOG Goal|
|-----|-----------------|------------|-------------------------|-------------------------|--|
|Oct  |       85%| 85| 88| 92|90|
|Nov  | ***85%***| 85| 88| 92|90|
|Dec  | ***91%***| 85| 88| 92|90|

- For the month of December, this performance data will generate a positive trend signal. The magnitude of the trend will be evaluated as 3, the formula below denotes how this magnitude is determined:
     - trend magnitude = (month t0 - month t2)/2
     - trend magnitude = **(91 - 85)/2 = 3**

## Implementation
The method operates with the current formula:
Month t0 performance - Month t2 performance / 2

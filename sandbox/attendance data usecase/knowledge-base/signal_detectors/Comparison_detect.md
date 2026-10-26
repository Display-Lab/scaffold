# Comparison Signal Detector
## Concept
The comparison signal detector function compares the performance level of a feedback recipient for a specfic measure against the level of a benchmark, such as the peer performance benchmarks or the goal value for that particular measure. This function evaluates differently for both types of gaps, both positive and negative, relative to the performance level and the list of comparator values that are pre-defined by the pipeline. When the recipient's performance level is above that of a comparator, the comparison _detect method denotes that there exists a positive gap in performance level, which is a kind of motivating information. When this detector is activated, the positive or negative gap motivating information is used to influence the rank of corresponding precision feedback message templates.

## Example
Below are examples of performance data that leads to the detection of a comparison signal.

|Month|Performance Level|Peer Average|75th Percentile Benchmark|90th Percentile Benchmark|MPOG Goal|
|-----|-----------------|------------|-------------------------|-------------------------|--|
|Oct  |       85%| 85| 88| 92|90|
|Nov  | ***85%***| 85| 88| 92|90|
|Dec  | ***91%***| 85| 88| 92|90|

- For the month of December, this performance data will generate a positive gap signal relative to the 50th and 75th peer performance percentile benchmarks, as well as a negative gap signal between the performance level and the 90th percentile benchmark. 

## Implementation

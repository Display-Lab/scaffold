# Signal detectors
Signal detectors are functions that identify specific types of motivating performance information in performance data. 

## Motivating performance information 
Motivating performance information is the information that healthcare professionals seek when viewing a performance dashboard or feedback report, to interpret their performance data. This including comparisons, trends, achievements, and losses that can guide future efforts to improve or sustain performance. These types of information are defined in the [Performance Summary Display Ontology](https://bioportal.bioontology.org/ontologies/PSDO). 

### Comparisons
1. Positive gap
2. Negative gap
3. Consecutive positive gaps
4. Consecutive negative gaps

### Trends
1. Improving trend
2. Worsening trend


### Performance events 
1. Achievement
2. Loss

# Implementation
A [Precision Feedback Pipeline](https://github.com/Display-Lab/precision-feedback-pipeline) uses several signal detectors in series to identify motivating performance information, according to the following workflow (top-down):
1) [extract_signals](https://github.com/Display-Lab/precision-feedback-pipeline/blob/main/bitstomach/bitstomach.py)
- Loops over performance measures, calling each signal detection method
- Adds signals to a knowledge graph as new instances of motivating information
2) [comparison _detect](https://github.com/Display-Lab/precision-feedback-pipeline/blob/main/bitstomach/signals/_comparison.py)
- detects comparison signals in the performance data from a list of pre-defined comparators. Comparisons result from differences between performance levels and the values of the pre-defined comparator level list. This method calculates the simple difference between the comparator and performance level, and returns a list of resources representing each detected signal
3) [trend _detect](https://github.com/Display-Lab/precision-feedback-pipeline/blob/main/bitstomach/signals/_trend.py)
- detects trend signals, where trend equates to the performance level rate of change month over month. This method can detect monotonic positive and negative trends over three months. The method records the slope as a moderator PSDO.performance_trend_content

In esteemer, the moderator methods reads motivating information identified by signal detectors from the graph, extracting the values and types of moderators from the motivating information that then affect the score of a message template.


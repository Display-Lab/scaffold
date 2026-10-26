# Social Approach Vignette
## Introduction
This vignette illustrates the process for creating precision feedback messages about a recipient's performance approaching an explicit target, such as a top performer benchmark or peer average. These messages use the social approach causal pathway, which specifies feedback messages that may motivate providers by delivering information about their performance nearing a benchmark. Example messages that use social approach are "your performance is approaching the peer average this month for the measure GLU-01" and "your performance is approaching the peer 90th percentile benchmark this month for the measure ABX-01-OB".

This vignette also contains examples of data features and other entities that a precision feedback system uses to evaluate the potential success of a precision feedback message. An example of such an entity is a [peer average comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000126), which is defined in the [Performance Summary Display Ontology <sub>(GH)</sub>](https://github.com/Display-Lab/psdo) as an average representing the mean performance of a peer group. 

## Performance Data
Each month, MPOG receives data about operative case quality and outcomes from approximately 60 healthcare institutions. MPOG calculates performance for each provider individually, for approximately 35 performance measures of quality and outcomes. One example of these measures is [TOC-02: Postoperative Transfer of Care to PACU <sub>(MPOG)</sub>](https://spec.mpog.org/Spec/Public/22).

### Benchmark comparators
MPOG calculates performance benchmarks and averages for each institution. One comparator is a [peer 90th percentile benchmark <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000129), which represents the 90th percentile for performance among providers at an institution, for each measure. Another is the [peer average comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000126), which is the mean performance for all providers at an insitution, for each measure.

### Healthcare professional performance
Bob, a nurse anesthetist (CRNA) at Max Commuity Hospital, has the following performance data over the last 6 months for the TOC-02 measure:

|Month|Performance Level|Peer Average|75th Percentile Benchmark|90th Percentile Benchmark|MPOG Goal|
|-----|---------|---|---|---|---|
|Jul  |      75%| 80| 85| 90| 90|
|Aug  |      75%| 80| 85| 90| 90|
|Sept |      75%| 80| 85| 90| 90|
|Oct  |      75%| 80| 85| 90| 90|
|Nov  |***78%***| 80| 85| 90| 90|
|Dec  |***84%***| 80| 85| 90| 90|

Deepa, another CRNA at Midwest Medicine, a medical-school affiliated hospital, has the following performance data over the last 6 months for the TOC-02 measure:

|Month|Performance Level|Peer Average|75th Percentile Benchmark|90th Percentile Benchmark|MPOG Goal|
|-----|---------|---|---|---|---|
|Jul  |      95%| 80| 85| 90| 90|
|Aug  |      95%| 80| 85| 90| 90|
|Sept |      95%| 80| 85| 90| 90|
|Oct  |      95%| 80| 85| 90| 90|
|Nov  |***84%***| 80| 85| 90| 90|
|Dec  |***89%***| 80| 85| 90| 90|

## Preference data
Preferences for precision feedback are elicited through a preference survey that providers can take. The preference survey produces a preference model for each provider that, with the provider's permission, is shared with MPOG to maintain. MPOG analyses preference data that is shared to identify population-level preference segments. These segments are generated as preference profiles that can serve as a default preference model for an organization, or which can be selected by providers who do not take the preference survey, but who identify preferences that are close enough to their own in the settings menu for the precision feedback system.

Bob's preference data (Individual profile from conjoint analysis survey) :

|Motivating information |Utility value|Description                                                                     |
|-----------------------|-------------|--------------------------------------------------------------------------------|
|Social better	        |-3           |Performance is high this month.                                                 |
|Social gain            |-4           |Performance was previously low, but it has improved to reach the peer benchmark.|
|Social stayed better   |-5           |Performance is consistently high (no recent change).                            |
|Worsening             	|6 	      |Performance is worsening.                                                       |
|Improving	        |-14          |Performance is improving.                                                       |
|Social loss            |5            |Performance was previously high, but it has dropped below the peer average.     |
|Social worse           |5            |Performance is low this month.                                                  |
|Social stayed worse    |5            |Performance has remained below average (no recent change).                      |
|Social approach        |5	      |Performance is improving, getting closer to the peer benchmark.                 |
|Goal gain              |-4 	      |Performance was previously low, but it has improved to reach the goal.          |
|Goal loss	        |5 	      |Performance was previously high, but it has dropped below the goal.             |
|Goal approach          |5            |Performance is improving, getting closer to the goal.                           |

|Display format         |Utility value|
|-----------------------|-------------|
|Bar chart              |0            |
|Line chart             |0	      |
|Text only              |1            |

Deepa's preference data (Individual profile from conjoint analysis survey) :

|Motivating information |Utility value|Description                                                                     |
|-----------------------|-------------|--------------------------------------------------------------------------------|
|Social better	        |-13          |Performance is high this month.                                                 |
|Social gain            |-14 	      |Performance was previously low, but it has improved to reach the peer benchmark.|
|Social stayed better   |5            |Performance is consistently high (no recent change).                            |
|Worsening             	|3  	      |Performance is worsening.                                                       |
|Improving	        |4            |Performance is improving.                                                       |
|Social loss            |3 	      |Performance was previously high, but it has dropped below the peer average.     |
|Social worse           |5            |Performance is low this month.                                                  |
|Social stayed worse    |2            |Performance has remained below average (no recent change).                      |
|Social approach        |5	      |Performance is improving, getting closer to the peer benchmark.                 |
|Goal gain              |-8	      |Performance was previously low, but it has improved to reach the goal.          |
|Goal loss	        |3 	      |Performance was previously high, but it has dropped below the goal.             |
|Goal approach          |5            |Performance is improving, getting closer to the goal.                           |

|Display format         |Utility value|
|-----------------------|-------------|
|Bar chart              |0            |
|Line chart             |1            |
|Text only              |0            |

# Precision feedback message generation
To generate precision feedback, MPOG sends de-identified performance and preference data to a precision feedback system that processes each provider's data with their peer comparator performance data. The precision feedback system produces and evaluates candidate messages using metadata from message templates, then selects an optimal precision feedback message to return to MPOG. The precision feedback system is a knowledge-based system that is comprised of the following parts: a knowledge base, a software pipeline, and a web service.

## Precision Feedback Knowledge Base
The knowledge base contains the following components: causal pathways, message templates, and performance measures.

## Social Approach Causal Pathway
This pathway describes the influence of feedback interventions informing the recipient that their performance is approaching that of a social comparator, such as a top performer benchmark or peer average. The causal pathway model is made up of preconditions, moderators, mechanisms, and outcomes.

### Preconditions
Preconditions are factors necessary for the success of a social approach precision feedback intervention. The social approach causal pathway has the following preconditions:

Information content preconditions:
1. [Social comparator content <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000095)
2. [Negative performance gap content <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000105)
3. [Positive performance trend content <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000099)

Message preconditions:
1. [Social comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000045)
2. [Negative performance gap set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000116)
3. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)
 
### Moderators
Moderators are factors that inhibit or promote the influence of the feedback intervention on the recipient. The social approach causal pathway has the following moderators:
1. `Message recency` - The number of months since this message was delivered previously.
2. `Message delivery count` - How many times has the recipient previously received this message in the last year?  
3. `Regulatory fit` - To what extent is the message aligned to the behavior/task's characteristics, context, and recipient personality (motivated by bad outcome prevention vs. good outcome promotion).
4. `Gap size` - How large is the gap between the recipient's performance level and that of the social comparator?
5. `Slope of trend` - Derivative of the performance measure in the time domain

### Mechanisms
Mechanisms are factors that the intervention operates through to influence the feedback recipient. Adapted from [Carey et. al. 2019](https://doi.org/10.1093/abm/kay078). The social approach pathway has the following mechanisms:
1. `Awareness (knowledge)` - The message may change the recipient's awareness of their performance level, its change over time, and of their peers' performance via institutional benchmarks.
2. `Subjective norms` - The message may influence the recipient by creating or reinforcing knowledge of their peers' performance and their relative status within their peer group.
3. `Motivation` - The message may give the recipient purpose or direction towards changing their performance for a given measure.
4. `Optimism` - The message may influence the recipient's confidence that things will happen for the best and they will continue to increase their performance, gaining social status.

### Outcomes
A successful precision feedback intervention leveraging the social approach pathway should increase clinical process performance improvement.

## Message templates
Message templates represent possible motivational messages that a precision feedback system can send. There are three message templates that the precision feedback system can access for this vignette: 

The `Approach Top 10 Peer Benchmark`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/drop_below_peer_average.json) message reads as follows:
> Your performance is approaching the top 10% peer benchmark this month for the measure [Measure name].

This message template `is about` [<sub>(OntoBee)</sub>](https://ontobee.org/ontology/IAO?iri=http://purl.obolibrary.org/obo/IAO_0000136) the following data features:
1. [Social comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000045) 
2. [Negative performance gap set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000116)
3. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)
4. [Peer 90th percentile benchmark <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000126)
5. Display format compatability: [Line Graph <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/IAO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FIAO_0000573), [Bar Chart <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/STATO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FSTATO_0000166)

The `Approach Top 25 Peer Benchmark`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/approach_top_25_peer_benchmark.json) message reads as follows:
> Your performance is approaching the top 25% peer benchmark this month for the measure [Measure name].

This message template `is about` [<sub>(OntoBee)</sub>](https://ontobee.org/ontology/IAO?iri=http://purl.obolibrary.org/obo/IAO_0000136) the following data features:
1. [Social comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000045) 
2. [Negative performance gap set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000116)
3. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)
4. [Peer 75th percentile benchmark <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000129)

The `Approach Peer Average` [<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/approach_peer_average.json) message reads as follows:
> Your performance is approaching the peer average this month for the measure [Measure name].

This message template `is about` [<sub>(OntoBee)</sub>](https://ontobee.org/ontology/IAO?iri=http://purl.obolibrary.org/obo/IAO_0000136) the following data features:
1. [Social comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000045) 
2. [Negative performance gap set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000116)
3. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)
4. [Peer average comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000126)

## Software Pipeline (Precision Feedback Pipeline)
### Recipient annotation generation (Bitstomach)
The first stage of the pipeline is a script called Bitstomach. This script analyzes recipient's performance data and generates features called **annotations**. These annotations describe features of the performance data such as performance trends over time, or how performance measures relate to other values like peer performance benchmarks and institutional performance goals.

**Annotations for Bob's performance data for the most recent month:**
1. `Social comparator content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000095)
2. `Positive performance trend content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000099)
3. `Negative performance gap content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000105)
    - *with respect to* [Peer 75th percentile comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000128)
    - *with respect to* [Peer 90th percentile comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000129)
    - *with respect to* [Goal comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000046)
4. `Positive performance gap content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000104) 
    - *with respect to* [Peer average comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000126)

**Annotations for Deepa's performance data for the most recent month:**
1. `Social comparator content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000095)
2. `Positive performance trend content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000099)
3. `Negative performance gap content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000105)
	- *with respect to* [Peer 90th percentile comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000129)
	- *with respect to* [Goal comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000046)
4. `Positive performance gap content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000104) 
    - *with respect to* [Peer 75th percentile comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000128)
    - *with respect to* [Peer average comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000126)

### Candidate Message Generation (Candidate Smasher)
The second stage of the pipeline creates two candidate messages that may be appropriate for each recipient to recieve. It does this by searching through the message template library and selecting two message templates with annotations that match those annotations of the recipient's performance.

**Bob's candidate messages (A & B):**

**Candidate Message A** is the `Approach Top 10 Peer Benchmark`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/drop_below_peer_average.json) message template, which has the following annotations *in common* with the performance annotations:
1. [Social comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000045) 
2. [Negative performance gap set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000116)
3. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)
4. ~~[Peer 90th percentile benchmark <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000126)~~

**Candidate Message B** is the `Approach Top 25 Peer Benchmark`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/approach_top_25_peer_benchmark.json) message template, which has the following annotations *in common* with the performance annotations:
1. [Social comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000045) 
2. [Negative performance gap set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000116)
3. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)
4. [Peer 75th percentile benchmark <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000129)

Both candidate messages have annotations matching those generated from Bob's performance data, and are therefore appropriate as candidate messages.

**Deepa's candidate messages (α & β):**

**Candidate Message α**  is the `Approach Top 10 Peer Benchmark`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/drop_below_peer_average.json) message template, which has the following annotations *in common* with the performance annotations:
1. [Social comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000045) 
2. [Negative performance gap set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000116)
3. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)
4. [Peer 90th percentile benchmark <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000126)

**Candidate Message β** is the `Approach Top 25 Peer Benchmark`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/approach_top_25_peer_benchmark.json) message template, which has the following annotations *in common* with the performance annotations:
1. [Social comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000045) 
2. [Negative performance gap set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000116)
3. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)
4. ~~[Peer 75th percentile benchmark <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000129)~~

Both candidate messages have annotations matching those generated from Deepa's performance data, and are therefore appropriate as candidate messages.

### Candidate Message Preconditions Evaluation (ThinkPudding)
The third stage of the pipeline processes and evaluates the candidate messages for each persona based on preconditions. It compares the annotations associated with the message candidates and checks them against the persona's performance data annotations to determine which candidate messages are acceptable based on message preconditions.

For Bob, **Candidate B** is acceptable by the causal pathway **social approach**.

For Deepa, **Candidate α** is acceptable by the causal pathway **social approach**.

### Candidate Message Moderator Evaluation and Selection (Esteemer)
The fourth stage of the pipeline consists of an algorithm which ranks acceptable candidate messages. It ranks these candidates based on applying weights to and then summing a number of moderators, with the end goal to determine which message may be the most motivating to provide to the recipient. The moderators which influence the rank of a candidate message are:
$$\text{Performance trend slope, }  \Delta_{\text{performance}}$$
$$\text{Performance gap size, }  G_{\text{performance}}$$
$$\text{Achievement or loss recency, } t_{\text{event}}$$
$$\text{Feedback history, } t_{\text{message}} \text{ and } N_{\text{received}}$$
$$\text{Individual feedack preferences, } F_{\text{pref}}$$

The overall algortihm can be represented as:
$$F_{\text{pref}} \Biggl[ C_{\text{data}} \biggl( \Bigl( X_s \| \Delta_{\text{performance}}  \| \Bigr) + \Bigl( X_{gs} \| G_{\text{performance}} \| \Bigr) \biggr) \\
    + \\
    C_{\text{history}} \Bigl( \bigl(X_e \cdot t_{\text{event}}\bigr) + \bigl(X_m \cdot t_{\text{message}}\bigr) + \bigl(X_N \cdot N_{\text{received}}\bigr) \Bigr) \Biggr]$$

<!-- No changes need to be made below this line when propagating to new vignettes-->
The Esteemer algorithm uses weighting coefficients, which vary based on the particularities of each causal pathway. For the social loss causal pathway, the weighting coefficients are:

| Moderator          | G<sub>performance</sub> | Δ<sub>performance</sub> | t<sub>event</sub> | t<sub>message</sub> | N<sub>received</sub> | Data component | History component |
|--------------------|-------------------------|-------------------------|-------------------|---------------------|----------------------|----------------|-------------------|
| Coefficient Term   | X<sub>gs</sub>          | X<sub>s</sub>           | X<sub>e</sub>     | X<sub>m</sub>       | X<sub>N</sub>        |C<sub>data</sub>|C<sub>history</sub>|
| Value              | 0.5                     | 0.8                     | -0.5              | -0.1                | -0.1                | 1              | 1                 |

<!-- Values above need to be changed for each causal pathway -->
<!--

As an example, appropriate values based on this vignette are filled in for Eugene's **Candidate B** message, and evaluate like so:
$$F_{\text{pref}} \biggl( 1 \Bigl( \Bigl( 0.5 \| 6 \| \Bigr) + \Bigl( 0.5 \| 5 \| \Bigr) \Bigr) + 1 \Bigl( (0.5 \cdot 12) + (0.5 \cdot 12) + (0.5 \cdot 0) \Bigr) \biggr) = (19.5)F_{\text{pref}}$$  
Gaile's acceptable social loss candidate evaluates similarly:
$$F_{\text{pref}} \biggl( 1 \Bigl( 0.5 \| 7 \| \Bigr)\Bigl( 0.5 \| 1 \| \Bigr) + 1 \Bigl( (0.5 \cdot 12) + (0.5 \cdot 12) + (0.5 \cdot 0) \Bigr) \biggr) = (13.75)F_{\text{pref}}$$  
<!-- Equations above need to be re-evaluated for each causal pathway -->

Of note, each persona has more than one measure's worth of data, therefore for each persona there are potentially many acceptable candidates, utilizing different causal pathways regarding different measures. Esteemer evaluates each acceptable candidate measure with differing coefficient weights depending on the causal pathway. 

### Message Generation and Delivery (Pictoralist)
The fifth and final stage of the pipeline generates visual representations of the selected message based on the recipient's performance data, and sends this output off for delivery to the recipient.
The script takes in the selected message and performance data of the recipient as inputs. It then uses the recipient's display preferences to generate a figure that visualize's the reciepients performance over time related to the given measure and causal pathway. It returns the figure as an image encoded as a base64 string, alongside other elements of the precision feedback message. The precision feedback email is then created using this figure, the necessary text data, and is then sent to the recipient.

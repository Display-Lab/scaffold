# Improving Causal Pathway Vignette

## Introduction

This vignette illustrates the process for generating precision feedback messages about a recipient's performance when it is improving. Feedback messages about improving performance motivate providers by enhancing providers' knowledge about their performance trends and fostering a sense of optimism. Example feedback messages that are part of the Improving Causal Pathway include "Your performance is improving" and "Congratulations on your improved performance." 

A healthcare quality improvement consortium called the Multicenter Perioperative Outcomes Group (MPOG) uses precision feedback to prioritize motivating performance information about the quality and outcomes of operative cases. A performance measure that MPOG assesses for operative cases regards the minimization of the use of climate-sensitive anesthetic gases: [BP-03: Low Map Prevention < 65](https://spec.mpog.org/Spec/Public/34).

## Performance Data

A healthcare quality improvement consortium called the Multicenter Perioperative Outcomes Group (MPOG) uses precision feedback to prioritize motivating performance information about the quality and outcomes of operative cases. A performance measure that MPOG assesses for operative cases regards the minimization of the use of climate-sensitive anesthetic gases: [BP-03: Low Map Prevention < 65](https://spec.mpog.org/Spec/Public/34).

### Healthcare professional performance
MPOG has received operative case data from last month about Gaile and Gaile's cases and that of their peers. MPOG calculates the following performance information for the measure BP-03:

### Healthcare professional performance
Deepa, a dedicated Certified Registered Nurse Anesthetist (CRNA) at Midwest Medicine, has the following performance data over the last 6 months for BP-03:

|Month|Performance Level|Peer Average|75th Percentile Benchmark|90th Percentile Benchmark|MPOG Goal|
|-----|---------|---|---|---|---|
|Jul  |      75%| 80| 85| 90| 90|
|Aug  |      75%| 80| 85| 90| 90|
|Sept |      75%| 80| 85| 90| 90|
|Oct  |      75%| 80| 85| 90| 90|
|Nov  |***82%***| 80| 85| 90| 90|
|Dec  |***87%***| 80| 85| 90| 90|

Gaile, a resident at Midwest Medicine, has the following performance data over the last 6 months for BP-03:

|Month|Performance Level|Peer Average|75th Percentile Benchmark|90th Percentile Benchmark|MPOG Goal|
|-----|---------|---|---|---|---|
|Jul  |      85%| 85| 88| 92| 90|
|Aug  |      85%| 85| 88| 92| 90|
|Sept |      85%| 85| 88| 92| 90|
|Oct  |      85%| 85| 88| 92| 90|
|Nov  |***87%***| 85| 88| 92| 90|
|Dec  |***90%***| 85| 88| 92| 90|

## Preference data
Preferences for precision feedback are elicited through a preference survey that providers can take. The preference survey produces a preference model for each provider that, with the provider's permission, is shared with MPOG to maintain. MPOG analyses preference data that is shared to identify population-level preference segments. These segments are generated as preference profiles that can serve as a default preference model for an organization, or which can be selected by providers who do not take the preference survey, but who identify preferences that are close enough to their own in the settings menu for the precision feedback system.

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

Gaile's preference data (Midwest Medicine group profile) :

|Motivating information |Utility value|Description                                                                     |
|-----------------------|-------------|--------------------------------------------------------------------------------|
|Social better	        |-2           |Performance is high this month.                                                 |
|Social gain            |13	      |Performance was previously low, but it has improved to reach the peer benchmark.|
|Social stayed better   |6            |Performance is consistently high (no recent change).                            |
|Worsening             	|-22	      |Performance is worsening.                                                       |
|Improving	        |3            |Performance is improving.                                                       |
|Social loss            |10	      |Performance was previously high, but it has dropped below the peer average.     |
|Social worse           |-15          |Performance is low this month.                                                  |
|Social stayed worse    |-8           |Performance has remained below average (no recent change).                      |
|Social approach        |15	      |Performance is improving, getting closer to the peer benchmark.                 |
|Goal gain              |13	      |Performance was previously low, but it has improved to reach the goal.          |
|Goal loss	        |10	      |Performance was previously high, but it has dropped below the goal.             |
|Goal approach          |14           |Performance is improving, getting closer to the goal.                           |

|Display format         |Utility value|
|-----------------------|-------------|
|Bar chart              |1            |
|Line chart             |0	      |
|Text only              |0            |

# Precision feedback message generation
To generate precision feedback, MPOG sends de-identified performance and preference data to a precision feedback system that processes each provider's data with their peer comparator performance data. The precision feedback system produces and evaluates candidate messages using metadata from message templates, then selects an optimal precision feedback message to return to MPOG. The precision feedback system is a knowledge-based system that is comprised of the following parts: 1) A knowledge base, 2) A software pipeline, and 3) A web service.

## Precision Feedback Knowledge Base
The knowledge base contains the following components: Causal pathways, message templates, and performance measures.

## Improving Causal Pathway
This pathway describes the influence of feedback interventions that show the message recipient that their performance has improved. The causal pathway model is made up of preconditions, moderators, mechanisms, and outcomes.

### Preconditions
Preconditions for improving are factors that are necessary for the success of the feedback intervention using this pathway. The improving pathway has the following preconditions:

Information content preconditions:
1. [Positive performance trend content<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO/?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000099)

Message preconditions:
1. [Positive performance trend set<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO/?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)
 
### Moderators
Moderators are factors that inhibit or promote the influence of the feedback intervention on the recipient. The improving causal pathway has the following moderators:
1. `Message recency` - The number of months since this message was delivered previously.
2. `Message delivery count` - How many times has the recipient previously received this message in the last year?  
3. `Regulatory fit` - To what extent is this message aligned with characteristics of the behavior/task, context, and recipient personality, with regard to motivation to avoid negative outcomes / problem (prevention focus), or motivation to achieve positive outcomes / develop and learn (promotion focus)?
4. `Gap size` - How large is the gap between the recipient's performance level and that of the social comparator?

### Mechanisms
Mechanisms are factors that the intervention operates through to influence the feedback recipient. The social loss pathway has the following mechanisms:
1. `Awareness (knowledge)`: The message may change the recipient's awareness of their high performance, relative to peers.
2. `Optimism` - The message may influence the recipient's confidence that things will happen for the best and they will continue to increase their performance, gaining social status.

### Outcomes
The expected outcome of the successful influence of an email that uses the improving pathway is clinical process performance improvement.

## Message templates
Message templates represent a possible motivational message that a precision feedback system can send. There are two message templates that the precision feedback system can access for this vignette: 

A. `The Performance Improving`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/performance_improving.json) message template contains the following message: 
> Your performance is improving this month for the measure [measure name].

This message template `is about`[<sub>(OntoBee)</sub>](http://purl.obolibrary.org/obo/IAO_0000136) the following features of performance data:
1. [Positive performance trend set<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO/?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)
2. Display format compatibility: [Line Graph <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/IAO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FIAO_0000573), [Bar Chart <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/STATO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FSTATO_0000166)<!--, text only (TODO ?)-->

B. The `Congrats Improved Performance`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/congrats_improved_performance.json) message template contains the following message: 
> Congratulations on your improved performance this month for the measure [measure name].

This message template [is about<sub>(BP)</sub>](http://purl.obolibrary.org/obo/IAO_0000136) the following features of performance data:
1. [Positive performance trend set<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO/?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)
2. Display format compatibility: [Line Graph <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/IAO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FIAO_0000573), [Bar Chart <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/STATO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FSTATO_0000166)<!--, text only (TODO ?) -->

## Software Pipeline (Precision Feedback Pipeline)
### Recipient annotation generation (Bitstomach)
The first stage of the pipeline is a script called Bitstomach. This script analyzes recipient's performance data and generates features called **annotations**. These annotations describe features of the performance data such as performance trends over time, or how performance measures relate to other values like peer performance benchmarks and institutional performance goals.

**Annotations for Deepa's performance data for the most recent month:** 
1. `Social comparator content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000095)
2. `Positive performance trend content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000099)
3. `Negative performance gap content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000105)
    - *with respect to* [Peer 90th percentile comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000129)
    - *with respect to* [Goal comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000046)
4. `Positive performance gap content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000104) 
    - *with respect to* [Peer average comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000126)
    - *with respect to* [Peer 75th percentile comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000128)

**Annotations for Gaile's performance data for the most recent month:**
1. `Social comparator content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000095)
2. `Positive performance trend content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000099)
3. `Negative performance gap content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000105)
	- *with respect to* [Peer 90th percentile comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000129)
4. `Positive performance gap content` [<sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000104)
	- *with respect to* [Goal comparator element <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000046)
    - *with respect to* [Peer 75th percentile comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000128)
    - *with respect to* [Peer average comparator <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000126)

### Candidate Message Generation (Candidate Smasher)
The second stage of the pipeline creates two candidate messages that may be appropriate for each recipient to recieve. It does this by searching through the message template library and selecting two message templates with annotations that match those annotations of the recipient's performance.

**Deepa's candidate messages (A & B):**

**Candidate Message A** is the `The Performance Improving`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/performance_improving.json) message template, which has the following annotations *in common* with the performance annotations:
1. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)

**Candidate Message B** is the `Congrats Improved Performance`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/congrats_improved_performance.json) message template, which has the following annotations *in common* with the performance annotations:
1. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)

Both candidate messages have annotations matching those generated from Deepa's performance data, and are therefore appropriate as candidate messages.

**Gaile's candidate messages (α & β):**

**Candidate Message α** is the `The Performance Improving`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/performance_improving.json) message template, which has the following annotations *in common* with the performance annotations:
1. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)

**Candidate Message β** is the `Congrats Improved Performance`[<sub>(GH)</sub>](https://github.com/Display-Lab/knowledge-base/blob/main/message_templates/congrats_improved_performance.json) message template, which has the following annotations *in common* with the performance annotations:
1. [Positive performance trend set <sub>(BP)</sub>](https://bioportal.bioontology.org/ontologies/PSDO?p=classes&conceptid=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FPSDO_0000120)

Both candidate messages have annotations matching those generated from Gaile's performance data, and are therefore appropriate as candidate messages.

### Candidate Message Preconditions Evaluation (ThinkPudding)
The third stage of the pipeline processes and evaluates the candidate messages for each persona based on preconditions. It compares the annotations associated with the message candidates and checks them against the persona's performance data annotations to determine which candidate messages are acceptable based on message preconditions. 

For Deepa, **Candidate B** is acceptable by the causal pathway **improving**.

For Gaile, **Candidate α** is acceptable by the causal pathway **improving**.

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
| Value              | 0                       | 0.8                     | 0              | -0.1                | -0.1                 | 1              | 1                 |

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

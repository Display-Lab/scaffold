# Precision Feedback Knowledge Base (PFKB)
![](https://img.shields.io/badge/stable_version-v1.8-blue)

PFKB is a collection of models and algorithms for the purpose of generating precision feedback. It is designed to be used by [SCAFFOLD](https://github.com/Display-Lab/scaffold) (Scalable Coaching and Appreciation Feedback For Optimal Learning and Decision-making), a precision feedback system. processing clinical performance data to identify coaching and appreciation feedback messages that may represent the highest-value performance information an organization has for healthcare professionals to learn to improve and sustain their clinical performance.


## Elements of the Knowledge Base
The Precision Feedback Knowledge Base is comprised of five primary elements. These elements are 1) quality measures, 2) message templates, 3) motivating performance information, 4) causal pathway models, and 5) message scoring models. Each element is described in detail below. We have also developed a collection of vignettes to illustrate the function of PFKB within a precision feedback system. PFKB is a work in progress that currently contains working examples of quality measures, message templates, and causal pathway models. Motivating performance information and message scoring models are not yet fully implemented as a part of the PFKB.

Taken together, all of the elements in the knowledge base can be used by a precision feedback system to prioritize motivating feedback messages. For example, if a person (the precision feedback message recipient) is performing below average but is improving, a precision feedback system could use information about the recipient's preferences and past performance to determine whether or not to prioritize and deliver one of the following messages: "You are not a top performer", "Your performance is improving", "Your performance is approaching the benchmark", or "You may have an opportunity to improve."


### Performance measures
Each performance measure is an indicator or metric that represents a standard for measuring performance, here providers of healthcare services. Performance measures are commonly grouped into process measures that assess care-related decisions and actions, and outcome measures that assess the resulting impact on patients' experiences and health.


### Message templates
A message template is a concise text statement that describes clinical performance in terms of brief events or a healthcare professional's perforamnce status. Example message templates are "Your performance dropped below average", "You reached the goal", and "You are a top performer". Each message may potentially be matched with a healthcare professional's performance data, and be scored by a precision feedback system to identify it's motivational potential as a coaching or appreciation message.  The message templates in PFKB are implemented semantically in a computer-processable format using a linked-data approach (JSON-LD), based on the Performance Summary Display Ontology (PSDO).


### Motivating performance information
Motivating performance information is the information that healthcare professionals seek when viewing a performance dashboard or feedback report, to interpret their performance data. This including comparisons, trends, acheivements, and losses that can guide future efforts to improve or sustain performance. We have developed a set of functions that annotate performance information with the motivating performance information for any feedback recipient.


### Causal pathway models
Causal pathway models are logic models that associate a message template with the necessary motivating performance information in performance data, and the intended purpose of the message that can be used to score its motivational potential, as a coaching or appreciation feedback messages. Each causal pathway specifies the influence of *motivating information*, such as performance comparisons, on health-related outcomes through a feedback recipient. As elements of the knowledge base, causal pathways serve the dual purposes of 1) explaining why feedback interventions may influence behavior (i.e. program theory), and 2) configuring a precision feedback intervention to generate messages that can be delivered to recipients in emails, reports, or by other means. The causal pathways are implemented semantically in a computer-processable format using a linked-data approach (JSON-LD), based on the Performance Summary Display Ontology (PSDO) and the Causal Pathway Ontology (CPO).


### Message scoring models (in progress)
Message scoring models assess the motivational potential of possible messages, based on a message template and the recipients' performance data, to be delivered as coaching or appreciation messages to healthcare professionals. These scoring models receive a set of acceptable candidate messages and their motivating performance information annotations as inputs, and score messages based on the moderating characteristics specified in the causal pathway model for each acceptable candidate message. A message scoring models are planned for coaching, appreciation, and to enable organizations to adjust the proportion of coaching and appreciation messages that a precision feedback message system provides, as high-priority messages are selected and delivered to individuals and teams.


## Illustration of PFKB use with vignettes about anesthesia care
Vignettes tell a narrative story that demonstrate the use of PFKB by a precision feedback system, for two personas who represent anesthesia providers with different preferences and different performance data. Each vignette is also associated with one casual pathway and associated message templates. Each vignette includes example performance data, motivating performance information, and example messages formatted according to relevant message templates. The purpose of each vignette is to bring together the core components of the knowledge base as they would be used to generate precision performance feedback. Overall, the vignettes illustrate how a causal pathway is used by a precision feedback system to deliver motivating information to one or more feedback recipients, based on their performance data, their preferences, and a collection of message templates that determine a minimal set of possible feedback interventions.

This project is supported by funding from the NIH National Library of Medicine awards: "A knowledge-based message tailoring system" (1K01 LM012528-01) and "A scalable service to improve health care quality through precision audit and feedback" (5R01LM013894-01).

## Knowledge Base Component File Locations

The causal pathways are located in the /causal_pathways directory.

The message templates are located in the /message_templates directory.

Specifications of quality measures are kept in the file measures.json.

Each causal pathway is described in a corresponding vignette directory.


## Governance Policy
The knowledge base contains files on a spectrum of developmental states, from robustly functional to pre-pseudocode. Versioning of the knowledge base may implement breaking changes, and as such a registry of stable pairs are maintained by the Display-Lab team. Stable release pairs of the software pipeline and knowledge base are recorded as new versions are released, to ensure full functionality of the pipeline despite the changing nature of the knowledge base. Future versions of the knowledge base may be independent of the software pipeline's version, and may be developed for standalone uses.

|Release Pair| Knowledge Base Version | Software Pipeline Version | 
|-|-|-|
| 2/12/25 | ![Knowledge-Base](https://img.shields.io/badge/version-v1.8-blue) | ![SCAFFOLD](https://img.shields.io/badge/version-v2.1-blue) |







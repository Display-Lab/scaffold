
## Overview

## Motivating information

## History elements
In calculating the final score the contribution of history is inverted and multiplied by a per causal pathway weight (the less history the higher the score). When the message or measure has been selected more often or more recently the history score would be lower.

The individual moderators listed below are weighted on a per causal pathway basis using weights from the MPM. The MPM weightings are only relative weightings for different history sub moderators. The _history_ column of the MPM contains the between-causal-pathway weights. The calculated value applying moderator weights and between-causal-pathway weight is still an inverse moderator. So the final history score is calculated by inverting the calculated value. For example, for the _social better_ pathway:
```
 history_score = 1 - (message_recurrence * 0.14 + message_recency * 0.14 + measure_recurrence * 0.72) / (0.14 + 0.14 + 0.72) * 0.7
 ```
In the above example for the _social better_ example measure recurrence is more important than message recurrence or message recency. The weights per causal pathway should sum up to 1 but, just in case they don't, we also normalize the total history score by deviding by individual moderator weights. After applying the MPM weight on moderators the between-causal-pathway weight (0.7 for _social better_) is applied. Then, because history is an inverse moderator, the final history score is adjusted using 1 minus the calculated value. 

 `history_score` will be a value between 0 and 1 with 0 being the least motivational (the most history) and 1 being the most motivational (the least history).

The final scoring algorithm incorporates the history score directly:
```
score = motivating_score * 1 + history_score * 2 + preferences_score * 1.3
```

### message_recurrence (0-1, 1 is most history = least motivational potentional)
The _signal property_ is the number of times the candidate message has been selected in the last 12 month. Actual data may not contain all month. This is just a simple count.

The _moderator_ is the count devided by 12. 0 is no recurrence and 1 is 12 messages in the last year.

### message_recency (0-1, 1 is most recent history = least motivational potentional)
The _signal property_ is the number of month since the last time this candidate message was selected. 

The _moderator_ is 1 minus the count, devided by 12. 1 is message was sent most recently, and 0 is the message has not been sent in the last year.

### measure_recurrence (0-1, 1 is most history = least motivational potentional)
The _signal property_ is the number of times a message for this candidate's measure has been selected in the last 12 month. Actual data may not contain all month. This is just a simple count.

The _moderator_ is the count devided by 12. 0 is no recurrence and 1 is 12 messages with the same measure in the last year.

### measure_recency (0-1, 1 is most recent history = least motivational potentional)
The _signal property_ is the number of month since the last time a message for this candidate's measure has been selected. 

The _moderator_ is 1 minus the count, devided by 12. 1 is a message with this measure was sent most recently, and 0 is a message with this measure has not been sent in the last year.

### history column
This column contains the between-causal-pathway weights.


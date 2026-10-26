# Precision Feedback Knowledge Base (PFKB) - Changelog
## Version 1.1.1
### 2/28/24 (release not published)
 - Added motivating performance information and message scoring models directories
 - Reorganized files and added description in readmes





## Version 0.1.2
### 11/6/23 (release not published)
**Patch:** Measure name change in input_messages
- Crosscheck and correct changes from measures.json against input_message.json files

## Version 0.1.2
### 11/6/23 (release not published)
**Patch:** Message template changes
- Fixed message text keys to have internally consistent programmatically acceptable keys for filling with information when createprecisionfeedback process is run
    - Not updated for:
        - congrats_improved_performance 
        - consistently_high_performance
        - remain_low_performance
        - Potentially not moving forward with these templates, other cedar changes in the works but not in this patch
- Separated parts of the message text into text message and additional message text
    - Supporting this change with changes to pictoralist

**Patch:** Update vignettes with standard template for all software pipeline sections
- Updated introductory texts on all software pipeline sections for:
    - Goal Approach
    - Goal Gain

- Updated Esteemer and Pictoralist sections for the following vignettes:  
    - Goal Loss
    - Improving
    - Social Approach
    - Social Better
    - Social Worse
    - Worsening
    - NOTE: Need to calculate and enable example ranks for all personas


- TODO: Annotations and other persona-specific details need to be updated to reflect the personas in use for the following:  
    - Goal Approach
    - Goal Gain

## Version 0.1.0
### 10/24/23 (release not published)
**Improvement:** Added changelog  
- Implementing semantic versioning for PFKB, first step towards initial release
    - Need to have proper version control prior to pilot for rollback protection, work around breaking changes
    - See the governance policy [here][def]

**Improvement:** Added all extant measures used by MPOG to measures definition file  
- Will prevent errors from generating based on the sending of an "improper" measure  
    - Intend to have data pre-processed to avoid informational process and inverse measures
    - Using measures.json to filter (really more elegant error handling) a potential feature >1.0.0 
[def]: https://github.com/Display-Lab/knowledge-base#governance-policy

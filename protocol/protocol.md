# Protocol Capstone Enefit
## Basic info

* [Project](https://www.kaggle.com/competitions/predict-energy-behavior-of-prosumers/overview)
* [Kanban Board](https://github.com/users/VadymKhvoinytskyi/projects/1/views/1)
* [Milestones](https://github.com/VadymKhvoinytskyi/Enefit-capstone-project/milestones?with_issues=no)

## Open questions
1. Why has datablock 1 no corresponding client? (there were assumptions, but not solved)

## NEXT 1.12.23 
### Plan for today
* Continue working on merge
* Firgure out, why our merge of train and client on datablock_id generates empty Nat values in date and how this is a problem

## 30.11.23
### Plan for today
Merge data (in group) - and/or quick EDA on individual tables (subgroups/individual)?

* Data Block ID 0 abd 1 have no corresponding entries in train

## 29.11.23 - Getting to know the data structure
* Mainly discussed when data is gathered for prediction and how the relate to each other
* Assumption: data will be merged/circle around data_block_id, because those data blocks take in to account that certain data availability is lagging (via API). [See details here](https://www.kaggle.com/competitions/predict-energy-behavior-of-prosumers/discussion/455833) and [here](https://www.kaggle.com/competitions/predict-energy-behavior-of-prosumers/discussion/455100).
* Alternative idea is to merge on client.csv and forecast dates, but potentially this brings the problem of lagging (see above) back into play
* Consumption and Production is held in separate columns. Unclear yet if we would have different models for consumption / production prediction. But in message from [host](https://www.kaggle.com/competitions/predict-energy-behavior-of-prosumers/discussion/455833) it asks about net consumption, so that might not be way to go.

<img src="./resources/enefit_data_chart.png">
<img src="./resources/Enefit_train_data_mindmap.png">
<img src="./resources/data_avail.png">
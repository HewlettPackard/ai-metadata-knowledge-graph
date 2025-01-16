## Nomenclature mapping of various data sources


| CMF | Papers-with-code | OpenML | Kaggle | Huggingface |
|-----|------------------|--------|--------|-------------|
| **Pipeline** | Paper |  | NA | NA |
| End to end AI pipeline which consists of (i) processing stages such as data pre-processing, training, testing, evaluation and so on (ii) artifacts such as dataset, pre-processed data, models and so on |
| **Project** | Task | Task	| Task | Task |
| What is the task being performed in the pipeline? Example: Image classification, Video instance segmentation |
| **Stage(s)** | Available in the Paper | NA | NA | NA |
| Processing stages of a pipeline such as data pre-processing, training, testing and so on.	|
| **Execution(s)** | Only one execution is available for all the pipelines from these sources. OpenML has multiple executions for some pipeline but requires additional processing and not explicitly available. |
| Different executions of the same pipeline with varying input or parameters for any or multiple stages of a pipeline |	
| **Artifacts** |
| Various components of an AI pipeline that undergoes various processing stages in a pipeline. Artifacts can be dataset, pre-processed data, models and so on |
| _Dataset_ | Dataset | Dataset | Dataset | Dataset | 
| What is the dataset used in the pipeline?|	
| _Model_ | Method | Flow (Model name is available under flow) | Model | |
| Name of the model(s) used in the pipeline. Example: Resnet, Custom CNN |
| **Parameters** |
| Parameters can be model parameters, hyperparameters and other pipeline parameters. |
| _Model Parameters_ | Method | Flow (Model parameters is available under flow) |  | Model (Model parameters is available under models)
| Model parameters can be number of layers, number of embedding dimensions and so on |	
| _Hyperparameters_ | Available in the Paper | Parameters are available under runs and flows |  | Available for some under model page |
|mWhat are the corresponding hyperparameter setting required to train the model? Any additional regularization and generalization techniques used? |				
| **Metrics** |
| Metrics that can be used to evaluate the pipeline. It could be model evaluation metrics or performance evaluation metrics	|
| _Evaluation_ | Evaluations (The Evaluations end point contains evaluation metrics for a given task) |	Evaluations | | Available for some under model page|
| What are the evaluation metrics used to evaluate the task? Example: F1 score, median retrieval score |			
| _Results_ | Results | Evaluations |  |  |
| What are the best scores obtained for the evaluation metrics mentioned above? | 	



## Amount of data from the data sources

| Componenets | Papers-with-code | OpenML | CMF | Kaggle | HuggingFace |
|-------------|------------------|--------|-----|--------|-------------|
| #Pipelines | ~ 1 Mi | ~ 10 Mi | ~100 | 160,000 | 76,920 |
| #Tasks | 3685 | 46,592 | 46 | ~200+ | 397 |
| #Datasets | 12,212 | 3438 | 45+ | 173,645 | 11,540 |
| #Models | 2000 | 16,316 | 33 | NA | 76,920 |







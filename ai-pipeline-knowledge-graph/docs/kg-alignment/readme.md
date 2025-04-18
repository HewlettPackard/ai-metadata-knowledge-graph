## Data Sources
#### Papers-with-code
Papers-with-Code provides extensive metadata for research papers and associated code repositories, encompassing over 1 million entries. The metadata covers various components and stages of AI pipelines described in the papers. Through their API, Papers-with-Code offers metadata including PDF URLs, GitHub repository links, task details, dataset information, methods employed, and evaluation metrics/results. While not all stages of metadata are available for every paper through the API, the information can still be obtained by referring to the research papers and their code repositories.

#### OpenML
OpenML provides metadata on machine learning pipelines logged by users, offering detailed information on tasks, datasets, flows, runs with parameter settings, and evaluations. OpenML encompasses eight major task types executed on various datasets, resulting in 1,600 unique tasks. For each task, most recent 500 runs have been collected which amounts to a total of 330,000 runs.

#### Huggingface
Huggingface is a model hub that offers users access to numerous pretrained models. It covers a wide range of tasks, including computer vision, natural language processing, tabular data, reinforcement learning, and multimodal learning. Huggingface provides model-centric information, along with datasets and evaluations, enabling the construction of complete pipelines. Currently, approximately 50,000 pipelines have been collected from Huggingface.


## Alignment of KG Concepts
As the data from various sources follow different nomenclature and data structure, we propose Common Metadata Ontology(CMO) to unify them. The mapping of each data source to CMO can be found below.


|     **Nodes   in Common Metadata Ontology**                                                                             |     **Papers-with-Code**                  |     **OpenML**                   |     **Huggingface**                   |
|---------------------------------------------------------------------------------------------------------------------|-----------------------------------------|------------------------------|-------------------------------------|
|     **Pipeline:**  AI pipeline executed to solve a Task                                                               |     Extracted from   Paper              |     Flow                     |     Extracted from   Models         |
|     **Report:**     Any   published text document regarding the pipeline implementation                                  |     Paper                               |     Extracted from   runs    |     Extracted from   Model Cards    |
|     **Task:**     The   AI Task for which the pipeline is implemented. Example: image classification                     |     Task                                |     Task type   + Dataset    |     Pipeline   Tag                  |
|     **Framework:**     The   framework used to implement the pipeline and their code repository                          |     Extracted from   Git Repository     |     Extracted from   Runs    |     Library                         |
|     **Stage:**     Various   stages of the pipeline such as data preprocessing, training, testing or   evaluation        |     Generated                           |     Generated                |     Generated                       |
|     **Execution:**     Multiple   executions of a given stage in a pipeline                                              |     Generated                           |     Runs                     |     Generated                       |
|     **Artifact:**     Artifacts   such as model, dataset and metric generated at the end of each execution               |     Generated                           |     Generated                |     Generated                       |
|     **Metric:**     Subclass   of artifact. The evaluation result of each execution                                      |     Evaluation   and Results            |     Extracted from   runs    |     N/A                             |
|     **Dataset:**     Subclass   of artifact. The dataset used in each execution.                                         |     Dataset                             |     Dataset                  |     Dataset                         |
|     **Model:**     Subclass   of artifact. The model used in each execution or produced as a result of an   execution    |     Method                              |     Extracted from   Flow    |     Model                           |
|     **Hyperparameters:**     Parameter   setting using for each execution of a stage                                     |     N/A                                 |     Extracted from   runs    |     N/A                             |


The current data source do not provide a detailed information on the stage (data preprocessing, training or testing) of the pipeline excution. On the other hand, we know that the pipeline metadata exposed are for train/test stages. Hence we generate the information for stage and so execution. The properties of each node can be found at [common-metadata-ontology](../common-metadata-ontology/readme.md).



## Data Sources
This repository consists of a list of data sources from which the pipeline metadata were collected. The code to download data for respective data sources can be found here.

### OpenML

In OpenML, the API for each item is slightly different from the dataframe collected and saved as a CSV. The overall description is included here. In order to access the data, please contact the repo owner.

**Datasets** <br />
Dataset consists of dataset name, characteristics and downloadable link. There are 4333 datasets, of which 3438 are unique. The number of unique dataset in the Task dataframe is 2727, meaning, only 2727 datasets have runs. The rest of them were not utilized to run any machine learning tasks yet.

**Tasks** <br />
A task consists of a dataset, together with a machine learning task to perform, such as classification or clustering and an evaluation method. For supervised tasks, this also specifies the target column in the data. There were  more than 46,000 tasks and only 8 of them are unique.

**Flows** <br />
Flows consists of machine learning algorithm from a particular library or framework. It contains, name, parameters of the algorithm and the version that was used in the runs. This is a unique list of all algorithms used in all of their runs. Each run has a flow id mentioned. Using this the list of runs where a particular flow(machine learning algorithm) was used can be determined. There are 16316 flows.

**Runs** <br />
A run is a particular flow, that is algorithm, with a particular parameter setting, applied to a particular task. There are 10 million runs and the dataframe for runs is yet to be obtained.

For more information, please refer the documentation - https://docs.openml.org/#tasks <br />
For more information on API functions and calls, please refer - https://docs.openml.org/Python-API/


### PapersWithCode
PapersWithCode consits of 980k papers. From each paper we can collect abstract, dataset, task, methods, result, evluation metrics, paper url and code repository url. But this information is not available for all the papers through their API. Further, papers specific to a conference can also be collected. Refer to the readme inside papers-with-code for detailed information

**Datasets** <br />
Dataset consists of id, name and external URL to the dataset page where a download link can also be found. There are 11220 datasets. They do not have characteristics of the datasets.

**Tasks** <br />
Task consists of id, name of the task and description if available. There are 3166 unique tasks obtained from 980k papers. The tasks from PapersWithCode are more specific than OpenMl. Example: Video instance segmentation, Video object segmentation, Tropical cyclone intensity forecasting and so on.

**Result** <br />
Results are specific to papers and can be obtained for a given paper-id. It consists of list of metrics used along with their best values reported in the paper.  


For more information about the API documentation, please visit - https://paperswithcode.com/api/v1/docs/ . You can play with the API through the Swagger UI. <br />
To download the data, please visit - https://github.com/paperswithcode/paperswithcode-data






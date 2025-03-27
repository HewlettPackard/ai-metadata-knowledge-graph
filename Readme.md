## AI Pipeline Metadata Knowledge Graph
<p align="justify">
The emergence of advanced Artificial Intelligence (AI) models has driven the development of frameworks and approaches that focus on automating model training and hyperparameter tuning of end-to-end AI pipelines. However, other crucial stages of these pipelines such as dataset selection, feature engineering, and model optimization for deployment have received less attention. Improving efficiency of end-to-end AI pipelines requires metadata of past executions of AI pipelines and all their stages. Regenerating metadata history by re-executing existing AI pipelines is computationally challenging and impractical. To address this issue, we propose to source AI pipeline metadata from open-source platforms like Papers-with-Code, OpenML, and Hugging Face. However, integrating and unifying the varying terminologies and data formats from these diverse sources is a challenge. In this paper, we present a solution by introducing Common Metadata Ontology (CMO) which is used to construct an extensive AI Pipeline Metadata Knowledge Graph (AIMKG) consisting of 1.6 million pipelines. Through semantic enhancements, the pipeline metadata in AIMKG is also enriched for downstream tasks such as search and recommendation of AI pipelines. We perform quantitative and qualitative evaluations on AIMKG to search and recommend relevant pipelines to user query. For quantitative evaluation we propose a custom aggregation model that outperforms other baselines by achieving a retrieval accuracy (R@1) of 76.3%. Our qualitative analysis shows that  AIMKG-based recommender retrieved relevant pipelines in 78% of test cases compared to the state-of-the-art MLSchema based recommender which retrieved relevant responses in 51% of the cases. AIMKG serves as an atlas for navigating the evolving AI landscape, providing practitioners with a comprehensive factsheet for their applications. It guides AI pipeline optimization, offers insights and recommendations for improving AI pipelines, and serves as a foundation for data mining and analysis of evolving AI workflows.
 </p>

<br>

<div style="text-align: center; margin-bottom: 20px;">
  <figure style='display: table'>
  <img src='figures/UI.png'>
  <p>
    Figure 1:Dashboard of AI pipeline Recommender that uses Dynamic AI Pipeline Constructor to recommend relevant pipelines
  </p>
</figure>
</div>

<br>


### AIMKG Set up Guide
The construction details of AIMKG and recommendation can be found below in the next sections. To set up AIMKG, please follow the steps below. The steps below show how to download open source data and ingest it into the neo4j database. You can skip this step and directly operate on preloaded graph data as per instructions later. 

* Download the most recent version of docker as per your OS from here - https://docs.docker.com/desktop/release-notes/ and install the `docker` and `docker-compose-plugin` on your system
* Navigate to `ai-pipeline-knowledge-graph` folder. Create a .env file using env-example as template. and modify the parameters in .env file. Change the $USER and UID=`id -u` and GID=`id -g` in .env file. To find out the values `echo $USER` and `echo $UID` from your command terminal
* Create a virtual environment `python3 -m venv <myenv>` and activate it using `source <myenv>/bin/activate` or `conda create -n aimkg python=3.9` and activate it `conda activate aimkg`
* Run `pip install -r requirements.txt`
* Create a folder named `$HOME/graph_data` where the neo4J graph database will be created
* Create a folder named `$HOME/neo4j_plugins`. 
Download the neo4j plugin [apoc-5.16.0-extended.jar](https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/5.16.0/apoc-5.16.0-extended.jar) or (https://drive.google.com/file/d/12iVJVKnC4H-dYCx_-vhaKJwk9zzpXWzy/view?usp=sharing) and put it into the folder named `$HOME/neo4j_plugins`.
* Create a folder named `$HOME/raw_files` where the neo4j source data will be stored
* Download the sample dataset (dataset-small.zip) for AIMKG from [here](https://drive.google.com/drive/folders/1FcUOe98w7Mlcfg49icSAuCdFh-PH72GE?usp=sharing). Unzip into a folder named `raw_files`. `unzip dataset-small.zip -d $HOME/raw_files`. The resulting folder should have `$HOME/raw_files/nodes` and `$HOME/raw_files/relationships`
* Update the paths used in the docker-compose.yml file. Mention full path. For example: 
* * `$HOME/raw_files:/var/lib/neo4j/import`
* * `$HOME/graph_data:/data`
* * `$HOME/neo4j_plugins:/var/lib/neo4j/plugins`
* The docker-compose recipe in `ai-pipeline-knowledge-graph` folder stands up a neo4j local instance and a jupyter server. Command to stand up both containers `docker compose up --build -d`
* Access the notebook server at: `https://localhost:8888` 
* Access the neo4J Browser at: `https://localhost:7474`. 
* Run the notebook named `small_dataset.ipynb` to ingest data into the graph database (from `$HOME/raw_files` into $HOME/graph_data )
* The graph can be explored with the sample queries given in the [Sample Queries](#sample-queries) section . 

#### Datasets 
* We have provided three kinds of datasets: 
* Small dataset is [`dataset-small.zip`](https://drive.google.com/file/d/1JEdhTNE2OmZLcXrNqzg91srSF11zsfi5/view?usp=drive_link) This is a small randomly selected subset of all open source data. This is loaded by running the notebook: `small_dataset.ipynb` 
* Full dataset is [`dataset-large.zip`](https://drive.google.com/file/d/1kDExDrVAXC6fqJvc4PLW3L45slDMavvV/view?usp=drive_link). This is loaded by running the notebook s `pwc_kg.ipynb, openml_kg.ipynb and hf_kg.ipynb` IN THAT ORDER. The `$HOME/raw_files` folder should look like `raw_files/pwc`, `raw_files/open-ml` and `raw_files/huggingface`
* Neo4J Dump: This the state of the neo4J database after the full database is loaded. This can be directly used by downloading neo4j_dump.zip, unzip it and put this data into `$HOME/graph_data` folder (leave `$HOME/raw_files` folder empty. Since the data is already in the neo4J format, you can directly execute the sample queries [Sample Queries](#sample-queries) below in the neo4j browser. There is no need to execute any notebooks in that case. 


#### Sample Queries to explore AIMKG manually
Following are some sample queries that can be run to test and visualize the data. Enter them in the `neo4j$:` CLI on `http://localhost:7474` (after logging in with credentials you set in .env file). The LIMIT 250 is to enable limited data to be displayed (can be removed on a more capable system)

* Pipelines used for text classification:
```
MATCH path= ((:Task {category:'classification', modality:'text'})-[r1]-(p:Pipeline)-[r2]-(m)) RETURN path LIMIT 250
```

* Pipelines with classification as task (not necessarily text):
```
MATCH path = ((:Pipeline)-[]->(:Task {category:'classification'})) RETURN path LIMIT 250
```

* Datasets used text recognition
```
MATCH path = ((:Task {category:'recognition', modality:'text'})-[]-(:Pipeline)-[]-(:Stage)-[]-(:Execution)-[]-(:Artifact)-[](:Dataset)) RETURN path LIMIT 250
```


* Shows all Metrics generated on/from MNIST dataset
```
MATCH path = ((:Dataset {srcID:'mnist'})-[]-(:Artifact)-[]-(:Metric)) RETURN path LIMIT 250
```


* Datasets and Models used by pipelines that executes some form of 'image detection' task
```
MATCH (a:Artifact)-[r3]-(e:Execution)-[r4]-(s:Stage)-[r5]-(p:Pipeline)-[r6]-(t:Task{category:'detection', modality:'image'})
WITH a,e,s,p,t,r3,r4,r5,r6
MATCH (d:Dataset)-[r1]-(a)-[r2]-(m:Model)
RETURN d, a, m, e, s, p, t, r1, r2, r3,r4, r5, r6 limit 100

```

* Pipelines which are from papers-with-code and enriched with models from huggingface.
```
MATCH (t:Task)-[r1]-(p:Pipeline {source:'papers-with-code'})-[r2]-(s:Stage)-[r3]-(e:Execution)-[r4]-(a:Artifact)
WITH t,p,s,e,a,r1,r2,r3,r4
MATCH (d:Dataset)-[r5]-(a)-[r6]-(m:Model {source:'huggingface'})
return t,p,s,e,a,r1,r2,r3,r4,d,m,r5,r6 LIMIT 250
```

* Dataset, model and pipelines that uses the modelclass 'gpt2'
```
MATCH (d:Dataset)-[r1]-(a:Artifact)-[r2]-(m:Model {modelClass:'gpt2'})
WITH d,a,m,r1,r2
MATCH (a)-[r3]-(e:Execution)-[r4]-(s:Stage)-[r5]-(p:Pipeline)-[r6]-(t:Task)
RETURN d, a, m, e, s, p, t, r1, r2, r3,r4, r5, r6 limit 100

```

### AI Pipeline Recommendation Server Set Up Guide
Once the neo4j is up and running with AIMKG, the following steps will open-up a UI to query the graph using natural language or find pipelines based on similar datasets, similar models or similar tasks
* Navigate to `aimkg-recommender-UI` folder. Copy the .env file that worked in `ai-pipeline-knowledge-graph` folder. `cp ../ai-pipeline-knowledge-graph/.env .`
* Navigate to `aimkg-recommender-UI/utils` folder and run `python compute_embeddings.py`. This is a one-time step done once. Take ~54 minutes on `dataset-large.zip` (on a system with V100). This reads credentials in `aimkg-recommender-UI/.env` created earlier. To skip this step, you can download and preprocessed files below.  
```
~/ai-metadata-knowledge-graph/aimkg-recommender-UI/utils$ python compute_embeddings.py
Computing task embeddings..
100%| 10511/10511 [01:49<00:00, 95.62it/s]
Computing dataset embeddings..
100%| 53387/53387 [09:16<00:00, 95.87it/s]
Computing dataset embeddings..
100%| 281410/281410 [44:14<00:00, 106.01it/s]
```
* `python python compute_embeddings.py` will produce the following files. To save time, you can download them (if not recomputing) to `aimkg-recommender-UI/utils/` :  
  ** [`dataset_embeddings_all.h5`](https://drive.google.com/file/d/1d2L6-OWZfN-Nv69ygA4fanv8kWhQK4cH/view?usp=drive_link)  - 150 MB
  ** [`model_embeddings_all.h5`](https://drive.google.com/file/d/1-zyh0NParauYC5xKSAbJwO8n9EkdrqSK/view?usp=drive_link) - 833 MB
  ** [`task_embeddings_all.h5`](https://drive.google.com/file/d/17psxOmCDQ2G3a0lilHiJgLnwO2kIFroR/view?usp=drive_link) - 31.1 MB

* Option 1: Navigate back to the `aimkg-recommender-UI`. Run `docker-compose --build -d up`. This will standup neo4J in container and once healthy allow `aimkg-recommender-ui` to start. 
* Option 2: Navigate back to the `aimkg-recommender-UI` folder and run `python app.py` natively and the UI will stand up at the address mentioned in your terminal. 
* The UI is accessible at: `http://localhost:9089`. The sample of the UI is shown in Figure 1

* For more information on what is possible with the UI please watch the demo [here](https://drive.google.com/drive/folders/1KEZJuyDLj3i9qWgXEigrhvuJ73a1OXak?usp=sharing)
* To manually make queries to the Webserver (bypassing the UI), the following can be used:

The available endpoints are: 


| Endpoint           | Function       
|-------------------|-----------------
| /recommendation/query | Returns num_recommendations for a given dataset OR task OR model OR pipeline     
| /search/query | Returns exact match results for a given dataset OR task OR model OR pipeline         
| /search/cypher_query | Returns the result of a Cypher query passed in the body of the POST   


** To send a recommendation request of similar pipelines for `task: image generation` 
```
curl -X POST http://localhost:9089/recommendation/query \
-H "Content-Type: application/json" \
-d '{
  "dataset": "",
  "task": "image generation",
  "model": "",
  "pipeline": "",
  "num_recommendations": 3
}'
```

** To search all pipeline information for `dataset: Food258K` 
```
curl -X POST http://localhost:9089//search/query \
-H "Content-Type: application/json" \
-d '{
  "dataset": "Food258K",
  "task": "",
  "model": "",
  "query_type": "OR"
}' | jq
```

** To search all pipeline information for `task: Causal Inference` 
```
curl -X POST http://localhost:9089//search/query \
-H "Content-Type: application/json" \
-d '{
  "dataset": " Causal Inference",
  "task": "",
  "model": "",
  "query_type": "OR"
}' | jq
```

** To search all pipeline information via CYPHER query (enables powerful searches) 
```
curl -X POST http://localhost:9089/search/cypher_query \
-H "Content-Type: application/json" \
-d '{
  "cypher_query" : " MATCH (a:Artifact)-[r3]-(e:Execution)-[r4]-(s:Stage)-[r5]-(p:Pipeline)-[r6]-(t:Task{category:'generation', modality:'image'}) WITH a,e,s,p,t,r3,r4,r5,r6 MATCH (d:Dataset)-[r1]-(a)-[r2]-(m:Model) RETURN d, a, m, e, s, p, t, r1, r2, r3,r4, r5, r6 LIMIT 300 "
}' | jq
```

### Full Paper
The full paper along with supplementary materials can be found here [Constructing a metadata knowledge graph as an atlas for demystifying AI pipeline optimization](https://www.frontiersin.org/journals/big-data/articles/10.3389/fdata.2024.1476506/full)

### Video
The demo video of AI pipeline Recommendation can be found here - [Demo of AI pipeline Recommender](https://drive.google.com/drive/folders/1KEZJuyDLj3i9qWgXEigrhvuJ73a1OXak?usp=sharing)

<br>


### AIMKG Construction
The construction of AIMKG is described in the figure below. The construction involves following steps:

* Data Collection
* Exploratory Data Analysis
* Common Metadata Ontology
* Mapping Concepts to Common Metadata Ontology
* Semantic Enrichments
* Data Ingestion to Graph Database(Neo4j)

<br>

<div align="center">
    <p><strong><em>Construction of AI pipeline Metadata Knowledge Graph</em></strong></p>
    <img src="figures/annotated_arch.png" alt="kg-const" width="80%">
</div>



#### 1. Data Collection

* **Papers-with-code:** <p align="justify"> Papers-with-Code provides extensive metadata for research papers and associated code repositories, encompassing over 1 million entries. The metadata covers various components and stages of AI pipelines described in the papers. Through their API, Papers-with-Code offers metadata including PDF URLs, GitHub repository links, task details, dataset information, methods employed, and evaluation metrics/results. While not all stages of metadata are available for every paper through the API, the information can still be obtained by referring to the research papers and their code repositories. </p>

* **OpenML:** <p align="justify"> OpenML provides metadata on machine learning pipelines logged by users, offering detailed information on tasks, datasets, flows, runs with parameter settings, and evaluations. OpenML encompasses eight major task types executed on various datasets, resulting in 1,600 unique tasks. For each task, most recent 500 runs have been collected which amounts to a total of 330,000 runs. </p>

* **Huggingface:** <p align="justify"> Huggingface is a model hub that offers users access to numerous pretrained models. It covers a wide range of tasks, including computer vision, natural language processing, tabular data, reinforcement learning, and multimodal learning. Huggingface provides model-centric information, along with datasets and evaluations, enabling the construction of complete pipelines. Currently, approximately 50,000 pipelines have been collected from Huggingface. </p>


#### 2. Exploratory Data Analysis
<p align="justify">
The exploratory data analysis of collected data showed different data structures and varying nomeclatures to denote similar concepts. For example, the concept model is referred is methods in Papers-with-code, flow in OpenML and models in Huggingface.
</p>

<br>
<table align="center">
  <tr>
    <td align="center">
      <p><i>Graph Data Model: Papers-with-code</i></strong></p>
      <img src="figures/gdm_pwc.svg" alt="Image 1" width="200">
    </td>
    <td align="center">
      <p><i>Graph Data Model: OpenML</i></strong></p>
      <img src="figures/gdm_openml.svg" alt="Image 2" width="200">
    </td>
  </tr>
  <tr>
    <td align="center">
      <p><i>Graph Data Model: Common Metadata Framework</i></strong></p>
      <img src="figures/gdm_cmf.svg" alt="Image 3" width="200">
    </td>
    <td align="center">
      <p><i>Graph Data Model: Huggingface</i></strong></p>
      <img src="figures/gdm_hf.svg" alt="Image 4" width="200">
    </td>
  </tr>
</table>




#### 3. Common Metadata Ontology
<p align="justify">
The data collected from above mentioned sources consists of 
<a href="ai-pipeline-datasources/readme.md">different nomenclature and data structures</a>. 
In order to unify them, Common Metadata Ontology (CMO) was designed based on the principles of 
<a href="https://github.com/HewlettPackard/cmf">Common Metadata Framework (CMF)</a> which follows a pipeline-centric framework. 
MLFlow, which follows a model-centric approach will require separate instantiation of each model even if they are being executed for the same pipeline, say, Entity Extraction from Semi-Structed documents. 
CMF encompasses all the models and datasets of a pipeline under single instantiation enabling search of best execution path. 
The overview of CMO can be found below and the details can be found at 
<a href="common-metadata-ontology/readme.md">common-metadata-ontology</a> folder.
</p>

<br>
<div align="center">
    <p><strong><em>Overview of Common Metadata Ontology</em></strong></p>
    <img src="figures/cmo_properties.png" alt="CMO" width="90%">
</div>



#### 4. Mapping
The concepts from Papers-with-code, OpenML and Huggingface are mapped to CMO to construct AIMKG. The details of mapping of each sources to Common Metadata Ontology can be found in [mapping](mapping/mapping_readme.md) folder.

#### 5.Semantic Enrichments
<p align="justify">
In order to enable contextually relevant queries, semantic enrichments are performed on the data entities. For example, in the figure below, the user searched for "Image Detection" task and its pipeline. It can be noticed that both "2D Object Detection" and "3D object Detection" are returned as results which do not explicitly have the name "image" in them. Such semantic enhancements are done for tasks, datasets and models. The methods and techniques are detailed [here](semantic-enrichments/semantics_readme.md) 
</p>

<div align="center">
    <p><strong><em> </em></strong></p>
    <img src="figures/sample_query.png" alt="CMO" width="90%">
</div>

<br>

#### 6. Data Ingestion
The data gathered and semantically enriched are then loaded to Neo4j Graph DB to perform serach and recommendation. The steps to set-up the graph DB are mentioned in the section [Set Up Guide](#aimkg-set-up-guide)


## Publications
* <p align="justify"> Venkataramanan, Revathy, Aalap Tripathy, Tarun Kumar, Sergey Serebryakov, Annmary Justine, Arpit Shah, Suparna Bhattacharya et al. "Constructing a Metadata Knowledge Graph as an atlas for demystifying AI Pipeline optimization." Frontiers in Big Data 7: 1476506. <a href="https://www.frontiersin.org/journals/big-data/articles/10.3389/fdata.2024.1476506/full">Link to the paper</a> </p>
* <p align="justify"> Venkataramanan, Revathy, Aalap Tripathy, Martin Foltin, Hong Yung Yip, Annmary Justine, and Amit Sheth. "Knowledge graph empowered machine learning pipelines for improved efficiency, reusability, and explainability." IEEE Internet Computing 27, no. 1 (2023): 81-88. <a href ="https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=10044293&casa_token=gZ8lwivSW1oAAAAA:5390SDEkYDpck4EduA3iUG6fO5Vdbi3WRcyTpJTv0yz_lliAb8xurwH3z2SvlOzqTT932dKPvfk&tag=1"> Link to the paper </a> </p>
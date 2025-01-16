###
# Copyright (2024) Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###


"""
This script maps the exisiting relationships from PWC to Metadata Knowlege graph. It also computes new relationships that
are expected in the metadata knowledge graph but not present in the papers-with-code graph data model.

Dependent on the data collected from papers-with-code API 

Mapping of nodes:
papers --> pipelines
methods --> models
Rest of the node names remain the same
"""

import pandas as pd
import os
import csv
import json


# Source data path
SRC_DATA_PATH_JSON = 'data/pwc'
SRC_DATA_PATH_CSV = 'kg-data/pwc/nodes'

# Relationship CSV files created will be stored in both the places
DEST_LUSTRE_PATH = 'kg-data/pwc/relationships'
DEST_LOCAL_PATH = 'kg-data/pwc/relationships'


# Helper Functions
def tuple_to_csv(headers, tuples_list, filepaths):
    """
    headers: column names of csv file to be generated. Type: list of strings
    tuple_list: list of tuples, where each tuple is a row
    filename: name of the csv file to be saved
    """
    for filepath in filepaths:
        with open(filepath,'w') as out:
            csv_out=csv.writer(out)
            csv_out.writerow(headers)
            for row in tuples_list:
                csv_out.writerow(row)
        print("File saved at:", filepath)



def rel_pipeline_task():
    # pipeline.csv: paper_id
    # paper_related.json: paper_id --> task_ids
    # tasks.csv: src_id --> generated_task_id

    pipeline_filepath = os.path.join(SRC_DATA_PATH_CSV, 'pipelines.csv')
    df_pipeline = pd.read_csv(pipeline_filepath)

    task_filepath = os.path.join(SRC_DATA_PATH_CSV, 'tasks.csv')
    df_task = pd.read_csv(task_filepath)

    paper_related_filepath = os.path.join(SRC_DATA_PATH_JSON, 'paper-related.json')
    paper_related_data = json.load(open(paper_related_filepath, 'r'))

    # create a map for paper_id to pipeline_id
    paper_pipeline_map = {}
    for i in range(0,len(df_pipeline)):
        paper_pipeline_map[str(df_pipeline['src_id'][i])] = str(df_pipeline['pipeline_id'][i])
    
    # create a map for pwc_task_id to generated_task_id
    task_map = {}
    for j in range(0,len(df_task)):
        task_map[str(df_task['src_id'][j])] = str(df_task['task_id'][j])
    
    print(len(task_map))
    
    # create relationships
    tuples_list = []
    counter = 0
    temp_list = []
    for paper_id in paper_related_data:
        tasks = paper_related_data[paper_id]['tasks']
        pipeline_id = paper_pipeline_map[paper_id]

        for element in tasks:
            pwc_task_id = str(element['id'])
            try:
                tuples_list.append((pipeline_id, task_map[pwc_task_id]))
            except KeyError as e:
                # print("KeyError:", e)
                temp_list.append(pwc_task_id)
                counter = counter + 1

    print(len(set(temp_list)))
    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'rel-pipeline-task.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'rel-pipeline-task.csv')
    tuple_to_csv(headers=['pipeline_id', 'task_id'], tuples_list=tuples_list, filepaths=[filepath1, filepath2])




def rel_pipeline_framework():
    pipeline_filepath = os.path.join(SRC_DATA_PATH_CSV, 'pipelines.csv')
    df_pipeline = pd.read_csv(pipeline_filepath)

    framework_filepath = os.path.join(SRC_DATA_PATH_CSV, 'frameworks.csv')
    df_framework = pd.read_csv(framework_filepath)

    paper_related_filepath = os.path.join(SRC_DATA_PATH_JSON, 'paper-related.json')
    paper_related_data = json.load(open(paper_related_filepath, 'r'))

    # create a map for paper_id to pipeline_id
    paper_pipeline_map = {}
    for i in range(0,len(df_pipeline)):
        paper_pipeline_map[df_pipeline['src_id'][i]] = df_pipeline['pipeline_id'][i]
    
    # create a map for url to generated framework_id
    url_framework_map = {}
    for j in range(0,len(df_framework)):
        url_framework_map[df_framework['url'][j]] = df_framework['framework_id'][j]
    
    # create relationships
    tuples_list = []
    counter = 0
    for paper_id in paper_related_data:
        counter = counter + 1
        frameworks = paper_related_data[paper_id]['git-repos']
        pipeline_id = paper_pipeline_map[paper_id]
        for element in frameworks:
            pwc_url = element['url']
            tuples_list.append((pipeline_id, url_framework_map[pwc_url]))
            print("Pipeline--Framework. Counter:", str(counter) + '/' + str(len(paper_related_data)))
    
    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'rel-pipeline-framework.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'rel-pipeline-framework.csv')
    tuple_to_csv(headers=['pipeline_id', 'framework_id'], tuples_list=tuples_list, filepaths=[filepath1, filepath2])



def rel_pipeline_stage():
    stage_filepath = os.path.join(SRC_DATA_PATH_CSV, 'stages.csv')
    df = pd.read_csv(stage_filepath)
    
    tuples_list = []
    for idx in range(0,len(df)):
        print("Pipeline--Stage. Counter:", str(idx) + '/' + str(len(df)))
        tuples_list.append((df['pipeline_id'][idx], df['stage_id'][idx]))

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'rel-pipeline-stage.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'rel-pipeline-stage.csv')
    tuple_to_csv(headers=['pipeline_id', 'stage_id'], tuples_list=tuples_list, filepaths=[filepath1, filepath2])


def rel_stage_execution():
    execution_filepath = os.path.join(SRC_DATA_PATH_CSV, 'executions.csv')
    df = pd.read_csv(execution_filepath)

    tuples_list = []
    for idx in range(0,len(df)):
        print("Stage--Execution. Counter:" + str(idx) + '/' + str(len(df)))
        tuples_list.append((df['stage_id'][idx], df['execution_id'][idx]))

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'rel-stage-execution.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'rel-stage-execution.csv')
    tuple_to_csv(headers=['stage_id', 'execution_id'], tuples_list=tuples_list, filepaths=[filepath1, filepath2])
    


def rel_execution_artifact():
    artifact_filepath = os.path.join(SRC_DATA_PATH_CSV, 'artifacts.csv')
    df = pd.read_csv(artifact_filepath)

    tuples_list = []
    for idx in range(0,len(df)):
        print("Execution--Artifact. Counter:", str(idx) + '/' + str(len(df)))
        tuples_list.append((df['execution_id'][idx], df['artifact_id'][idx]))

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'rel-execution-artifact.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'rel-execution-artifact.csv')
    tuple_to_csv(headers=['execution_id', 'artifact_id'], tuples_list=tuples_list, filepaths=[filepath1, filepath2])



def rel_execution_metric():
    metric_filepath = os.path.join(SRC_DATA_PATH_CSV, 'metrics.csv')
    df_metric = pd.read_csv(metric_filepath)

    execution_filepath = os.path.join(SRC_DATA_PATH_CSV, 'executions.csv')
    df_execution = pd.read_csv(execution_filepath)

    paper_related_filepath = os.path.join(SRC_DATA_PATH_JSON, 'paper-related.json')
    paper_related_data = json.load(open(paper_related_filepath, 'r'))

    # create a map for pwc result id to metric id
    result_metric_map = {}
    for i in range(0, len(df_metric)):
        result_metric_map[str(df_metric['src_id'][i])] = df_metric['metric_id'][i]
    
    # create paper_execution_map
    paper_execution_map = {}
    for j in range(0, len(df_execution)):
        paper_execution_map[df_execution['pwc_paper_id'][j]] = df_execution['execution_id'][j]
    
    # print(result_metric_map)

    tuples_list = []
    counter = 0
    err = 0
    for pid in paper_related_data:
        counter = counter + 1
        execution_id = paper_execution_map[pid]
        results = paper_related_data[pid]['results']
        for element in results:
            pwc_result_id = str(element['id'])
            try:
                tuples_list.append((execution_id,  result_metric_map[pwc_result_id]))   
                # print("Execution--Metric. Counter:" + str(counter) + '/' + str(len(paper_related_data))) 
            except KeyError as e:
                # print("KeyError:", e)
                err = err + 1

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'rel-execution-metric.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'rel-execution-metric.csv')
    tuple_to_csv(headers=['execution_id', 'metric_id'], tuples_list=tuples_list, filepaths=[filepath1, filepath2])



def rel_artifact_dataset():
    artifact_filepath = os.path.join(SRC_DATA_PATH_CSV, 'artifacts.csv')
    df_artifact = pd.read_csv(artifact_filepath)

    dataset_filepath = os.path.join(SRC_DATA_PATH_CSV, 'datasets.csv')
    df_dataset = pd.read_csv(dataset_filepath)

    paper_related_filepath = os.path.join(SRC_DATA_PATH_JSON, 'paper-related.json')
    paper_related_data = json.load(open(paper_related_filepath, 'r'))


    # create a map for paper-id to artifact-id
    paper_artifact_map = {}
    for i in range(0,len(df_artifact)):
        paper_artifact_map[df_artifact['pwc_paper_id'][i]] = df_artifact['artifact_id'][i]
    
    # create a map for pwc dataset id to generated dataset_id
    dataset_map = {}
    for j in range(0, len(df_dataset)):
        dataset_map[str(df_dataset['src_id'][j])] = df_dataset['dataset_id'][j]
    
    tuples_list = []
    counter = 0
    err = 0
    for pid in paper_related_data:
        counter = counter + 1
        artifact_id = paper_artifact_map[pid]
        datasets = paper_related_data[pid]['datasets']
        for element in datasets:
            pwc_dataset_id = str(element['id'])
            try:
                tuples_list.append((artifact_id, dataset_map[pwc_dataset_id]))
            except KeyError: # Total key error: 1698/1Million
                err = err + 1

        print("Artifact--Dataset. Counter:" + str(counter) + '/' + str(len(paper_related_data)))

    print("Length of Data:", len(tuples_list))
    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'rel-artifact-dataset.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'rel-artifact-dataset.csv')
    tuple_to_csv(headers=['artifact_id', 'dataset_id'], tuples_list=tuples_list, filepaths=[filepath1, filepath2])   
    


def rel_artifact_model():
    artifact_filepath = os.path.join(SRC_DATA_PATH_CSV, 'artifacts.csv')
    df_artifact = pd.read_csv(artifact_filepath)

    model_filepath = os.path.join(SRC_DATA_PATH_CSV, 'models.csv')
    df_model = pd.read_csv(model_filepath)

    paper_related_filepath = os.path.join(SRC_DATA_PATH_JSON, 'paper-related.json')
    paper_related_data = json.load(open(paper_related_filepath, 'r'))

    # create a map for paper-id to artifact-id
    paper_artifact_map = {}
    for i in range(0,len(df_artifact)):
        paper_artifact_map[df_artifact['pwc_paper_id'][i]] = df_artifact['artifact_id'][i]

    # create a map for pwc model id (pwc method id) to generated model id
    model_map = {}
    for j in range(0, len(df_model)):
        model_map[df_model['src_id'][j]] = df_model['model_id'][j]

    tuples_list = []
    counter = 0
    for pid in paper_related_data:
        counter = counter + 1
        artifact_id = paper_artifact_map[pid]
        datasets = paper_related_data[pid]['methods']
        for element in datasets:
            pwc_model_id = element['id']
            tuples_list.append((artifact_id, model_map[pwc_model_id]))
            print("Artifact--Model. Counter:" + str(counter) + '/' + str(len(paper_related_data)))

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'rel-artifact-model.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'rel-artifact-model.csv')
    tuple_to_csv(headers=['artifact_id', 'model_id'], tuples_list=tuples_list, filepaths=[filepath1, filepath2])  


def rel_artifact_metric():
    artifact_filepath = os.path.join(SRC_DATA_PATH_CSV, 'artifacts.csv')
    df_artifact = pd.read_csv(artifact_filepath)

    metric_filepath = os.path.join(SRC_DATA_PATH_CSV, 'metrics.csv')
    df_metric = pd.read_csv(metric_filepath)

    paper_related_filepath = os.path.join(SRC_DATA_PATH_JSON, 'paper-related.json')
    paper_related_data = json.load(open(paper_related_filepath, 'r'))

     # create a map for paper-id to artifact-id
    paper_artifact_map = {}
    for i in range(0, len(df_artifact)):
        paper_artifact_map[df_artifact['pwc_paper_id'][i]] = df_artifact['artifact_id'][i]

    # create a map for pwc result id to metric id
    result_metric_map = {}
    for j in range(0, len(df_metric)):
        result_metric_map[str(df_metric['src_id'][j])] = df_metric['metric_id'][j]
    
    tuples_list = []
    counter = 0
    err = 0
    for pid in paper_related_data:
        counter = counter + 1
        artifact_id = paper_artifact_map[pid]
        results = paper_related_data[pid]['results']
        for element in results:
            pwc_result_id = str(element['id'])
            try:
                tuples_list.append((artifact_id,  result_metric_map[pwc_result_id]))
            except KeyError as e:
                err = err + 1
            print("Artifact--Metric. Counter:" + str(counter) + '/' + str(len(paper_related_data)))

    print("Total Data points:", len(tuples_list))
    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'rel-artifact-metric.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'rel-artifact-metric.csv')
    tuple_to_csv(headers=['artifact_id', 'metric_id'], tuples_list=tuples_list, filepaths=[filepath1, filepath2])       
   


def rel_pipeline_report():
    report_filepath = os.path.join(SRC_DATA_PATH_CSV, 'reports.csv')
    df = pd.read_csv(report_filepath)

    tuples_list = []
    for idx in range(0,len(df)):
        tuples_list.append((df['pipeline_id'][idx], df['report_id'][idx]))
        print("Pipeline--Report. Counter:" + str(idx) + '/' + str(len(df)))

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'rel-pipeline-report.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'rel-pipeline-report.csv')
    tuple_to_csv(headers=['pipeline_id', 'report_id'], tuples_list=tuples_list, filepaths=[filepath1, filepath2])        



# FUNCTION CALLS
rel_pipeline_framework()
rel_pipeline_stage()
rel_stage_execution() 
rel_execution_metric() # there are some 13k KEY ERRORS in this function. Issue is with metrics
rel_execution_artifact()
rel_artifact_dataset()
rel_artifact_model()
rel_artifact_metric()  # there are some 13k KEY ERRORS in this function. Issue is with metrics
rel_pipeline_report()
rel_pipeline_task() # ISSUE HERE

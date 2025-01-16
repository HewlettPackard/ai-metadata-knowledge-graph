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
This script is supposed to be ran after running nodes_from_pwc.py and relation_from_pwc.py
This script consists of additional post processing functions to compute semantic properties
    1) Compute dataset modality based on the tasks the dataset is associated with
    2) Compute task modality from task taxonomy
"""
import os
import json
import pandas as pd

CSV_LUSTRE_PATH = 'kg-data/pwc/nodes/'
CSV_LOCAL_PATH = 'kg-data/pwc/nodes/'

SRC_DATA_PATH_JSON = 'data/pwc'

def dataset_modality_from_pipeline():
    # calculates dataset modality based on the papers it is associated with
    # Open datasets.csv and pipelines.csv
    dataset_df = pd.read_csv(os.path.join(CSV_LUSTRE_PATH, 'datasets.csv'))
    pipeline_df = pd.read_csv(os.path.join(CSV_LUSTRE_PATH, 'pipelines.csv'))

    # create a temp_dict. Key: pwc_dataset_id, value: list of pipeline_ids/paper_ids
    paper_related_filepath = os.path.join(SRC_DATA_PATH_JSON, 'paper-related.json')
    paper_related_data = json.load(open(paper_related_filepath, 'r'))
    dataset_pid_map = {}
    total_len = len(paper_related_data)
    for idx, pid in enumerate(paper_related_data):
        print("Creating temp dict:" + str(idx) + '/' + str(total_len))
        dataset_ids = [each['id'] for each in paper_related_data[pid]['datasets']]
        for dataset_id in dataset_ids:
            try:
                exist_pids = dataset_pid_map[str(dataset_id)]
                exist_pids.append(str(pid))
                dataset_pid_map[str(dataset_id)] = list(set(exist_pids))
            
            except KeyError:
                dataset_pid_map[str(dataset_id)] = [str(pid)]
    

    # create a temp dict. Key: dataset_id, Values: list of task id
    modality_list = []
    error_counter = 0
    total_length = len(dataset_df)
    for i in range(0,len(dataset_df)):
        src_dataset_id = dataset_df['src_id'][i]
        try:
            src_pids = dataset_pid_map[str(src_dataset_id)]
            print("Iterating through dataset:" + str(i) + '/' + str(total_length))
            for pid in src_pids:
                row = pipeline_df.loc[pipeline_df['src_id'] == str(pid)]
                modality = row['modality'].values
                modality_list = modality_list + modality
            
            unique_modalities = list(set(modality_list))
            if len(unique_modalities) > 1: # captures multimodality
                unique_modalities.append("multimodal")
                unique_modalities = list(set(unique_modalities)) # if multimodal is there twice, this handles it
            
            modality_string = ",".join(unique_modalities)
            dataset_df['modality'][i] = modality_string
            print("Modality:",modality_string)
        except KeyError:
            error_counter = error_counter + 1
        
    # save the file
    dataset_df.write_to_csv(os.path.join(CSV_LOCAL_PATH, 'datasets.csv'))
    dataset_df.write_to_csv(os.path.join(CSV_LUSTRE_PATH, 'datasets.csv'))
    print("Files saved")




def task_modality_from_taxonomy():
    """
    More tasks are associated with taxonomy, meaning more tasks have modality.
    After calculating their modality using their name, we additional calculate it using taxonomy
    If any of these tasks do not have description originally and if the content from taxonomy has, we update the description
    """
    task_df = pd.read_csv(os.path.join(CSV_LUSTRE_PATH, 'tasks.csv'))
    new_df = task_df

    # open all the taxonomy files
    area = json.load(open('/home/venkatre/kg_recommender/data/pwc/taxonomy/area_data.json', 'r'))
    first_child = json.load(open('/home/venkatre/kg_recommender/data/pwc/taxonomy/first_child.json', 'r'))
    second_child = json.load(open('/home/venkatre/kg_recommender/data/pwc/taxonomy/second_child.json', 'r'))

    # create a temp map of second-child-id to area-id. 
    # TODO - One second child task can have two parents? Check that
    task_area_map = {}
    for tid in second_child:
        temp_list = []
        # existing_data = task_area_map[tid]
        first_child_id = second_child[tid]['first_child_id'] # always 1
        area_name = first_child[first_child_id]['area_id']
        temp_list.append(area_name)
        # temp_list.append(existing_data)
        task_area_map[tid] = area_name

    
    temp_modality_list = []
    counter = 0
    for i in range(0,len(task_df)):
        src_id = task_df['src_id'][i]
        curr_desc = task_df['description'][i]
        try:
            new_modality = task_area_map[src_id]
            curr_modality = task_df['modality'][i]
            curr_modality = curr_modality.split(",")
            print(curr_modality)

            temp_modality_list.append(new_modality)
            temp_modality_list = temp_modality_list + curr_modality

            final_mod = list(set(temp_modality_list))
            if "none" in final_mod:
                final_mod.remove("none")
            print(temp_modality_list, final_mod)
            final_modality = ",".join(final_mod)
            new_df['modality'][i] = final_modality

            # fill in descriptions as well
            if curr_desc == "none" and second_child[src_id]['desc'] != "":
                new_df['description'][i] = second_child[src_id]['desc']
        except KeyError:
            pass
        temp_modality_list = []

    new_df.to_csv(os.path.join(CSV_LOCAL_PATH, 'tasks.csv'))
    new_df.to_csv(os.path.join(CSV_LUSTRE_PATH, 'tasks.csv'))
    print("Files saved")




def dataset_modality_from_task():
    # calculates dataset modality based on the tasks it is associated with
    # Open datasets.csv and pipelines.csv
    dataset_df = pd.read_csv(os.path.join(CSV_LUSTRE_PATH, 'datasets.csv'))
    new_dataset_df = dataset_df
    task_df = pd.read_csv(os.path.join(CSV_LUSTRE_PATH, 'tasks.csv'))

    # create a temp_dict. Key: pwc_dataset_id, value: list of task_ids
    paper_related_filepath = os.path.join(SRC_DATA_PATH_JSON, 'paper-related.json')
    paper_related_data = json.load(open(paper_related_filepath, 'r'))
    dataset_tid_map = {}
    total_len = len(paper_related_data)
    for idx, pid in enumerate(paper_related_data):
        print("Creating temp dict:" + str(idx) + '/' + str(total_len))
        dataset_ids = [each['id'] for each in paper_related_data[pid]['datasets']]
        task_ids = [each['id'] for each in paper_related_data[pid]['tasks']]
        for dataset_id in dataset_ids:
            try:
                exist_tids = dataset_tid_map[str(dataset_id)]
                exist_tids = exist_tids + task_ids
                dataset_tid_map[str(dataset_id)] = list(set(exist_tids))
            
            except KeyError:
                dataset_tid_map[str(dataset_id)] = task_ids
    

    # create a temp dict. Key: dataset_id, Values: list of task id
    modality_list = []
    error_counter = 0
    total_length = len(dataset_df)
    for i in range(0,len(dataset_df)):
        src_dataset_id = dataset_df['src_id'][i]
        try:
            task_ids = dataset_tid_map[str(src_dataset_id)]
            print("Iterating through dataset:" + str(i) + '/' + str(total_length))
            for task_id in task_ids:
                row = task_df.loc[task_df['src_id'] == str(task_id)]
                modality = row['modality'].values
                modality_list = modality_list + modality
            
            unique_modalities = list(set(modality_list))
            if len(unique_modalities) > 1: # captures multimodality
                unique_modalities.append("multimodal")
                unique_modalities = list(set(unique_modalities)) # if multimodal is there twice, this handles it
            
            modality_string = ",".join(unique_modalities)
            new_dataset_df['modality'][i] = modality_string
            print("Dataset:", src_dataset_id)
            print("Modality:", modality_string)
            print("\n")
        except KeyError:
            error_counter = error_counter + 1
    
    # save the file
    new_dataset_df.to_csv(os.path.join(CSV_LOCAL_PATH, 'datasets.csv'))
    new_dataset_df.to_csv(os.path.join(CSV_LUSTRE_PATH, 'datasets.csv'))
    print("Files saved")
 



# fuction calls - DO NOT CHANGE THE ORDER

task_modality_from_taxonomy()
dataset_modality_from_task()

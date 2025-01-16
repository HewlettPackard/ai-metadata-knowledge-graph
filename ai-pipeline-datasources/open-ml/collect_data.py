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


from collections import OrderedDict
import openml
import pandas
import xml
import json
import os

# mention path here to collect the data
DATA_FOLDER = 'data/open-ml'


def collect_dataset_url(df_url):
    print("Collecting openml url and downloadable url for the datasets...")
    df = pandas.read_csv(df_url)
    dataset_id = df['did'].tolist()
    openml_url = []
    download_url = []
    for id in dataset_id:
        if id == 41190:
            pass
        else:
            try:
                print(id)
                dataset = openml.datasets.get_dataset(id)
                openml_url.append(dataset.openml_url)
                download_url.append(dataset.url)
            except FileNotFoundError:
                openml_url.append(None)
                download_url.append(None)
            except openml.exceptions.OpenMLServerException:
                openml_url.append(None)
                download_url.append(None)
            except xml.parsers.expat.ExpatError:
                openml_url.append(None)
                download_url.append(None)
            except openml.exceptions.OpenMLServerError:
                openml_url.append(None)
                download_url.append(None)
            except openml.exceptions.OpenMLHashException:
                openml_url.append(None)
                download_url.append(None)
        
    print(len(dataset_id))
    print("Openml URL:", len(openml_url))
    print("Download URL:", len(download_url))

    df['openml_url'] = openml_url
    df['download_url'] = download_url

    df.to_csv(os.path.join(DATA_FOLDER, 'dataset2.csv'))
    print("File saved")


def save_file(data):
    filename = os.path.join(DATA_FOLDER, 'runs.json')
    if os.path.exists(filename):
        dict1 = json.load(open(filename, 'r'))
        dict1.update(data)
        fp = open(filename, 'w')
        json.dump(dict1, fp)
    else:
        fp = open(filename, 'w')
        json.dump(data, fp)


def collect_runs():
    run_ids = list(range(1,1000000))
    data = {}
    for rid in run_ids:
        run_id = rid
        print("Collecting run id:" + str(run_id) + '/' + str(len(run_ids)))
        try:
            run_ = openml.runs.get_run(run_id=run_id)
            data[run_id] = {
            'flow_id': run_.flow_id,
            'dataste_id': run_.dataset_id,
            'task_id': run_.task_id,
            'task_type': run_.task_type,
            'parameter_settings': run_.parameter_settings,
            'setup_string': run_.setup_string,
            'setup_id': run_.setup_id,
            'output_files': run_.output_files,
            'tags': run_.tags,
            'uploader': run_.uploader,
            'uploader_name': run_.uploader_name,
            'evaluations': run_.evaluations,
            'fold_evaluations': run_.fold_evaluations,
            'sample_evaluations': run_.sample_evaluations,
            'data_content': run_.data_content,
            'trace': run_.trace,
            'model': run_.model,
            'task_evaluation_measure': run_.task_evaluation_measure,
            'flow_name': run_.flow_name,
            'predictions_url': run_.predictions_url,
            'task': run_.task,
            'flow': run_.flow,
            'run_id': run_.run_id,
            'description': run_.description_text,
            'run_details': run_.run_details
            }

        except:
            data[run_id] = {
                'flow_id': None,
                'dataste_id': None,
                'task_id': None,
                'task_type': None,
                'parameter_settings': [],
                'setup_string': None,
                'setup_id': None,
                'output_files': OrderedDict(),
                'tags': None,
                'uploader': None,
                'uploader_name': None,
                'evaluations': OrderedDict(),
                'fold_evaluations': OrderedDict(),
                'sample_evaluations': OrderedDict(),
                'data_content': None,
                'trace': None,
                'model': None,
                'task_evaluation_measure': None,
                'flow_name': None,
                'predictions_url': None,
                'task': None,
                'flow': None,
                'run_id': None,
                'description': None,
                'run_details': None
                }

        if run_id % 10 == 0:
            print(data)
            save_file(data)
            data = {}

# collect_runs()


# data = json.load(open('../data/open-ml/runs.json', 'r'))
# print(data)

# Flows - the set up using which the pipeline is ran
df_flows = openml.flows.list_flows(output_format="dataframe")
df_flows.to_csv(os.path.join(DATA_FOLDER, 'flows.csv'))
print("Flows saved..")

# Dataset
df_dataset = openml.datasets.list_datasets(output_format="dataframe")
df_dataset.to_csv(os.path.join(DATA_FOLDER, 'datasets.csv'))
print("Datasets saved..")

# Task
df_task = openml.tasks.list_tasks(output_format="dataframe")
df_task.to_csv(os.path.join(DATA_FOLDER, 'tasks.csv'))
print("Tasks saved..")




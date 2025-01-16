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

from paperswithcode import PapersWithCodeClient 
import os
import time
import json
from task import collect_tasks
from collect_all_papers import collect_papers, collect_paper_related_data
import pprint
from tqdm import tqdm
import requests

"""
This script collects the detailed information of tasks, datasets, methods, evaluations and results.
The generated files are:
all-papers.json
paper-related-data.json
pwc-tasks.json
pwc-methods.json
pwc-datasets.json
pwc-evaluations.json
pwc-eval-results.json

"""



client = PapersWithCodeClient()
pp = pprint.PrettyPrinter(indent=2)

# mention path here to collect data
DATA_FOLDER = 'data/pwc'


def collect_datasets():
    filename = os.path.join(DATA_FOLDER, 'pwc/pwc-datasets.json')
    items_limit = 500
    dataset_count = client.dataset_list().count
    page_count = int(dataset_count / items_limit) + 2 #range() won't inlcude the last number. Hence +2
    data = {}
    start_page = 1
    for i in range(1, page_count):
        print("Collecting datasets. Page number:" + str(i) + '/' + str(page_count))
        result = client.dataset_list(items_per_page=items_limit, page=i) 
        for dataset in result.results:
            data[str(dataset.id)] = dict(dataset)
    
    print("Length of data:", len(data))
    json.dump(data, open(filename, 'w'))
    print("File saved at:", filename)


def collect_methods():
    filename = os.path.join(DATA_FOLDER, 'pwc/pwc-methods.json')
    items_limit = 1
    method_count = client.method_list().count
    page_count = int(method_count / items_limit) + 2 #range() won't inlcude the last number. Hence +2
    data = {}
    try:
        for i in range(1, page_count):
            print("Collecting methods. Page number:" + str(i) + '/' + str(page_count))
            result = client.method_list(items_per_page=items_limit, page=i) 
            for method in result.results:
                data[str(method.id)] = dict(method)
    except:
        pass
    
    print("Length of data:", len(data))
    json.dump(data, open(filename, 'w'))
    print("File saved at:", filename)


def collect_evaluations():
    filename = os.path.join(DATA_FOLDER, 'pwc/pwc-evaluations.json')
    items_limit = 500
    eval_count = client.evaluation_list().count
    page_count = int(eval_count / items_limit) + 2 #range() won't inlcude the last number. Hence +2
    data = {}
    for i in range(1, page_count):
        print("Collecting evaluations. Page number:" + str(i) + '/' + str(page_count))
        result = client.evaluation_list(items_per_page=items_limit, page=i) 
        for eval in result.results:
            data[str(eval.id)] = dict(eval)
    
    print("Length of data:", len(data))
    json.dump(data, open(filename, 'w'))
    print("File saved at:", filename)


def collect_evalID_results():
    """
    This function collects all the results obtained for an evaluation.
    It creates a key-value pair. Key is the evaluationID and values are a list of dict of results.
    This function is dependent on collect_evalautions function. Hence it should be run after that.
    """
    data = json.load(open(os.path.join(DATA_FOLDER, 'pwc/pwc-evaluations.json'), 'r'))
    filename = os.path.join(DATA_FOLDER, 'pwc/pwc-eval-results.json')
    new_data = {}
    counter = 0
    for ev_id in tqdm(data):
        req_str = "https://paperswithcode.com/api/v1/evaluations/{}/results/".format(ev_id)
        response = requests.get(req_str)
        try:
            new_data[ev_id] = response.json()['results']
        except:
            new_data[ev_id] = []
    print("Length of data:", len(new_data))
    json.dump(new_data, open(filename, 'w'))
    print("File saved at:", filename)


def collect_results():
    """
    This functions creates a json file containing all the results. 
    """
    # TODO - check if one result is associated with multiple evaluatiosn

    data = json.load(open(os.path.join(DATA_FOLDER,'pwc/pwc-eval-results.json'), 'r'))
    filename = os.path.join(DATA_FOLDER, 'pwc/pwc-results.json')
    new_data = {}
    counter = 0
    print("Creating results...")
    for eval_id in tqdm(data):
        results = data[eval_id]
        for ele in results:
            # ele['evaluation_id'] = eval_id
            result_id = ele['id']
            new_data[result_id] = ele
        print(len(new_data))
    
    json.dump(new_data, open(filename, 'w'))


def collect_methods_from_papers():
    """
    Collecting the method information from paper as method-API throws validationError for many data
    """
    paper_data = json.load(open(os.path.join(DATA_FOLDER, 'pwc/paper-related.json'), 'r'))
    data = {}
    counter = 0
    for pid in paper_data:
        methods_list = paper_data[pid]['methods']
        for method in methods_list:
            mid = method['id']
            data[mid] = method
        counter = counter + 1
        print("Collecting methods from paper:", counter)

    print("Length of methods:", len(data))
    json.dump(data, open(os.path.join(DATA_FOLDER, 'pwc/pwc-methods.json'), 'w'))



collect_datasets()

# # Collecting the method information from paper as method-API throws validationError for many data
collect_methods_from_papers()

collect_evaluations()

collect_evalID_results()

collect_results()

# # Collect task involves post processing and hence written as a separate script.
collect_tasks()

# Collects all the papers (paper id, title, abstract, url, conference, publication)
collect_papers()

# Collects dataset, task, methods, results and git repos for each of the papers
collect_paper_related_data()


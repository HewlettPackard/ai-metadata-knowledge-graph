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



from pydoc import cli
from xml.sax import default_parser_list
from paperswithcode import PapersWithCodeClient 
import json
import os
from tqdm import tqdm
import requests

"""
This script collects all the information on the paper. First it collects from papers-API. And then using PID, it collects
tasks, datasets, methods, results and git repos for a given PID(paper-id).

The main functions are called from collect_data.py
"""
# mention path here to collect data
DATA_FOLDER = 'data/pwc'

client = PapersWithCodeClient()

def get_data(filename):
    if os.path.exists(filename):
        data = json.load(open(filename, 'r'))
    else:
        data = {}
    return data


def save_data(data, filename):
    if os.path.exists(filename):
        print("File already exists. Appending to existing data")
        dict1 = json.load(open(filename, 'r'))
        dict1.update(data)
        print("Length of data:", len(dict1))
        fp = open(filename, 'w')
        json.dump(dict1, fp)
    else:
        fp = open(filename, 'w')
        json.dump(data, fp)
    
    return {}



def collect_papers():
    filename = os.path.join(DATA_FOLDER, 'pwc/all-papers.json')
    num_items = 10
    papers_page = client.paper_list(items_per_page=num_items)
    page_count = papers_page.count
    data = get_data(filename) # get the existing data to append to it
    start_page = 1 # it should be 1
    with tqdm(total=page_count, desc='Collecting papers from each page...') as pbar:
        for i in range(start_page, page_count):
            # print("Collecting paper info. Page:" + str(i) + "/" + str(page_count))
            try:
                papers_page = client.paper_list(items_per_page=num_items, page=i)
                for res in papers_page.results:
                    x = dict(res)
                    x['published'] = str(x['published'])
                    data[x['id']] = x
                    # print("Length of data:", len(data))
            except:
                pass

            # save data to a file periodically
            if i % 100 == 0:
                data = save_data(data, filename)
            pbar.update(1)
    # final save
    data = save_data(data, filename)



def get_tasks(pid):
    try:
        tasks_ = list(client.paper_task_list(pid).results)
        tasks = [dict(i) for i in tasks_]
    except:
        tasks = []
    return tasks

def get_datasets(pid):
    try:
        datasets_ = list(client.paper_dataset_list(pid).results)
        datasets = [dict(i) for i in datasets_]
    except:
        datasets = []
    return datasets

def get_methods(pid):
    try:
        methods_ = list(client.paper_method_list(pid).results)
        methods = [dict(i) for i in methods_]
    except:
        methods = []
    return methods

def get_results(pid):
    try:
        # results_ = list(client.paper_result_list(pid).results) --> return empty results as API changed
        url = "https://paperswithcode.com/api/v1/papers/{}/results/".format(pid)
        res = requests.get(url)
        res = res.json()
        results = res['results']
    except:
        results = []
    return results


def get_git_repos(pid):
    try:
        git_repos_ = list(client.paper_repository_list(pid).results)
        git_repos = [dict(i) for i in git_repos_]
    except:
        git_repos = []
    return git_repos


def collect_paper_related_data():
    data = json.load(open(os.path.join(DATA_FOLDER, 'pwc/all-papers.json'),'r'))
    filename = os.path.join(DATA_FOLDER, 'pwc/paper-related.json')
    # COMMENT THE FOLLOWING BLOCK OF CODE WHEN NECESSARY
    related = json.load(open(filename, 'r'))
    related_ids = [i for i in related]
    all_ids = [j for j in data]
    rem_ids = set(all_ids).symmetric_difference(related_ids)
    ####################################################
    related_dict = {}
    # rem_ids = [pid for pid in data]
    total = len(rem_ids)
    for counter, pid in enumerate(rem_ids):
        print("Collecting related data for papers:" + str(counter) + '/' + str(total))
        related_dict[pid] = {
                            'datasets': get_datasets(pid),
                            'tasks': get_tasks(pid),
                            'methods': get_methods(pid),
                            'results': get_results(pid),
                            'git-repos': get_git_repos(pid)}

        if len(related_dict) % 1000 == 0:
            save_data(related_dict, filename)
            related_dict = {} # ensures not a lot of data stays in the main memory

    save_data(related_dict, filename)

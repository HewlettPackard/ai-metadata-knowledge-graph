
import pickle
import inflect
from paperswithcode import PapersWithCodeClient 
import re
import os
import time
import json


p = inflect.engine()
client = PapersWithCodeClient()

"""
This script consists of function calls to paper-with-code API to collect task information.
The main function sof this script is called from collect_data.py.
"""

ROOT = '/lustre/venkatre/data/pwc'



def get_task_areas():
    print("Collecting task areas..")
    task_areas = client.area_list().results
    areas = []
    for area in task_areas:
        areas.append({'id': area.id, 'name': area.name})
    return areas


def collect_task_by_area():
    """
    Creates a dict with task-id as key and task_area_id and task_area_name as values.
    """
    task_areas = get_task_areas()
    data_dict = {}
    for area in task_areas:    
        tasks_in_area = client.area_task_list(area_id=area['id']).results
        task_ids = [task.id for task in tasks_in_area]
        for tid in task_ids:
            data_dict[tid] = {'task_area_id': area['id'],
                              'task_area_name': area['name']}
    return data_dict


def append_task_area(data, task_area_dict):
    print("Appending task areas..")
    new_data = {}
    for tid in data:
        current_data = data[tid]
        try:
            task_area = task_area_dict[tid]
        except KeyError:
            task_area = {'task_area_id': None, 'task_area_name': None}
        new_data[tid] = {**current_data, **task_area}
    return new_data


def collect_children_parents(data):
    print("Collecting children and parents of each tasks..")
    counter = 0
    total_len = len(data)
    for tid in data:
        try:
            task_children = client.task_child_list(task_id=tid).results
            task_parents = client.task_parent_list(task_id=tid).results
            task_children_ids = [ele.id for ele in task_children]
            task_parent_ids = [ele.id for ele in task_parents]
            data[tid]['children'] = task_children_ids
            data[tid]['parents'] = task_parent_ids
            counter += 1
            print('Collecting children and parent for task number:' + str(counter) + '/' + str(total_len))
        except:
            pass
    return data

# def collect_task_pid_map():
#     task_data = json.load(open('../data/pwc/pwc-tasks.json', 'r'))
#     task_ids = [i for i in task_data]
#     map_dict = {}
#     for counter, tid in enumerate(task_ids):
#         print("Collecting task-pid map:" +  str(counter) + '/' + str(len(task_ids)))
#         try:
#             res = client.task_paper_list(tid).results
#             paper_ids = [each.id for each in res]
#             map_dict[tid] = paper_ids
#         except:
#             # to avoid key error when using the file
#             map_dict[tid] = []
    
#     json.dump(map_dict, open('../data/pwc/pwc-task-pid-map.json', 'w'))
#     print("Task-PID map saved.")



# Call this function to collect all the tasks
def collect_tasks():
    """
    creates a json file with task-id as the key and another dict as value which contains other params as key-value pairs
    """
    print("Collecting tasks..")
    filename = os.path.join(ROOT, 'pwc-tasks.json')
    items_limit = 500
    task_count = client.task_list().count
    page_count = int(task_count / items_limit) + 2 #range() won't inlcude the last number. Hence +2
    data = {}
    for i in range(1, page_count):
        print("Collecting tasks. Page number:" + str(i) + '/' + str(page_count))
        result = client.task_list(items_per_page=items_limit, page=i) 
        for task in result.results:
            # task_token = process_task_titles(task.name)
            data[str(task.id)] = {'id': task.id,
                                'name': task.name, 
                                'description': task.description}
        time.sleep(3)
    
    
    data = collect_children_parents(data)
    task_area_data = collect_task_by_area()
    final_data = append_task_area(data, task_area_data)


    print("------------",len(final_data))
    json.dump(final_data, open(filename, 'w'))
    print("File saved at:", filename)

    # collect_task_pid_map()



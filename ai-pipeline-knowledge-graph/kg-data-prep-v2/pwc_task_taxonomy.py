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
This script will prepare the pwc_taxonomy crawled from the web to csv format. Specifically to suit KG_Version2 (ID are generated from UUID)
"""


import pandas as pd
import os
import csv
import json
import re
import inflect
import hashlib
import uuid

# Source data path
SRC_DATA_PATH = 'data/pwc'

# CSV files created will be stored in both the places
DEST_LUSTRE_PATH = 'kg-data/pwc/nodes'
DEST_LOCAL_PATH = 'kg-data/pwc/nodes'


# Helper functions
def create_uuid_from_string(string):
    hex_string = int(hashlib.sha1(string.encode("utf-8")).hexdigest(), 16) % (10 ** 10)
    return str(hex_string)


# writes nodes to csv
def write_to_csv(data, filepaths):
    # writing to a csv file
    csv_data = data
    for filepath in filepaths:
        csv_data_file = open(filepath, 'w')
        # create the csv writer object
        csv_writer = csv.writer(csv_data_file)

        # Counter variable used for writing
        # headers to the CSV file
        count = 0
        for element in csv_data:
            if count == 0:
                # Writing headers of CSV file
                header = element.keys()
                csv_writer.writerow(header)
                count += 1
            # Writing data of CSV file
            csv_writer.writerow(element.values())
        csv_data_file.close()
        print("File saved at:", filepath)


# writes relationship ids to csv
def tuple_to_csv(headers, tuples_list, filepaths):
    """
    headers: column names of csv file to be generated. Type: list of strings
    tuple_list: list of tuples, where each tuple is a row
    filepath: destination filepath of the csv file to be saved
    """
    for filepath in filepaths:
        with open(filepath,'w') as out:
            csv_out=csv.writer(out)
            csv_out.writerow(headers)
            for row in tuples_list:
                csv_out.writerow(row)
        print("File saved at:", filepath)




# Collect only the nodes from area and first child. Second child is the task name and we already have that info
# But use second child ID while creating relationships

def taxonomy_graph():
    area_data = json.load(open(os.path.join(SRC_DATA_PATH, "area_data.json"), "r"))
    area_nodes = []
    sub_area_nodes = []
    area_relationships = []
    sub_area_relationships = []

    for aid in area_data:
        area_uid = create_uuid_from_string(aid)
        area_nodes.append({'area_id': area_uid,
            'src_id': aid,
            'name': area_data[aid]['name'],
            'url': area_data[aid]['url']
        })
        
    
    first_child = json.load(open(os.path.join(SRC_DATA_PATH, "first_child.json"), "r"))
    # keys - area_id, first_child_id, second_child_ids, url
    for fid in first_child:
        area_id = first_child[fid]['area_id']
        area_uid = create_uuid_from_string(area_id)
        second_childs = first_child[fid]['second_child_ids']
        first_child_uid = create_uuid_from_string(fid)
        
        sub_area_dict = {'sub_area_id': first_child_uid,
                        'src_id': fid,
                        'name': first_child[fid]['first_child_name'],
                        'url': first_child[fid]['url']}
        
        sub_area_nodes.append(sub_area_dict)
        area_relationships.append((area_uid, first_child_uid))

        for tid in second_childs:
            task_uid = create_uuid_from_string(tid)
            sub_area_relationships.append((first_child_uid, task_uid))
    
    write_to_csv(area_nodes, [os.path.join(DEST_LOCAL_PATH, 'nodes/task_areas.csv'), os.path.join(DEST_LUSTRE_PATH, 'nodes/task_areas.csv')])
    write_to_csv(sub_area_nodes, [os.path.join(DEST_LOCAL_PATH, 'nodes/task_sub_areas.csv'), os.path.join(DEST_LUSTRE_PATH, 'nodes/task_sub_areas.csv')])
    tuple_to_csv(headers=['area_id', 'sub_area_id'], tuples_list=area_relationships, filepaths=[os.path.join(DEST_LOCAL_PATH, 'relationships/rel-task-area-sub-area.csv'), os.path.join(DEST_LUSTRE_PATH, 'relationships/rel-task-area-sub-area.csv')])
    tuple_to_csv(headers=['sub_area_id', 'task_id'], tuples_list=sub_area_relationships, filepaths=[os.path.join(DEST_LOCAL_PATH, 'relationships/rel-task-sub-area-task.csv'), os.path.join(DEST_LUSTRE_PATH, 'relationships/rel-task-sub-area-task.csv')])

        



taxonomy_graph()
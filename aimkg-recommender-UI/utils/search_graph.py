from .neo4j_connection import Neo4jConnection
from dotenv import load_dotenv
import os
import random
from .d3_graph import neo4j_to_d3

load_dotenv()
URI = 'bolt://localhost:7687'
USER = os.getenv("NEO4J_USER_NAME")
PASSWORD = os.getenv("NEO4J_PASSWD")
AUTH = (os.getenv("NEO4J_USER_NAME"), os.getenv("NEO4J_PASSWD"))

# Instantiate Neo4j connection
neo4j_obj = Neo4jConnection(uri=URI, 
                    user=USER,
                    pwd=PASSWORD)


def neo4j_to_names(result, limit=1000):
    names_list = []
    for item in result:
        curr_dict = dict(item[0])
        names_list.append(curr_dict['name'])
    if limit is None:
        names_list.sort()
        return names_list
    else:
        names_list = list(set(names_list))
        if '' in names_list:
            names_list.remove('')
        # random.shuffle(names_list)
        names_list = names_list[:limit]
        names_list.sort()
        return names_list


def drop_down_values(limit=1000):

    task_query = """MATCH (n:Task) return properties(n)"""
    task_res = neo4j_obj.query(task_query)
    task_names = neo4j_to_names(task_res, limit=limit)

    dataset_query = """MATCH (n:Dataset) return properties(n)"""
    dataset_res = neo4j_obj.query(dataset_query)
    dataset_names = neo4j_to_names(dataset_res, limit=limit)
    dataset_names.append('CalTech 101 Silhouettes')

    model_query = """MATCH (n:Model) return properties(n)"""
    model_res = neo4j_obj.query(model_query)
    model_names = neo4j_to_names(model_res,limit=limit)
    return {'task': task_names, 'dataset': dataset_names, 'model': model_names}


def get_OR_query_results(task=None, dataset=None, model=None):
    results = []

    if task != "None":
        task_query ="""MATCH (task:Task {name:$task_name})
            OPTIONAL MATCH (task)-[r1]-(pipeline:Pipeline)
            OPTIONAL MATCH (pipeline)-[r2]-(stage:Stage)
            OPTIONAL MATCH (stage)-[r3]-(execution:Execution)
            OPTIONAL MATCH (execution)-[r4]-(artifact:Artifact)
            OPTIONAL MATCH (artifact)-[r5]-(dataset:Dataset)
            OPTIONAL MATCH (artifact)-[r6]-(model:Model)
            OPTIONAL MATCH (artifact)-[r7]-(metric:Metric)
            OPTIONAL MATCH (pipeline)-[r8]-(framework:Framework)
            OPTIONAL MATCH (pipeline)-[r9]-(report:Report)
            RETURN task, pipeline, stage, execution, artifact, dataset, model, metric, framework, report, r1, r2, r3, r4, r5, r6, r7, r8, r9
            limit 100"""
        task_parameters = {'task_name': task}
        task_res = neo4j_obj.query(task_query, parameters=task_parameters)
        results.append(task_res)

    if dataset != "None":
        dataset_query ="""MATCH (dataset:Dataset {name:$dataset_name})
            OPTIONAL MATCH (dataset)-[r5]-(artifact:Artifact)
            OPTIONAL MATCH (artifact)-[r6]-(model:Model)
            OPTIONAL MATCH (artifact)-[r7]-(metric:Metric)
            OPTIONAL MATCH (artifact)-[r4]-(execution:Execution)
            OPTIONAL MATCH (execution)-[r3]-(stage:Stage)
            OPTIONAL MATCH (stage)-[r2]-(pipeline:Pipeline)
            OPTIONAL MATCH (pipeline)-[r1]-(task:Task)
            OPTIONAL MATCH (pipeline)-[r8]-(framework:Framework)
            OPTIONAL MATCH (pipeline)-[r9]-(report:Report)
            RETURN task, pipeline, stage, execution, artifact, dataset, model, metric, framework, report, r1, r2, r3, r4, r5, r6, r7, r8, r9
            limit 100"""
        dataset_parameters = {'dataset_name': dataset}
        dataset_res = neo4j_obj.query(dataset_query, parameters=dataset_parameters)
        results.append(dataset_res)

    if model != "None":
        model_query ="""MATCH (model:Model {name:$model_name})
            OPTIONAL MATCH (task:Task)-[r1]-(pipeline:Pipeline)
            OPTIONAL MATCH (pipeline)-[r2]-(stage:Stage)
            OPTIONAL MATCH (stage)-[r3]-(execution:Execution)
            OPTIONAL MATCH (execution)-[r4]-(artifact:Artifact)
            OPTIONAL MATCH (artifact)-[r5]-(dataset:Dataset)
            OPTIONAL MATCH (artifact)-[r6]-(model)
            OPTIONAL MATCH (artifact)-[r7]-(metric:Metric)
            OPTIONAL MATCH (pipeline)-[r8]-(framework:Framework)
            OPTIONAL MATCH (pipeline)-[r9]-(report:Report)
            RETURN task, pipeline, stage, execution, artifact, dataset, model, metric, framework, report, r1, r2, r3, r4, r5, r6, r7, r8, r9
            limit 100"""
        model_parameters = {'model_name': model}
        model_res = neo4j_obj.query(model_query, parameters=model_parameters)
        results.append(model_res)
    
    if task == "None" and dataset == "None" and model == "None":
        query_str = """
        MATCH (met:Metric)-[r1]-(a:Artifact)-[r2]-(e:Execution)-[r3]-(s:Stage)-[r4]-(p:Pipeline)-[r5]-(t:Task)
        WITH met, a, e, s, p, t, r1, r2, r3, r4, r5
        MATCH (d:Dataset)-[r6]-(a)-[r7]-(m:Model)
        RETURN d, a, m, e, s, p, t, met, r1, r2, r3, r4, r5, r6, r6 limit 100
        """
        res = neo4j_obj.query(query_str)
        results.append(res)

    return results

# NOTE: THIS QUERY ALWAYS RETURNS THE SAME RESULT
# def build_AND_query(task=None, dataset=None, model=None):
#     # Initialize the base query
#     base_query = """
#             OPTIONAL MATCH (task)-[r1]-(pipeline:Pipeline)
#             OPTIONAL MATCH (pipeline)-[r2]-(stage:Stage)
#             OPTIONAL MATCH (stage)-[r3]-(execution:Execution)
#             OPTIONAL MATCH (execution)-[r4]-(artifact:Artifact)
#             OPTIONAL MATCH (artifact)-[r5]-(dataset:Dataset)
#             OPTIONAL MATCH (artifact)-[r6]-(model:Model)
#             OPTIONAL MATCH (artifact)-[r7]-(metric:Metric)
#             OPTIONAL MATCH (pipeline)-[r8]-(framework:Framework)
#             OPTIONAL MATCH (pipeline)-[r9]-(report:Report)
#     """

#     # Conditions list for AND combinations
#     conditions = []

#     if task != "None":
#         conditions.append("task.name = '{}'".format(task))
#     if dataset != "None":
#         conditions.append("dataset.name = '{}'".format(dataset))
#     if model != "None":
#         conditions.append("model.name = '{}'".format(model))

#     # Build the query based on AND conditions
#     if conditions:
#         query = base_query + " WHERE " + " AND ".join(conditions)
#     else:
#         query = base_query

#     query += """ RETURN task, pipeline, stage, execution, artifact, dataset, model, metric, framework, report, 
#     r1, r2, r3, r4, r5, r6, r7,r8, r9 LIMIT 300"""

#     print("Generated AND Query:", query)
#     return query


def search_pipelines(query_task=None, query_dataset=None, query_model=None, query_type='OR'):
    if query_type == 'OR':
        results = get_OR_query_results(task=query_task, dataset=query_dataset, model=query_model)
        if results == []:
            return {'nodes':[], 'links':[]} 
        else:
            res_d3_graphs = neo4j_to_d3(results) 
            return res_d3_graphs

    # if query_type == 'AND':
    #     query_str = build_AND_query(task=query_task, dataset=query_dataset, model=query_model)
    #     result = neo4j_obj.query(query_str)
    #     if result is None:
    #         return {'nodes':[], 'links':[]} 
    #     else:
    #         res_d3_graphs = neo4j_to_d3([result]) # expects list of neo4j results
    #         return res_d3_graphs
    

def search_custom_query(query_str):
    result = neo4j_obj.query(query_str)
    result = [result] # neo4j_d3_graph handles list of graphs. So expects result in list of neo4j_records format
    result_d3_graph = neo4j_to_d3(result)
    return result_d3_graph

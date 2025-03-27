from .neo4j_connection import Neo4jConnection
from .d3_graph import neo4j_to_d3
from dotenv import load_dotenv
import os
import torch
from sentence_transformers import SentenceTransformer
import torch.nn.functional as F
from tqdm import tqdm
import time
import h5py
import glob

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# DEVICE = torch.device("cpu")
embedding_model = SentenceTransformer("all-mpnet-base-v2").to(DEVICE)

load_dotenv()
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER_NAME")
PASSWORD = os.getenv("NEO4J_PASSWD")
AUTH = (os.getenv("NEO4J_USER_NAME"), os.getenv("NEO4J_PASSWD"))

# Instantiate Neo4j connection
neo4j_obj = Neo4jConnection(uri=URI, 
                    user=USER,
                    pwd=PASSWORD)

def find_file_path(filename, search_directory="."):
    # Use glob to search recursively in the current directory for the file
    for file_path in glob.iglob(f"{search_directory}/**/{filename}", recursive=True):
        return os.path.abspath(file_path)
    return None


def create_tokens(tid):
    tokens = tid.split("-")
    return tokens

def convert_json(result):
    data_dict = {}
    for item in result:
        curr_dict = dict(item[0])
        item_id = curr_dict['itemID']
        name = curr_dict['name']
        curr_dict['tokens'] = create_tokens(name)
        data_dict[item_id] = curr_dict
    return data_dict

def get_models():
    nodes= """MATCH (n:Model) RETURN properties(n)""" 
    res = neo4j_obj.query(nodes)
    data_dict = convert_json(res)
    return data_dict

def get_model_node(id):
    nodes= """MATCH (n:Model {itemID:$id}) RETURN properties(n)""" 
    parameters = {'id':id}
    res = neo4j_obj.query(nodes, parameters)
    data_dict = convert_json(res)
    return data_dict


# TODO: change the query here
def get_result_pipelines(model_ids):
    """
    For the given task ids (top similar ones) get the entire pipeline and return to the main function
    """
    results = []
    for dataset_id in model_ids:
        query_str = """MATCH (dataset:Dataset {itemID:$dataset_id})
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
            limit 20"""
        parameters = {'dataset_id':dataset_id}
        res = neo4j_obj.query(query_str, parameters)
        results.append(res)
    return results


# TODO: Modify as per model features
def get_explanations(query_model, top_task_ids, task_dict):
    explanations = [] #first element is always query task
    explanations.append({'title':'Query', 'content': {'Name': query_model.title(), 'Label': 'Dataset', 
                         'Properties Computed': {'Model Class':'',
                                                 }}})
    for i, tid in enumerate(top_task_ids):
        curr_item = task_dict[tid]
        explanations.append({'title':'Recommendation-'+str(i+1), 'content':{'Name': curr_item['name'].title(), 'Similarity Score':'', 
                             'Similar Properties':{'Tokens':curr_item['tokens'], 'Model Class':curr_item['modelClass']}}})
    
    return explanations




def get_similar_models(query_model, num_res=3):
    start_time = time.time()
    num_res=3
    # test - compute just embedding similarity from all the files
    data_dict = get_models()

    filename = 'model_embeddings_all.h5'
    filepath = find_file_path(filename=filename)
    with h5py.File(filepath, 'r') as f:
        # Load the datasets
        embedding_ids = f['embedding_ids'][:]  # Reads all the IDs
        embeddings = f['embeddings'][:]    

    model_ids = [id.decode('utf-8') for id in embedding_ids]  # Decode if IDs are stored as byte strings
    embeddings = torch.tensor(embeddings).to(DEVICE)  # Convert embeddings to a torch tensor

    query_embedding = torch.tensor(embedding_model.encode(str(query_model))).view(1, -1).to(DEVICE)
    

    cos_sim =  F.cosine_similarity(query_embedding, embeddings, dim=1)
    print(len(cos_sim), cos_sim.device)
    # Sort the tensor in descending order and get the indices
    sorted_tensor, sorted_indices = torch.sort(cos_sim, descending=True)
    indices = sorted_indices[:num_res]
    top_ids = [model_ids[idx] for idx in indices]
    explanations = get_explanations(query_model, top_ids, data_dict)
    neo4j_results = get_result_pipelines(top_ids)
    result_d3_graphs = neo4j_to_d3(neo4j_results)
    result_items = {'nodes': result_d3_graphs['nodes'], 'links':result_d3_graphs['links'], 'explanations':explanations}
    print("Time Taken",time.time()-start_time)
    similar_item_dict = []
    for id in top_ids:
        similar_item_dict.append(get_model_node(id))
    return result_items, similar_item_dict

# get_similar_models("clinical llama")
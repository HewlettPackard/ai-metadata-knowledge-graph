"""
This needs to be executed once when we set up the demo
This script computes embeddings for all the task, dataset, model, pipeline_title and pipeline_abstracts
"""
# TODO - store emebddings in secondary storage

from neo4j_connection import Neo4jConnection
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import os
from tqdm import tqdm
import torch
import h5py
import numpy as np

load_dotenv()
URI = 'bolt://localhost:7687'
USER = os.getenv("NEO4J_USER_NAME")
PASSWORD = os.getenv("NEO4J_PASSWD")
AUTH = (os.getenv("NEO4J_USER_NAME"), os.getenv("NEO4J_PASSWD"))

# Instantiate Neo4j connection
neo4j_obj = Neo4jConnection(uri=URI, 
                    user=USER,
                    pwd=PASSWORD)


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
embedding_model = SentenceTransformer("all-mpnet-base-v2").to(DEVICE)
EMBED_DIM=768


class ComputeEmbeddings():
    def __init__(self, model):
        self.embedding_model = model
        # Wrap the model with DataParallel to use multiple GPUs
        # self.embedding_model = torch.nn.DataParallel(self.embedding_model)
        # Set the model to evaluation mode
        # self.embedding_model.eval()
    
    def create_tokens(self, item_name):
        tokens_ = item_name.split(" ")
        tokens = [t.lower() for t in tokens_]
        return tokens
        
    def convert_json(self, result):
        data_dict = {}
        for item in result:
            curr_dict = dict(item[0])
            item_id = curr_dict['itemID']
            name = curr_dict['name']
            curr_dict['tokens'] = self.create_tokens(name)
            data_dict[item_id] = curr_dict
        return data_dict

    def get_item_nodes(self, item):
        get_nodes_query = """MATCH (n:{}) RETURN properties(n)""" 
        get_nodes_query = get_nodes_query.format(item)
        res = neo4j_obj.query(get_nodes_query)
        data_dict = self.convert_json(res)
        return data_dict
    
    def task_embeddings(self):
        task_dict = self.get_item_nodes(item='Task')
        print("Computing task embeddings..")
        task_ids = []
        task_embeds = []
        for key in tqdm(task_dict):
            curr_item = task_dict[key]
            # if curr_item['source'] == 'papers-with-code' or curr_item['source'] == 'huggingface':
            item_id = curr_item['itemID']
            name = curr_item['name']
            task_ids.append(item_id)
            embedding = torch.tensor(self.embedding_model.encode(str(name))).cpu()
            task_embeds.append(embedding)
                # filepath = os.path.join('task_embeddings', str(item_id) + '.pt')
                # torch.save(embedding, filepath)
            
        with h5py.File('task_embeddings_all.h5', 'w') as f:
            f.create_dataset('embedding_ids', data=np.array(task_ids, dtype='S32'))  # Store as fixed-length byte strings
            f.create_dataset('embeddings', data=np.array(task_embeds))
        return "Task embeddings complete"
    
    
    def dataset_embeddings(self):
        dataset_dict = self.get_item_nodes(item='Dataset')
        print("Computing dataset embeddings..")
        dataset_ids = []
        embeddings = []
        for key in tqdm(dataset_dict):
            curr_item = dataset_dict[key]
            # if curr_item['source'] == 'papers-with-code' or curr_item['source'] == 'huggingface':
            item_id = curr_item['itemID']
            dataset_ids.append(item_id)
            name = curr_item['name']
            embedding = torch.tensor(self.embedding_model.encode(str(name))).cpu()
            embeddings.append(embedding)
                # filepath = os.path.join('dataset_embeddings', str(item_id) + '.pt')
                # torch.save(embedding, filepath)
        
        with h5py.File('dataset_embeddings_all.h5', 'w') as f:
            f.create_dataset('embedding_ids', data=np.array(dataset_ids, dtype='S32'))  # Store as fixed-length byte strings
            f.create_dataset('embeddings', data=np.array(embeddings))
        return "Dataset embeddings complete"
    
    def model_embeddings(self):
        model_dict = self.get_item_nodes(item='Model')
        print("Computing dataset embeddings..")
        model_ids = []
        embeddings = []
        for key in tqdm(model_dict):
            curr_item = model_dict[key]
            # if curr_item['source'] == 'papers-with-code' or curr_item['source'] == 'huggingface':
            item_id = curr_item['itemID']
            name = curr_item['name']
            embedding = torch.tensor(self.embedding_model.encode(str(name))).cpu()
            # filepath = os.path.join('model_embeddings', str(item_id) + '.pt')
            # torch.save(embedding, filepath)
            model_ids.append(item_id)
            embeddings.append(embedding)

        
        with h5py.File('model_embeddings_all.h5', 'w') as f:
            f.create_dataset('embedding_ids', data=np.array(model_ids, dtype='S32'))  # Store as fixed-length byte strings
            f.create_dataset('embeddings', data=np.array(embeddings))
        return "Model embeddings complete"
    
    def pipeline_embeddings(self):
        pipeline_dict = self.get_item_nodes(item='Pipeline')
        print("Computing dataset embeddings..")
        pipeline_ids = []
        embeddings = []
        for key in tqdm(pipeline_dict):
            curr_item = pipeline_dict[key]
            if curr_item['source'] == 'papers-with-code' or curr_item['source'] == 'huggingface':
                item_id = curr_item['itemID']
                name = curr_item['name']
                embedding = torch.tensor(self.embedding_model.encode(str(name))).cpu()
                pipeline_ids.append(item_id)
                embeddings.append(embedding)

        
        with h5py.File('pipeline_embeddings_all.h5', 'w') as f:
            f.create_dataset('embedding_ids', data=np.array(pipeline_ids, dtype='S32'))  # Store as fixed-length byte strings
            f.create_dataset('embeddings', data=np.array(embeddings))
    
        return "Pipeline title embeddings complete"
    

com_obj = ComputeEmbeddings(model=embedding_model)
com_obj.task_embeddings()
com_obj.dataset_embeddings()
com_obj.model_embeddings()
# com_obj.pipeline_embeddings()
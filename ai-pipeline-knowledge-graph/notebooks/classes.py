# This is a supporting py file to generate/compute task similarity. Filename: task_ggraph.ipynb
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


import json
import torch
import torch.nn as nn
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import time


class AdjacencyMatrix:
    def __init__(self, model, embedding_folder):
        super(AdjacencyMatrix, self).__init__()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = model.to(self.device)
        print(next(self.model.parameters()).device)
        self.embedding_folder = embedding_folder
        self.cos = nn.CosineSimilarity(dim=1, eps=1e-6)

    def save_embeddings(self, task_data):
        print("Creating one-time emebddings as it is not present or creating embeddings as requested by the user..")
        start = time.time()
        print("Start")
        for tid in task_data:
            task_dict = task_data[tid]
            task1_name = task_dict['name']
            embedding = self.model.encode(task1_name)
            embedding = embedding.tolist()
            filename = str(tid) + '.pt'
            filepath = os.path.join(self.embedding_folder, filename)
            torch.save(embedding, filepath)
        print("All files saved. Time taken to generate and save files", time.time()-start)


    def open_embeddings(self, task_data):
        print("Opening embeddings to create embedding matrix")
        embeddings = []
        for tid in task_data:
            task_filename = str(tid) + '.pt'
            task_embed = torch.tensor(torch.load(os.path.join(self.embedding_folder, task_filename))).tolist()
            embeddings.append(task_embed)

        return torch.tensor(embeddings)


    def get_embedding_similarity(self, task_dict, embedding_matrix):
        """
        task1_dict = task details for which similarity will be calculated aganist all other task name embeddings
        embedding_matrix: tensors of embeddings generated for all task names. len(embedding_matrix) = len(task_names)
        """
        task_filename = str(task_dict['taskID']) + '.pt'
        # Open the saved embedding for a given task (arg:task_dict)
        task_embed = torch.tensor(torch.load(os.path.join(self.embedding_folder, task_filename))).to(self.device).view(1,-1)
        # Set embedding matrix to GPU
        embedding_matrix = embedding_matrix.to(self.device)
        # compute cosine similarity for a task name aganist all other task names 
        cos_sim = self.cos(task_embed, embedding_matrix).tolist()
        return cos_sim

    def get_task_category_similarity(self, curr_task_dict, tasks_data):
        """
        curr_task_dict: a dict of a given task details for which similarity will be calculated aganist all other tasks
        tasks_data: the json file where all the task information is stored as dict
        return: a list of similarity metric for (task-i) versus (task-1 to n), where n is the total number of tasks
        """
        curr_task_category = curr_task_dict['category']
        category_sim = []
        for tid in tasks_data:
            other_task_category = tasks_data[tid]['category']
            # print(curr_task_category, other_task_category)
            if len(curr_task_category) == 0 and len(other_task_category) == 0:
                category_score = 0.0
            else:
                # compute the IOU
                category_score = len(set(curr_task_category).intersection(set(other_task_category))) / len(set(curr_task_category).union(set(other_task_category)))

            category_sim.append(category_score)
    
        return category_sim


    def get_task_modality_similarity(self, curr_task_dict, tasks_data):
        """
        curr_task_dict: a dict of a given task details for which similarity will be calculated aganist all other tasks
        tasks_data: the json file where all the task information is stored as dict
        return: a list of similarity metric for (task-i) versus (task-1 to n), where n is the total number of tasks
        """
        curr_task_modality = curr_task_dict['modality']
        modality_sim = []
        for tid in tasks_data:
            other_task_modality = tasks_data[tid]['modality']
            if len(curr_task_modality) == 0 and len(other_task_modality) == 0:
                modality_score = 0.0
            else:
                # compute the IOU
                modality_score = len(set(curr_task_modality).intersection(set(other_task_modality))) / len(set(curr_task_modality).union(set(other_task_modality)))

            modality_sim.append(modality_score)
        return modality_sim

    def get_token_matching_similarity(self, curr_task_dict, tasks_data):
        """
        curr_task_dict: a dict of a given task details for which similarity will be calculated aganist all other tasks
        tasks_data: the json file where all the task information is stored as dict
        return: a list of similarity metric for (task-i) versus (task-1 to n), where n is the total number of tasks
        """
        curr_task_tokens = curr_task_dict['tokens']
        token_sim = []
        for tid in tasks_data:
            other_task_tokens = tasks_data[tid]['tokens']
            # compute matching words score using IOU / embeddings
            common_task_tokens = set(curr_task_tokens).intersection(set(other_task_tokens))
            common_words_score = len(common_task_tokens) / len(set(curr_task_tokens).union(set(other_task_tokens)))
            token_sim.append(common_words_score)

        return token_sim


    def custom_sim(self, curr_task_dict, tasks_data, embedding_matrix, threshold=0):
        """
        curr_task_dict: a dict a given task for which the similarity will be calculated aganist all other tasks
        tasks_data: task details for all the tasks
        threshold: similarity threshold. Similarity values below this threshold will be ignored (set to 0)
        return: a list of similarity metric for (task-i) versus (task-1 to n), where n is the total number of tasks
        """

        embed_sim = self.get_embedding_similarity(curr_task_dict, embedding_matrix)
        category_sim = self.get_task_category_similarity(curr_task_dict, tasks_data)
        modality_sim = self.get_task_modality_similarity(curr_task_dict, tasks_data)
        token_sim = self.get_token_matching_similarity(curr_task_dict, tasks_data)

        similarity = np.array([embed_sim, modality_sim, category_sim, token_sim])
        similarity_score = np.mean(similarity, axis=0)
        
        # Set similairty values below threshold value to zero
        similarity[similarity < threshold] = 0
 
        return similarity_score
    

    def create(self, tasks_data, new_task_dict=None, sim_threshold=0, compute_embeddings=True):
        """
        creates a new adjancency matrix from tasks_data provided.
        """
        if new_task_dict == None:
            embedding_path = os.path.exists(self.embedding_folder)
            if not embedding_path:
                os.mkdir(self.embedding_folder)
            # if compute_embeddings:
            start_time = time.time()
            self.save_embeddings(tasks_data)
            print("Time taken to generate embeddings and store:", time.time()-start_time)
            return 0
            print("Creating Ajacency Matrix..")
            # Open the embeddings generated for all tasks and concatenate into one matrix
            embedding_matrix = self.open_embeddings(tasks_data)
            adj_matrix = []
            for task_id in tasks_data:
                current_task_dict = tasks_data[task_id]
                similarity = self.custom_sim(current_task_dict, tasks_data, embedding_matrix, sim_threshold) # send both the task data as a dict
                adj_matrix.append(similarity)

            adj_matrix = np.array(adj_matrix)
            return adj_matrix
        else:
            # New task
            # Call create embeddings with new task_dict
            self.save_embeddings(new_task_dict)
            # Call custom sim with new_task as curr_dict and rest as task data
            print("Creating Ajacency Matrix for the new data..")
            # Open the embeddings generated for all tasks and concatenate into one matrix
            embedding_matrix = self.open_embeddings(tasks_data)
            adj_matrix = []
            for task_id in new_task_dict:
                curr_task_dict = new_task_dict[task_id]
                similarity = self.custom_sim(curr_task_dict, tasks_data, embedding_matrix, sim_threshold)
                adj_matrix.append(similarity)
            return np.array(adj_matrix)

        
class LoadData:
    def __init__(self, conn):
        super(LoadData, self).__init__()
        self.conn = conn
        pass

    def load_task_nodes(self, task_dict, new_task_dict=None):
        if new_task_dict:
            data_dict = new_task_dict
        else:
            data_dict = task_dict
        # load the nodes    
        for tid in data_dict:
            curr_dict = data_dict[tid]
            query_str = """MERGE (task:SemTask {taskID: $taskID}) 
            ON CREATE SET task.name = $name, task.taskDesc = $desc, task.modality = $modality, task.category = $category"""
            params = {'taskID':curr_dict['taskID'],
                    'name':curr_dict['name'],
                    'desc':curr_dict['taskDesc'],
                    'modality': curr_dict['modality'],
                    'category':curr_dict['category']}
            res = self.conn.query(query_str, parameters=params)
        print("Tasks loaded")
    

    def load_similarities(self, task_tuples):
        """
        Input data format: list of tuples - [(task1, task2, similarity),(task1, task2, similarity)...]
        """
        for item in task_tuples:
            query_str = """ MATCH (t:SemTask {taskID: $tid1})
            MATCH (tt:SemTask {taskID: $tid2})
            MERGE (t)-[r:isSimilar]-(tt)
            ON CREATE SET r.value = toFloat($value);
            """
            params = {'tid1': item[0],
                    'tid2': item[1],
                    'value': item[2]}
            res = self.conn.query(query_str, parameters=params)
        print("Loaded similarity values")

    def create_tuples(self, task_ids, adj_matrix, new_task_id=None):
        # TODO - detect duplicates
        
        # Helper function to convert adjacency matrix to required format
        if new_task_id == None:
            tuples_list = []
            for i, lst in enumerate(adj_matrix):
                tid1 = task_ids[i]
                for j in list(range(len(lst))):
                    sim_val = lst[j]
                    tid2 = task_ids[j]
                    if tid1 == tid2:
                        pass
                    else:
                        tuples_list.append((tid1, tid2, sim_val))
            return tuples_list
        else:
            tuples_list = []
            for i, lst in enumerate(adj_matrix):
                tid1 = new_task_id[i]
                for j in list(range(len(lst))):
                    sim_val = lst[j]
                    tid2 = task_ids[j]
                    if tid1 == tid2:
                        pass
                    else:
                        tuples_list.append((tid1, tid2, sim_val))
            return tuples_list
                

    
    def load_data(self, task_dict, adj_matrix, new_task_dict=None):
        task_ids = [tid for tid in task_dict]
    
        if new_task_dict:
            print("New Task")
            new_task_id = [i for i in new_task_dict]
            tuples_list = self.create_tuples(task_ids, adj_matrix, new_task_id)
            self.load_task_nodes(task_dict, new_task_dict)
        else:
            # All tasks
            tuples_list = self.create_tuples(task_ids, adj_matrix)
            self.load_task_nodes(task_dict)
             
        self.load_similarities(tuples_list)

        
class TaskProperties:
    def __init__(self):
        super(TaskProperties, self).__init__()
        self.task_category_vocab = ['recognition', 'regression','reconstruction', 'segmentation', 'detection', 'generation', 'harmonization', 'translation','classification', 'adaptation', 'search', 'analysis', 'extraction', 'retrieval', 'annotation', 'generalization', 'augmentation', 'anonymization', 'prediction', 'correlation', 'fusion', 'matching', 'synthesis', 'understanding', 'testing', 'parsing', 'identification', 'transfer', 'spotting', 'estimation', 'resolution', 'clustering', 'separation', 'localization', 'summarization', 'reccommendation', 'expansion', 'labeling', 'imaging', 'interpretation', 'captioning', 'retrieval', 'selection', 'assessment', 'registration', 'forecasting', 'planning', 'tracking', 'inference','grounding', 'disambiguation', 'reasoning', 'comprehension', 'reading', 'reduction', 'completion', 'compression', 'decomposition', 'learning', 'sampling', 'verification', 'animation','interpolation', 'visualizaiton', 'propagation', 'mining', 'surveillance', 'diagnosis', 'ranking', 'optimization', 'synthesis', 'anomaly', 'linking']

        # Task Modality vocabulary
        self.image_vocab = ['2d', '3d', 'image', 'visual', 'depth']
        self.text_vocab = ['text', 'word', 'language', 'lingual', 'dialogue', 'dialog', 'textual', 'word', 'translation', 'question', 'answering', 'conversational', 'conversation']
        self.video_vocab = ['video']
        self.audio_vocab = ['audio', 'voice']
        self.multi_vocab = ['multi', 'cross', 'multimodal', 'crossmodal']
        self.super_class = ['image', 'text', 'video', 'audio']
        
        
    def compute_category(self, item_tokens):
        tokens = list(item_tokens)
        inter = list(set(tokens).intersection(set(self.task_category_vocab)))
        if len(inter) > 0:
            category = inter[0]
        else:
            category = "none"
        return category


    def compute_modality(self, item_tokens):
        tokens = list(item_tokens)
        modality_list = []
        # check for images
        if len(set(tokens).intersection(set(self.image_vocab))) > 0:
            modality_list.append('image')

        # check for text
        elif len(set(tokens).intersection(set(self.text_vocab))) > 0:
            modality_list.append('text')

        # check for audio
        elif len(set(tokens).intersection(set(self.audio_vocab))) > 0:
            modality_list.append('audio')

        # check for video
        elif len(set(tokens).intersection(set(self.video_vocab))) > 0:
            modality_list.append('video')

        # check for multimodal
        elif len(set(tokens).intersection(set(self.multi_vocab))) > 0:
            modality_list.append('multimodal')
        else:
            pass
        # If title has image and text but not multimodal or cross modal, the following case will capture it
        if len(set(modality_list).intersection(set(self.super_class))) > 0:
            modality_list.append('multimodal')

        if len(modality_list) > 0:
            modality = modality_list[0]
        else:
            modality = "none"
        return modality


    
class NewTask:
    def __init__(self, conn):
        super(NewTask, self).__init__()
        self.conn = conn
        pass
    
    def create_tokens(self, tid):
        tokens = tid.split("-")
        return tokens

    def convert_json(self, result):
        data_dict = {}
        for item in result:
            curr_dict = dict(item[0])
            tid = curr_dict['taskID']
            curr_dict['tokens'] = self.create_tokens(tid)
            data_dict[tid] = curr_dict
        return data_dict
    
    def get_tasks(self):
        get_task_nodes= """ MATCH (n:SemTask) RETURN properties(n) LIMIT 10""" 
        res = self.conn.query(get_task_nodes)
        task_dict = self.convert_json(res)
        return task_dict
    
    def new_task_dict(self, tid):
        task_prop = TaskProperties()
        tokens = self.create_tokens(tid)
        category = task_prop.compute_category(tokens)
        modality = task_prop.compute_modality(tokens)
        taskName = ' '.join(tokens)
        taskName = taskName.capitalize()
        data_dict = {}
        data_dict[tid] = {'taskID': tid,
                          'name':taskName,
                          'tokens': tokens,
                          'modality':modality,
                          'category':category,
                          'taskDesc':'none'}
        return data_dict
    
    def compute_similarity(self, tid, model, embedding_folder):
        new_task_dict = self.new_task_dict(tid)
        exist_task_dict = self.get_tasks()
        exist_task_dict.update(new_task_dict)
        adj = AdjacencyMatrix(model, embedding_folder)
        adj_matrix = adj.create(exist_task_dict, new_task_dict)
        return new_task_dict, exist_task_dict, adj_matrix
task_category_vocab = ['recognition', 'regression','reconstruction', 'segmentation', 'detection', 'generation', 'harmonization', 'translation', 'classification', 'adaptation', 'search', 'analysis',
'extraction', 'retrieval', 'annotation', 'generalization', 'augmentation', 'anonymization', 'prediction', 'correlation', 'fusion', 'matching', 'synthesis', 'understanding',
'testing', 'parsing', 'identification', 'transfer', 'spotting', 'estimation', 'resolution', 'clustering', 'separation', 'localization', 'summarization', 'reccommendation',
'expansion', 'labeling', 'imaging', 'interpretation', 'captioning', 'retrieval', 'selection', 'assessment', 'registration', 'forecasting', 'planning', 'tracking', 'inference',
'grounding', 'disambiguation', 'reasoning', 'comprehension', 'reading', 'reduction', 'completion', 'compression', 'decomposition', 'learning', 'sampling', 'verification', 'animation',
'interpolation', 'visualizaiton', 'propagation', 'mining', 'surveillance', 'diagnosis', 'ranking', 'optimization', 'synthesis', 'anomaly', 'linking']

# Task Modality vocabulary
image_vocab = ['2d', '3d', 'image', 'visual', 'depth', 'pixel', 'voxel', 'RBG', 'action', 'object', 'facial',
'pose', 'grayscale', 'texture', 'pattern','face', 'scene', 'imagery', 'imaging', 'image-based', 'vision', 'computer-vision', 'computer vision']
text_vocab = ['text', 'word', 'language', 'lingual', 'dialogue', 'dialog', 'corpus', 'sentence', 'reading', 'news', 'reviews', 
'grammar', 'grammatical', 'natural-language-processing', 'nlp', 'natural language processing',
'textual', 'translation', 'question', 'answering', 'conversational', 'conversation', 'entity', 'document', 'paragraph', 'paraphrase']
video_vocab = ['video', 'video-based', 'motion']
audio_vocab = ['audio', 'voice', 'speech', 'sound', 'headphone', 'music', 'spoken']
multi_vocab = ['multi', 'cross', 'multimodal', 'crossmodal', 'multi-modal']
super_class = ['image', 'text', 'video', 'audio']




from .neo4j_connection import Neo4jConnection
from .d3_graph import neo4j_to_d3
from dotenv import load_dotenv
import os
import torch
from sentence_transformers import SentenceTransformer
import torch.nn.functional as F
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

def compute_category(item_tokens):
    tokens = list(item_tokens)
    inter = list(set(tokens).intersection(set(task_category_vocab)))
    if len(inter) > 0:
        category = ','.join(inter)
    else:
        category = "none"
    return category


def compute_modality(item_tokens):
    tokens = list(item_tokens)
    modality_list = []
    # check for images
    if len(set(tokens).intersection(set(image_vocab))) > 0:
        modality_list.append('image')

    # check for text
    elif len(set(tokens).intersection(set(text_vocab))) > 0:
        modality_list.append('text')

    # check for audio
    elif len(set(tokens).intersection(set(audio_vocab))) > 0:
        modality_list.append('audio')
    
    # check for video
    elif len(set(tokens).intersection(set(video_vocab))) > 0:
        modality_list.append('video')
    
    # check for multimodal
    elif len(set(tokens).intersection(set(multi_vocab))) > 0:
        modality_list.append('multimodal')
    else:
        pass
    
    # If title has image and text but not multimodal or cross modal, the following case will capture it
    if len(set(modality_list).intersection(set(super_class))) > 1:
        modality_list.append('multimodal')
    
    if len(modality_list) > 0:
        modality = ','.join(modality_list)
    else:
        modality = "none"
    return modality


def create_tokens(tid):
    tokens_ = tid.split(" ")
    tokens = [t.lower() for t in tokens_]
    return tokens

def convert_json(result):
    data_dict = {}
    for item in result:
        curr_dict = dict(item[0])
        # if curr_dict['source'] == 'papers-with-code' or curr_dict['source'] == 'huggingface':
        item_id = curr_dict['itemID']
        name = curr_dict['name']
        curr_dict['tokens'] = create_tokens(name)
        data_dict[item_id] = curr_dict
    return data_dict

def get_pipelines():
    get_pipeline_nodes= """MATCH (n:Pipeline) RETURN properties(n)""" 
    res = neo4j_obj.query(get_pipeline_nodes)
    data_dict = convert_json(res)
    return data_dict

def get_pipeline_node(id):
    get_pipeline_nodes= """MATCH (n:Pipeline {itemID:$id}) RETURN properties(n)"""
    parameters = {'id':id}
    res = neo4j_obj.query(get_pipeline_nodes, parameters)
    data_dict = convert_json(res)
    return data_dict


def get_result_pipelines(pipeline_ids):
    """
    For the given task ids (top similar ones) get the entire pipeline and return to the main function
    """
    results = []
    for pid in pipeline_ids:
        query_str = """
            MATCH (pipeline:Pipeline {itemID:$pipeline_id})
            OPTIONAL MATCH (pipeline)-[r1]-(task:Task)
            OPTIONAL MATCH (pipeline)-[r2]-(stage:Stage)
            OPTIONAL MATCH (stage)-[r3]-(execution:Execution)
            OPTIONAL MATCH (execution)-[r4]-(artifact:Artifact)
            OPTIONAL MATCH (artifact)-[r5]-(dataset:Dataset)
            OPTIONAL MATCH (artifact)-[r6]-(model:Model)
            OPTIONAL MATCH (artifact)-[r7]-(metric:Metric)
            OPTIONAL MATCH (pipeline)-[r8]-(framework:Framework)
            OPTIONAL MATCH (pipeline)-[r9]-(report:Report)
            RETURN task, pipeline, stage, execution, artifact, dataset, model, metric, framework, report, r1, r2, r3, r4, r5, r6, r7, r8, r9
            limit 20
            """
        parameters = {'pipeline_id':pid}
        res = neo4j_obj.query(query_str, parameters)
        results.append(res)
    return results


def get_explanations(query_task, top_task_ids, top_sim_scores, task_dict):
    explanations = [] #first element is always query task
    explanations.append({'title':'Query', 'content': {'Name': query_task.title(), 'Label': 'Pipeline', 
                         'Properties Computed': {}}})
    for i, tid in enumerate(top_task_ids):
        curr_item = task_dict[tid]
        explanations.append({'title':'Recommendation-'+str(i+1), 'content':{'Name': curr_item['name'].title(), 'Similarity Score':str(round(top_sim_scores[i].item(), 3)), 
                             'Similar Properties':{}}})
    
    return explanations


def compute_IOU(tokens1, tokens2):
    return len(set(tokens1).intersection(tokens2))/len(set(tokens1).union(tokens2))


def get_token_sim(query_task, task_dict):
    query_tokens = create_tokens(query_task)
    sims = []
    for id in task_dict:
        sims.append(compute_IOU(query_tokens, task_dict[id]['tokens']))
    return sims


def get_modality_sim(query_task, task_dict):
    query_modality = compute_modality(query_task)
    sims = []
    for id in task_dict:
        sims.append(compute_IOU(query_modality.split(","), task_dict[id]['modality'].split(",")))
    return sims


def get_category_sim(query_task, task_dict):
    query_category= compute_category(query_task)
    sims = []
    for id in task_dict:
        sims.append(compute_IOU(query_category.split(","), task_dict[id]['category'].split(",")))
    return sims


def get_similar_pipelines(query_pipeline, num_res=10):
    print("similar pipeline function called")
    start_time = time.time()
    num_res=3
    # check if we are able to calculate modality or category
    # if there are values, then pass this as constraint and pick only those tasks for similarity computation
    # Or, use the stored files and compute cosine similarity.. pick top 200 results and compute custom similarity only for those?
    # have the option to include or exclude modality and category computation in similarity calculation if category and modality are not available
    
    # test - compute just embedding similarity from all the files
    pipeline_dict = get_pipelines()


    filename = 'pipeline_embeddings_all.h5'
    filepath = find_file_path(filename=filename)
    with h5py.File(filepath, 'r') as f:
        # Load the datasets
        embedding_ids = f['embedding_ids'][:]  # Reads all the IDs
        embeddings = f['embeddings'][:]    

    pipeline_ids = [id.decode('utf-8') for id in embedding_ids]  # Decode if IDs are stored as byte strings
    embeddings = torch.tensor(embeddings).to(DEVICE)  # Convert embeddings to a torch tensor

    query_embedding = torch.tensor(embedding_model.encode(str(query_pipeline))).view(1, -1).to(DEVICE)

    cos_sim =  F.cosine_similarity(query_embedding, embeddings, dim=1)
    # token_sim = torch.tensor(get_token_sim(query_task, task_dict)).to(DEVICE)
    # modality_sim = torch.tensor(get_modality_sim(query_task, task_dict)).to(DEVICE)
    # category_sim = torch.tensor(get_category_sim(query_task, task_dict)).to(DEVICE)
    # print(len(token_sim), len(modality_sim), len(category_sim))

    # mean_sim = (cos_sim + token_sim + modality_sim + category_sim) / 4

    # Sort the tensor in descending order and get the indices
    sorted_tensor, sorted_indices = torch.sort(cos_sim, descending=True)
    indices = sorted_indices[:num_res]
    top_pipeline_ids = [pipeline_ids[idx] for idx in indices]
    top_sim_scores = sorted_tensor[:num_res]
    print("Len of top pipelines:", len(top_pipeline_ids))
    explanations = get_explanations(query_pipeline, top_pipeline_ids, top_sim_scores, pipeline_dict)
    neo4j_results = get_result_pipelines(top_pipeline_ids)
    result_d3_graphs = neo4j_to_d3(neo4j_results)
    result_items = {'nodes': result_d3_graphs['nodes'], 'links':result_d3_graphs['links'], 'explanations':explanations}
    # print(result_items)
    print("Time Taken:",time.time()-start_time)
    similar_item_dict = []
    for id in top_pipeline_ids:
        similar_item_dict.append(get_pipeline_node(id))
    return result_items, similar_item_dict

# get_similar_pipelines("medical image segmentation")
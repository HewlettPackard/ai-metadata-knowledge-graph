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
This script creates csv files for nodes to be loaded in to the knowlege graph. These files (nodes) are created by 
mapping Huggingface data nomenclature to the proposed metadata ontology nomenclature. Also, it computes additional property 
values for the concepts.

"""

import os
import pandas as pd
import hashlib
import uuid
import csv
import json
import pickle

# Task Category vocabulary
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

# Framework Vocabulary
framework_vocab = ['pytorch', 'tf', 'tensorboard']


# Source data path
SRC_DATA_PATH = 'data/huggingface'

# CSV files created will be stored in both the places
DEST_LUSTRE_PATH = 'kg-data/huggingface/nodes'
DEST_LOCAL_PATH = 'kg-data/huggingface/nodes'

print("Reading files...")

dataset_info = json.load(open(os.path.join(SRC_DATA_PATH, 'hugging_face_datasets_info.json')))
model_info = json.load(open(os.path.join(SRC_DATA_PATH, 'hugging_face_models_info.json')))
model_card_data = json.load(open(os.path.join(SRC_DATA_PATH, 'Hugging_face_model_metrics.json'))) # list of dicts
model_readme_df = pd.read_csv(os.path.join(SRC_DATA_PATH, 'model_readmes.csv'))

#create a dict for model-readme
model_readme_map = {}
for i in range(0,len(model_readme_df)):
    model_readme_map[str(model_readme_df['model'][i])] = str(model_readme_df['location'][i])



# Helper functions
def create_uuid_from_string(string):
    hex_string = int(hashlib.sha1(string.encode("utf-8")).hexdigest(), 16) % (10 ** 10)
    return str(hex_string)


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


def tokenize(item):
    tokens = item.split(" ")
    return tokens


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


def get_model_dataset():
    """
    A function that returns a dict
    {'<model_id>': [<list of datasets>], ...}
    """
    # generate dict from dataset_model_pickle file 
    data_dict1 = {}
    dataset_model = pickle.load(open(os.path.join(SRC_DATA_PATH, 'dataset_models.pickle'), 'rb'))
    for item in dataset_model:
        model_id = str(item['model']) # string
        dataset_ids = item['datasets'] # list
        if type(dataset_ids) == list:
            data_dict1[model_id] = dataset_ids
        else:
            pass
    

    # generate dict from model_card_info
    data_dict2 = {}
    for item in model_card_data:
        model_id = str(item['modelId'])

        # In some cases, dataset_type key is not present
        try:
            dataset_id = item['dataset_type']
        except KeyError:
            dataset_id = None
        
        # If the dataset_type key is not present, pass
        if dataset_id is None:
            pass
        else:
            try:
                exisiting_list = data_dict2[model_id]
                updated_list = exisiting_list + [str(dataset_id)]
                data_dict2[model_id] = list(set(updated_list))
            except KeyError:
                data_dict2[model_id] = [dataset_id]


    # merge both the data
    final_data_dict = {}
    counter = 0
    m1s = [m for m in data_dict1]
    m2s = [m for m in data_dict2]
    all_model_ids = list(set(m1s).union(set(m2s)))
    for model_id in all_model_ids:

        # check if model_id is present in data_dict1
        try:
            dict1_dataset_ids = data_dict1[model_id]
        except KeyError:
            dict1_dataset_ids = []
        
        # check if model_id is present in data_dict2
        try:
            dict2_dataset_ids = data_dict2[model_id]
        except KeyError:
            dict2_dataset_ids = []

        # try catch to pass Type Error while merging
        try:
            cum_dataset_ids = dict1_dataset_ids + dict2_dataset_ids
            final_data_dict[model_id] = list(set(cum_dataset_ids))
        except TypeError:
            # happens in 8 cases
            counter += 1
            pass

    return final_data_dict
                            


def get_model_description(model_id):
    try:
        filepath = model_readme_map[model_id]
        with open(filepath, 'r') as file:
            content = file.read()
            return content
    except KeyError:
        return "none"
    
    except UnicodeDecodeError:
        return "none"
    


# Functions related to node creation
# For huggingface, the papers associated with it are papers related to the model and not the pipeline
# Huggingface is centered around models. Therefore, model + task makes a pipeline. 
# A model is used only for a given task but using multiple datasets
def pipelines():
    pipeline_data_list = []
    stage_data_list = []
    execution_data_list = []
    artifact_data_list = []
    framework_data_list = []
    model_data_list = []
    model_dataset_dict = get_model_dataset()

    for i, item in enumerate(model_info):
        print("Pipeline and other nodes:" + str(i) + '/' + str(len(model_info)))
        src_model_id = item['modelId']
        model_id = create_uuid_from_string(src_model_id)
        description = get_model_description(src_model_id)
        try:
            model_name = item['model-index']['name']
        except KeyError:
            model_name = src_model_id
        
        try:
            model_class = item['config']['model_type']
        except KeyError:
            model_class = 'none'
        
        model_url = 'https://huggingface.co/' + str(src_model_id)

        model_data = {'model_id': model_id,
            'model_name': model_name,
            'model_class': str(model_class),
            'description': "none",
            'source': 'huggingface',
            'src_id': src_model_id,
            'url': str(model_url)
        }

        model_data_list.append(model_data)

        if "None" in str(item['pipeline_tag']):
            item['pipeline_tag'] = "Pipeline"
            src_task_id = "none"
        else:
            src_task_id = str(item['pipeline_tag'])

        pipeline_name = str(item['pipeline_tag']) + " using " + str(model_name)
        pipeline_id = create_uuid_from_string(pipeline_name)
        pipeline_data = {'pipeline_id': pipeline_id,
                    'pipeline_name': pipeline_name,
                    'source': 'huggingface',
                    'src_id': '',
                    'src_task_id': src_task_id,
                    'src_model_id': item['modelId'], # for relationship construction
                    # 'src_task_id': src_task_id # for relationship construction
            }
        pipeline_data_list.append(pipeline_data)


        # Framework Construction
        tags = item['tags']
        common = set(tags).intersection(set(framework_vocab))
        framework_name = ",".join(common)
        framework_id = create_uuid_from_string(framework_name)
        framework_data = {'framework_id': framework_id,
        'framework_name': framework_name,
        'framework_version': '',   
        'source': 'huggingface',
        'url': '',
        'pipeline_id': pipeline_id
        }
        framework_data_list.append(framework_data)


        # Stage construction
        stage_name = 'test'
        stage_string = str(pipeline_name) + ' stage ' + stage_name
        stage_id = create_uuid_from_string(stage_string)
        stage_data = {'stage_id': stage_id,
                            'stage_name': stage_name,
                            'source': 'huggingface',
                            'pipeline_id': pipeline_id,
                            'pipeline_name': pipeline_name,
                            'properties': ""
                }
        stage_data_list.append(stage_data)

        
        # Some models have executed the same task with different dataset. Therefore, each model + dataset makes a separate execution and artifact
        try:
            # if model id is present in model_dataset_dict,
            dataset_id_list = model_dataset_dict[src_model_id]
            for i, did in enumerate(dataset_id_list):
                # Execution construction
                execution_name = pipeline_name + '-' + stage_name + '-exe' + str(i)
                execution_id = create_uuid_from_string(execution_name)
                execution_data = {'execution_id': execution_id,
                                        'execution_name': execution_name,
                                        'pipeline_id': pipeline_id,
                                        'pipeline_name': pipeline_name,
                                        'stage_id': stage_id,
                                        'source': 'huggingface',
                                        'command': 'none',
                                        'properties': 'none',
                                        'src_model_id': src_model_id,
                                        'src_dataset_id': did                    
                                        }
                execution_data_list.append(execution_data)


                # Artifact Construction
                artifact_name = str(pipeline_name) + ' -artifacts-' + str(execution_id)
                artifact_id = create_uuid_from_string(artifact_name)
                artifact_data = {'artifact_id': artifact_id, 
                                        'artifact_name': artifact_name,
                                        'pipeline_id': pipeline_id,
                                        'pipeline_name': pipeline_name,
                                        'source': 'huggingface',
                                        'execution_id': execution_id,
                                        'src_model_id': src_model_id,
                                        'src_dataset_id': did
                        }
                artifact_data_list.append(artifact_data)

        
        except KeyError:
            # model_id is not present in model_datasets. Therefore only one execution
                # Execution construction
                execution_name = pipeline_name + '-' + stage_name + '-exe' + '1'
                execution_id = create_uuid_from_string(execution_name)
                execution_data = {'execution_id': execution_id,
                                        'execution_name': execution_name,
                                        'pipeline_id': pipeline_id,
                                        'pipeline_name': pipeline_name,
                                        'stage_id': stage_id,
                                        'source': 'huggingface',
                                        'command': 'none',
                                        'properties': 'none',
                                        'src_model_id': src_model_id,
                                        'src_dataset_id': 'none'                    
                                        }
                execution_data_list.append(execution_data)


                # Artifact Construction
                artifact_name = str(pipeline_name) + ' -artifacts-' + str(execution_id)
                artifact_id = create_uuid_from_string(artifact_name)
                artifact_data = {'artifact_id': artifact_id, 
                                        'artifact_name': artifact_name,
                                        'pipeline_id': pipeline_id,
                                        'pipeline_name': pipeline_name,
                                        'source': 'huggingface',
                                        'execution_id': execution_id,
                                        'src_model_id': src_model_id,
                                        'src_dataset_id': 'none'
                        }
                artifact_data_list.append(artifact_data)

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'pipelines.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'pipelines.csv')
    write_to_csv(pipeline_data_list, [filepath1, filepath2])

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'models.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'models.csv')
    write_to_csv(model_data_list, [filepath1, filepath2])

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'stages.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'stages.csv')
    write_to_csv(stage_data_list, [filepath1, filepath2])

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'executions.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'executions.csv')
    write_to_csv(execution_data_list, [filepath1, filepath2])

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'artifacts.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'artifacts.csv')
    write_to_csv(artifact_data_list, [filepath1, filepath2])

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'frameworks.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'frameworks.csv')
    write_to_csv(framework_data_list, [filepath1, filepath2])




def metrics():
    print("Metric nodes..")
    metric_data_list = []
    for item in model_card_data:
        model_id = item['modelId']
        try:
            dataset_id = item['dataset_type'] # In 8 cases this info is not present
            metric_name = item['name']
            metric_value = item['value']
            metric_string = str(model_id) + str(metric_name) + str(metric_value)
            metric_id = create_uuid_from_string(metric_string)
            data = {'metric_id': metric_id,
                    'metrics': str(metric_name) +':'+str(metric_value),
                    'source': 'huggingface',
                    'src_model_id': model_id,
                    'src_dataset_id': dataset_id
            }
            metric_data_list.append(data)
        except KeyError:
            pass

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'metrics.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'metrics.csv')
    write_to_csv(metric_data_list, [filepath1, filepath2])


def tasks():
    print("Task nodes...")
    # pipeline_tag from models_info has the task information
    task_list = []
    for item in model_info:
        task_list.append(str(item['pipeline_tag']))
    
    task_list = list(set(task_list))
    
    task_data_list = []
    for t in task_list:
        task_id = create_uuid_from_string(t)
        src_id = str(t)
        task_tokens = t.split("-")
        task_name = " ".join(task_tokens).capitalize()
        category = compute_category(task_tokens)
        modality = compute_modality(task_tokens)
        description = 'none'

        data = {'task_id': task_id,
        'task_name': task_name,
        'task_type': '',
        'category': str(category),
        'modality': str(modality),
        'description': str(description),
        'source': 'huggingface',
        'src_id': src_id}

        task_data_list.append(data)
    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'tasks.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'tasks.csv')
    write_to_csv(task_data_list, [filepath1, filepath2])


def reports():
    print("Report nodes..")
    paper_data = json.load(open(os.path.join(SRC_DATA_PATH, 'arxiv_paper_info.json'), 'r'))
    report_data_list = []
    for arxiv_id in paper_data:
        curr_item = paper_data[arxiv_id]
        report_id = create_uuid_from_string(curr_item['title'])
        abstract = curr_item['abstract']
        abstract = abstract.replace(",", "")
        abstract = abstract.replace("\\", "")

        title = curr_item['title']
        title = title.replace(",", " ")

        report_data = {'report_pdf_url': str(curr_item['pdf_url']),
                    'report_id': report_id,
                    'title': title,
                    'abstract_url': '',
                    'abstract': abstract,
                    "source": 'huggingface',
                    'arxiv_id': arxiv_id,
                    'src_id':arxiv_id
        }
        report_data_list.append(report_data)

    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'reports.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'reports.csv')
    write_to_csv(report_data_list, [filepath1, filepath2])



def datasets():
    dataset_data_list = []
    for i, item in enumerate(dataset_info):
        print("Huggingface Datasets:" + str(i) + '/' + str(len(dataset_info)))
        src_id = item['id']
        dataset_id = create_uuid_from_string(src_id)

        # dataset name creation
        dataset_name = src_id.split("/")[-1].capitalize()

        # citation = item['citation']
        description = item['description']
        if description == None: # this prevents issues with null values while loading into the database
            description = "none"
        else:
            description = description.replace(",", "")
            description = description.replace("\\", "")

        url = 'https://huggingface.co/datasets/' + str(src_id)

        dataset_name_tokens = tokenize(dataset_name)
        dataset_desc_tokens = tokenize(description)
        tokens = dataset_desc_tokens+dataset_name_tokens
        modality = compute_modality(tokens)

        data = {'dataset_id': dataset_id,
        'dataset_name': dataset_name,
        'modality': modality,
        'description': str(description),
        'url': str(url),
        'source': 'huggingface',
        'src_id':src_id
        }
        dataset_data_list.append(data)
    print("Length of dataset",len(dataset_data_list))
    filepath1 = os.path.join(DEST_LUSTRE_PATH, 'datasets.csv')
    filepath2 = os.path.join(DEST_LOCAL_PATH, 'datasets.csv')
    write_to_csv(dataset_data_list, [filepath1, filepath2])





# Function calls
datasets()
tasks()
reports()
metrics()
pipelines() # this has pipeline, stage, execution, artifact, framework
# HF does not have metric and parameter info
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



#################################################################################################
# This file is responsible to collect datasets and models from hugging face hub api
# Script by Arpit Shah
###############################################################################################
import pandas as pd
from huggingface_hub import HfApi, list_models, ModelFilter, ModelCardData, EvalResult
from huggingface_hub import list_datasets, DatasetFilter, DatasetCardData
from huggingface_hub import hf_hub_download
import logging
import sys
import os
import json
import datetime


text_tasks = ['text-generation','text-classification','question-answering','text-retrieval', 'summarization','translation']
image_tasks = ['image-classification', 'image-generation', 'text-to-image','object-detection', 'image-segmentation']


dataset_tasks = text_tasks + image_tasks
model_tasks = text_tasks + image_tasks

class FilterParams:
    filter_datasets_by_tasks = dataset_tasks
    filter_models_by_tasks = model_tasks
    size_range = ['100M<n<1B', '10M<n<100M', '1B<n<10B']

class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime.datetime):
            return z.isoformat()
        if isinstance(z, ModelCardData):
            return (vars(z))
        elif isinstance(z, EvalResult):
            return (vars(z))
        elif isinstance(z, DatasetCardData):
            return (vars(z))
        else:
            return super().default(z)


class HuggingFace:

    def __init__(self, token=None, location= None):
        self.token = token
        self.hf_api = HfApi(
            endpoint="https://huggingface.co",  # Can be a Private Hub endpoint.
            token=self.token,  # Token is not persisted on the machine.
        )
        self.hf_data = location
        self.models_path = os.path.join(self.hf_data, 'hugging_face_models_info')
        self.datasets_path = os.path.join(self.hf_data, 'hugging_face_datasets_info')
        self.HF_HOME = 'hugging_face_data'
        self.dataset_with_model = os.path.join(self.hf_data, 'dataset_with_model')
        self.model_metrics = os.path.join(self.hf_data, 'Hugging_face_model_metrics')
        os.environ['HF_HOME'] = self.HF_HOME
        self.model_card = os.path.join(self.hf_data, 'hugging_face_models_cards')
        

            
    def get_models_info(self, tasks=False, card_data=True, fetch_config=True,
                        sort="likes", dump_json=True) -> pd.DataFrame:
        '''
        :param tasks: list of tasks
        :param card_data: card data(dataset) information needed or not
        :param fetch_config: config information needed or not
        :param sort: sort by, default download
        :return: pandas dataframe containing models information
        '''
        models_df = pd.DataFrame()
        models = []
        try:
            if tasks:
                for task in FilterParams.filter_models_by_tasks:
                    filters = ModelFilter(task=task)
                    models_list = list_models(filter=filters, cardData=card_data, fetch_config=fetch_config, sort=sort,
                                              direction=-1)
                    models_list = [vars(x) for x in list(models_list)]
                    models_list = [{key: val for key, val in sub.items() if key != 'siblings'} for sub in models_list]
                    models_df = pd.concat([models_df, pd.json_normalize(models_list, sep='_')], axis=0)
                    models.extend(models_list)
            else:
                models = list_models(cardData=card_data, fetch_config=fetch_config, sort=sort, direction=-1)
                models = [vars(x) for x in list(models)]
                models_df = pd.concat([models_df, pd.json_normalize(models, sep='_')], axis=0)
            models_df.fillna('', inplace=True)
            models_df = models_df.applymap(lambda x: x.encode('unicode_escape').
                                           decode('utf-8') if isinstance(x, str) else x)
            dt_cols = models_df.select_dtypes(include=['datetime64[ns, UTC]']).columns
            for col in dt_cols:
                    models_df[col] = models_df[col].dt.tz_localize(None)
            models_df.to_excel(f"{self.models_path}.xlsx", index=False)
            if dump_json:
                with open(f'{self.models_path}.json', 'w', encoding='utf-8') as f:
                    json.dump(models, f,cls=DateTimeEncoder)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            logging.error("ERROR: " + str(e))
            raise e
        return models_df

    def get_datasets_info(self, dataset_filters=True, card_data=True, dump_json=True) -> pd.DataFrame:
        '''

        :param dataset_filters: class huggingface_hub.DatasetFilter object
        :param size_range: filter by size of datasets,default 100M to 10B
        :param card_data: card data information
        :return: pandas dataframe
        '''

        datasets_df = pd.DataFrame()
        datasets = []
        try:
            if dataset_filters:
                dataset_filter = DatasetFilter()
                for task in FilterParams.filter_datasets_by_tasks:
                    for size in FilterParams.size_range:
                        dataset_filter.task_categories = task
                        dataset_filter.size_categories = size
                        datasets_list = list_datasets(filter=dataset_filter, full=True)
                        datasets_list = [vars(x) for x in list(datasets_list)]
                        datasets_df = pd.concat([datasets_df, pd.json_normalize(datasets_list, sep='_')], axis=0)
                        datasets.extend(datasets_list)
            else:
                datasets = list_datasets(full=True)
                datasets = [vars(x) for x in list(datasets)]
                datasets_df = pd.concat([datasets_df, pd.json_normalize(datasets, sep='_')], axis=0)
            datasets_df.fillna('', inplace=True)
            datasets_df = datasets_df.applymap(lambda x: x.encode('unicode_escape').
                                               decode('utf-8') if isinstance(x, str) else x)
            dt_cols = datasets_df.select_dtypes(include=['datetime64[ns, UTC]']).columns
            for col in dt_cols:
                    datasets_df[col] = datasets_df[col].dt.tz_localize(None)
            datasets_df.to_excel(f"{self.datasets_path}.xlsx", index=False)
            print("dataset saved")
            if dump_json:
                # print(dump_json)
                print(f'{self.datasets_path}.json')
                with open(f'{self.datasets_path}.json', 'w', encoding='utf-8') as f:
                    json.dump(datasets, f, cls=DateTimeEncoder)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            logging.error("ERROR: " + str(e))
            raise e
        return datasets_df

    def main(self):
        datasets_info = self.get_datasets_info()
        print(len(datasets_info))
        model_info = self.get_models_info(tasks=True)
        print(len(model_info))

    @staticmethod
    def convert_to_list(x):
        x = x.replace('[', '').replace(']', '')
        return [i.replace('"', '').replace("'", '').strip() for i in x.split(',')]

    def get_datasets_with_models(self,dump_json=True):
        try:
            try:
                with open(f'{self.models_path}.json') as model_file:
                    models = model_file.read()
                models_info = json.loads(models)
                dataset_associated_with_models_json = [{'datasets': x['cardData']['datasets'], 'model': x['id']} for x in
                                                  models_info if  x['cardData'] is not None and
                                                  x.__contains__('cardData') and x['cardData'].__contains__('datasets') and x['cardData'].__contains__('datasets') is not None]
                dataset_associated_with_models = pd.DataFrame(dataset_associated_with_models_json)
            except Exception as e:
                logging.error("Failed to parse json file..trying with excel file")
                models_info_df = pd.read_excel(f"{self.models_path}.xlsx")
                models_info_df.dropna(subset='cardData_datasets', inplace=True)
                models_info_df['cardData_datasets'] = models_info_df['cardData_datasets'].apply(str)
                dataset_associated_with_models = models_info_df[['modelId', 'cardData_datasets']]
                dataset_associated_with_models.rename({"cardData_datasets": "datasets", "modelId": "model"}, axis=1,
                                                      inplace=True)
                dataset_associated_with_models_json = dataset_associated_with_models.to_dict(orient='records')
            dataset_associated_with_models.to_excel(f"{self.dataset_with_model}.xlsx", index=False)
            if dump_json:
                with open(f'{self.dataset_with_model}.json', 'w', encoding='utf-8') as f:
                    json.dump(dataset_associated_with_models_json, f)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            logging.error("ERROR: " + str(e))
            raise e
        return dataset_associated_with_models

    def download_model_readmes(self):
        with open(f'{self.models_path}.json') as model_file:
            models = model_file.read()
        models_info = json.loads(models)
        models = [x['id'] for x in models_info]
        dataset_with_readme = []
        dataset_without_readme = []
        try:
            for model in models:
                try:
                    card = hf_hub_download(model, 'README.md')
                    dataset_with_readme.append({"model": model, "location": card})
                except:
                    logging.info(f"No readme found for model: {model}")
                    dataset_without_readme.append(model)
            with open(f'{self.model_card}.json', 'w') as f:
                json.dump(dataset_with_readme, f)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            logging.error("ERROR: " + str(e))
            raise e

    def extract_evaluation_results(self):
        if os.path.isfile(f'{self.models_path}.json'):
                with open(f'{self.models_path}.json') as f:
                    file_contents = f.read()
                model_json = json.loads(file_contents)
        else:
            raise ValueError("Models file not found")
        has_eval = list(filter(lambda x: 'model-index' in x['tags'],model_json))
        # print(has_eval[0])
        # sys.exit()
        extracted_data = pd.DataFrame()
        for data in has_eval:
            metrics_data = pd.DataFrame()
            if (data.__contains__('cardData')) and (data['cardData'] is not None) and (data['cardData'].__contains__('model-index')) and (data['cardData']['model-index'] is not None):
                for i in data['cardData']['model-index']:
                    for j in i['results']:
                        metrics = pd.json_normalize(j,'metrics',[['task','name'],['task','type'],['dataset','name'],['dataset','type'],['dataset','args']],sep='_',errors='ignore')      
                        metrics_data = pd.concat([metrics_data,metrics]) 
                metrics_data['modelId'] = data['modelId']
                extracted_data = pd.concat([extracted_data,metrics_data])
        # print(extracted_data.head(1))
        # sys.exit()
        extracted_data.reset_index(drop=True,inplace=True)
        metrics_data = [ v.dropna().to_dict() for k,v in extracted_data.iterrows() ]
        with open(f'{self.model_metrics}.json', 'w') as f:
            json.dump(metrics_data, f)
        extracted_data.fillna('',inplace=True)
        extracted_data = extracted_data[['modelId','name','type','value','verified','task_name','task_type','dataset_name',
                'dataset_type','dataset_args']]
        extracted_data.to_excel(f'{self.model_metrics}.xlsx',index=False)

if __name__ == "__main__":
    # mention paths here
    HuggingFace(location='data/huggingface').main()
    HuggingFace(location='data/huggingface').get_datasets_with_models()
    HuggingFace(location='data/huggingface').extract_evaluation_results()
    HuggingFace(location='data/huggingface').download_model_readmes()

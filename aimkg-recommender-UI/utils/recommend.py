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
This will query for the entire pipeline and return it to the front-end
If more than one element is passed as input, return pipelines that satisfies all
"""
from .task import get_similar_tasks
from .dataset import get_similar_datasets
from .model import get_similar_models
from .pipeline import get_similar_pipelines

def get_recommendations(query_task=None, query_dataset=None, query_model=None, query_pipeline=None, num_res=3, sim_threshold=0.1):
    print(type(query_task), type(query_dataset), type(query_model), type(query_pipeline))
    if query_task is not None and query_task != "":
        # print("recommend.py", num_res)
        task_results = get_similar_tasks(query_task, num_res=num_res)
        return task_results
    
    if query_dataset is not None and query_dataset != "":
        dataset_results = get_similar_datasets(query_dataset, num_res=num_res)
        return dataset_results
    
    if query_model is not None and query_model != "":
        model_results = get_similar_models(query_model, num_res=num_res)
        return model_results
    
    if query_pipeline is not None and query_pipeline != "":
        pipeline_results = get_similar_pipelines(query_pipeline, num_res=num_res)
        return pipeline_results


    

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
        task_results, similar_item_dict = get_similar_tasks(query_task, num_res=num_res)
        return task_results, similar_item_dict
    
    if query_dataset is not None and query_dataset != "":
        dataset_results, similar_item_dict = get_similar_datasets(query_dataset, num_res=num_res)
        return dataset_results, similar_item_dict
    
    if query_model is not None and query_model != "":
        model_results, similar_item_dict = get_similar_models(query_model, num_res=num_res)
        return model_results, similar_item_dict
    
    if query_pipeline is not None and query_pipeline != "":
        pipeline_results, similar_item_dict = get_similar_pipelines(query_pipeline, num_res=num_res)
        return pipeline_results, similar_item_dict


    

from flask import Flask, request, jsonify, render_template
from utils.recommend import get_recommendations
import utils.search_graph as search_graph
import os
import json

import logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# Get the prepoluated values and keep it ready
print("Getting dropdown values..")
DROP_DOWN_VALUES = search_graph.drop_down_values(limit=1000)


##############################
app = Flask(__name__)


@app.route('/')
def home():
    print("At home")
    return render_template('recommendation.html')

####################################### RECOMMENDATION ################################
@app.route('/recommendation')
def recommendation():
    return render_template('recommendation.html')


# Route for recommendation query
@app.route('/recommendation/query', methods=['POST'])
def recommend_graphs():
    data = request.json
    dataset = data.get('dataset')
    task = data.get('task')
    model = data.get('model')
    pipeline = data.get('pipeline')
    num_reco = data.get('num_recommendations')
    print("app.py",num_reco)

    # Process the recommendation-specific query
    results = get_recommendations(query_task=task, query_dataset=dataset, query_model=model, query_pipeline=pipeline, num_res=num_reco, sim_threshold=0.1)
    print("Recommendation query processed")
    # json_data = json.dumps(results, sort_keys=False)  # Prevents alphabetical sorting
    return jsonify(results)


######################################### SEARCH ####################################
@app.route('/search')
def search():
    return render_template('search.html', 
                           dropdown_dataset=DROP_DOWN_VALUES['dataset'], 
                           dropdown_task=DROP_DOWN_VALUES['task'],
                           dropdown_model=DROP_DOWN_VALUES['model'])


# Route for search query
@app.route('/search/query', methods=['POST'])
def search_query():
    data = request.json
    dataset = data.get('dataset')
    task = data.get('task')
    model = data.get('model')
    query_type = data.get('query_type')
    # Process the search-specific query
    d3_graphs = search_graph.search_pipelines(query_task=task, query_dataset=dataset, query_model=model, query_type=query_type)
    return jsonify(d3_graphs)


@app.route('/search/cypher_query', methods=['POST'])
def search_cypher_query():
    data = request.json
    cypher_query = data.get('cypher_query')
    print("CYPHER QUERY:", cypher_query)
    d3_graphs = search_graph.search_custom_query(cypher_query)
    return jsonify(d3_graphs)

if __name__ == '__main__':
    app.run(debug=True, port=9089, extra_files=['templates/recommendation.html', 'templates/search.html', 'static/css/styles.css', 'static/js/graph.js','static/js/list.js'])

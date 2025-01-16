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


from flask import Flask, request, jsonify, render_template
from utils.recommend import get_recommendations
import utils.search_graph as search_graph
import os
import json

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

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

import neo4j

# TODO: Handle node duplicates - create a dict of nodes and append them to node list.
def neo4j_to_d3(results):
    """
    Converts a list of Neo4j query results into D3.js format.
    
    Args:
        results (list): A list of Neo4j query results where each result corresponds to nodes and relationships.

    Returns:
        result_d3_graphs (dict): A dictionary with nodes and links suitable for D3.js visualization.
    """
    # Initialize a dictionary to hold nodes and links
    result_d3_graphs = {
        "nodes": [],
        "links": []
    }
    
    # Use sets to avoid duplicates
    nodes_set = set()
    links_set = set()
    # Iterate over each Neo4j result
    for result in results:
        for record in result:  # Iterate through each Neo4j record
            # Extract nodes and relationships from the record
            # print(type(re))
            for key in record.keys():
                element = record[key]
                
                # Check if the element is a node
                if isinstance(element, neo4j.graph.Node):
                    # Check if the node has been processed already
                    if element.id not in nodes_set:
                        nodes_set.add(element.id)
                        result_d3_graphs["nodes"].append({
                            "id": element.id,
                            "labels": list(element.labels)[0],
                            "properties": dict(element)  # Convert node properties to a dictionary
                        })
                # Check if the element is a relationship
                elif isinstance(element, neo4j.graph.Relationship):
                    link_id = (element.start_node.id, element.end_node.id, element.type)
                    
                    if link_id not in links_set:
                        links_set.add(link_id)
                        result_d3_graphs["links"].append({
                            "source": element.start_node.id,
                            "target": element.end_node.id,
                            "type": element.type,
                            "properties": dict(element)  # Convert relationship properties to a dictionary
                        })

    return result_d3_graphs
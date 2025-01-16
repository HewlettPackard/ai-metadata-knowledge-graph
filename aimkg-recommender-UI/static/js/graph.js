// Define your custom color mapping based on label names
const customColors = {
    "Task": "#3E854E",
    "Pipeline": "#DB6260",
    "Stage": "#B0DC88",
    "Execution": "#1B468F",
    "Artifact": "#CCC3A0",  
    "Model": "#24615D",      
    "Dataset": "#A85931",    
    "Metric": "#DBA746", 
    "Report": "#C49DD1",   
    "Framework": "#88C8DC",  
};

// Default color if label is not in the customColors mapping
const defaultColor = "#7f7f7f"; 

// Function to render the actual graph using D3 with nodes and links from the backend
function renderGraph(nodes, links) {
    console.log('Rendering Graph with Nodes:', nodes); // Log nodes data
    console.log('Rendering Graph with Links:', links); // Log links data

    // Check if the data is null or empty
    if (!nodes || !links || nodes.length === 0 || links.length === 0) {
        // Show the error modal
        $('#error-modal').modal('show');
        return; // Exit the function without rendering the graph
    }

    // Clear existing content
    d3.select("#result-segment").html("");

    const svg = d3.select("#result-segment")
    .append("svg")    
    .attr("width", "100%")  // Set width to 100% of the parent container
    .attr("height", "100%") // Set height to 100% of the parent container
    .style("display", "block"); 

    svg.selectAll("*").remove(); // Clear existing graph elements

    // // Define arrow markers for directed edges
    // svg.append("defs").append("marker")
    //     .attr("id", "arrow") // Marker ID
    //     .attr("viewBox", "0 -5 10 10")
    //     .attr("refX", 15) // Adjust to place the arrowhead properly
    //     .attr("refY", 0)
    //     .attr("markerWidth", 6)
    //     .attr("markerHeight", 6)
    //     .attr("orient", "auto")
    //     .append("path")
    //     .attr("d", "M0,-5L10,0L0,5") // Path for the arrow shape
    //     .attr("fill", "#999");


    const width = +svg.node().getBoundingClientRect().width || 800;
    const height = +svg.node().getBoundingClientRect().height || 600;

    const zoom = d3.zoom()
        .scaleExtent([0.05, 10])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
        });

    svg.call(zoom);

    const g = svg.append("g");

    // Ensure that `source` and `target` are correctly linked to node IDs
    links.forEach(link => {
        if (typeof link.source === 'object') link.source = link.source.id;
        if (typeof link.target === 'object') link.target = link.target.id;
    });

    const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links)
        .id(d => d.id)
        .distance(link => link.length || 40) // Reduce distance for closer links
    )
    .force("charge", d3.forceManyBody().strength(-60)) // Decrease the repulsion strength for closer graphs
    .force("center", d3.forceCenter(width / 2, height / 2));


    const link = g.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("stroke-width", 1)
        .attr("marker-end", "url(#end)")
        .attr("data-type", d => d.type);

    // Add labels to the links
    // const linkLabels = g.append("g")
    //     .selectAll("text")
    //     .data(links)
    //     .enter().append("text")
    //     .attr("class", "link-label")
    //     .attr("dy", -5) // Adjust to position label correctly
    //     .attr("text-anchor", "middle")
    //     .style("font-size", "10px") // Set the text size here
        // .text(d => d.type);

    const node = g.append("g")
        .attr("stroke", "#fff")
        .attr("stroke-width", 0)
        .selectAll("circle")
        .data(nodes)
        .enter().append("circle")
        .attr("r", 15)
        .attr("fill", d => customColors[d.labels] || defaultColor) // Use custom color mapping
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on("mouseover", showNodeCard) // Show card on hover
        .on("mouseout", hideNodeCard) // Hide card on mouse out if not pinned
        .on("click", toggleNodeCard); // Toggle card on click

    // Adding floating labels next to nodes
    const floatingText = g.append("g")
        .selectAll("text")
        .data(nodes)
        .enter().append("text")
        .attr("font-size", 10) // Font size for floating text
        .attr("dy", -10) // Adjust vertical positioning above the node
        .attr("text-anchor", "middle") // Center the text horizontally
        .text(d => d.labels) // Display node label
        .attr("pointer-events", "none"); // Disable pointer events on text to avoid interfering with drag

    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        // linkLabels
        //     .attr("x", d => (d.source.x + d.target.x) / 2)
        //     .attr("y", d => (d.source.y + d.target.y) / 2);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);

        // Update the position of floating labels
        floatingText
            .attr("x", d => d.x)
            .attr("y", d => d.y - 20); // Position slightly above the node
    });

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // Function to determine node color based on label
    function getNodeColor(label) {
        return customColors[label] || defaultColor;
    }

    let lastClickedNode = null; // Track the last clicked node

    // Show the floating card with node details on hover
    function showNodeCard(event, d) {
        const card = document.getElementById('node-card');

        // If the card is not pinned, update the card's content
        if (!card.classList.contains('pinned')) {
            updateCardContent(d);
            card.style.display = 'block';
        } else {
            // If the card is pinned but we're hovering over a new node, update the content
            if (lastClickedNode !== d) {
                updateCardContent(d);
            }
        }
    }

    // Hide the floating card on mouse out
    function hideNodeCard() {
        const card = document.getElementById('node-card');

        // Only hide if not pinned by a click
        if (!card.classList.contains('pinned')) {
            card.style.display = 'none';
        }
    }

    // Toggle the floating card on click
    function toggleNodeCard(event, d) {
        const card = document.getElementById('node-card');

        // Check if the same node is clicked twice
        if (lastClickedNode === d && card.classList.contains('pinned')) {
            card.classList.remove('pinned');
            card.style.display = 'none'; // Hide when clicked again
            lastClickedNode = null; // Reset the last clicked node
        } else {
            card.classList.add('pinned');
            updateCardContent(d); // Update content when pinned
            lastClickedNode = d; // Track the last clicked node
        }
    }

    // Function to update the card content and style
    function updateCardContent(d) {
        document.getElementById('card-title').textContent = (d.labels || "Node Label").toUpperCase();
        // document.getElementById('card-title').style.backgroundColor = getNodeColor(d.labels);
        document.getElementById('card-content').innerHTML = formatProperties(d.properties);
    }

    // Function to format properties as key-value pairs with minimal spacing
    function formatProperties(properties) {
        let formatted = ''; // Initialize an empty string
        for (const [key, value] of Object.entries(properties)) {
            formatted += `<strong>${key}:</strong> ${value}<br>`; // Each key-value pair on a new line
        }
        return formatted;
    }

}

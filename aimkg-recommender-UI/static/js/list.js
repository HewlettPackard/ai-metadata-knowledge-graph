// Function to set grid layout for rendering cards
function setGridLayout(numberOfColumns = 3, cellWidth = 250) {
    // Set up the #result-segment for a grid layout
    const resultSegment = document.getElementById('result-segment');
    resultSegment.style.display = 'grid';
    resultSegment.style.gridTemplateColumns = `repeat(${numberOfColumns}, minmax(${cellWidth}px, 1fr))`; // Set columns and min width
    resultSegment.style.gap = '10px';
    resultSegment.style.padding = '20px';
    resultSegment.style.overflow = 'auto'; // Ensure content stays inside
    resultSegment.style.alignItems = 'start'; // Align grid items to the start
}

// Function to render cards inside the result segment
function renderList(data, numberOfColumns = 4, cellWidth = 250) {
    // Clear existing content and set grid layout with adjustable number of columns and cell width
    const resultSegment = document.getElementById('result-segment');
    resultSegment.innerHTML = ''; // Clear previous content
    setGridLayout(numberOfColumns, cellWidth); // Pass the desired number of columns and cell width

    // Use D3 to render the cards as grid items inside the #result-segment
    const container = d3.select("#result-segment")
        .attr("width", "100%")
        .attr("height", "100%")
        .style("display", "grid")  // Ensure display grid is applied
        .style("gridTemplateColumns", `repeat(${numberOfColumns}, minmax(${cellWidth}px, 1fr))`)  // Adjust number of columns and width
        .style("gap", "10px");  // Add spacing between grid items

    container.selectAll(".card")
        .data(data)
        .enter()
        .append("div")
        .attr("class", "ui card custom-card")  // Add class for styling
        .style("max-width", "100%")  // Set to 100% to fit within the grid cell
        .style("height", "200px") // Fixed height for the cards
        .style("margin", "0") // Ensure no extra margin is causing misalignment
        .style("overflow-wrap", "break-word")  // Match overflow handling
        .html(d => `
            <div class="content" style="flex: 0 0 auto;">
                <div class="header">${d.labels}</div>
            </div>
            <div class="content" style="height: 170px; overflow-y: auto;"> <!-- Set height and enable scroll -->
                ${Object.entries(d.properties)
                    .map(([key, value]) => `<p><strong>${key}:</strong> ${value}</p>`)
                    .join('')}
            </div>
        `);
}


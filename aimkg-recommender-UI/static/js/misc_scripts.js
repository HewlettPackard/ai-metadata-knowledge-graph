// Function to render explanations dynamically with titles and content
function renderExplanations(data) {
    // // Your provided data
    // const data = [
    //     { title: 'Query', content: { Name: 'Something', Label: 'dataset', computed_properties: {} } },
    //     { title: 'Recommendation 1', content: { Name: 'soemthin1 something somethins something', 'Similarity Score': '0.3', 'Similar Properties': { tokens: ['ab', 'bc'], 'Embedding Similarity': '0.1', modality: ['image'] } } },
    //     { title: 'Recommendation 2', content: { Name: 'soemthin1', 'Similarity Score': '0.3', 'Similar Properties': { tokens: ['ab', 'bc'], 'Embedding Similarity': '0.1' } } },
    //     { title: 'Recommendation 3', content: { Name: 'soemthin1', 'Similarity Score': '0.3', 'Similar Properties': { tokens: ['ab', 'bc'], 'Embedding Similarity': '0.1', modality: ['image'] } } }
    // ];

    console.log("Explanation Data:", data)

    // Get the sidebar container
    const sidebar = document.getElementById('sidebar');

    // Clear existing segments
    sidebar.innerHTML = '';

    // Populate the sidebar with segments
    data.forEach((item, index) => {
        const segment = document.createElement('div');
        // Apply 'explanation-first-segment' class to the first segment and 'explanation-segment' class to others
        segment.className = index === 0 ? 'explanation-segment explanation-first-segment' : 'explanation-segment';

        // Create title element
        const title = document.createElement('div');
        title.className = 'segment-title';
        title.textContent = item.title;

        // Create content element
        const content = document.createElement('div');
        content.className = 'segment-content';
        content.textContent = item.content;

        // Call formatContent function to format the content object
        content.innerHTML = formatContent(item.content);

        // Append title and content to the segment
        segment.appendChild(title);
        segment.appendChild(content);
        sidebar.appendChild(segment);
    });

    // Function to format content with capitalization and proper formatting
    function formatContent(content) {
        let formatted = '';

        // Iterate over each key-value pair in the content object
        for (const key in content) {
            if (typeof content[key] === 'object' && !Array.isArray(content[key])) {
                // If the value is an object, display its properties
                formatted += `<strong>${capitalize(key)}:</strong><br>`;
                for (const subKey in content[key]) {
                    formatted += `&nbsp;&nbsp;&nbsp;&nbsp;<strong>${capitalize(subKey)}:</strong> ${formatValue(content[key][subKey])}<br>`;
                }
            } else {
                // Directly display the key-value pair
                formatted += `<strong>${capitalize(key)}:</strong> ${formatValue(content[key])}<br>`;
            }
        }

        return formatted;
    }

    // Function to format values, handling arrays and objects
    function formatValue(value) {
        if (Array.isArray(value)) {
            return value.join(', '); // Join array values with commas
        }
        return value; // Return the value directly if it's not an array
    }

    // Function to capitalize the first letter of a string
    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}





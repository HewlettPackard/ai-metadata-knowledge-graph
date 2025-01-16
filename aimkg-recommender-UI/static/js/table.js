// Sample data points
const dataPoints = [
    {
        title: "Card 1",
        properties: { Property1: "Value 1", Property2: "Value 2", Property3: "Value 3" }
    },
    {
        title: "Card 2",
        properties: { PropertyA: "Value A", PropertyB: "Value B", PropertyC: "Value C" }
    },
    {
        title: "Card 3",
        properties: { Key1: "Value X", Key2: "Value Y", Key3: "Value Z" }
    }
];

// Function to render the list of items as cards
function renderList(data) {
    const container = document.getElementById('cardContainer');
    container.innerHTML = ''; // Clear existing content

    data.forEach(item => {
        // Create card element
        const card = document.createElement('div');
        card.classList.add('card');

        // Create card title
        const cardTitle = document.createElement('div');
        cardTitle.classList.add('card-title');
        cardTitle.textContent = item.title;

        // Create properties list
        const propertiesList = document.createElement('ul');
        propertiesList.classList.add('card-properties');

        // Populate properties list
        for (const [key, value] of Object.entries(item.properties)) {
            const listItem = document.createElement('li');
            listItem.textContent = `${key}: ${value}`;
            propertiesList.appendChild(listItem);
        }

        // Append title and list to card
        card.appendChild(cardTitle);
        card.appendChild(propertiesList);

        // Append card to container
        container.appendChild(card);
    });
}

// Call renderList with the sample data points (you can remove this line and call renderList where needed)
renderList(dataPoints);

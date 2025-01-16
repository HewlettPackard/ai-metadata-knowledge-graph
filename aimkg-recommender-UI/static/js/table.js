
// # Copyright (2024) Hewlett Packard Enterprise Development LP
// #
// # Licensed under the Apache License, Version 2.0 (the "License");
// # You may not use this file except in compliance with the License.
// # You may obtain a copy of the License at
// #
// # http://www.apache.org/licenses/LICENSE-2.0
// #
// # Unless required by applicable law or agreed to in writing, software
// # distributed under the License is distributed on an "AS IS" BASIS,
// # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// # See the License for the specific language governing permissions and
// # limitations under the License.
// ###


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

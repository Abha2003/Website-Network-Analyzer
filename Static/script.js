function analyzeWebsite() {
    const url = document.getElementById('urlInput').value;
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        const resultTable = document.getElementById('resultTable');
        const resultTableBody = document.getElementById('resultTableBody');

        // Clear any previous results
        resultTableBody.innerHTML = '';
        
        // Show the table
        resultTable.style.display = 'block';

        if (data.error) {
            const row = document.createElement('tr');
            const cell1 = document.createElement('td');
            const cell2 = document.createElement('td');
            cell1.textContent = 'Error';
            cell2.textContent = data.error;
            row.appendChild(cell1);
            row.appendChild(cell2);
            resultTableBody.appendChild(row);
        } else {
            // Populate the table with the returned data
            for (let key in data) {
                if (data.hasOwnProperty(key)) {
                    let value = data[key];

                    // If value is an object (like WHOIS info), format it as JSON
                    if (typeof value === 'object') {
                        value = JSON.stringify(value, null, 2);
                    }

                    // Create a new row
                    const row = document.createElement('tr');
                    const cell1 = document.createElement('td');
                    const cell2 = document.createElement('td');

                    cell1.textContent = key;
                    cell2.textContent = value;

                    row.appendChild(cell1);
                    row.appendChild(cell2);
                    resultTableBody.appendChild(row);
                }
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

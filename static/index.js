function Show() {
    const processesDiv = document.getElementById('generatedProcesses');
    const tableBody = document.getElementById('processesTableBody');
    
    // Clear existing content
    tableBody.innerHTML = '';
    processesDiv.style.display = 'block';
    
    console.log('Fetching processes data...');
    fetch('/get_processes_data')
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error('No processes data available');
            }
            return response.text();
        })
        .then(data => {
            console.log('Received data:', data);
            
            // Split the data into lines and skip the header
            const lines = data.split('\n').filter(line => line.trim());
            console.log('Processed lines:', lines);
            
            if (lines.length <= 1) {
                throw new Error('No processes found in the file');
            }
            
            // Process each line (skip header)
            lines.slice(1).forEach(line => {
                const parts = line.trim().split(/\s+/);
                console.log('Processing line:', line, 'Parts:', parts);
                
                if (parts.length >= 4) {
                    const [pid, arrival, burst, priority] = parts;
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="text-center">${pid}</td>
                        <td class="text-center">${parseFloat(arrival).toFixed(2)}</td>
                        <td class="text-center">${parseFloat(burst).toFixed(2)}</td>
                        <td class="text-center">${priority}</td>
                    `;
                    tableBody.appendChild(row);
                }
            });
            
            // Add a nice header to the card
            const cardHeader = processesDiv.querySelector('.card-header');
            cardHeader.innerHTML = `
                <h3 class="mb-0">
                    <i class="fas fa-table me-2"></i>
                    Generated Processes (${tableBody.children.length} processes)
                </h3>
            `;
            
            console.log('Successfully displayed processes');
        })
        .catch(error => {
            console.error('Error:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        ${error.message}
                    </td>
                </tr>
            `;
        });
}

function generateAndShow() {
    const statusDiv = document.getElementById('generateStatus');
    const processesDiv = document.getElementById('generatedProcesses');
    
    // Hide the processes table while generating
    processesDiv.style.display = 'none';
    statusDiv.innerHTML = '<div class="alert alert-info"><i class="fas fa-spinner fa-spin me-2"></i>Generating new processes...</div>';
    
    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            statusDiv.innerHTML = '<div class="alert alert-success"><i class="fas fa-check-circle me-2"></i>Processes generated successfully!</div>';
            // Automatically show the generated processes
            Show();
        } else {
            throw new Error(data.message || 'Failed to generate processes');
        }
    })
    .catch(error => {
        statusDiv.innerHTML = `<div class="alert alert-danger"><i class="fas fa-exclamation-circle me-2"></i>Error: ${error.message}</div>`;
    });
} 
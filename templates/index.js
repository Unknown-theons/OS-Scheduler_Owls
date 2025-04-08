function Show() {
    const statusDiv = document.getElementById('generateStatus');
    statusDiv.innerHTML = '<div class="alert alert-info">Loading processes data...</div>';
    
    fetch('/get_processes_data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            const processesSection = document.getElementById('generatedProcesses');
            const tableBody = document.getElementById('processesTableBody');
            tableBody.innerHTML = ''; // Clear existing rows
            
            // Show the processes section
            processesSection.style.display = 'block';
            
            const rows = data.trim().split('\n');
            
            // Skip header row if it exists
            const startIndex = rows[0].toLowerCase().includes('process') ? 1 : 0;
            
            if (rows.length <= startIndex) {
                throw new Error('No process data found');
            }
            
            for (let i = startIndex; i < rows.length; i++) {
                const row = rows[i].trim();
                if (row) {
                    const tr = document.createElement('tr');
                    const columns = row.split(/\s+/);
                    columns.forEach(col => {
                        const td = document.createElement('td');
                        td.textContent = col;
                        tr.appendChild(td);
                    });
                    tableBody.appendChild(tr);
                }
            }
            statusDiv.innerHTML = '<div class="alert alert-success">Processes data loaded successfully!</div>';
        })
        .catch(error => {
            console.error('Error fetching processes data:', error);
            const processesSection = document.getElementById('generatedProcesses');
            processesSection.style.display = 'block';
            document.getElementById('processesTableBody').innerHTML = 
                '<tr><td colspan="4" class="text-center text-danger">Error loading processes data: ' + error.message + '</td></tr>';
            statusDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        });
}

async function generateAndShow() {
    const statusDiv = document.getElementById('generateStatus');
    statusDiv.innerHTML = '<div class="alert alert-info">Generating new processes...</div>';
    
    try {
        // Call the generate endpoint
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            statusDiv.innerHTML = '<div class="alert alert-success">Generation successful! Loading new processes...</div>';
            // Show the new process data immediately
            Show();
            // Reload the page after a short delay to show updated statistics
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            throw new Error(data.message || 'Generation failed');
        }
    } catch (error) {
        console.error('Error generating processes:', error);
        statusDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}
function Show() {
    fetch('/get_processes_data')
        .then(response => response.text())
        .then(data => {
            const output = document.getElementById('output1');
            output.innerHTML = '<h3 class="mb-3">Processes Data</h3>';
            
            const table = document.createElement('table');
            table.classList.add('table', 'table-striped', 'table-bordered');
            
            // Create header
            const thead = document.createElement('thead');
            thead.classList.add('table-dark');
            const headerRow = document.createElement('tr');
            const headers = ['Process ID', 'Arrival Time', 'Burst Time', 'Priority'];
            headers.forEach(headerText => {
                const th = document.createElement('th');
                th.textContent = headerText;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);

            const tbody = document.createElement('tbody');
            const rows = data.trim().split('\n');
            
            // Skip header row if it exists
            const startIndex = rows[0].toLowerCase().includes('process') ? 1 : 0;
            
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
                    tbody.appendChild(tr);
                }
            }
            table.appendChild(tbody);
            output.appendChild(table);
        })
        .catch(error => {
            console.error('Error fetching processes data:', error);
            document.getElementById('output1').innerHTML = '<div class="alert alert-danger">Error loading processes data</div>';
        });
}

async function generateAndShow() {
    const statusDiv = document.getElementById('generateStatus');
    statusDiv.innerHTML = '<div class="alert alert-info">Generating new processes...</div>';
    
    try {
        // Call the generate endpoint
        const response = await fetch('/generate', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            statusDiv.innerHTML = '<div class="alert alert-success">Generation successful!</div>';
            // Show the new process data immediately
            Show();
            // Reload the page after a short delay to show updated statistics
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            throw new Error(data.message || 'Generation failed');
        }
    } catch (error) {
        console.error('Error generating processes:', error);
        statusDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

$(document).ready(function() {
    $('#generateBtn').click(function() {
        var btn = $(this);
        btn.prop('disabled', true).text('Generating...');
        
        $.ajax({
            url: '/generate',
            method: 'POST',
            success: function(response) {
                if (response.status === 'success') {
                    location.reload();
                } else {
                    alert('Error generating processes');
                }
            },
            error: function() {
                alert('Error generating processes');
            },
            complete: function() {
                btn.prop('disabled', false).text('Generate New Processes');
            }
        });
    });
});
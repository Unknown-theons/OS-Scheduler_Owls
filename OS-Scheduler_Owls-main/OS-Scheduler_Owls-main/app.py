from flask import Flask, render_template, redirect, url_for, request
import subprocess
import os

app = Flask(__name__)

def read_processes():
    processes = []
    try:
        with open('processes.txt', 'r') as f:
            lines = f.readlines()
            # Skip header
            for line in lines[1:]:
                if line.strip():
                    data = line.split()
                    if len(data) >= 4:  # Make sure we have all required fields
                        processes.append({
                            'process_id': data[0],
                            'arrival_time': data[1],
                            'burst_time': data[2],
                            'priority': data[3]
                        })
    except FileNotFoundError:
        print('Process file not found')
    except Exception as e:
        print(f'Error reading process file: {e}')
    return processes

def read_input_params():
    default_params = {
        'processes_number': 'N/A',
        'arrival_time_stats': 'N/A',
        'burst_time_stats': 'N/A',
        'lambda_priority': 'N/A'
    }
    try:
        with open('inputFile.txt', 'r') as f:
            lines = f.readlines()
            if len(lines) >= 4:  # Make sure we have all required lines
                params = {
                    'processes_number': lines[0].split(':')[1].strip() if ':' in lines[0] else 'N/A',
                    'arrival_time_stats': lines[1].split(':')[1].strip() if ':' in lines[1] else 'N/A',
                    'burst_time_stats': lines[2].split(':')[1].strip() if ':' in lines[2] else 'N/A',
                    'lambda_priority': lines[3].split(':')[1].strip() if ':' in lines[3] else 'N/A'
                }
                return params
    except FileNotFoundError:
        print('Input file not found')
    except Exception as e:
        print(f'Error reading input file: {e}')
    return default_params

@app.route('/')
def index():
    processes = read_processes()
    params = read_input_params()
    return render_template('index.html', processes=processes, params=params)

@app.route('/fcfs')
def fcfs():
    try:
        # Run FCFS.py
        subprocess.run(['python', 'Schedulers/FCFS&SRTF/FCFS.py'], check=True)
        # Read FCFS results
        fcfs_output = None
        try:
            with open('fcfs_results.txt', 'r') as f:
                fcfs_output = f.read()
        except FileNotFoundError:
            pass
        
        processes = read_processes()
        params = read_input_params()
        return render_template('fcfs.html', processes=processes, params=params, fcfs_output=fcfs_output)
    except subprocess.CalledProcessError as e:
        print(f'Error running FCFS: {e}')
        return redirect(url_for('index'))

@app.route('/srtf')
def srtf():
    try:
        # Run SRTF.py
        subprocess.run(['python', 'Schedulers/FCFS&SRTF/SRTF.py'], check=True)
        # Read SRTF results
        srtf_output = None
        try:
            with open('srtf_results.txt', 'r') as f:
                srtf_output = f.read()
        except FileNotFoundError:
            pass
        
        processes = read_processes()
        params = read_input_params()
        return render_template('srtf.html', processes=processes, params=params, srtf_output=srtf_output)
    except subprocess.CalledProcessError as e:
        print(f'Error running SRTF: {e}')
        return redirect(url_for('index'))

@app.route('/priority')
def priority():
    try:
        # Run Priority.py
        subprocess.run(['python', 'Schedulers/Priority&RoundRobin/periority.py'], check=True)
        # Read Priority results
        priority_output = None
        try:
            with open('priority_results.txt', 'r') as f:
                priority_output = f.read()
        except FileNotFoundError:
            pass
        
        processes = read_processes()
        params = read_input_params()
        return render_template('priority.html', processes=processes, params=params, priority_output=priority_output)
    except subprocess.CalledProcessError as e:
        print(f'Error running Priority: {e}')
        return redirect(url_for('index'))

@app.route('/round-robin')
def round_robin():
    try:
        # Run Round Robin.py
        subprocess.run(['python', 'Schedulers/Priority&RoundRobin/round robin.py'], check=True)
        # Read Round Robin results
        round_robin_output = None
        try:
            with open('round_robin_results.txt', 'r') as f:
                round_robin_output = f.read()
        except FileNotFoundError:
            pass
        
        processes = read_processes()
        params = read_input_params()
        return render_template('round_robin.html', processes=processes, params=params, round_robin_output=round_robin_output)
    except subprocess.CalledProcessError as e:
        print(f'Error running Round Robin: {e}')
        return redirect(url_for('index'))

@app.route('/generate', methods=['POST'])
def generate_processes():
    try:
        # Run InputGenerator.py
        subprocess.run(['python', 'ProcessGeneratorModule/InputGenerator.py'], check=True)
        # Run outputGenerator.py
        subprocess.run(['python', 'ProcessGeneratorModule/outputGenerator.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error generating processes: {e}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

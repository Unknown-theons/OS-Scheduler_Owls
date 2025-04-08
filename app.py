from flask import Flask, render_template, send_file, jsonify
from Schedulers.FCFS import read_processes, fcfs_scheduling
from Schedulers.SRTF import read_processes as srtf_read_processes, srtf_scheduling
import os
import subprocess

app = Flask(__name__)

def read_round_robin_input():
    """Read the Round Robin input data from file"""
    input_data = []
    try:
        with open("processes.txt", "r") as file:
            lines = file.readlines()[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    input_data.append({
                        'Process ID': parts[0],
                        'Arrival Time': float(parts[1]),
                        'Burst Time': float(parts[2]),
                        'Priority': int(parts[3])
                    })
    except FileNotFoundError:
        pass
    return input_data

def read_round_robin_results():
    """Read Round Robin results directly from the text file"""
    results = {
        'header': '',
        'processes': [],
        'avg_waiting': 0,
        'avg_turnaround': 0
    }
    
    try:
        with open("ProcessGeneratorModule/round_robin_results.txt", "r") as file:
            lines = file.readlines()
            if len(lines) >= 2:
                results['header'] = lines[0].strip()  # Save the header
                
                # Read process data
                for line in lines[2:]:  # Skip header and separator
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("Average"):
                        # Extract average values
                        if "Waiting Time:" in line:
                            results['avg_waiting'] = float(line.split(":")[1].strip())
                        elif "Turnaround Time:" in line:
                            results['avg_turnaround'] = float(line.split(":")[1].strip())
                    else:
                        # Process data line
                        parts = line.split()
                        if len(parts) >= 7:
                            process = {
                                'Process ID': parts[0],
                                'Arrival Time': float(parts[1]),
                                'Burst Time': float(parts[2]),
                                'Priority': int(parts[3]),
                                'Completion Time': float(parts[4]),
                                'Waiting Time': float(parts[5]),
                                'Turnaround Time': float(parts[6])
                            }
                            results['processes'].append(process)
    except FileNotFoundError:
        pass
    
    return results

@app.route('/')
def index():
    # Path to the processes.txt file
    file_path = "E:/MY PROJECT/Web devolopment/OS-Scheduler_Owls/processes.txt"
    srtf_results_path = "E:/MY PROJECT/Web devolopment/OS-Scheduler_Owls/ProcessGeneratorModule/srtf_results.txt"
    
    # Read processes and get FCFS scheduling results
    processes = read_processes(file_path)
    fcfs_results = fcfs_scheduling(processes)
    
    # Calculate FCFS averages
    if fcfs_results:
        total_waiting = sum(process['Waiting Time'] for process in fcfs_results)
        total_turnaround = sum(process['Turnaround Time'] for process in fcfs_results)
        n = len(fcfs_results)
        fcfs_avg_waiting = total_waiting / n
        fcfs_avg_turnaround = total_turnaround / n
    else:
        fcfs_avg_waiting = fcfs_avg_turnaround = 0
    
    # Read SRTF results from file
    srtf_processes = []
    srtf_avg_waiting = 0
    srtf_avg_turnaround = 0
    srtf_total_execution = 0
    
    try:
        with open(srtf_results_path, 'r') as file:
            lines = file.readlines()
            # Skip header
            current_section = "processes"
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("=== Averages ==="):
                    current_section = "averages"
                    continue
                
                if current_section == "processes":
                    parts = line.split('\t')
                    if len(parts) == 6:
                        srtf_processes.append({
                            'Process ID': parts[0],
                            'Arrival Time': float(parts[1]),
                            'Burst Time': float(parts[2]),
                            'Completion Time': float(parts[3]),
                            'Turnaround Time': float(parts[4]),
                            'Waiting Time': float(parts[5])
                        })
                elif current_section == "averages":
                    if "Average Waiting Time:" in line:
                        srtf_avg_waiting = float(line.split(': ')[1])
                    elif "Average Turnaround Time:" in line:
                        srtf_avg_turnaround = float(line.split(': ')[1])
                    elif "Total Execution Time:" in line:
                        srtf_total_execution = float(line.split(': ')[1])
    except FileNotFoundError:
        pass
    
    # Read Round Robin results
    rr_results = read_round_robin_results()
    
    return render_template('index.html', 
                         fcfs_processes=fcfs_results,
                         fcfs_avg_waiting=fcfs_avg_waiting,
                         fcfs_avg_turnaround=fcfs_avg_turnaround,
                         srtf_processes=srtf_processes,
                         srtf_avg_waiting=srtf_avg_waiting,
                         srtf_avg_turnaround=srtf_avg_turnaround,
                         srtf_total_execution=srtf_total_execution,
                         rr_results=rr_results)

@app.route('/get_processes_data')
def get_processes_data():
    file_path = "E:/MY PROJECT/Web devolopment/OS-Scheduler_Owls/processes.txt"
    return send_file(file_path)

@app.route('/get_input_data')
def get_input_data():
    file_path = "E:/MY PROJECT/Web devolopment/OS-Scheduler_Owls/inputFile.txt"
    return send_file(file_path)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Generate new processes
        subprocess.run(['python', 'ProcessGeneratorModule/InputGenerator.py'], check=True)
        subprocess.run(['python', 'ProcessGeneratorModule/outputGenerator.py'], check=True)
        
        # Run SRTF scheduling
        srtf_processes = srtf_read_processes("processes.txt")
        srtf_results = srtf_scheduling(srtf_processes)
        
        # Save SRTF results to file
        output_path = "ProcessGeneratorModule/srtf_results.txt"
        with open(output_path, 'w') as file:
            # Write header
            file.write("Process ID\tArrival Time\tBurst Time\tCompletion Time\tTurnaround Time\tWaiting Time\n")
            
            # Write process data
            for process in srtf_results["processes"]:
                file.write(f"{process['Process ID']}\t"
                          f"{process['Arrival Time']:.2f}\t"
                          f"{process['Burst Time']:.2f}\t"
                          f"{process['Completion Time']:.2f}\t"
                          f"{process['Turnaround Time']:.2f}\t"
                          f"{process['Waiting Time']:.2f}\n")
            
            # Write averages
            file.write("\n=== Averages ===\n")
            file.write(f"Average Waiting Time: {srtf_results['avg_waiting_time']:.2f}\n")
            file.write(f"Average Turnaround Time: {srtf_results['avg_turnaround_time']:.2f}\n")
            file.write(f"Total Execution Time: {srtf_results['total_execution_time']:.2f}\n")
        
        # Run Round Robin algorithm
        subprocess.run(['python', 'Round robin/round robin.py'], check=True)
        
        return jsonify({"status": "success"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

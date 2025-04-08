from flask import Flask, render_template, send_file, jsonify
from Schedulers.FCFS_SRTF.FCFS import read_processes, fcfs_scheduling
from Schedulers.FCFS_SRTF.SRTF import read_processes as srtf_read_processes, srtf_scheduling
import os
import subprocess

app = Flask(__name__)

def read_round_robin_input():
    """Read the Round Robin input data from file"""
    input_data = []
    try:
        file_path = os.path.join(os.path.dirname(__file__), "..", "ProcessGeneratorModule", "processes.txt")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")
            
        with open(file_path, "r") as file:
            lines = file.readlines()
            if not lines:
                raise ValueError("Input file is empty")
                
            # Skip header
            for line in lines[1:]:
                if line.strip():
                    try:
                        parts = line.split()
                        if len(parts) < 4:
                            raise ValueError(f"Invalid line format: {line.strip()}")
                            
                        input_data.append({
                            'Process ID': parts[0],
                            'Arrival Time': float(parts[1]),
                            'Burst Time': float(parts[2]),
                            'Priority': int(parts[3])
                        })
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Skipping invalid line: {line.strip()}. Error: {str(e)}")
                        continue
    except FileNotFoundError as e:
        print(f"Error reading input file: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error reading input file: {str(e)}")
        raise
        
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
        # Get the absolute path of the current file's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to Results_Data directory
        results_dir = os.path.join(current_dir, "Results_Data")
        # Create the directory if it doesn't exist
        os.makedirs(results_dir, exist_ok=True)
        # Construct the full path to the results file
        file_path = os.path.join(results_dir, "round_robin_results.txt")
        
        if not os.path.exists(file_path):
            # If file doesn't exist, create an empty one
            with open(file_path, 'w') as f:
                f.write("")
            return results
            
        with open(file_path, "r") as file:
            lines = file.readlines()
            if not lines:
                # If file is empty, return empty results
                return results
                
            # Try to read the header if it exists
            if len(lines) > 0:
                results['header'] = lines[0].strip()
                
            # Read process data if available
            if len(lines) >= 2:
                for line in lines[2:]:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.startswith("Average"):
                        try:
                            if "Waiting Time:" in line:
                                results['avg_waiting'] = float(line.split(":")[1].strip())
                            elif "Turnaround Time:" in line:
                                results['avg_turnaround'] = float(line.split(":")[1].strip())
                        except (ValueError, IndexError) as e:
                            print(f"Warning: Error parsing average line: {line}. Error: {str(e)}")
                    else:
                        try:
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
                        except (ValueError, IndexError) as e:
                            print(f"Warning: Skipping invalid process line: {line}. Error: {str(e)}")
                            continue
    except FileNotFoundError as e:
        print(f"Error reading results file: {str(e)}")
        return results
    except Exception as e:
        print(f"Unexpected error reading results file: {str(e)}")
        return results
    
    return results

@app.route('/')
def index():
    # Get the absolute path of the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the processes.txt file
    processes_dir = os.path.join(current_dir, "ProcessGeneratorModule")
    file_path = os.path.join(processes_dir, "processes.txt")
    
    # Path to SRTF results
    results_dir = os.path.join(current_dir, "Results_Data")
    srtf_results_path = os.path.join(results_dir, "srtf_results.txt")
    
    # Create Results_Data directory if it doesn't exist
    os.makedirs(results_dir, exist_ok=True)
    
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
    file_path = os.path.join(os.path.dirname(__file__), "..", "ProcessGeneratorModule", "processes.txt")
    return send_file(file_path)

@app.route('/get_input_data')
def get_input_data():
    file_path = os.path.join(os.path.dirname(__file__), "..", "ProcessGeneratorModule", "inputFile.txt")
    return send_file(file_path)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Get the absolute path of the current file's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Generate new processes
        processes_dir = os.path.join(current_dir, "ProcessGeneratorModule")
        input_generator_path = os.path.join(processes_dir, "InputGenerator.py")
        output_generator_path = os.path.join(processes_dir, "outputGenerator.py")
        
        if not os.path.exists(input_generator_path):
            return jsonify({"status": "error", "message": "InputGenerator.py not found"}), 500
        if not os.path.exists(output_generator_path):
            return jsonify({"status": "error", "message": "outputGenerator.py not found"}), 500
            
        subprocess.run(['python', input_generator_path], check=True)
        subprocess.run(['python', output_generator_path], check=True)
        
        # Run SRTF scheduling
        processes_path = os.path.join(processes_dir, "processes.txt")
        if not os.path.exists(processes_path):
            return jsonify({"status": "error", "message": "processes.txt not found"}), 500
            
        srtf_processes = srtf_read_processes(processes_path)
        srtf_results = srtf_scheduling(srtf_processes)
        
        # Save SRTF results to file
        results_dir = os.path.join(current_dir, "Results_Data")
        os.makedirs(results_dir, exist_ok=True)
        output_path = os.path.join(results_dir, "srtf_results.txt")
        
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
        round_robin_dir = os.path.join(current_dir, "Round_Robin")
        round_robin_path = os.path.join(round_robin_dir, "round_robin.py")
        if not os.path.exists(round_robin_path):
            return jsonify({"status": "error", "message": "round_robin.py not found"}), 500
            
        subprocess.run(['python', round_robin_path], check=True)
        
        return jsonify({"status": "success"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": f"Subprocess error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    try:
        app.run(debug=True, use_reloader=False)
    except SystemExit:
        pass
    except Exception as e:
        print(f"Error running Flask application: {str(e)}")

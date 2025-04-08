from flask import Flask, render_template, send_file, jsonify, send_from_directory
from Schedulers.FCFS_SRTF.FCFS import read_processes, fcfs_scheduling
from Schedulers.FCFS_SRTF.SRTF import read_processes as srtf_read_processes, srtf_scheduling
import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')

def get_absolute_path(relative_path):
    """Convert relative path to absolute path based on app root"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/algorithms')
def algorithms():
    return render_template('algorithms.html')

@app.route('/get_processes_data')
def get_processes_data():
    try:
        # Look for processes.txt in the ProcessGeneratorModule folder
        file_path = get_absolute_path("ProcessGeneratorModule/processes.txt")
        logger.debug(f"Attempting to read processes file from: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"Processes file not found at: {file_path}")
            return "No processes data available", 404
            
        # Read the file content
        with open(file_path, 'r') as file:
            content = file.read()
            
        if not content.strip():
            logger.error("Processes file is empty")
            return "No processes data available", 404
            
        logger.debug(f"Successfully read processes file. Content length: {len(content)}")
        return content
    except Exception as e:
        logger.error(f"Error in get_processes_data: {str(e)}")
        return str(e), 500

@app.route('/generate', methods=['POST'])
def generate():
    try:
        logger.debug("Starting process generation")
        
        # Get absolute paths
        input_generator = get_absolute_path("ProcessGeneratorModule/InputGenerator.py")
        output_generator = get_absolute_path("ProcessGeneratorModule/outputGenerator.py")
        
        # First run InputGenerator.py to create inputFile.txt
        logger.debug(f"Running input generator: {input_generator}")
        subprocess.run(['python', input_generator], check=True, cwd=os.path.dirname(input_generator))
        
        # Then run outputGenerator.py to create processes.txt
        logger.debug(f"Running output generator: {output_generator}")
        subprocess.run(['python', output_generator], check=True, cwd=os.path.dirname(output_generator))
        
        # Verify that processes.txt was created
        processes_path = get_absolute_path("ProcessGeneratorModule/processes.txt")
        if not os.path.exists(processes_path):
            raise Exception("Processes file was not created after generation")
            
        logger.debug("Process generation completed successfully")
        return jsonify({"status": "success"})
    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        logger.error(f"Error in generate: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def run_all_algorithms():
    """Run all scheduling algorithms and store their results"""
    try:
        # Get the processes file path
        processes_path = get_absolute_path("ProcessGeneratorModule/processes.txt")
        
        # Run FCFS
        processes = read_processes(processes_path)
        fcfs_results = fcfs_scheduling(processes)
        save_results("Schedulers/FCFS_SRTF/FCFS_Results.txt", fcfs_results)
        
        # Run SRTF
        processes = srtf_read_processes(processes_path)
        srtf_results = srtf_scheduling(processes)
        save_results("Schedulers/FCFS_SRTF/SRTF_Results.txt", srtf_results)
        
        # Run Round Robin
        processes_src = processes_path
        processes_dest = get_absolute_path("Schedulers/Priority&RoundRobin/processes.txt")
        with open(processes_src, 'r') as src, open(processes_dest, 'w') as dest:
            dest.write(src.read())
        
        round_robin_path = get_absolute_path("Schedulers/Priority&RoundRobin/round robin.py")
        subprocess.run(['python', round_robin_path], check=True, cwd=os.path.dirname(round_robin_path))
        
        # Run Priority
        priority_path = get_absolute_path("Schedulers/Priority&RoundRobin/periority.py")
        subprocess.run(['python', priority_path], check=True, cwd=os.path.dirname(priority_path))
        
    except Exception as e:
        logger.error(f"Error running algorithms: {str(e)}")
        raise

def save_results(filename, results):
    """Save algorithm results to a file"""
    try:
        # Get the absolute path for the results file
        file_path = get_absolute_path(filename)
        logger.debug(f"Saving results to: {file_path}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as file:
            # Write header
            file.write("🔄 FCFS Scheduling Results:\n")
            file.write("=" * 100 + "\n")
            file.write(f"{'Process ID':<12} {'Arrival Time':<14} {'Burst Time':<12} {'Completion':<12} "
                      f"{'Turnaround':<12} {'Waiting':<12}\n")
            file.write("-" * 100 + "\n")
            
            # Write process data
            for process in results['processes']:
                file.write(f"{process['Process ID']:<12} {process['Arrival Time']:<14.2f} {process['Burst Time']:<12.2f} "
                          f"{process['Completion Time']:<12.2f} {process['Turnaround Time']:<12.2f} "
                          f"{process['Waiting Time']:<12.2f}\n")
            
            # Write footer with averages
            file.write("=" * 100 + "\n")
            file.write(f"Average Waiting Time: {results['avg_waiting']:.2f}\n")
            file.write(f"Average Turnaround Time: {results['avg_turnaround']:.2f}\n")
                
        logger.debug(f"Successfully saved results to {file_path}")
    except Exception as e:
        logger.error(f"Error saving results to {filename}: {str(e)}")
        raise

@app.route('/run_fcfs', methods=['POST'])
def run_fcfs():
    try:
        # Run FCFS algorithm
        fcfs_path = get_absolute_path("Schedulers/FCFS_SRTF/FCFS.py")
        subprocess.run(['python', fcfs_path], check=True, cwd=os.path.dirname(fcfs_path))
        
        # Read results from file
        results_path = get_absolute_path("Schedulers/FCFS_SRTF/FCFS_Results.txt")
        return read_and_format_results(results_path)
    except Exception as e:
        logger.error(f"Error in run_fcfs: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/run_srtf', methods=['POST'])
def run_srtf():
    try:
        # Run SRTF algorithm
        srtf_path = get_absolute_path("Schedulers/FCFS_SRTF/SRTF.py")
        subprocess.run(['python', srtf_path], check=True, cwd=os.path.dirname(srtf_path))
        
        # Read results from file
        results_path = get_absolute_path("Schedulers/FCFS_SRTF/SRTF_Results.txt")
        return read_and_format_results(results_path)
    except Exception as e:
        logger.error(f"Error in run_srtf: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/run_round_robin', methods=['POST'])
def run_round_robin():
    try:
        # Run Round Robin algorithm
        round_robin_path = get_absolute_path("Schedulers/Priority&RoundRobin/round robin.py")
        subprocess.run(['python', round_robin_path], check=True, cwd=os.path.dirname(round_robin_path))
        
        # Read results from file
        results_path = get_absolute_path("Schedulers/Priority&RoundRobin/RoundRobin_Results.txt")
        return read_and_format_results(results_path)
    except Exception as e:
        logger.error(f"Error in run_round_robin: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/run_priority', methods=['POST'])
def run_priority():
    try:
        # Run Priority algorithm
        priority_path = get_absolute_path("Schedulers/Priority&RoundRobin/periority.py")
        subprocess.run(['python', priority_path], check=True, cwd=os.path.dirname(priority_path))
        
        # Read results from file
        results_path = get_absolute_path("Schedulers/Priority&RoundRobin/Priority_Results.txt")
        return read_and_format_results(results_path)
    except Exception as e:
        logger.error(f"Error in run_priority: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def read_and_format_results(file_path):
    """Read and format results from a file"""
    try:
        if not os.path.exists(file_path):
            raise Exception(f"Results file not found: {file_path}")
            
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
        results = {
            'processes': [],
            'avg_waiting': 0,
            'avg_turnaround': 0
        }
        
        # Skip header lines until we reach the process data
        start_processing = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("Process ID"):
                start_processing = True
                continue
                
            if line.startswith("=") and "=" * 100 in line:
                start_processing = False
                continue
                
            if start_processing and not line.startswith("-"):
                # Parse process data
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        results['processes'].append({
                            'Process ID': parts[0],
                            'Arrival Time': float(parts[1]),
                            'Burst Time': float(parts[2]),
                            'Completion Time': float(parts[3]),
                            'Turnaround Time': float(parts[4]),
                            'Waiting Time': float(parts[5])
                        })
                    except (IndexError, ValueError) as e:
                        logger.error(f"Error parsing process data from line: {line}, error: {str(e)}")
            
            # Parse averages
            if line.startswith("Average Waiting Time:"):
                try:
                    results['avg_waiting'] = float(line.split(":")[1].strip())
                except (IndexError, ValueError):
                    logger.error(f"Error parsing waiting time from line: {line}")
            elif line.startswith("Average Turnaround Time:"):
                try:
                    results['avg_turnaround'] = float(line.split(":")[1].strip())
                except (IndexError, ValueError):
                    logger.error(f"Error parsing turnaround time from line: {line}")
        
        logger.debug(f"Read results from {file_path}: {results}")
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error reading results from {file_path}: {str(e)}")
        raise

@app.route('/fcfs')
def fcfs_page():
    return render_template('fcfs.html')

@app.route('/srtf')
def srtf_page():
    return render_template('srtf.html')

@app.route('/roundrobin')
def roundrobin_page():
    return render_template('roundrobin.html')

@app.route('/priority')
def priority_page():
    return render_template('priority.html')

if __name__ == '__main__':
    try:
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Error starting Flask application: {str(e)}")
        raise

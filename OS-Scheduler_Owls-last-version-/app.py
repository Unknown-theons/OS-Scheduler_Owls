from flask import Flask, render_template, redirect, url_for, request, send_file
import subprocess
import os
import time
from functools import lru_cache
import sys
import random
import numpy as np
import math
from performance_analysis2 import plot_comparison
from datetime import datetime
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import logging
import glob
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the base directory path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create Flask app
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files

# Add static folder configuration
app.static_folder = os.path.join(BASE_DIR, 'static')
app.static_url_path = '/static'

# Create a symbolic link from static/Schedulers to Schedulers directory
schedulers_static_dir = os.path.join(app.static_folder, 'Schedulers')
schedulers_dir = os.path.join(BASE_DIR, 'Schedulers')

# Ensure static directory exists
if not os.path.exists(app.static_folder):
    os.makedirs(app.static_folder)

# Create symbolic link if it doesn't exist
if not os.path.exists(schedulers_static_dir):
    try:
        os.symlink(schedulers_dir, schedulers_static_dir)
    except Exception as e:
        logger.warning(f"Could not create symbolic link: {e}")
        # If symlink fails, try to copy the directory
        if os.path.exists(schedulers_dir):
            shutil.copytree(schedulers_dir, schedulers_static_dir)

# Ensure required directories exist
for dir_name in ['ProcessGeneratorModule', 'Schedulers', 'templates', 'static']:
    dir_path = os.path.join(BASE_DIR, dir_name)
    if not os.path.exists(dir_path):
        logger.warning(f"Directory {dir_path} does not exist, creating it...")
        os.makedirs(dir_path, exist_ok=True)

def generate_new_processes():
    """Generate new processes and write them directly to processes.txt"""
    try:
        # Generate random number of processes (3-10)
        num_processes = random.randint(3, 10)
        
        # Generate arrival times (0-15)
        arrival_times = [random.randint(0, 15) for _ in range(num_processes)]
        
        # Generate burst times (1-25)
        burst_times = [random.randint(1, 25) for _ in range(num_processes)]
        
        # Generate priorities using Poisson distribution
        lambda_priority = random.uniform(4, 10)
        priorities = np.random.poisson(lambda_priority, num_processes)
        priorities = [max(1, int(p)) for p in priorities]  # Ensure priorities are at least 1
        
        # Calculate statistics
        arrival_mean = np.mean(arrival_times)
        arrival_std = np.std(arrival_times)
        burst_mean = np.mean(burst_times)
        burst_std = np.std(burst_times)
        
        # Ensure directories exist
        process_dir = os.path.join(BASE_DIR, 'ProcessGeneratorModule')
        os.makedirs(process_dir, exist_ok=True)
        
        # Write to inputFile.txt
        input_file = os.path.join(process_dir, 'inputFile.txt')
        try:
            with open(input_file, 'w') as f:
                f.write(f"\nProccesses Number: {num_processes}\n")
                f.write(f"Mean and Standard Deviation for Arrival Time: ({arrival_mean:.1f}, {arrival_std:.1f})\n")
                f.write(f"Mean and Standard Deviation for Burst Time: ({burst_mean:.1f}, {burst_std:.1f})\n")
                f.write(f"Lambda Priority: {lambda_priority:.1f}\n")
        except IOError as e:
            print(f'Error writing to input file: {e}')
            return False
        
        # Write to processes.txt
        processes_file = os.path.join(process_dir, 'processes.txt')
        try:
            with open(processes_file, 'w') as f:
                f.write(f"{'Process ID':<15}{'Arrival Time':<15}{'Burst Time':<15}{'Priority':<15}\n")
                for i in range(1, num_processes + 1):  # Start from 1 and go to num_processes
                    f.write(f"P{i:<14}{arrival_times[i-1]:<15}{burst_times[i-1]:<15}{priorities[i-1]:<15}\n")
        except IOError as e:
            print(f'Error writing to processes file: {e}')
            return False
        
        # Clear caches
        read_processes.cache_clear()
        read_input_params.cache_clear()
        run_scheduler.cache_clear()
        
        return True
    except Exception as e:
        print(f'Error generating processes: {e}')
        return False

# Cache the process data for 5 seconds
@lru_cache(maxsize=1)
def read_processes():
    processes = []
    try:
        file_path = os.path.join(BASE_DIR, 'ProcessGeneratorModule', 'processes.txt')
        if not os.path.exists(file_path):
            print('Process file not found')
            return processes
            
        with open(file_path, 'r') as f:
            lines = f.readlines()
            if not lines:
                print('Process file is empty')
                return processes
                
            # Skip header
            for line in lines[1:]:
                if line.strip():
                    data = line.split()
                    if len(data) >= 4:  # Make sure we have all required fields
                        try:
                            processes.append({
                                'process_id': data[0],
                                'arrival_time': float(data[1]),
                                'burst_time': float(data[2]),
                                'priority': int(data[3])
                            })
                        except (ValueError, IndexError) as e:
                            print(f'Error parsing process data: {e}')
                            continue
    except Exception as e:
        print(f'Error reading process file: {e}')
    return processes

# Cache the input parameters for 5 seconds
@lru_cache(maxsize=1)
def read_input_params():
    default_params = {
        'processes_number': 'N/A',
        'arrival_time_stats': 'N/A',
        'burst_time_stats': 'N/A',
        'lambda_priority': 'N/A'
    }
    
    # First try to get number of processes from processes.txt
    try:
        file_path = os.path.join(BASE_DIR, 'ProcessGeneratorModule', 'processes.txt')
        if os.path.exists(file_path):
            with open(file_path, 'r') as proc_file:
                # Count the number of non-header lines
                process_count = sum(1 for line in proc_file if line.strip() and not line.startswith('Process ID'))
                default_params['processes_number'] = str(process_count)
    except Exception as e:
        print(f'Error reading processes file: {e}')
    
    # Then try to read from inputFile.txt
    try:
        input_file_path = os.path.join(BASE_DIR, 'ProcessGeneratorModule', 'inputFile.txt')
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    # Process each line
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        if 'Proccesses Number:' in line:
                            # Skip if we already have a valid process count
                            if default_params['processes_number'] == 'N/A':
                                default_params['processes_number'] = line.split(':')[1].strip()
                        elif 'Mean and Standard Deviation for Arrival Time:' in line:
                            default_params['arrival_time_stats'] = line.split(':')[1].strip()
                        elif 'Mean and Standard Deviation for Burst Time:' in line:
                            default_params['burst_time_stats'] = line.split(':')[1].strip()
                        elif 'Lambda Priority:' in line:
                            default_params['lambda_priority'] = line.split(':')[1].strip()
    except Exception as e:
        print(f'Error reading input file: {e}')
        
    return default_params

# Cache the scheduler results for 5 seconds
@lru_cache(maxsize=4)
def run_scheduler(scheduler_name):
    try:
        # Map scheduler names to their scripts and result files
        scheduler_map = {
            'fcfs': ('FCFS&SRTF', 'FCFS.py', 'FCFS&SRTF/fcfs_results.txt'),
            'srtf': ('FCFS&SRTF', 'SRTF.py', 'FCFS&SRTF/srtf_results.txt'),
            'priority': ('Priority&RoundRobin', 'priority.py', 'Priority&RoundRobin/priority_results.txt'),
            'round_robin': ('Priority&RoundRobin', 'round_robin.py', 'Priority&RoundRobin/round_robin_results.txt')
        }
        
        if scheduler_name not in scheduler_map:
            print(f'Error: Unknown scheduler {scheduler_name}')
            return None
            
        scheduler_dir, script_name, result_file = scheduler_map[scheduler_name]
        script_path = os.path.join(BASE_DIR, 'Schedulers', scheduler_dir, script_name)
        result_path = os.path.join(BASE_DIR, 'Schedulers', result_file)

        # Check if scheduler script exists
        if not os.path.exists(script_path):
            print(f'Error: Scheduler script {script_path} not found')
            return None

        # Check if processes.txt exists
        processes_file = os.path.join(BASE_DIR, 'ProcessGeneratorModule', 'processes.txt')
        if not os.path.exists(processes_file):
            print('Error: processes.txt not found')
            return None

        # Run the scheduler script with timeout
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                check=True,
                capture_output=True,
                text=True,
                timeout=5  # 5 second timeout
            )
            
            if result.returncode != 0:
                print(f'Error running {scheduler_name}: {result.stderr}')
                return None
                
        except subprocess.TimeoutExpired:
            print(f'Error: {scheduler_name} execution timed out')
            return None
        except subprocess.CalledProcessError as e:
            print(f'Error running {scheduler_name}: {e}')
            return None
            
        # Read and parse the results
        if os.path.exists(result_path):
            try:
                with open(result_path, 'r') as f:
                    lines = f.readlines()
                    if not lines:
                        print(f'Error: Result file {result_path} is empty')
                        return None
                    
                    # Parse the results into a structured format
                    results = {
                        'processes': [],
                        'averages': {
                            'waiting': 0.0,
                            'turnaround': 0.0
                        }
                    }
                    
                    # Skip header and separator lines
                    for line in lines[2:]:
                        line = line.strip()
                        if not line:
                            continue
                            
                        # Check if this is an average line
                        if 'Average' in line:
                            if 'Waiting Time:' in line:
                                results['averages']['waiting'] = float(line.split(':')[1].strip())
                            elif 'Turnaround Time:' in line:
                                results['averages']['turnaround'] = float(line.split(':')[1].strip())
                            continue
                            
                        # Parse process data
                        data = line.split()
                        if len(data) >= 6:  # Make sure we have all required fields
                            try:
                                process = {
                                    'pid': data[0],
                                    'arrival': float(data[1]),
                                    'burst': float(data[2]),
                                    'completion': float(data[3]),
                                    'turnaround': float(data[4]),
                                    'waiting': float(data[5])
                                }
                                results['processes'].append(process)
                            except (ValueError, IndexError) as e:
                                print(f'Error parsing process data: {e}')
                                continue
                    
                    return results
            except IOError as e:
                print(f'Error reading result file: {e}')
                return None
        else:
            print(f'Error: Result file {result_path} not found')
            return None
            
    except Exception as e:
        print(f'Unexpected error in {scheduler_name}: {e}')
        return None

@app.route('/')
def index():
    try:
        # Get processes
        processes = read_processes()
        
        # Get the comparison image from static directory
        static_dir = os.path.join(BASE_DIR, 'static')
        comparison_path = os.path.join(static_dir, 'scheduling_comparison.png')
        has_comparison = os.path.exists(comparison_path)
            
        # Get input parameters
        input_params = read_input_params()
        
        return render_template('index.html', 
                             processes=processes,
                             input_params=input_params,
                             has_comparison=has_comparison,
                             timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"))
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('index.html', 
                             processes=[],
                             input_params=read_input_params(),
                             has_comparison=False,
                             timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"),
                             error=str(e))

@app.route('/fcfs')
def fcfs():
    try:
        processes = read_processes()
        if not processes:
            return render_template('fcfs.html', processes=[], params={}, fcfs_output=None)
            
        params = read_input_params()
        fcfs_output = run_scheduler('fcfs')

        # Copy Gantt chart to static folder
        src_path = os.path.join(BASE_DIR, 'Schedulers', 'FCFS&SRTF', 'fcfs_gantt.png')
        dst_dir = os.path.join(BASE_DIR, 'static', 'Schedulers', 'FCFS&SRTF')
        dst_path = os.path.join(dst_dir, 'fcfs_gantt.png')
        
        # Create static directory structure if it doesn't exist
        os.makedirs(dst_dir, exist_ok=True)
        
        # Copy the file if it exists
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            logger.info(f"FCFS Gantt chart copied from {src_path} to {dst_path}")
        else:
            logger.warning(f"FCFS Gantt chart not found at {src_path}")
        
        return render_template('fcfs.html', processes=processes, params=params, fcfs_output=fcfs_output)
    except Exception as e:
        logger.error(f'Error in fcfs route: {e}')
        return render_template('fcfs.html', processes=[], params={}, fcfs_output=None)

@app.route('/srtf')
def srtf():
    try:
        processes = read_processes()
        if not processes:
            return render_template('srtf.html', processes=[], params={}, srtf_output=None)
            
        params = read_input_params()
        srtf_output = run_scheduler('srtf')

        # Copy Gantt chart to static folder
        src_path = os.path.join(BASE_DIR, 'Schedulers', 'FCFS&SRTF', 'srtf_gantt.png')
        dst_dir = os.path.join(BASE_DIR, 'static', 'Schedulers', 'FCFS&SRTF')
        dst_path = os.path.join(dst_dir, 'srtf_gantt.png')
        
        # Create static directory structure if it doesn't exist
        os.makedirs(dst_dir, exist_ok=True)
        
        # Copy the file if it exists
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            logger.info(f"SRTF Gantt chart copied from {src_path} to {dst_path}")
        else:
            logger.warning(f"SRTF Gantt chart not found at {src_path}")

        return render_template('srtf.html', processes=processes, params=params, srtf_output=srtf_output)
    except Exception as e:
        logger.error(f'Error in srtf route: {e}')
        return render_template('srtf.html', processes=[], params={}, srtf_output=None)

@app.route('/priority')
def priority():
    try:
        processes = read_processes()
        if not processes:
            return render_template('priority.html', processes=[], params={}, priority_output=None)
            
        params = read_input_params()
        priority_output = run_scheduler('priority')
        return render_template('priority.html', processes=processes, params=params, priority_output=priority_output)
    except Exception as e:
        print(f'Error in priority route: {e}')
        return render_template('priority.html', processes=[], params={}, priority_output=None)

@app.route('/round-robin')
def round_robin():
    try:
        processes = read_processes()
        if not processes:
            return render_template('round_robin.html', processes=[], params={}, round_robin_output=None)
            
        params = read_input_params()
        round_robin_output = run_scheduler('round_robin')
        return render_template('round_robin.html', processes=processes, params=params, round_robin_output=round_robin_output)
    except Exception as e:
        print(f'Error in round-robin route: {e}')
        return render_template('round_robin.html', processes=[], params={}, round_robin_output=None)

@app.route('/generate', methods=['POST'])
def generate_processes():
    try:
        success = generate_new_processes()
        if not success:
            logger.error('Failed to generate new processes')
            return redirect(url_for('index'))
            
        # Run all schedulers with the new processes
        for scheduler in ['fcfs', 'srtf', 'priority', 'round_robin']:
            run_scheduler(scheduler)
            
        # Generate new comparison chart
        try:
            from Schedulers.performance_analysis import main as analyze_performance
            plot_path = analyze_performance()
            
            if not plot_path:
                logger.error('Failed to generate comparison chart')
                return redirect(url_for('index'))
                
            logger.info(f'Successfully generated comparison chart: {plot_path}')
            return redirect(url_for('index'))
            
        except ImportError as e:
            logger.error(f'Error importing performance analysis module: {e}')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f'Error in performance analysis: {e}')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f'Error in generate route: {e}')
        return redirect(url_for('index'))

def cleanup_old_comparison_files(static_dir, keep_latest=5):
    """Clean up old comparison files, keeping only the latest ones"""
    try:
        if not os.path.exists(static_dir):
            print(f"Warning: Static directory {static_dir} does not exist")
            return
            
        # Get all comparison files
        comparison_files = [f for f in os.listdir(static_dir) if f.startswith('scheduling_comparison_')]
        
        if not comparison_files:
            print("No old comparison files to clean up")
            return
            
        # Sort by creation time (newest first)
        comparison_files.sort(key=lambda x: os.path.getctime(os.path.join(static_dir, x)), reverse=True)
        
        # Remove old files
        for old_file in comparison_files[keep_latest:]:
            try:
                file_path = os.path.join(static_dir, old_file)
                os.remove(file_path)
                print(f"Removed old comparison file: {old_file}")
            except Exception as e:
                print(f"Error removing old file {old_file}: {e}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

@app.route('/compare')
def compare_algorithms():
    """Compare all scheduling algorithms"""
    try:
        # Clear matplotlib cache
        plt.close('all')
        
        # Generate the comparison plot and get the output file path
        plot_path = plot_comparison()
        
        if plot_path is None:
            logger.warning("No valid results found for comparison")
            return render_template('compare.html', 
                                processes=read_processes(),
                                input_params=read_input_params(),
                                error="No valid results found for comparison")
        
        # Get the filename from the full path
        filename = os.path.basename(plot_path)
        
        # Add timestamp to force browser refresh
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return render_template('compare.html', 
                            processes=read_processes(),
                            input_params=read_input_params(),
                            comparison_file=filename,
                            timestamp=timestamp)
                            
    except Exception as e:
        logger.error(f"Error in compare_algorithms: {e}")
        return render_template('compare.html', 
                            processes=read_processes(),
                            input_params=read_input_params(),
                            error=str(e))

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        file_path = os.path.join(BASE_DIR, 'static', filename)
        if not os.path.exists(file_path):
            return "File not found", 404
            
        response = send_file(file_path)
        # Set headers to prevent caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        return response
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}")
        return "Error serving file", 500

if __name__ == '__main__':
    try:
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Ensure required directories exist
        for dir_name in ['ProcessGeneratorModule', 'Schedulers', 'templates', 'static']:
            dir_path = os.path.join(BASE_DIR, dir_name)
            if not os.path.exists(dir_path):
                logger.warning(f"Directory {dir_path} does not exist, creating it...")
                os.makedirs(dir_path, exist_ok=True)
        
        # Run the Flask app
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Error starting the application: {e}")
        sys.exit(1)

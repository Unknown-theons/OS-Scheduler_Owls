import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import importlib.util
import time
from matplotlib.animation import FuncAnimation
from datetime import datetime
import logging

# Get the absolute path of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_dir)

# Add scheduler directories to Python path
fcfs_srtf_dir = os.path.join(current_dir, "FCFS&SRTF")
priority_rr_dir = os.path.join(current_dir, "Priority&RoundRobin")

# Add base directory to Python path
sys.path.append(base_dir)

# Import the scheduling functions
spec = importlib.util.spec_from_file_location("FCFS", os.path.join(fcfs_srtf_dir, "FCFS.py"))
FCFS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FCFS)
fcfs_schedule = FCFS.fcfs_scheduling

spec = importlib.util.spec_from_file_location("SRTF", os.path.join(fcfs_srtf_dir, "SRTF.py"))
SRTF = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SRTF)
srtf_schedule = SRTF.srtf_scheduling

spec = importlib.util.spec_from_file_location("priority", os.path.join(priority_rr_dir, "priority.py"))
priority = importlib.util.module_from_spec(spec)
spec.loader.exec_module(priority)
priority_schedule = priority.highest_priority_first

spec = importlib.util.spec_from_file_location("round_robin", os.path.join(priority_rr_dir, "round_robin.py"))
round_robin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(round_robin)
rr_schedule = round_robin.round_robin_scheduling

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = float(arrival_time)
        self.burst_time = float(burst_time)
        self.priority = int(priority)

def generate_processes(n=10):
    """Generate n random processes for testing."""
    processes = []
    for i in range(1, n + 1):
        arrival_time = np.random.uniform(0, 10)
        burst_time = np.random.uniform(1, 20)
        priority = np.random.randint(1, 5)
        processes.append(Process(f"P{i}", arrival_time, burst_time, priority))
    return processes

def run_scheduler(scheduler_func, processes):
    """
    Run a scheduler with the given processes.
    Converts processes to the format expected by each scheduler.
    """
    # Convert processes to the format expected by each scheduler
    if scheduler_func in [fcfs_schedule, srtf_schedule]:
        # FCFS and SRTF use Process objects
        process_objects = []
        for p in processes:
            if scheduler_func == srtf_schedule:
                process_obj = SRTF.Process(p.pid, p.arrival_time, p.burst_time, p.priority)
            else:
                process_obj = FCFS.Process(p.pid, p.arrival_time, p.burst_time, p.priority)
            process_objects.append(process_obj)
        return scheduler_func(process_objects)
    elif scheduler_func == rr_schedule:
        # Round Robin uses Process objects
        process_objects = []
        for p in processes:
            process_obj = round_robin.Process(p.pid, p.arrival_time, p.burst_time, p.priority)
            process_objects.append(process_obj)
        return scheduler_func(process_objects, time_quantum=4.0)
    else:
        # Priority uses dictionaries
        process_list = []
        for p in processes:
            process_dict = {
                'pid': p.pid,
                'arrival': p.arrival_time,
                'burst': p.burst_time,
                'priority': p.priority
            }
            process_list.append(process_dict)
        return scheduler_func(process_list)

def calculate_metrics_from_dict(results, scheduler_name):
    """
    Calculate performance metrics from scheduler results.
    Handles different output formats from different schedulers.
    """
    total_waiting_time = 0
    total_turnaround_time = 0
    total_response_time = 0
    
    for process in results:
        if scheduler_name in ['FCFS', 'SRTF', 'Round Robin']:
            # These schedulers use consistent key names
            total_waiting_time += process['Waiting Time']
            total_turnaround_time += process['Turnaround Time']
            if 'First Response' in process:
                total_response_time += process['First Response'] - process['Arrival Time']
            else:
                total_response_time += process['Waiting Time']  # Approximation
        elif scheduler_name == 'Priority':
            # Priority scheduler uses different key names
            total_waiting_time += process['waiting_time']
            total_turnaround_time += process['turnaround_time']
            if 'start_time' in process and process['start_time'] != -1:
                total_response_time += process['start_time'] - process['arrival']
            else:
                total_response_time += process['waiting_time']  # Approximation
    
    n = len(results)
    return {
        'avg_waiting_time': total_waiting_time / n,
        'avg_turnaround_time': total_turnaround_time / n,
        'avg_response_time': total_response_time / n
    }

def compare_algorithms(processes):
    """Compare all scheduling algorithms with the same set of processes."""
    schedulers = {
        'FCFS': fcfs_schedule,
        'SRTF': srtf_schedule,
        'Priority': priority_schedule,
        'Round Robin': rr_schedule
    }
    
    results = {}
    for name, scheduler in schedulers.items():
        start_time = time.time()
        scheduled_results = run_scheduler(scheduler, processes)
        execution_time = time.time() - start_time
        
        metrics = calculate_metrics_from_dict(scheduled_results, name)
        metrics['execution_time'] = execution_time
        results[name] = metrics
    
    return results

def plot_comparison():
    """Create a real-time comparison of scheduling algorithms"""
    fig = None
    try:
        # Get the base directory path
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Define result files with absolute paths
        result_files = {
            'FCFS': os.path.join(BASE_DIR, 'Schedulers', 'FCFS&SRTF', 'fcfs_results.txt'),
            'SRTF': os.path.join(BASE_DIR, 'Schedulers', 'FCFS&SRTF', 'srtf_results.txt'),
            'Priority': os.path.join(BASE_DIR, 'Schedulers', 'Priority&RoundRobin', 'priority_results.txt'),
            'Round Robin': os.path.join(BASE_DIR, 'Schedulers', 'Priority&RoundRobin', 'round_robin_results.txt')
        }
        
        # Read results from all files
        results = {}
        for name, file in result_files.items():
            try:
                if not os.path.exists(file):
                    logger.warning(f"Result file {file} does not exist")
                    continue
                results[name] = read_scheduler_results(file)
            except Exception as e:
                logger.error(f"Error reading results for {name}: {e}")
                results[name] = None
        
        # Filter out None results
        valid_results = {k: v for k, v in results.items() if v is not None}
        if not valid_results:
            logger.error("No valid results found for any algorithm")
            return None
        
        # Set style for better web display
        plt.style.use('ggplot')
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot average waiting times
        algorithms = list(valid_results.keys())
        avg_waiting = [valid_results[algo]['avg_waiting'] for algo in algorithms]
        avg_turnaround = [valid_results[algo]['avg_turnaround'] for algo in algorithms]
        
        # Bar width
        width = 0.35
        
        # Plot waiting times
        bars1 = ax1.bar(algorithms, avg_waiting, width, color='#3498db', label='Average Waiting Time')
        ax1.set_ylabel('Time', fontsize=12)
        ax1.set_title('Comparison of Average Waiting Times', fontsize=14, pad=20)
        ax1.bar_label(bars1, padding=3, fontsize=10, fmt='%.1f')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Plot turnaround times
        bars2 = ax2.bar(algorithms, avg_turnaround, width, color='#2ecc71', label='Average Turnaround Time')
        ax2.set_ylabel('Time', fontsize=12)
        ax2.set_title('Comparison of Average Turnaround Times', fontsize=14, pad=20)
        ax2.bar_label(bars2, padding=3, fontsize=10, fmt='%.1f')
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Add process details
        process_details = []
        for algo in algorithms:
            if valid_results[algo]:
                process_details.append(f"{algo}: {valid_results[algo]['process_count']} processes")
        
        # Add process details to the plot
        plt.figtext(0.5, 0.01, '\n'.join(process_details), ha='center', fontsize=10, 
                   bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8))
        
        # Add timestamp to the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.figtext(0.5, 0.95, f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                    ha='center', fontsize=10, bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8))
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the figure with a timestamp in the filename
        output_file = os.path.join(BASE_DIR, f'scheduling_comparison_{timestamp}.png')
        plt.savefig(output_file, bbox_inches='tight', dpi=100)
        plt.close(fig)
        
        logger.info(f"Comparison plot saved to {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Error creating comparison plot: {e}")
        if fig:
            plt.close(fig)
        return None

def analyze_performance():
    """
    Main function to analyze performance of all schedulers.
    """
    # Read processes from processes.txt instead of generating random ones
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ProcessGeneratorModule", "processes.txt")
    processes = []
    try:
        with open(file_path, 'r') as file:
            # Skip the header line
            next(file)
            # Read each process
            for line in file:
                # Split by whitespace and remove empty strings
                data = [x for x in line.strip().split() if x]
                if len(data) >= 4:
                    pid = data[0]
                    arrival_time = float(data[1])
                    burst_time = float(data[2])
                    priority = int(data[3])
                    processes.append(Process(pid, arrival_time, burst_time, priority))
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

    # Compare algorithms with the actual processes
    results = compare_algorithms(processes)
    
    # Plot comparison
    plot_path = plot_comparison()
    
    return results, plot_path

if __name__ == "__main__":
    # Run performance analysis
    results, plot_path = analyze_performance()
    if results:
        print(f"\nComparison chart saved to: {plot_path}")
    else:
        print("Performance analysis failed.")


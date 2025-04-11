import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import importlib.util
import time
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        self.remaining_time = float(burst_time)
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.first_response = -1

def read_processes(file_path):
    """Read processes from the processes.txt file."""
    processes = []
    try:
        logger.info(f"Reading processes from {file_path}")
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
                    logger.info(f"Read process: {pid}, arrival: {arrival_time}, burst: {burst_time}, priority: {priority}")
    except FileNotFoundError:
        logger.error(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        logger.error(f"Error reading processes: {e}")
        return []
    return processes

def run_scheduler(processes, scheduler_name):
    """Run a specific scheduler and return its results."""
    try:
        logger.info(f"Running {scheduler_name} scheduler with {len(processes)} processes")
        if scheduler_name == 'FCFS':
            # Convert Process objects to dictionary format
            fcfs_processes = []
            for p in processes:
                fcfs_processes.append({
                    'pid': p.pid,
                    'arrival': p.arrival_time,
                    'burst': p.burst_time,
                    'remaining': p.burst_time,
                    'completion': 0,
                    'waiting': 0,
                    'turnaround': 0,
                    'response': -1
                })
            return fcfs_schedule(fcfs_processes)
        elif scheduler_name == 'SRTF':
            # Convert Process objects to dictionary format
            srtf_processes = []
            for p in processes:
                srtf_processes.append({
                    'pid': p.pid,
                    'arrival': p.arrival_time,
                    'burst': p.burst_time,
                    'remaining': p.burst_time,
                    'completion': 0,
                    'waiting': 0,
                    'turnaround': 0,
                    'response': -1
                })
            return srtf_schedule(srtf_processes)
        elif scheduler_name == 'Priority':
            # Convert processes to the format expected by priority_schedule
            priority_processes = []
            for p in processes:
                priority_processes.append({
                    'pid': p.pid,
                    'arrival': p.arrival_time,
                    'burst': p.burst_time,
                    'priority': p.priority
                })
            results = priority_schedule(priority_processes)
            # Convert results to match the format of other schedulers
            formatted_results = []
            for r in results:
                formatted_results.append({
                    'Process ID': r['pid'],
                    'Arrival Time': r['arrival'],
                    'Burst Time': r['burst'],
                    'Completion Time': r['finish_time'],
                    'Turnaround Time': r['turnaround_time'],
                    'Waiting Time': r['waiting_time'],
                    'First Response': r['start_time'] if 'start_time' in r else r['arrival']
                })
            return formatted_results
        elif scheduler_name == 'Round Robin':
            return rr_schedule(processes)
        else:
            logger.error(f"Unknown scheduler: {scheduler_name}")
            return None
    except Exception as e:
        logger.error(f"Error running {scheduler_name}: {e}")
        return None

def calculate_metrics_from_dict(results):
    """Calculate performance metrics from scheduler results."""
    if not results:
        logger.warning("No results to calculate metrics from")
        return None
        
    total_waiting = 0
    total_turnaround = 0
    total_response = 0
    count = 0
    
    # Handle FCFS and SRTF format
    if isinstance(results, dict) and 'processes' in results and 'averages' in results:
        return {
            'avg_waiting': results['averages']['waiting'],
            'avg_turnaround': results['averages']['turnaround'],
            'avg_response': results['averages']['response']
        }
    
    # Handle Priority and Round Robin format
    for process in results:
        if isinstance(process, dict):
            total_waiting += process.get('Waiting Time', 0)
            total_turnaround += process.get('Turnaround Time', 0)
            total_response += process.get('First Response', 0)
            count += 1
    
    if count == 0:
        logger.warning("No valid processes found in results")
        return None
        
    metrics = {
        'avg_waiting': total_waiting / count,
        'avg_turnaround': total_turnaround / count,
        'avg_response': total_response / count
    }
    logger.info(f"Calculated metrics: {metrics}")
    return metrics

def compare_algorithms(processes):
    """Compare all scheduling algorithms using the same set of processes."""
    schedulers = ['FCFS', 'SRTF', 'Priority', 'Round Robin']
    results = {}
    
    for scheduler in schedulers:
        logger.info(f"\nRunning {scheduler} scheduler...")
        scheduler_results = run_scheduler(processes, scheduler)
        if scheduler_results:
            metrics = calculate_metrics_from_dict(scheduler_results)
            if metrics:
                results[scheduler] = metrics
                logger.info(f"{scheduler} Results:")
                logger.info(f"Average Waiting Time: {metrics['avg_waiting']:.2f}")
                logger.info(f"Average Turnaround Time: {metrics['avg_turnaround']:.2f}")
                logger.info(f"Average Response Time: {metrics['avg_response']:.2f}")
            else:
                logger.warning(f"Could not calculate metrics for {scheduler}")
        else:
            logger.warning(f"No results returned for {scheduler}")
    
    return results

def read_scheduler_results(file_path):
    """Read and parse scheduler results from a file."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
        # Skip header and separator lines
        process_lines = [line for line in lines if line.strip() and not line.startswith('Process ID') and not line.startswith('-')]
        
        # Find the line with average values
        avg_line = None
        for line in lines:
            if 'Average' in line:
                avg_line = line
                break
        
        if not avg_line:
            logger.error(f"No average values found in {file_path}")
            return None
            
        # Extract average values
        avg_waiting = float(avg_line.split('Average Waiting Time:')[1].split()[0])
        avg_turnaround = float(avg_line.split('Average Turnaround Time:')[1].split()[0])
        
        results = {
            'process_count': len(process_lines),
            'avg_waiting': avg_waiting,
            'avg_turnaround': avg_turnaround
        }
        
        return results
    except Exception as e:
        logger.error(f"Error reading results from {file_path}: {e}")
        return None

def plot_comparison():
    """Create a real-time comparison of scheduling algorithms."""
    # Use Agg backend to avoid threading issues
    matplotlib.use('Agg')
    
    # Delete old comparison plots
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    os.makedirs(static_dir, exist_ok=True)
    for file in os.listdir(static_dir):
        if file.startswith('scheduling_comparison'):
            try:
                os.remove(os.path.join(static_dir, file))
            except:
                pass
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Read results from all scheduler files using absolute paths
    fcfs_results = read_scheduler_results(os.path.join(current_dir, 'FCFS&SRTF', 'fcfs_results.txt'))
    srtf_results = read_scheduler_results(os.path.join(current_dir, 'FCFS&SRTF', 'srtf_results.txt'))
    priority_results = read_scheduler_results(os.path.join(current_dir, 'Priority&RoundRobin', 'priority_results.txt'))
    round_robin_results = read_scheduler_results(os.path.join(current_dir, 'Priority&RoundRobin', 'round_robin_results.txt'))

    # Extract metrics
    metrics = {
        'FCFS': fcfs_results,
        'SRTF': srtf_results,
        'Priority': priority_results,
        'Round Robin': round_robin_results
    }

    # Create figure and subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Scheduling Algorithm Comparison', fontsize=16, y=1.05)

    # Define colors for each algorithm
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f']

    # Prepare data
    algorithms = list(metrics.keys())
    x = np.arange(len(algorithms))
    width = 0.35

    # Plot waiting times
    waiting_times = [metrics[algo]['avg_waiting'] for algo in algorithms]
    turnaround_times = [metrics[algo]['avg_turnaround'] for algo in algorithms]
    response_times = [metrics[algo].get('avg_response', 0) for algo in algorithms]

    # Plot Average Waiting Time
    bars1 = ax1.bar(x, waiting_times, width, color=colors)
    ax1.set_title('Average Waiting Time')
    ax1.set_xticks(x)
    ax1.set_xticklabels(algorithms, rotation=45)
    ax1.grid(True, linestyle='--', alpha=0.7)
    # Add values on top of bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom')

    # Plot Average Turnaround Time
    bars2 = ax2.bar(x, turnaround_times, width, color=colors)
    ax2.set_title('Average Turnaround Time')
    ax2.set_xticks(x)
    ax2.set_xticklabels(algorithms, rotation=45)
    ax2.grid(True, linestyle='--', alpha=0.7)
    # Add values on top of bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom')

    # Plot Average Response Time
    bars3 = ax3.bar(x, response_times, width, color=colors)
    ax3.set_title('Average Response Time')
    ax3.set_xticks(x)
    ax3.set_xticklabels(algorithms, rotation=45)
    ax3.grid(True, linestyle='--', alpha=0.7)
    # Add values on top of bars
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom')

    # Adjust layout
    plt.tight_layout()
    
    # Save the plot with fixed filename
    plot_path = os.path.join(static_dir, 'scheduling_comparison.png')
    plt.savefig(plot_path, bbox_inches='tight', dpi=100)
    plt.close('all')  # Close all figures to prevent memory leaks
    
    logger.info(f"Comparison plot saved to: {plot_path}")
    return plot_path

def analyze_performance():
    """
    Main function to analyze performance of all schedulers.
    """
    try:
        # Create static directory if it doesn't exist
        static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
        os.makedirs(static_dir, exist_ok=True)
        
        # Delete old comparison plots
        for file in os.listdir(static_dir):
            if file.startswith('scheduling_comparison'):
                try:
                    os.remove(os.path.join(static_dir, file))
                except:
                    pass
        
        # Generate comparison plot with fixed filename
        plot_path = os.path.join('static', 'scheduling_comparison.png')
        if not plot_path:
            logger.error("Failed to generate comparison plot")
            return None, None
            
        return None, plot_path
        
    except Exception as e:
        logger.error(f"Error in performance analysis: {e}")
        return None, None

def main():
    # Get the base directory path
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path to the processes.txt file
    file_path = os.path.join(base_dir, "ProcessGeneratorModule", "processes.txt")
    
    # Read processes from file
    processes = read_processes(file_path)
    if not processes:
        logger.error("No processes found in the input file")
        return
    
    # Compare algorithms and get results
    results = compare_algorithms(processes)
    if not results:
        logger.error("Failed to compare algorithms")
        return
    
    # Create comparison plot
    logger.info("Creating comparison plot")
    try:
        # Create static directory if it doesn't exist
        static_dir = os.path.join(base_dir, "static")
        os.makedirs(static_dir, exist_ok=True)
        
        # Delete old comparison plots
        for file in os.listdir(static_dir):
            if file.startswith('scheduling_comparison'):
                try:
                    os.remove(os.path.join(static_dir, file))
                except:
                    pass
        
        # Use fixed filename for the plot
        plot_path = os.path.join(static_dir, "scheduling_comparison.png")
        
        # Create the plot
        plt.figure(figsize=(12, 5))
        
        # Create two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Scheduling Algorithm Comparison', fontsize=16, y=1.05)
        
        # Define colors for each algorithm
        colors = ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f']
        
        # Plot data
        algorithms = list(results.keys())
        x = np.arange(len(algorithms))
        width = 0.35
        
        # Get metrics
        waiting_times = [results[algo]['avg_waiting'] for algo in algorithms]
        turnaround_times = [results[algo]['avg_turnaround'] for algo in algorithms]
        
        # Plot Average Waiting Time
        bars1 = ax1.bar(x, waiting_times, width, color=colors)
        ax1.set_title('Average Waiting Time')
        ax1.set_xticks(x)
        ax1.set_xticklabels(algorithms, rotation=45)
        ax1.grid(True, linestyle='--', alpha=0.7)
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom')
        
        # Plot Average Turnaround Time
        bars2 = ax2.bar(x, turnaround_times, width, color=colors)
        ax2.set_title('Average Turnaround Time')
        ax2.set_xticks(x)
        ax2.set_xticklabels(algorithms, rotation=45)
        ax2.grid(True, linestyle='--', alpha=0.7)
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(plot_path, bbox_inches='tight', dpi=100)
        plt.close('all')
        
        logger.info(f"Comparison plot saved to: {plot_path}")
        return plot_path
        
    except Exception as e:
        logger.error(f"Error creating comparison plot: {e}")
        return None

if __name__ == "__main__":
    main() 
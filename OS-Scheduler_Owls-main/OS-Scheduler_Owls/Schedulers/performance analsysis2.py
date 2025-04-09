import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import importlib.util
import time
from matplotlib.animation import FuncAnimation

# Add scheduler directories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
fcfs_srtf_dir = os.path.join(current_dir, "FCFS&SRTF")
priority_rr_dir = os.path.join(current_dir, "Priority&RoundRobin")
# We'll still use importlib for everything that isn't a clean module name
sys.path.append(fcfs_srtf_dir)

# Import the scheduling functions from clean‑named files
spec = importlib.util.spec_from_file_location("FCFS", os.path.join(fcfs_srtf_dir, "FCFS.py"))
FCFS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FCFS)
fcfs_schedule = FCFS.fcfs_scheduling

spec = importlib.util.spec_from_file_location("SRTF", os.path.join(fcfs_srtf_dir, "SRTF.py"))
SRTF = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SRTF)
srtf_schedule = SRTF.srtf_scheduling

# Import modules with special‑character filenames
periority_path   = os.path.join(priority_rr_dir, "periority.py")
round_robin_path = os.path.join(priority_rr_dir, "round robin.py")

spec = importlib.util.spec_from_file_location("periority", periority_path)
periority = importlib.util.module_from_spec(spec)
spec.loader.exec_module(periority)
priority_schedule = periority.highest_priority_first

spec = importlib.util.spec_from_file_location("round_robin", round_robin_path)
round_robin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(round_robin)
rr_schedule = round_robin.round_robin_scheduling

# … rest of your code unchanged …
class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = float(arrival_time)
        self.burst_time = float(burst_time)
        self.priority = int(priority)
        self.remaining_time = float(burst_time)
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.start_time = -1
        self.response_time = 0
        self.executed = False
        self.in_queue = False

def generate_processes(n=10):
    processes = []
    for i in range(n):
        arrival_time = np.random.randint(0, 10)
        burst_time = np.random.randint(1, 20)
        priority = np.random.randint(1, 5)
        processes.append(Process(i+1, arrival_time, burst_time, priority))
    return processes

def calculate_metrics_from_dict(results, scheduler_name):
    total_waiting_time = 0
    total_turnaround_time = 0
    total_response_time = 0
    
    for process in results:
        if scheduler_name == 'FCFS' or scheduler_name == 'SRTF':
            # FCFS and SRTF use these keys
            total_waiting_time += process['Waiting Time']
            total_turnaround_time += process['Turnaround Time']
            total_response_time += process['Waiting Time']  # Using waiting time as approximation
        elif scheduler_name == 'Priority':
            # Priority scheduler uses these keys
            total_waiting_time += process['waiting_time']
            total_turnaround_time += process['turnaround_time']
            total_response_time += process['waiting_time']
        elif scheduler_name == 'Round Robin':
            # Round Robin uses these keys
            total_waiting_time += process['waiting']
            total_turnaround_time += process['turnaround']
            total_response_time += process['waiting']
    
    n = len(results)
    return {
        'avg_waiting_time': total_waiting_time / n,
        'avg_turnaround_time': total_turnaround_time / n,
        'avg_response_time': total_response_time / n
    }

def run_scheduler(scheduler_func, processes):
    # For FCFS and SRTF, we need to convert to their Process class
    if scheduler_func in [fcfs_schedule, srtf_schedule]:
        process_objects = []
        for p in processes:
            if scheduler_func == srtf_schedule:
                # Use SRTF's Process class for SRTF scheduler
                process_obj = SRTF.Process(p.pid, p.arrival_time, p.burst_time, p.priority)
            else:
                # Use FCFS's Process class for FCFS scheduler
                process_obj = FCFS.Process(p.pid, p.arrival_time, p.burst_time, p.priority)
            process_objects.append(process_obj)
        return scheduler_func(process_objects)
    else:
        # For Priority and Round Robin, convert to dictionary format
        process_list = []
        for p in processes:
            if scheduler_func == priority_schedule:
                # Priority scheduler expects different keys
                process_list.append({
                    'pid': p.pid,
                    'arrival': p.arrival_time,
                    'burst': p.burst_time,
                    'priority': p.priority
                })
            else:
                # Round Robin uses the same format as before
                process_list.append({
                    'id': p.pid,
                    'arrival': p.arrival_time,
                    'burst': p.burst_time,
                    'priority': p.priority
                })
        if scheduler_func == rr_schedule:
            # Round Robin needs a quantum parameter
            return scheduler_func(process_list, quantum=2.0)
        return scheduler_func(process_list)

def compare_algorithms(processes):
    results = {}
    
    # Run each scheduler
    schedulers = {
        'FCFS': fcfs_schedule,
        'SRTF': srtf_schedule,
        'Priority': priority_schedule,
        'Round Robin': rr_schedule
    }
    
    for name, scheduler in schedulers.items():
        start_time = time.time()
        scheduled_results = run_scheduler(scheduler, processes)
        execution_time = time.time() - start_time
        metrics = calculate_metrics_from_dict(scheduled_results, name)
        metrics['execution_time'] = execution_time
        results[name] = metrics
    
    return results

def plot_comparison(results):
    metrics = ['avg_waiting_time', 'avg_turnaround_time']  # Only these two metrics
    algorithms = list(results.keys())
    
    # Define a set of distinct colors for the bars
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']  # Different colors for each algorithm
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))  # Changed to 1 row, 2 columns
    axes = axes.flatten()
    
    for i, metric in enumerate(metrics):
        values = [results[algo][metric] for algo in algorithms]
        bars = axes[i].bar(algorithms, values, color=colors)
        axes[i].set_title(f'{metric.replace("_", " ").title()}')
        axes[i].set_ylabel('Time (ms)')
        
        # Add value labels on top of each bar
        for bar in bars:
            height = bar.get_height()
            axes[i].text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}',
                        ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()

def analyze_performance():
    # Generate random processes
    processes = generate_processes(10)
    
    # Compare algorithms
    results = compare_algorithms(processes)
    
    # Plot results
    plot_comparison(results)
    
    # Print detailed results
    print("\nDetailed Performance Analysis:")
    for algo, metrics in results.items():
        print(f"\n{algo}:")
        for metric, value in metrics.items():
            print(f"{metric.replace('_', ' ').title()}: {value:.2f}")

if __name__ == "__main__":
    analyze_performance()

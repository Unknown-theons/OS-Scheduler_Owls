import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = float(arrival_time)
        self.burst_time = float(burst_time)
        self.priority = int(priority)
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0

def read_processes(file_path):
    """Read processes from the processes.txt file."""
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
                    processes.append({
                        'pid': pid,
                        'arrival': arrival_time,
                        'burst': burst_time,
                        'remaining': burst_time,
                        'completion': 0,
                        'waiting': 0,
                        'turnaround': 0,
                        'response': -1
                    })
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    return processes

def create_gantt_chart(execution_history, processes):
    """Create a Gantt chart for the FCFS scheduling."""
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Get unique process IDs and create a mapping to y-positions
    process_ids = sorted(set(h['pid'] for h in execution_history))
    y_pos = {pid: i for i, pid in enumerate(process_ids)}
    
    # Create a color map for processes
    colors = plt.cm.tab10(np.linspace(0, 1, len(process_ids)))
    color_map = {pid: colors[i] for i, pid in enumerate(process_ids)}
    
    # Plot each execution block
    for exec_slice in execution_history:
        pid = exec_slice['pid']
        start = exec_slice['start']
        end = exec_slice['end']
        duration = end - start
        
        # Create the bar
        ax.barh(y_pos[pid], duration, left=start, height=0.6, 
                color=color_map[pid], edgecolor='black', linewidth=1)
        
        # Add text labels
        ax.text(start + duration/2, y_pos[pid], f'P{pid}',
                ha='center', va='center', color='white')
    
    # Customize the plot
    ax.set_yticks([y_pos[pid] for pid in process_ids])
    ax.set_yticklabels([f'P{pid}' for pid in process_ids])
    ax.set_xlabel('Time')
    ax.set_title('FCFS Scheduling Gantt Chart')
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)
    
    # Add process legend
    handles = [plt.Rectangle((0,0),1,1, color=color_map[pid]) 
              for pid in process_ids]
    ax.legend(handles, [f'P{pid}' for pid in process_ids],
             title='Processes', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the chart
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    chart_path = os.path.join(base_dir, 'Schedulers', 'FCFS&SRTF', 'fcfs_gantt.png')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    
    # Save the chart
    plt.savefig(chart_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return chart_path

def fcfs_scheduling(processes):
    """
    Implement First Come First Serve (FCFS) scheduling algorithm.
    - Processes are executed in order of arrival
    - Non-preemptive: Once a process starts, it runs to completion
    """
    if not processes:
        return []

    # Sort processes by arrival time
    processes.sort(key=lambda x: x['arrival'])
    current_time = processes[0]['arrival']
    completed = []
    execution_history = []
    
    print("\nFCFS Scheduling Execution Sequence:")
    print("=" * 80)
    
    for process in processes:
        # Track first response time
        if process['response'] == -1:
            process['response'] = current_time
            print(f"Time {current_time:.1f}: Process {process['pid']} starts execution")
        
        # Calculate execution time
        execution_time = process['burst']
        execution_end = current_time + execution_time
        
        # Record execution
        execution_history.append({
            'pid': process['pid'],
            'start': current_time,
            'end': execution_end
        })
        
        print(f"Time {current_time:.1f}-{execution_end:.1f}: Executing {process['pid']}")
        
        # Update process state
        process['completion'] = execution_end
        process['turnaround'] = execution_end - process['arrival']
        process['waiting'] = process['turnaround'] - process['burst']
        completed.append(process)
        current_time = execution_end
        
        print(f"Time {current_time:.1f}: Process {process['pid']} completed")
    
    print("=" * 80)
    
    # Create Gantt chart
    create_gantt_chart(execution_history, completed)
    
    # Calculate averages
    total_waiting = sum(p['waiting'] for p in completed)
    total_turnaround = sum(p['turnaround'] for p in completed)
    total_response = sum(p['response'] - p['arrival'] for p in completed)
    n = len(completed)
    
    return {
        'processes': completed,
        'averages': {
            'waiting': total_waiting / n if n > 0 else 0,
            'turnaround': total_turnaround / n if n > 0 else 0,
            'response': total_response / n if n > 0 else 0
        }
    }

def print_results(results):
    """Print the scheduling results in a formatted manner."""
    if not results:
        print("No processes to schedule.")
        return

    # Write results to file
    try:
        # Get the base directory path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        result_path = os.path.join(base_dir, 'Schedulers', 'FCFS&SRTF', 'fcfs_results.txt')
        
        with open(result_path, 'w') as f:
            # Write header
            f.write(f"{'Process ID':<12} {'Arrival Time':<14} {'Burst Time':<12} {'Completion':<12} "
                f"{'Turnaround':<12} {'Waiting':<12}\n")
            f.write("-" * 100 + "\n")
            
            # Write process data
            for process in results['processes']:
                f.write(f"{process['pid']:<12} {process['arrival']:<14.2f} {process['burst']:<12.2f} "
                    f"{process['completion']:<12.2f} {process['turnaround']:<12.2f} "
                    f"{process['waiting']:<12.2f}\n")
            
            # Write averages
            f.write("\nAverage Waiting Time: {:.2f}\n".format(results['averages']['waiting']))
            f.write("Average Turnaround Time: {:.2f}\n".format(results['averages']['turnaround']))
            
        print(f"Results written to {result_path}")
    except Exception as e:
        print(f"Error writing results to file: {e}")

def main():
    # Get the base directory path
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Path to the processes.txt file
    file_path = os.path.join(base_dir, "ProcessGeneratorModule", "processes.txt")
    
    # Read processes from file
    processes = read_processes(file_path)
    
    # Run FCFS scheduling
    print("\nRunning FCFS Scheduling...")
    results = fcfs_scheduling(processes)
    
    # Print and save results
    if results['processes']:
        print_results(results)
    else:
        print("No processes to schedule.")

if __name__ == "__main__":
    main()
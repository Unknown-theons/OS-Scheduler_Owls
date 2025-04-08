import os

def read_processes(filename):
    """
    Reads process data from a text file.
    Assumes the file has a header and columns:
    Process ID, Arrival Time, Burst Time, Priority.
    """
    processes = []
    with open(filename, 'r') as file:
        # Read all lines and skip header
        lines = file.readlines()[1:]
        for line in lines:
            # Skip empty lines
            if line.strip():
                parts = line.split()
                process = {
                    'id': parts[0],
                    'arrival': float(parts[1]),
                    'burst': float(parts[2]),
                    'priority': int(parts[3])
                }
                processes.append(process)
    return processes

def round_robin_scheduling(processes, quantum=4):
    """
    Simulates Round Robin Scheduling considering arrival times.
    Returns list of processes with their timing information.
    """
    n = len(processes)
    # Create a copy of processes to not modify original data
    rr_processes = []
    for p in processes:
        rr_processes.append({
            'id': p['id'],
            'arrival': p['arrival'],
            'burst': p['burst'],
            'priority': p['priority'],
            'remaining': p['burst'],  # Remaining burst time
            'completion': 0,  # Completion time
            'turnaround': 0,  # Turnaround time
            'waiting': 0  # Waiting time
        })
    
    current_time = min(p['arrival'] for p in rr_processes)
    completed = 0
    
    # Keep track of when each process last executed
    last_execution = {p['id']: p['arrival'] for p in rr_processes}
    
    while completed < n:
        # Find the next process to execute
        executed = False
        for process in rr_processes:
            if process['remaining'] > 0 and process['arrival'] <= current_time:
                executed = True
                
                # Calculate waiting time since last execution
                wait_since_last = current_time - last_execution[process['id']]
                if wait_since_last > 0:
                    process['waiting'] += wait_since_last
                
                # Execute for quantum time or remaining time
                execution_time = min(quantum, process['remaining'])
                current_time += execution_time
                process['remaining'] -= execution_time
                last_execution[process['id']] = current_time
                
                # If process completes
                if process['remaining'] == 0:
                    process['completion'] = current_time
                    process['turnaround'] = process['completion'] - process['arrival']
                    completed += 1
                break
        
        # If no process was executed, move time forward
        if not executed:
            current_time += 1
    
    return rr_processes

def save_results_to_file(processes, output_path):
    """Save Round Robin scheduling results to a file"""
    # Calculate averages
    n = len(processes)
    avg_waiting = sum(p['waiting'] for p in processes) / n
    avg_turnaround = sum(p['turnaround'] for p in processes) / n
    
    with open(output_path, 'w') as file:
        # Write header
        header = "Process Arrival   Burst   Priority  Completion  Waiting   Turnaround"
        file.write(header + "\n")
        file.write("-" * len(header) + "\n")
        
        # Write process data
        for process in processes:
            file.write(f"{process['id']:<8}{process['arrival']:<10.2f}{process['burst']:<8.2f}"
                      f"{process['priority']:<10}{process['completion']:<11.2f}"
                      f"{process['waiting']:<10.2f}{process['turnaround']:<10.2f}\n")
        
        # Write averages
        file.write(f"\nAverage Waiting Time: {avg_waiting:.2f}\n")
        file.write(f"Average Turnaround Time: {avg_turnaround:.2f}\n")

def print_results(processes):
    """Print scheduling results to console"""
    header = "Process Arrival   Burst   Priority  Completion  Waiting   Turnaround"
    print(header)
    print("-" * len(header))
    for proc in processes:
        print(f"{proc['id']:<8}{proc['arrival']:<10.2f}{proc['burst']:<8.2f}"
              f"{proc['priority']:<10}{proc['completion']:<11.2f}"
              f"{proc['waiting']:<10.2f}{proc['turnaround']:<10.2f}")

if __name__ == '__main__':
    # File paths
    input_path = os.path.join(os.path.dirname(__file__), "..", "ProcessGeneratorModule", "processes.txt")
    output_path = os.path.join(os.path.dirname(__file__), "..", "ProcessGeneratorModule", "round_robin_results.txt")
    
    # Read processes
    processes = read_processes(input_path)
    
    # Run Round Robin scheduling
    quantum = 4  # Time quantum for Round Robin
    scheduled_processes = round_robin_scheduling(processes, quantum)
    
    # Save and print results
    save_results_to_file(scheduled_processes, output_path)
    print_results(scheduled_processes)
    
    # Print averages
    n = len(scheduled_processes)
    avg_waiting = sum(p['waiting'] for p in scheduled_processes) / n
    avg_turnaround = sum(p['turnaround'] for p in scheduled_processes) / n
    print(f"\nAverage Waiting Time: {avg_waiting:.2f}")
    print(f"Average Turnaround Time: {avg_turnaround:.2f}")
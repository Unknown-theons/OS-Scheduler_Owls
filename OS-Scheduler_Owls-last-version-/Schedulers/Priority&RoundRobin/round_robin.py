import os

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
                    priority = int(data[3])
                    processes.append(Process(pid, arrival_time, burst_time, priority))
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    return processes

def round_robin_scheduling(processes, time_quantum=4.0):
    """
    Implement Round Robin scheduling algorithm.
    - Each process gets a fixed time quantum (4.0 units)
    - Processes are executed in FIFO order
    - If a process is not completed, it goes to the back of the queue
    - Context switching happens after each quantum or when process completes
    """
    if not processes:
        return []

    # Create working copies of processes
    process_list = []
    for p in processes:
        process_list.append({
            'pid': p.pid,
            'arrival': p.arrival_time,
            'burst': p.burst_time,
            'remaining': p.burst_time,
            'completion': 0,
            'first_response': -1,  # Track when process first gets CPU
            'last_execution': 0
        })

    # Sort processes by arrival time
    process_list.sort(key=lambda x: x['arrival'])
    
    current_time = process_list[0]['arrival']  # Start with first arrival
    completed = []
    ready_queue = []
    execution_history = []
    
    print("\nRound Robin Execution Sequence (Quantum = 4.0):")
    print("=" * 80)
    
    while process_list or ready_queue:
        # Add newly arrived processes to ready queue
        while process_list and process_list[0]['arrival'] <= current_time:
            new_process = process_list.pop(0)
            ready_queue.append(new_process)
            print(f"Time {current_time:.1f}: Process {new_process['pid']} arrived")
            
        if not ready_queue:
            if process_list:
                current_time = process_list[0]['arrival']
                continue
            break
            
        # Get next process from front of queue (FIFO)
        current_process = ready_queue.pop(0)
        
        # Track first response time
        if current_process['first_response'] == -1:
            current_process['first_response'] = current_time
            print(f"Time {current_time:.1f}: Process {current_process['pid']} gets CPU first time")
        
        # Calculate execution time for this quantum
        execution_time = min(time_quantum, current_process['remaining'])
        execution_end = current_time + execution_time
        
        # Record execution slice
        execution_history.append({
            'pid': current_process['pid'],
            'start': current_time,
            'end': execution_end
        })
        
        print(f"Time {current_time:.1f}-{execution_end:.1f}: Executing {current_process['pid']} "
              f"(Remaining: {current_process['remaining']:.1f})")
        
        # Update process state
        current_process['remaining'] -= execution_time
        current_time = execution_end
        
        # Add newly arrived processes before handling current process completion
        while process_list and process_list[0]['arrival'] <= current_time:
            new_process = process_list.pop(0)
            ready_queue.append(new_process)
            print(f"Time {current_time:.1f}: Process {new_process['pid']} arrived")
        
        # Handle process completion or re-queue
        if current_process['remaining'] <= 0:
            current_process['completion'] = current_time
            completed.append(current_process)
            print(f"Time {current_time:.1f}: Process {current_process['pid']} completed")
        else:
            # Process used its quantum but didn't complete, add to back of queue
            ready_queue.append(current_process)
            print(f"Time {current_time:.1f}: Process {current_process['pid']} back to queue")
    
    print("=" * 80)
    
    # Calculate timing metrics
    results = []
    for process in completed:
        # Get all execution slices for this process
        process_executions = [e for e in execution_history if e['pid'] == process['pid']]
        
        # Calculate waiting time (time spent not executing)
        waiting_time = 0
        last_end = process['arrival']
        for exec_slice in process_executions:
            waiting_time += exec_slice['start'] - last_end
            last_end = exec_slice['end']
        
        turnaround_time = process['completion'] - process['arrival']
        
        results.append({
            "Process ID": process['pid'],
            "Arrival Time": process['arrival'],
            "Burst Time": process['burst'],
            "Completion Time": process['completion'],
            "Turnaround Time": turnaround_time,
            "Waiting Time": waiting_time,
            "First Response": process['first_response']
        })
    
    return sorted(results, key=lambda x: x["Process ID"])

def print_results(results):
    """Print the scheduling results in a formatted manner."""
    if not results:
        print("No processes to schedule.")
        return

    print("\nRound Robin Scheduling Results:")
    print("=" * 100)
    print(f"{'Process ID':<12} {'Arrival Time':<14} {'Burst Time':<12} {'Completion':<12} "
        f"{'Turnaround':<12} {'Waiting':<12} {'First Response':<12}")
    print("-" * 100)
    
    total_waiting = 0
    total_turnaround = 0
    
    for process in results:
        print(f"{process['Process ID']:<12} {process['Arrival Time']:<14.2f} {process['Burst Time']:<12.2f} "
            f"{process['Completion Time']:<12.2f} {process['Turnaround Time']:<12.2f} "
            f"{process['Waiting Time']:<12.2f} {process['First Response']:<12.2f}")
        
        total_waiting += process['Waiting Time']
        total_turnaround += process['Turnaround Time']
    
    n = len(results)
    avg_waiting = total_waiting / n
    avg_turnaround = total_turnaround / n
    
    print("=" * 100)
    print(f"Average Waiting Time: {avg_waiting:.2f}")
    print(f"Average Turnaround Time: {avg_turnaround:.2f}")

    # Write results to file
    try:
        # Get the base directory path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        result_path = os.path.join(base_dir, 'Schedulers', 'Priority&RoundRobin', 'round_robin_results.txt')
        
        with open(result_path, 'w') as f:
            f.write(f"{'Process ID':<12} {'Arrival Time':<14} {'Burst Time':<12} {'Completion':<12} "
                f"{'Turnaround':<12} {'Waiting':<12} {'First Response':<12}\n")
            f.write("-" * 100 + "\n")
            
            for process in results:
                f.write(f"{process['Process ID']:<12} {process['Arrival Time']:<14.2f} {process['Burst Time']:<12.2f} "
                    f"{process['Completion Time']:<12.2f} {process['Turnaround Time']:<12.2f} "
                    f"{process['Waiting Time']:<12.2f} {process['First Response']:<12.2f}\n")
            
            f.write("\nAverage Waiting Time: {:.2f}\n".format(avg_waiting))
            f.write("Average Turnaround Time: {:.2f}\n".format(avg_turnaround))
    except Exception as e:
        print(f"Error writing results to file: {e}")

def main():
    # Get the base directory path
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Path to the processes.txt file
    file_path = os.path.join(base_dir, "ProcessGeneratorModule", "processes.txt")
    
    # Read processes from file
    processes = read_processes(file_path)
    
    # Apply Round Robin scheduling
    results = round_robin_scheduling(processes)
    
    # Print results
    print_results(results)

if __name__ == "__main__":
    main() 
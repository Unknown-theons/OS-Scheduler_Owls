import os

def read_processes_from_file(filename):
    processes = []
    with open(filename, "r") as file:
        lines = file.readlines()
    
    if len(lines) <= 1:  # Check if the file has only a header or is empty
        raise ValueError("The processes file is empty or missing data.")
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 4:
            raise ValueError(f"Invalid line format: {line}")
        pid = parts[0]
        arrival = float(parts[1])
        burst = float(parts[2])
        priority = int(parts[3])
        processes.append({
            'pid': pid,
            'arrival': arrival,
            'burst': burst,
            'priority': priority
        })
        print(f"Read process: {pid} with arrival time {arrival}")  # Debug print
    return processes

def highest_priority_first(processes):
    """
    Implement Priority scheduling algorithm.
    - Lower priority number means higher priority
    - Preemptive: Current process can be preempted by a higher priority process
    - If priorities are equal, use FCFS
    """
    if not processes:
        return []
        
    # Create working copies and add remaining time
    process_list = []
    for p in processes:
        process_list.append({
            'pid': p['pid'],
            'arrival': p['arrival'],
            'burst': p['burst'],
            'priority': p['priority'],
            'remaining': p['burst'],
            'start_time': -1,
            'finish_time': 0,
            'waiting_time': 0
        })
    
    # Sort by arrival time initially
    process_list.sort(key=lambda x: x['arrival'])
    current_time = process_list[0]['arrival']
    completed = []
    ready_queue = []
    execution_history = []
    
    print("\nPriority Scheduling Execution Sequence:")
    print("=" * 80)
    
    while process_list or ready_queue:
        # Add newly arrived processes to ready queue
        while process_list and process_list[0]['arrival'] <= current_time:
            new_process = process_list.pop(0)
            ready_queue.append(new_process)
            print(f"Time {current_time:.1f}: Process {new_process['pid']} arrived (Priority: {new_process['priority']})")
            
            # Sort ready queue by priority (lower number = higher priority)
            ready_queue.sort(key=lambda x: (x['priority'], x['arrival']))
            
            # Check if we need to preempt current process
            if len(ready_queue) > 1 and ready_queue[0]['priority'] < ready_queue[-1]['priority']:
                print(f"Time {current_time:.1f}: Process {ready_queue[0]['pid']} preempts {ready_queue[-1]['pid']}")
                
        if not ready_queue:
            if process_list:
                current_time = process_list[0]['arrival']
                continue
            break
            
        # Get highest priority process
        current_process = ready_queue[0]
        
        # Set start time if not already set
        if current_process['start_time'] == -1:
            current_process['start_time'] = current_time
            print(f"Time {current_time:.1f}: Process {current_process['pid']} starts execution")
            
        # Calculate next arrival time
        next_arrival = float('inf')
        if process_list:
            next_arrival = process_list[0]['arrival']
            
        # Calculate execution time until next event
        execution_time = min(
            current_process['remaining'],
            next_arrival - current_time if next_arrival != float('inf') else current_process['remaining']
        )
        
        # Record execution
        execution_history.append({
            'pid': current_process['pid'],
            'start': current_time,
            'end': current_time + execution_time
        })
        
        print(f"Time {current_time:.1f}-{(current_time + execution_time):.1f}: "
              f"Executing {current_process['pid']} (Priority: {current_process['priority']})")
        
        # Update process state
        current_process['remaining'] -= execution_time
        current_time += execution_time
        
        # Check if process completed
        if current_process['remaining'] <= 0:
            current_process['finish_time'] = current_time
            ready_queue.remove(current_process)
            completed.append(current_process)
            print(f"Time {current_time:.1f}: Process {current_process['pid']} completed")
            
    print("=" * 80)
    
    # Calculate timing metrics
    results = []
    for process in completed:
        # Get all execution slices for this process
        process_executions = [e for e in execution_history if e['pid'] == process['pid']]
        
        # Calculate waiting time
        waiting_time = 0
        last_time = process['arrival']
        for exec_slice in process_executions:
            waiting_time += exec_slice['start'] - last_time
            last_time = exec_slice['end']
            
        turnaround_time = process['finish_time'] - process['arrival']
        process['waiting_time'] = waiting_time
        process['turnaround_time'] = turnaround_time
        results.append(process)
    
    return sorted(results, key=lambda x: x['pid'])

def write_results_to_file(results, avg_waiting_time, avg_turnaround_time):
    """Write the scheduling results to a file, sorted by completion time."""
    try:
        # Get the base directory path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        result_path = os.path.join(base_dir, 'Schedulers', 'Priority&RoundRobin', 'priority_results.txt')
        
        # Sort results by completion time
        sorted_results = sorted(results, key=lambda x: x['finish_time'])
        
        with open(result_path, 'w') as f:
            f.write(f"{'Process ID':<12} {'Arrival Time':<14} {'Burst Time':<12} {'Priority':<10} "
                   f"{'Start Time':<12} {'Finish Time':<12} {'Turnaround':<12} {'Waiting':<12}\n")
            f.write("-" * 100 + "\n")
            
            for process in sorted_results:
                f.write(f"{process['pid']:<12} {process['arrival']:<14.2f} {process['burst']:<12.2f} "
                       f"{process['priority']:<10} {process['start_time']:<12.2f} "
                       f"{process['finish_time']:<12.2f} {process['turnaround_time']:<12.2f} "
                       f"{process['waiting_time']:<12.2f}\n")
            
            f.write("\nAverage Waiting Time: {:.2f}\n".format(avg_waiting_time))
            f.write("Average Turnaround Time: {:.2f}\n".format(avg_turnaround_time))
    except Exception as e:
        print(f"Error writing results to file: {e}")

if __name__ == "__main__":
    filename = os.path.join(os.path.dirname(__file__), "..", "..", "ProcessGeneratorModule", "processes.txt")
    try:
        processes = read_processes_from_file(filename)
        print("Processes read from file:")
        for p in processes:
            print(p)
        
        scheduled_processes = highest_priority_first(processes)
        
        print("Scheduled Processes:")
        total_waiting_time = 0
        total_turnaround_time = 0
        for p in scheduled_processes:
            print(f"Process {p['pid']} - Start: {round(p['start_time'], 2)}, Finish: {round(p['finish_time'], 2)}, "
                  f"Waiting: {round(p['waiting_time'], 2)}, Turnaround: {round(p['turnaround_time'], 2)}")
            total_waiting_time += p['waiting_time']
            total_turnaround_time += p['turnaround_time']
        
        # Calculate averages
        avg_waiting_time = total_waiting_time / len(scheduled_processes)
        avg_turnaround_time = total_turnaround_time / len(scheduled_processes)
        
        print(f"\nAverage Waiting Time: {round(avg_waiting_time, 2)}")
        print(f"Average Turnaround Time: {round(avg_turnaround_time, 2)}")
        
        # Write results to file
        write_results_to_file(scheduled_processes, avg_waiting_time, avg_turnaround_time)
        
    except Exception as e:
        print(f"Error: {e}")
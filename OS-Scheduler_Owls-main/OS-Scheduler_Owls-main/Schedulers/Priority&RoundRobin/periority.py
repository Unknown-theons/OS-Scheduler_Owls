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
    return processes
def highest_priority_first(processes):
  
    # Sort processes by arrival time then by priority
    processes = sorted(processes, key=lambda x: (x['arrival'], x['priority']))
    time = 0
    completed_processes = []
    ready_queue = []
    remaining_processes = processes.copy()
    
    while remaining_processes or ready_queue:
        # Add processes that have arrived by the current time to the ready queue
        for process in remaining_processes[:]:
            if process['arrival'] <= time:
                ready_queue.append(process)
                remaining_processes.remove(process)
        
        if ready_queue:
            # Choose the process with the highest priority (lowest numerical value)
            ready_queue.sort(key=lambda x: x['priority'])
            current_process = ready_queue.pop(0)
            
            # Calculate times for the current process
            start_time = time
            finish_time = start_time + current_process['burst']
            waiting_time = start_time - current_process['arrival']
            turnaround_time = finish_time - current_process['arrival']
            
            # Update process details with the computed times
            current_process['start_time'] = start_time
            current_process['finish_time'] = finish_time
            current_process['waiting_time'] = waiting_time
            current_process['turnaround_time'] = turnaround_time
            
            completed_processes.append(current_process)
            time = finish_time  # Move time forward to the finish of the current process
        else:
            # If no process is ready, simply increment time
            time += 1
    
    return completed_processes

def save_results_to_file(processes, filename='priority_results.txt'):
    if not processes:
        return

    with open(filename, 'w') as f:
        f.write("====================================================================================================\n")
        f.write(f"{'Process ID':<12} {'Arrival Time':<13} {'Burst Time':<11} {'Priority':<10} {'Completion':<11} {'Turnaround':<11} {'Waiting':<8}\n")
        f.write("----------------------------------------------------------------------------------------------------\n")

        total_waiting = 0
        total_turnaround = 0

        for process in processes:
            f.write(f"{process['pid']:<12} {process['arrival']:<13.2f} {process['burst']:<11.2f} "
                  f"{process['priority']:<10} {process['finish_time']:<11.2f} {process['turnaround_time']:<11.2f} "
                  f"{process['waiting_time']:<8.2f}\n")

            total_waiting += process['waiting_time']
            total_turnaround += process['turnaround_time']

        n = len(processes)
        avg_waiting = total_waiting / n
        avg_turnaround = total_turnaround / n

        f.write("====================================================================================================\n")
        f.write(f"Average Waiting Time: {avg_waiting:.2f}\n")
        f.write(f"Average Turnaround Time: {avg_turnaround:.2f}\n")

def print_results(processes):
    if not processes:
        print("No processes to schedule.")
        return

    print("\nPriority Scheduling Results:")
    print("=" * 100)
    print(f"{'Process ID':<12} {'Arrival Time':<14} {'Burst Time':<12} {'Priority':<10} {'Completion':<12} {'Turnaround':<12} {'Waiting':<12}")
    print("-" * 100)

    total_waiting = 0
    total_turnaround = 0

    for process in processes:
        print(f"{process['pid']:<12} {process['arrival']:<14.2f} {process['burst']:<12.2f} "
              f"{process['priority']:<10} {process['finish_time']:<12.2f} {process['turnaround_time']:<12.2f} "
              f"{process['waiting_time']:<12.2f}")

        total_waiting += process['waiting_time']
        total_turnaround += process['turnaround_time']

    n = len(processes)
    avg_waiting = total_waiting / n
    avg_turnaround = total_turnaround / n

    print("=" * 100)
    print(f"Average Waiting Time: {avg_waiting:.2f}")
    print(f"Average Turnaround Time: {avg_turnaround:.2f}")

if __name__ == "__main__":
    filename = os.path.join(os.path.dirname(__file__), "..", "..", "processes.txt")
    try:
        # Read processes from file
        processes = read_processes_from_file(filename)
        
        scheduled_processes = highest_priority_first(processes)
        
        print_results(scheduled_processes)
        save_results_to_file(scheduled_processes, os.path.join(os.path.dirname(__file__), "..", "..", "priority_results.txt"))
    except Exception as e:
        print(f"Error: {e}")
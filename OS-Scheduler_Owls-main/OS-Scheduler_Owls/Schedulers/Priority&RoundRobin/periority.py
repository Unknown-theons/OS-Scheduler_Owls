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
        
        # حساب المتوسطات
        avg_waiting_time = total_waiting_time / len(scheduled_processes)
        avg_turnaround_time = total_turnaround_time / len(scheduled_processes)
        
        print(f"\nAverage Waiting Time: {round(avg_waiting_time, 2)}")
        print(f"Average Turnaround Time: {round(avg_turnaround_time, 2)}")
    except Exception as e:
        print(f"Error: {e}")
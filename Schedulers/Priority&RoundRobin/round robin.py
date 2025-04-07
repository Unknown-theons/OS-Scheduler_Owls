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

def round_robin_scheduling(processes, quantum):
    """
    Simulates Round Robin Scheduling considering arrival times.
    
    Each process is a dict with keys: 'id', 'arrival', 'burst', 'priority'
    The function calculates the waiting and turnaround times.
    """
    n = len(processes)
    # Initialize additional keys for simulation
    for proc in processes:
        proc['remaining'] = proc['burst']  # Remaining burst time
        proc['completion'] = 0            # Completion time
        proc['waiting'] = 0               # Waiting time
        proc['turnaround'] = 0            # Turnaround time
        proc['start'] = None              # First time execution

    time = 0
    ready_queue = []
    # Sort processes by arrival time for easier management
    processes_sorted = sorted(processes, key=lambda x: x['arrival'])
    i = 0  # Index for processes_sorted

    # Continue until all processes are done
    while i < n or ready_queue:
        # If no process is in the ready queue, jump time to next arrival
        if not ready_queue:
            time = max(time, processes_sorted[i]['arrival'])
            ready_queue.append(processes_sorted[i])
            i += 1

        # Pop the first process in the ready queue
        current_proc = ready_queue.pop(0)
        # Record first time execution if not already set
        if current_proc['start'] is None:
            current_proc['start'] = time

        # Determine execution time for this cycle
        exec_time = min(quantum, current_proc['remaining'])
        time += exec_time
        current_proc['remaining'] -= exec_time

        # Add processes that have arrived during this time slice to the ready queue
        while i < n and processes_sorted[i]['arrival'] <= time:
            ready_queue.append(processes_sorted[i])
            i += 1

        # If the process is not finished, add it back to the end of the ready queue
        if current_proc['remaining'] > 0:
            ready_queue.append(current_proc)
        else:
            # Process finished; record its completion, turnaround, and waiting times
            current_proc['completion'] = time
            current_proc['turnaround'] = current_proc['completion'] - current_proc['arrival']
            current_proc['waiting'] = current_proc['turnaround'] - current_proc['burst']

    return processes

def print_results(processes):
    """
    Prints a table of process scheduling results.
    """
    header = f"{'Process':<8}{'Arrival':<10}{'Burst':<8}{'Priority':<10}{'Completion':<12}{'Waiting':<10}{'Turnaround':<12}"
    print(header)
    print('-' * len(header))
    for proc in processes:
        print(f"{proc['id']:<8}{proc['arrival']:<10.2f}{proc['burst']:<8.2f}{proc['priority']:<10}{proc['completion']:<12.2f}{proc['waiting']:<10.2f}{proc['turnaround']:<12.2f}")
if __name__ == '__main__':
    # Specify the file name containing the process data
    filename = os.path.join(os.path.dirname(__file__), "..", "..", "ProcessGeneratorModule", "processes.txt")
    # Read processes from file
    processes = read_processes(filename)
    
    # Define the time quantum for the Round Robin scheduling
    quantum = 2.0  # You can adjust this value as needed
    
    # Run the Round Robin scheduling simulation
    scheduled_processes = round_robin_scheduling(processes, quantum)
    
    # Print the scheduling results
    print_results(scheduled_processes)
    
    # حساب متوسط وقت الانتظار ومتوسط وقت الدوران
    total_waiting_time = sum(proc['waiting'] for proc in scheduled_processes)
    total_turnaround_time = sum(proc['turnaround'] for proc in scheduled_processes)
    n = len(scheduled_processes)
    
    avg_waiting_time = total_waiting_time / n
    avg_turnaround_time = total_turnaround_time / n
    
    print("\nAverage Waiting Time:", round(avg_waiting_time, 2))
    print("Average Turnaround Time:", round(avg_turnaround_time, 2))
import os
from heapq import heappush, heappop

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
        self.start_time = -1

def read_processes(file_path):
    """Read processes from the processes.txt file."""
    processes = []
    try:
        with open(file_path, 'r') as file:
            next(file)  # skip header
            for line in file:
                data = [x for x in line.split() if x]
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

def srtf_scheduling(processes):
    """Implement SRTF scheduling algorithm with float-based timing."""
    if not processes:
        return []

    n = len(processes)
    current_time = 0.0
    completed = 0
    ready_queue = []
    results = []
    process_map = {p.pid: p for p in processes}
    visited = set()

    while completed < n:
        # Add newly arrived processes to ready queue
        for process in processes:
            if (
                process.arrival_time <= current_time 
                and process.remaining_time > 0 
                and process.pid not in visited
            ):
                heappush(ready_queue, (process.remaining_time, process.arrival_time, process.pid))
                visited.add(process.pid)

        if not ready_queue:
            current_time += 0.1
            current_time = round(current_time, 1)
            continue

        # Get process with shortest remaining time
        _, _, pid = heappop(ready_queue)
        process = process_map[pid]

        # Set start time if not already set
        if process.start_time == -1:
            process.start_time = current_time

        # Execute for 0.1 unit
        process.remaining_time -= 0.1
        process.remaining_time = round(process.remaining_time, 1)
        current_time += 0.1
        current_time = round(current_time, 1)

        # If completed
        if process.remaining_time <= 0:
            process.completion_time = current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time

            results.append({
                "Process ID": process.pid,
                "Arrival Time": process.arrival_time,
                "Burst Time": process.burst_time,
                "Completion Time": process.completion_time,
                "Turnaround Time": process.turnaround_time,
                "Waiting Time": process.waiting_time,
                "Start Time": process.start_time
            })

            completed += 1
        else:
            # Not finished? Back in the heap you go
            heappush(ready_queue, (process.remaining_time, process.arrival_time, process.pid))

    return sorted(results, key=lambda x: x["Process ID"])

def print_results(results):
    """Print the scheduling results in a formatted manner."""
    if not results:
        print("No processes to schedule.")
        return

    print("\n⏱️ SRTF Scheduling Results:")
    print("=" * 100)
    print(f"{'Process ID':<12} {'Arrival Time':<14} {'Burst Time':<12} {'Completion':<12} "
          f"{'Turnaround':<12} {'Waiting':<12}")
    print("-" * 100)

    total_waiting = 0
    total_turnaround = 0

    for process in results:
        print(f"{process['Process ID']:<12} {process['Arrival Time']:<14.2f} {process['Burst Time']:<12.2f} "
              f"{process['Completion Time']:<12.2f} {process['Turnaround Time']:<12.2f} "
              f"{process['Waiting Time']:<12.2f}")

        total_waiting += process['Waiting Time']
        total_turnaround += process['Turnaround Time']

    n = len(results)
    avg_waiting = total_waiting / n
    avg_turnaround = total_turnaround / n

    print("=" * 100)
    print(f"Average Waiting Time: {avg_waiting:.2f}")
    print(f"Average Turnaround Time: {avg_turnaround:.2f}")

def main():
    # Adjust folder name here if needed
    file_path = os.path.join(os.path.dirname(__file__), "..", "ProcessGeneratorModule", "processes.txt")

    # Read processes
    processes = read_processes(file_path)

    # Run SRTF
    results = srtf_scheduling(processes)

    # Show results
    print_results(results)

if __name__ == "__main__":
    main()

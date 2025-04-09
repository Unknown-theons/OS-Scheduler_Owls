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
                "process_id": process.pid,
                "arrival_time": process.arrival_time,
                "burst_time": process.burst_time,
                "completion": process.completion_time,
                "turnaround": process.turnaround_time,
                "waiting": process.waiting_time,
                "start_time": process.start_time
            })

            completed += 1
        else:
            # Not finished? Back in the heap you go
            heappush(ready_queue, (process.remaining_time, process.arrival_time, process.pid))

    return sorted(results, key=lambda x: x["process_id"])

def print_results(results):
    """Print the scheduling results in a formatted manner."""
    if not results:
        print("No processes to schedule.")
        return

    print("\n SRTF Scheduling Results:")
    print("=" * 100)
    print(f"{'Process ID':<12} {'Arrival Time':<14} {'Burst Time':<12} {'Completion':<12} "
          f"{'Turnaround':<12} {'Waiting':<12}")
    print("-" * 100)

    total_waiting = 0
    total_turnaround = 0

    for process in results:
        print(f"{process['process_id']:<12} {process['arrival_time']:<14.2f} {process['burst_time']:<12.2f} "
              f"{process['completion']:<12.2f} {process['turnaround']:<12.2f} "
              f"{process['waiting']:<12.2f}")

        total_waiting += process['waiting']
        total_turnaround += process['turnaround']

    n = len(results)
    avg_waiting = total_waiting / n
    avg_turnaround = total_turnaround / n

    print("=" * 100)
    print(f"Average Waiting Time: {avg_waiting:.2f}")
    print(f"Average Turnaround Time: {avg_turnaround:.2f}")

def save_results_to_file(results, filename='srtf_results.txt'):
    with open(filename, 'w') as f:
        f.write("====================================================================================================\n")
        f.write(f"{'Process ID':<12} {'Arrival Time':<13} {'Burst Time':<11} {'Completion':<11} {'Turnaround':<11} {'Waiting':<8}\n")
        f.write("----------------------------------------------------------------------------------------------------\n")

        total_waiting = 0
        total_turnaround = 0

        for result in results:
            f.write(f"{result['process_id']:<12} {result['arrival_time']:<13.2f} {result['burst_time']:<11.2f} {result['completion']:<11.2f} {result['turnaround']:<11.2f} {result['waiting']:<8.2f}\n")
            total_waiting += result['waiting']
            total_turnaround += result['turnaround']

        n = len(results)
        avg_waiting = total_waiting / n
        avg_turnaround = total_turnaround / n

        f.write("====================================================================================================\n")
        f.write(f"Average Waiting Time: {avg_waiting:.2f}\n")
        f.write(f"Average Turnaround Time: {avg_turnaround:.2f}\n")

def main():
    # Adjust folder name here if needed
    file_path = os.path.join(os.path.dirname(__file__),"..", "..", "processes.txt")

    # Read processes
    processes = read_processes(file_path)

    # Run SRTF
    results = srtf_scheduling(processes)

    # Save results to file
    save_results_to_file(results, os.path.join(os.path.dirname(__file__),"..", "..", "srtf_results.txt"))

    # Print results
    print_results(results)

if __name__ == "__main__":
    main()

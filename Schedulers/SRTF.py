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
        return {
            "processes": [],
            "avg_waiting_time": 0,
            "avg_turnaround_time": 0,
            "total_execution_time": 0
        }

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

        # Set start time if not set
        if process.start_time == -1:
            process.start_time = current_time

        # Process for 0.1 time unit
        process.remaining_time -= 0.1
        process.remaining_time = round(process.remaining_time, 1)
        current_time += 0.1
        current_time = round(current_time, 1)

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
                "Waiting Time": process.waiting_time
            })

            completed += 1
        else:
            heappush(ready_queue, (process.remaining_time, process.arrival_time, process.pid))

    # Sort results by Process ID
    sorted_results = sorted(results, key=lambda x: x["Process ID"])
    
    # Calculate averages
    total_waiting = sum(p["Waiting Time"] for p in sorted_results)
    total_turnaround = sum(p["Turnaround Time"] for p in sorted_results)
    avg_waiting = round(total_waiting / n, 2)
    avg_turnaround = round(total_turnaround / n, 2)
    total_execution = round(max(p["Completion Time"] for p in sorted_results), 2)

    return {
        "processes": sorted_results,
        "avg_waiting_time": avg_waiting,
        "avg_turnaround_time": avg_turnaround,
        "total_execution_time": total_execution
    }

def print_results(results):
    """Print the scheduling results in a formatted manner."""
    if not results["processes"]:
        print("No processes to schedule.")
        return

    print("\n SRTF Scheduling Results:")
    print("=" * 100)
    print(f"{'Process ID':<12} {'Arrival Time':<14} {'Burst Time':<12} {'Completion':<12} "
          f"{'Turnaround':<12} {'Waiting':<12}")
    print("-" * 100)

    for process in results["processes"]:
        print(f"{process['Process ID']:<12} {process['Arrival Time']:<14.2f} {process['Burst Time']:<12.2f} "
              f"{process['Completion Time']:<12.2f} {process['Turnaround Time']:<12.2f} "
              f"{process['Waiting Time']:<12.2f}")

    print("=" * 100)
    print(f"Average Waiting Time: {results['avg_waiting_time']:.2f}")
    print(f"Average Turnaround Time: {results['avg_turnaround_time']:.2f}")
    print(f"Total Execution Time: {results['total_execution_time']:.2f}")

def save_results(results, file_path):
    """Save the scheduling results to a file."""
    try:
        with open(file_path, 'w') as file:
            # Write header
            file.write("Process ID\tArrival Time\tBurst Time\tCompletion Time\tTurnaround Time\tWaiting Time\n")
            
            # Write process data
            for process in results["processes"]:
                file.write(f"{process['Process ID']}\t"
                          f"{process['Arrival Time']:.2f}\t"
                          f"{process['Burst Time']:.2f}\t"
                          f"{process['Completion Time']:.2f}\t"
                          f"{process['Turnaround Time']:.2f}\t"
                          f"{process['Waiting Time']:.2f}\n")
            
            # Write averages
            file.write("\n=== Averages ===\n")
            file.write(f"Average Waiting Time: {results['avg_waiting_time']:.2f}\n")
            file.write(f"Average Turnaround Time: {results['avg_turnaround_time']:.2f}\n")
            file.write(f"Total Execution Time: {results['total_execution_time']:.2f}\n")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    # Adjust folder name here if needed
    input_file_path = os.path.join(os.path.dirname(__file__), "..", "ProcessGeneratorModule", "processes.txt")
    output_file_path = os.path.join(os.path.dirname(__file__), "..", "ProcessGeneratorModule", "srtf_results.txt")

    # Read processes
    processes = read_processes(input_file_path)

    # Run SRTF
    results = srtf_scheduling(processes)

    # Show results in console
    print_results(results)

    # Save results to file
    save_results(results, output_file_path)

if __name__ == "__main__":
    main()

import os

# Add the ProcessGeneratorModule folder to the Python path
#sys.path.append(os.path.abspath(r"B:\Akuma\Uni\2nd year\second semester\OS\OS-Scheduler_Owls-main\OS-Scheduler_Owls-main\ProcessGeneratorModule"))

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

def fcfs_scheduling(processes):
    """Implement FCFS scheduling algorithm."""
    if not processes:
        return []

    # Sort processes by arrival time (and process ID for tie-breaking)
    processes.sort(key=lambda x: (x.arrival_time, x.pid))
    
    current_time = 0
    results = []

    for process in processes:
        # If there's a gap between processes, move time to next arrival
        if current_time < process.arrival_time:
            current_time = process.arrival_time
        
        # Calculate times
        process.completion_time = current_time + process.burst_time
        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time
        
        # Add to results
        results.append({
            "Process ID": process.pid,
            "Arrival Time": process.arrival_time,
            "Burst Time": process.burst_time,
            "Completion Time": process.completion_time,
            "Turnaround Time": process.turnaround_time,
            "Waiting Time": process.waiting_time
        })
        
        # Update current time
        current_time = process.completion_time

    return results

def print_results(results):
    """Print the scheduling results in a formatted manner."""
    if not results:
        print("No processes to schedule.")
        return

    print("\n🔄 FCFS Scheduling Results:")
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
    # Path to the processes.txt file
    file_path = os.path.join(os.path.dirname(__file__), "..", "ProcessGeneratorModule", "processes.txt")
    
    # Read processes from file
    processes = read_processes(file_path)
    
    # Apply FCFS scheduling
    results = fcfs_scheduling(processes)
    
    # Print results
    print_results(results)

if __name__ == "__main__":
    main()
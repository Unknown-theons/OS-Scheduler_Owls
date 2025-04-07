import matplotlib.pyplot as plt
import numpy as np

def calculate_metrics(results):
    """Calculate average waiting and turnaround times."""
    if not results:
        return 0, 0
    
    total_waiting = sum(p["Waiting Time"] for p in results)
    total_turnaround = sum(p["Turnaround Time"] for p in results)
    n = len(results)
    
    return total_waiting/n, total_turnaround/n

def compare_algorithms(fcfs_results, srtf_results, priority_results, rr_results):
    """Compare performance metrics of different scheduling algorithms."""
    # Calculate metrics
    fcfs_wait, fcfs_tat = calculate_metrics(fcfs_results)
    srtf_wait, srtf_tat = calculate_metrics(srtf_results)
    priority_wait, priority_tat = calculate_metrics(priority_results)
    rr_wait, rr_tat = calculate_metrics(rr_results)
    
    print("\n📊 Performance Comparison")
    print("=" * 70)
    print(f"{'Algorithm':<15}{'Avg Wait Time':<20}{'Avg Turnaround Time':<20}")
    print("-" * 70)
    print(f"{'FCFS':<15}{fcfs_wait:<20.2f}{fcfs_tat:<20.2f}")
    print(f"{'SRTF':<15}{srtf_wait:<20.2f}{srtf_tat:<20.2f}")
    print(f"{'Priority':<15}{priority_wait:<20.2f}{priority_tat:<20.2f}")
    print(f"{'Round Robin':<15}{rr_wait:<20.2f}{rr_tat:<20.2f}")
    print("=" * 70)
    
    return {
        'FCFS': (fcfs_wait, fcfs_tat),
        'SRTF': (srtf_wait, srtf_tat),
        'Priority': (priority_wait, priority_tat),
        'Round Robin': (rr_wait, rr_tat)
    }

def plot_comparison(metrics):
    """Create performance comparison plots."""
    algorithms = list(metrics.keys())
    waiting_times = [m[0] for m in metrics.values()]
    turnaround_times = [m[1] for m in metrics.values()]
    
    # Set up the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot waiting times
    ax1.bar(algorithms, waiting_times, color=['blue', 'green', 'orange', 'purple'])
    ax1.set_title('Average Waiting Time Comparison')
    ax1.set_ylabel('Time Units')
    
    # Plot turnaround times
    ax2.bar(algorithms, turnaround_times, color=['blue', 'green', 'orange', 'purple'])
    ax2.set_title('Average Turnaround Time Comparison')
    ax2.set_ylabel('Time Units')
    
    plt.tight_layout()
    plt.savefig('scheduling_comparison.png')
    print("\n📈 Performance comparison plot saved as 'scheduling_comparison.png'")

def analyze_performance(fcfs_results, srtf_results, priority_results, rr_results):
    """Perform complete performance analysis of scheduling algorithms."""
    metrics = compare_algorithms(fcfs_results, srtf_results, priority_results, rr_results)
    plot_comparison(metrics)
    
    return metrics

if __name__ == "__main__":
    # Example usage with sample results
    sample_fcfs = [
        {"Waiting Time": 0, "Turnaround Time": 5},
        {"Waiting Time": 5, "Turnaround Time": 9}
    ]
    sample_srtf = [
        {"Waiting Time": 0, "Turnaround Time": 4},
        {"Waiting Time": 3, "Turnaround Time": 7}
    ]
    sample_priority = [
        {"Waiting Time": 1, "Turnaround Time": 6},
        {"Waiting Time": 4, "Turnaround Time": 8}
    ]
    sample_rr = [
        {"Waiting Time": 2, "Turnaround Time": 7},
        {"Waiting Time": 3, "Turnaround Time": 9}
    ]
    
    analyze_performance(sample_fcfs, sample_srtf, sample_priority, sample_rr)
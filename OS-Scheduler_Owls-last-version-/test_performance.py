import os
import sys
import subprocess

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import generate_new_processes
from performance_analysis2 import plot_comparison

def run_scheduler(script_path, processes_file):
    try:
        # Set the PYTHONPATH to include the current directory
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
        
        result = subprocess.run([sys.executable, script_path], 
                              check=True, 
                              capture_output=True, 
                              text=True,
                              env=env)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")
        print(e.stdout)
        print(e.stderr)

def run_test():
    print("Generating new processes...")
    generate_new_processes()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processes_file = os.path.join(base_dir, "ProcessGeneratorModule", "processes.txt")
    
    print("\nRunning FCFS scheduler...")
    fcfs_script = os.path.join(base_dir, "Schedulers", "FCFS&SRTF", "FCFS.py")
    run_scheduler(fcfs_script, processes_file)
    
    print("\nRunning SRTF scheduler...")
    srtf_script = os.path.join(base_dir, "Schedulers", "FCFS&SRTF", "SRTF.py")
    run_scheduler(srtf_script, processes_file)
    
    print("\nRunning Priority scheduler...")
    priority_script = os.path.join(base_dir, "Schedulers", "Priority&RoundRobin", "periority.py")
    run_scheduler(priority_script, processes_file)
    
    print("\nRunning Round Robin scheduler...")
    rr_script = os.path.join(base_dir, "Schedulers", "Priority&RoundRobin", "round robin.py")
    run_scheduler(rr_script, processes_file)
    
    print("\nGenerating performance comparison...")
    plot_comparison()

if __name__ == "__main__":
    run_test() 
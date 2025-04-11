import matplotlib.pyplot as plt
import numpy as np
import os
import time
from datetime import datetime
import glob
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_result_file(result_file):
    """Validate that a result file exists and is readable"""
    try:
        if not os.path.exists(result_file):
            logger.warning(f"Result file {result_file} does not exist")
            return False
            
        if not os.access(result_file, os.R_OK):
            logger.warning(f"Result file {result_file} is not readable")
            return False
            
        if os.path.getsize(result_file) == 0:
            logger.warning(f"Result file {result_file} is empty")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error validating result file {result_file}: {e}")
        return False

def read_scheduler_results(result_file):
    """Read scheduler results and extract waiting and turnaround times"""
    try:
        if not validate_result_file(result_file):
            return None
            
        with open(result_file, 'r') as f:
            lines = f.readlines()
            waiting_times = []
            turnaround_times = []
            avg_waiting = 0
            avg_turnaround = 0
            process_count = 0
            
            for line in lines:
                if line.strip() and not line.startswith('Process ID'):
                    parts = line.split()
                    if len(parts) >= 6:
                        try:
                            waiting_time = float(parts[5])
                            turnaround_time = float(parts[4])
                            
                            # Validate the times are non-negative
                            if waiting_time < 0 or turnaround_time < 0:
                                logger.warning(f"Invalid time value in {result_file}: {line.strip()}")
                                continue
                                
                            waiting_times.append(waiting_time)
                            turnaround_times.append(turnaround_time)
                            process_count += 1
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Error parsing line in {result_file}: {line.strip()}")
                            continue
                elif 'Average Waiting Time:' in line:
                    try:
                        avg_waiting = float(line.split(':')[1].strip())
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing average waiting time in {result_file}")
                elif 'Average Turnaround Time:' in line:
                    try:
                        avg_turnaround = float(line.split(':')[1].strip())
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing average turnaround time in {result_file}")
            
            if not waiting_times or not turnaround_times:
                logger.warning(f"No valid process data found in {result_file}")
                return None
                
            # Validate that averages match calculated values
            calculated_avg_waiting = sum(waiting_times) / len(waiting_times)
            calculated_avg_turnaround = sum(turnaround_times) / len(turnaround_times)
            
            if abs(calculated_avg_waiting - avg_waiting) > 0.01 or abs(calculated_avg_turnaround - avg_turnaround) > 0.01:
                logger.warning(f"Average values in {result_file} do not match calculated values")
                avg_waiting = calculated_avg_waiting
                avg_turnaround = calculated_avg_turnaround
                
            return {
                'waiting_times': waiting_times,
                'turnaround_times': turnaround_times,
                'avg_waiting': avg_waiting,
                'avg_turnaround': avg_turnaround,
                'process_count': process_count
            }
    except Exception as e:
        logger.error(f"Error reading {result_file}: {e}")
        return None

def cleanup_old_comparison_files(static_dir, keep_latest=5):
    """Clean up old comparison files, keeping only the latest ones"""
    try:
        if not os.path.exists(static_dir):
            logger.warning(f"Static directory {static_dir} does not exist")
            return
            
        comparison_files = glob.glob(os.path.join(static_dir, 'scheduling_comparison_*.png'))
        
        if not comparison_files:
            logger.info("No old comparison files to clean up")
            return
            
        comparison_files.sort(key=os.path.getmtime, reverse=True)
        
        for old_file in comparison_files[keep_latest:]:
            try:
                os.remove(old_file)
                logger.info(f"Removed old comparison file: {old_file}")
            except Exception as e:
                logger.error(f"Error removing old file {old_file}: {e}")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def plot_comparison():
    """Create a real-time comparison of scheduling algorithms"""
    fig = None
    try:
        # Get the base directory path
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # Define result files with absolute paths
        result_files = {
            'FCFS': os.path.join(BASE_DIR, 'fcfs_results.txt'),
            'SRTF': os.path.join(BASE_DIR, 'srtf_results.txt'),
            'Priority': os.path.join(BASE_DIR, 'priority_results.txt'),
            'Round Robin': os.path.join(BASE_DIR, 'round_robin_results.txt')
        }
        
        # Read results from all files
        results = {}
        for name, file in result_files.items():
            try:
                if not os.path.exists(file):
                    logger.warning(f"Result file {file} does not exist")
                    continue
                results[name] = read_scheduler_results(file)
            except Exception as e:
                logger.error(f"Error reading results for {name}: {e}")
                results[name] = None
        
        # Filter out None results
        valid_results = {k: v for k, v in results.items() if v is not None}
        if not valid_results:
            logger.error("No valid results found for any algorithm")
            return None
        
        # Set style for better web display
        plt.style.use('ggplot')
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot average waiting times
        algorithms = list(valid_results.keys())
        avg_waiting = [valid_results[algo]['avg_waiting'] for algo in algorithms]
        avg_turnaround = [valid_results[algo]['avg_turnaround'] for algo in algorithms]
        
        # Bar width
        width = 0.35
        
        # Plot waiting times
        bars1 = ax1.bar(algorithms, avg_waiting, width, color='#3498db', label='Average Waiting Time')
        ax1.set_ylabel('Time', fontsize=12)
        ax1.set_title('Comparison of Average Waiting Times', fontsize=14, pad=20)
        ax1.bar_label(bars1, padding=3, fontsize=10, fmt='%.1f')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Plot turnaround times
        bars2 = ax2.bar(algorithms, avg_turnaround, width, color='#2ecc71', label='Average Turnaround Time')
        ax2.set_ylabel('Time', fontsize=12)
        ax2.set_title('Comparison of Average Turnaround Times', fontsize=14, pad=20)
        ax2.bar_label(bars2, padding=3, fontsize=10, fmt='%.1f')
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Add process details
        process_details = []
        for algo in algorithms:
            if valid_results[algo]:
                process_details.append(f"{algo}: {valid_results[algo]['process_count']} processes")
        
        # Add process details to the plot
        plt.figtext(0.5, 0.01, '\n'.join(process_details), ha='center', fontsize=10, 
                   bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8))
        
        # Add timestamp to the plot
        plt.figtext(0.5, 0.95, f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                    ha='center', fontsize=10, bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8))
        
        # Adjust layout
        plt.tight_layout()
        
        # Create static/Schedulers directory if it doesn't exist
        static_dir = os.path.join(BASE_DIR, 'static', 'Schedulers')
        os.makedirs(static_dir, exist_ok=True)
        
        # Save the figure with a fixed name, overwriting any existing file
        output_file = os.path.join(static_dir, 'scheduling_comparison.png')
        plt.savefig(output_file, bbox_inches='tight', dpi=100)
        plt.close(fig)
        
        logger.info(f"Comparison plot saved to {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"Error creating comparison plot: {e}")
        if fig:
            plt.close(fig)
        return None

if __name__ == "__main__":
    plot_comparison() 
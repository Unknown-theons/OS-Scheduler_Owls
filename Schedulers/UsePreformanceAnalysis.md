# Performance Analysis Module

This module provides tools for analyzing and comparing different CPU scheduling algorithms, specifically FCFS (First Come First Serve) and SRTF (Shortest Remaining Time First).

## Features

- Calculate average waiting times and turnaround times
- Compare performance metrics between algorithms
- Generate visual comparisons using matplotlib
- Export comparison plots as PNG files

## Usage

```python
from Schedulers.PerformanceAnalysis import analyze_performance

# Example results from scheduling algorithms
fcfs_results = [
    {"Waiting Time": 0, "Turnaround Time": 5},
    {"Waiting Time": 5, "Turnaround Time": 9}
]
srtf_results = [
    {"Waiting Time": 0, "Turnaround Time": 4},
    {"Waiting Time": 3, "Turnaround Time": 7}
]

# Analyze and compare the results
metrics = analyze_performance(fcfs_results, srtf_results)
```

## Functions

### `calculate_metrics(results)`

Calculates average waiting and turnaround times for a set of process results.

Parameters:

- `results`: List of dictionaries containing "Waiting Time" and "Turnaround Time" for each process

Returns:

- Tuple of (average_waiting_time, average_turnaround_time)

### `compare_algorithms(fcfs_results, srtf_results)`

Compares performance metrics between FCFS and SRTF algorithms.

Parameters:

- `fcfs_results`: Results from FCFS scheduling
- `srtf_results`: Results from SRTF scheduling

Returns:

- Dictionary containing metrics for both algorithms

### `plot_comparison(metrics)`

Generates visual comparison plots of the algorithms' performance.

Parameters:

- `metrics`: Dictionary containing performance metrics for each algorithm

Output:

- Saves plot as 'scheduling_comparison.png'

## Output Example

```
📊 Performance Comparison
==================================================
Algorithm      Avg Wait Time    Avg Turnaround Time
--------------------------------------------------
FCFS          2.50            7.00
SRTF          1.50            5.50
==================================================

📈 Performance comparison plot saved as 'scheduling_comparison.png'
```

## Dependencies

- matplotlib
- numpy

## Installation

```bash
pip install matplotlib numpy
```

## Integration

To integrate with your scheduling algorithms:

1. Import the analysis module:

```python
from PerformanceAnalysis import analyze_performance
```

2. After running your scheduling algorithms, pass their results to the analyzer:

```python
metrics = analyze_performance(fcfs_results, srtf_results)
```

3. View the comparison in the console and check the generated plot in 'scheduling_comparison.png'

## Visualization

The module generates two bar charts:

- Average Waiting Time Comparison
- Average Turnaround Time Comparison

Charts are saved as 'scheduling_comparison.png' in the current directory.

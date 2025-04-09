# OS Scheduler Project

## Overview

The OS Scheduler is a crucial component of an operating system responsible for CPU scheduling. It selects processes from the ready queue and assigns the CPU based on specific criteria such as the chosen scheduling algorithm and whether the process scheduling is preemptive or non-preemptive. A dispatcher component handles the actual allocation of CPU resources to the selected process.

This project consists of two main components:

- **Process Generation Module**
- **Scheduling Module**

## Process Generator Module

The process generator creates a set of processes with the following parameters:

- **Arrival Time**
- **Burst Time**
- **Priority**

These parameters are randomly generated following the specified distributions. The generator takes an input text file with the following format:

```
Line 1: Number of processes
Line 2: Mean and standard deviation for arrival time
Line 3: Mean and standard deviation for burst time
Line 4: Lambda for priority
```

After processing the input, the module outputs another text file formatted as follows:

```
Line 1: Number of processes
Line 2: Process_ID Arrival_Time Burst_Time Priority
...
```

## OS Scheduler Module

This module reads the output from the process generator and schedules processes from the Ready Queue using various algorithms. The implemented scheduling algorithms include:

1. **Non-Preemptive Highest Priority First**
2. **First Come First Serve (FCFS)**
3. **Round Robin**
4. **Preemptive Shortest Remaining Time First (SRTF)**

For each algorithm, the project demonstrates the impact on the same input by calculating and presenting:

- Turnaround time
- Waiting time
- Average values

A bonus will be awarded for visualizing the results using graphs. Advanced implementations such as a website or a full-fledged application will also receive extra credit.

## Assumptions

- **Priority Tie-Breaking:** Any tie between processes (e.g., same arrival time and priority) is broken by the order of processes (e.g., P1 executes before P2).
- **Priority Value:** The greatest numerical value indicates the highest priority.
- **No I/O Wait:** Processes do not wait for events or request I/O, meaning they do not enter a waiting state.

## Deliverables

1. **Sample Input and Output Files**
2. **Source Code**
3. **Executable File**
4. **Report Document**

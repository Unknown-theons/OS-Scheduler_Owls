Overview

The OS Scheduler is a crucial component of an operating system responsible for CPU scheduling. It selects processes from the ready queue and assigns the CPU based on specific scheduling algorithms. This project involves implementing an OS scheduler that supports multiple scheduling algorithms and visualizes their impact.

Features

Process generation module that creates processes with randomly generated parameters.

Scheduling module implementing multiple CPU scheduling algorithms.

Performance analysis including turnaround time, waiting time, and averages.

Optional visualization of scheduling results through graphs.

GUI for user interaction.

Modules

1. Process Generator

Generates processes based on input parameters and writes them to a file.

Input Format:

Line 1: Number of processes
Line 2: Mean and standard deviation for arrival time
Line 3: Mean and standard deviation for burst time
Line 4: Lambda for priority

Output Format:

Line 1: Number of processes
Line 2: Process_ID Arrival_Time Burst_Time Priority

2. OS Scheduler

Reads the generated process file and schedules the processes using the following algorithms:

Non-Preemptive Highest Priority First

First Come First Serve (FCFS)

Round Robin

Preemptive Shortest Remaining Time First (SRTF)

The scheduler presents detailed analysis and comparison of each algorithm.

Assumptions

Higher numerical priority value means higher priority.

No I/O waiting; all processes remain in the ready queue until execution.

Ties in arrival time and priority are resolved in process order.

Deliverables

Sample input and output files.

Source code.

Executable file.

Report including analysis and screenshots.

Requirements

Any programming language of choice.

GUI implementation is mandatory.

Installation

Clone the repository:

git clone https://github.com/your-repo/os-scheduler.git

Navigate to the project directory:

cd os-scheduler

Install dependencies (if applicable):

pip install -r requirements.txt  # Python example

Run the application:

python main.py  # Example command

Usage

Provide input files with required parameters.

Choose a scheduling algorithm.

View the results and performance analysis.

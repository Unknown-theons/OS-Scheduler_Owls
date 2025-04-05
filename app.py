from flask import Flask, render_template, send_file, jsonify
from Schedulers.FCFS import read_processes, fcfs_scheduling
import os
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    # Path to the processes.txt file
    file_path = "E:/MY PROJECT/Web devolopment/OS-Scheduler_Owls/processes.txt"

    
    # Read processes and get scheduling results
    processes = read_processes(file_path)
    results = fcfs_scheduling(processes)
    
    # Calculate averages
    if results:
        total_waiting = sum(process['Waiting Time'] for process in results)
        total_turnaround = sum(process['Turnaround Time'] for process in results)
        n = len(results)
        avg_waiting = total_waiting / n
        avg_turnaround = total_turnaround / n
    else:
        avg_waiting = avg_turnaround = 0
    
    return render_template('index.html', 
                         results=results,
                         avg_waiting=avg_waiting,
                         avg_turnaround=avg_turnaround)

@app.route('/get_processes_data')
def get_processes_data():
    file_path = "E:/MY PROJECT/Web devolopment/OS-Scheduler_Owls/processes.txt"
    return send_file(file_path)

@app.route('/get_input_data')
def get_input_data():
    file_path = "E:/MY PROJECT/Web devolopment/OS-Scheduler_Owls/inputFile.txt"
    return send_file(file_path)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Run the InputGenerator script to generate new input
        subprocess.run(['python', 'ProcessGeneratorModule/InputGenerator.py'], check=True)
        # Run the outputGenerator script to generate processes
        subprocess.run(['python', 'ProcessGeneratorModule/outputGenerator.py'], check=True)
        return jsonify({"status": "success"})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

import re
import numpy as np
import os

# Define file paths relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, "inputFile.txt")
processes_file = os.path.join(script_dir, "processes.txt")

def read_Entire_File(Filename):
   # Open the file in read mode
   with open(Filename, "r") as file:
    content = file.read()  # Reads the entire content of the file
    print(content)  # Print the content to the console

def read_line_by_line(Filename):
   with open(Filename,"r") as file:
      lines = file.readlines()
      file.close
   return lines #retun a list of lines 

def Extract_numbers(line_Order, usecase):
    if usecase == 1: #first UseCase for Int Numbers
        str_2_int = ""
        for char in line_Order:
            if char.isdigit():
                str_2_int += char   
        try:
            str_2_int = int(str_2_int)
        except ValueError:
            print("there's a slicing error, code: SE_LN21")
            str_2_int = None
        return str_2_int

    if usecase == 2: #Second UseCase for Float and multiple numbers
        str_2_float = [float(n) for n in re.findall(r'\d+\.\d+', line_Order)]
        return str_2_float
   

def Predict_and_Confirm_Values(ProcessesNumber, Mean, STDE):
   np.random.seed(42)  # Set a fixed seed to get the same result each time

   # Feasibility check: max σ with all x>0 is μ*sqrt(N-1)
   if STDE > Mean * np.sqrt(ProcessesNumber-1):
      raise ValueError("Cannot have strict positivity with these mean/std parameters.")

   while True:
      # generate n-1 values that have mean and STDE work as lambda [it generates values around mean and STDE]
      list_of_processes = np.random.normal(loc=Mean, scale=STDE, size=ProcessesNumber-1)  # mean = height, STDE = width, of the bell

      # Ensure all values are non-negative
      list_of_processes = np.maximum(list_of_processes, 0)  # Replace any negative values with 0

      required_Sum = Mean * ProcessesNumber  # check REQUIRED sum
      current_Sum = np.sum(list_of_processes)  # check CURRENT sum

      # Calculate the last value needed to match the required sum
      last_Value = required_Sum - current_Sum

      # If last value is negative, adjust it to ensure a non-zero value
      if last_Value <= 0:
         last_Value = 1e-6  # Set to a tiny positive value

      # Add the last value to the list
      list_of_processes = np.append(list_of_processes, last_Value)

      # Now loop: enforce strict positivity, then re‑match mean & STDE by an affine transform
      eps = 1e-6
      for _ in range(20):
         # clip to ensure no zeros or negatives
         list_of_processes = np.maximum(list_of_processes, eps)

         # compute current stats
         cur_mean = np.mean(list_of_processes)
         cur_std  = np.std(list_of_processes)

         # linear rescale to match target mean & STDE
         scaling_factor = STDE / cur_std
         list_of_processes = (list_of_processes - cur_mean) * scaling_factor + Mean

         # if now all > 0, we're done
         if np.all(list_of_processes > eps):
            break

      # If after the rescale+clip loop we have strict positivity, exit outer loop
      if np.all(list_of_processes > eps):
         break

   # Round the values and convert it from numpy float to regular float 
   list_of_processes = [round(float(i), 1) for i in list_of_processes]

   return list_of_processes  # return a list of processes

def Merge_lists_to_DIC(ProcessesNumber, AT_List, BT_List, P_List):
   ProcessDic = {}

   for i in range(ProcessesNumber):
      ProcessDic[i] = {
         "Process ID:": "P" + str(i),
         "Arrival Time:": AT_List[i],
         "Burst Time:": BT_List[i],
         "Priority:": P_List[i]
         
      }
   return ProcessDic

def Write_DIC_to_Text_File(ProcessDic, filename):
   # Open a file to write
   with open(filename, 'w') as file:
      # Write the header row
      file.write(f"{'Process ID':<15}{'Arrival Time':<15}{'Burst Time':<15}{'Priority':<15}\n")
      
      # Write each process's details
      for key, value in ProcessDic.items():
            # Extract details from the dictionary
            process_id = value["Process ID:"]
            arrival_time = value["Arrival Time:"]
            burst_time = value["Burst Time:"]
            priority = value["Priority:"]
            
            # Write the data in a formatted way (align columns)
            file.write(f"{process_id:<15}{arrival_time:<15}{burst_time:<15}{priority:<15}\n")

if __name__ == "__main__":
    lines_list = read_line_by_line(input_file)

    ProcessNumbers = Extract_numbers(lines_list[1],1) # Output: Int
    print(f"Number of Processes: {ProcessNumbers}\n")

    ArrivalTime = Extract_numbers(lines_list[2],2) # Output: [Mean, STDR]
    ArrivalTime_List = Predict_and_Confirm_Values(ProcessNumbers, ArrivalTime[0], ArrivalTime[1])

    BurstTime = Extract_numbers(lines_list[3],2) # Output: [Mean, STDR]
    BurstTime_List = Predict_and_Confirm_Values(ProcessNumbers, BurstTime[0], BurstTime[1])

    Priority = Extract_numbers(lines_list[4],2) # Output: [Float]
    priority2_List = np.random.poisson(Priority, ProcessNumbers) #generate random priorities around the given num

    # Convert np.int32 to int
    priority2_list = [int(x) for x in priority2_List]

    Merged = Merge_lists_to_DIC(ProcessNumbers, ArrivalTime_List, BurstTime_List, priority2_list)

    Write_DIC_to_Text_File(Merged, processes_file)
    read_Entire_File(processes_file)
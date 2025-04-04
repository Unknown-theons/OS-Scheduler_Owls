#each process has burst time, pirority, arrival time, process id 
#mean and standard devi for burst time and arrival time
import random
import os
import numpy as np
import math

# Define the file name globally
inputFile = "inputFile.txt"

# Check if the file exists
if os.path.exists(inputFile):
    print("File exists, ERROR CODE: FE101_Betch_L7")
else:
    print("File does not exist, creating a new file.")


def calc_Mean_STDR(ProccessesDictinory,Type):
        mean = 0
        STDR= 0
        mean_And_STDR = []
        NumOfProccesses = len(ProccessesDictinory)
        
        for i in range (NumOfProccesses):
            mean = ProccessesDictinory["P"+str(i)][Type] + mean
        mean = mean/NumOfProccesses

        for n in range (NumOfProccesses):
            STDR = (ProccessesDictinory["P"+str(n)][Type] - mean)**2 + STDR
        STDR = STDR / NumOfProccesses

        STDR = math.sqrt(STDR)
        
        Rounded_Mean = round(mean, 1)
        Rounded_STDR = round(STDR, 1)

        mean_And_STDR.append((Rounded_Mean, Rounded_STDR))
        return mean_And_STDR

def generateDataPoints():
    ProccessesDictinory = {}

    numOf_Processes = random.randint(3, 10) #generate random number between 3 and 10 for proccesses

    # loop the number of proccesses generated
    for i in range(numOf_Processes):
        DIC_process_ID = "P" + str(i)  # convert process ID to string cuz error if not
        DIC_process_ArrivalTime = random.randint(0, 15)
        DIC_process_BurstTime = random.randint(1, 25)

        ProccessesDictinory[DIC_process_ID] = {
            "Arrival Time": DIC_process_ArrivalTime,
            "Burst Time": DIC_process_BurstTime,
            }
    return ProccessesDictinory
        
def generateFileInput(ProccessesDictinory):
        #lambda_value = float(input("What do you want the priorities to be centered around? ")) ##enter value of lambda priority
        lambda_value = random.uniform(4,10)
        lambda_value = round(lambda_value, 1)

        mean_STRD_4_Arrivaltime = calc_Mean_STDR(ProccessesDictinory,"Arrival Time") #Calc Mean and standard deviation for arrival time
        mean_STRD_4_BurstTime = calc_Mean_STDR(ProccessesDictinory,"Burst Time")#Calc Mean and standard deviation for Burst time

        numOf_Processes = len(ProccessesDictinory)#check how many proccesses are there

        with open(inputFile, "w") as file:
            file.write(f"\nProccesses Number: {numOf_Processes}\n")
            file.write(f"Mean and Standard Deviation for Arrival Time: {mean_STRD_4_Arrivaltime}\n")
            file.write(f"Mean and Standard Deviation for Burst Time: {mean_STRD_4_BurstTime}\n")
            file.write(f"Lambda Priority: {lambda_value}\n")

def readFile():
    # Open the file in read mode
    with open("inputFile.txt", "r") as file:
        content = file.read()  # Reads the entire content of the file
        print(content)  # Print the content to the console

dic = generateDataPoints()
generateFileInput(dic)
readFile()
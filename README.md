# Folder Structure

- **InputGenerator.py** – Generates process data and writes initial parameters to an input file.
- **outputGenerator.py** – Reads the input file, refines the data by predicting process metrics, and writes a comprehensive processes file.
- **inputFile.txt** – Auto-generated file containing raw process statistics.
- **processes.txt** – Auto-generated file containing the final merged process details with calculated priorities.

---

# InputGenerator.py

This module is responsible for the initial data generation process. Its key functionalities include:

- **File Management:**  
  Checks for the existence of `inputFile.txt` to avoid data collision. If the file exists, it logs an error message; otherwise, it creates a new file.

- **Process Data Generation:**  
  Randomly generates a set of processes (between 3 and 10). For each process, it assigns:
  - An **arrival time** (random integer between 0 and 15).
  - A **burst time** (random integer between 1 and 25).

- **Statistical Calculation:**  
  Computes the mean and standard deviation for both arrival and burst times using a custom function. These values are crucial for downstream processing.

- **File Output:**  
  Writes the following to `inputFile.txt`:
  - Total number of processes.
  - Calculated mean and standard deviation for arrival and burst times.
  - A randomly generated lambda value representing a priority centering parameter.

---

# outputGenerator.py

This module takes the baton to refine and enhance the initial data. Its primary responsibilities include:

- **Data Extraction:**  
  Reads `inputFile.txt` line-by-line and extracts numerical values using regular expressions. This includes:
  - The number of processes.
  - Mean and standard deviation values for arrival and burst times.
  - The lambda priority value.

- **Data Prediction & Confirmation:**  
  Utilizes NumPy to generate values that align with the extracted statistical parameters. It ensures that:
  - The predicted arrival and burst times closely match the intended mean and standard deviation.
  - The final adjustment of values ensures consistency with the desired sum and distribution properties.

- **Priority Generation:**  
  Generates process priorities using a Poisson distribution, adding an extra layer of realistic randomness to the simulation.

- **Data Merging & Final Output:**  
  Merges the individual data components into a unified dictionary, which is then written to `processes.txt`. The output is formatted neatly in columns for clarity and ease of interpretation.

---

# How to Run

1. **Setup:**  
   Ensure you have Python 3 installed along with the required libraries:
   - `numpy`
   - `math`
   - `random`
   - `re`
   - `os`

2. **Execution:**  
   - Run **InputGenerator.py** first to generate the initial input data:
     ```bash
     python InputGenerator.py
     ```
   - Next, run **outputGenerator.py** to process the data and generate the final output:
     ```bash
     python outputGenerator.py
     ```

3. **Outcome:**  
   Upon successful execution, you'll find `inputFile.txt` and `processes.txt` in the folder, containing detailed process metrics ready for further analysis.

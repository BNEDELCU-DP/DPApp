import csv
import glob
import numpy as np
import os


def custom_sort_key(filename):
    """
    Custom sorting key for filenames.
    Keys as A-1, A-2,..., A-9, A-10, A-11,..., B-1, B-2,..., B-9, B-10,...
    """
    # Split the filename into parts
    parts = filename.split('-')
    
    # Extract the prefix (e.g., 'A') and the number (e.g., '1')
    prefix = parts[0].upper()  # Ensure case insensitivity for the prefix
    number = int(parts[1])     # Convert the number part to an integer for correct numeric sorting
    
    # Return a tuple (prefix, number) for sorting
    return (prefix, number)

def getCSVFiles(csv_files_directory):
    """Return a list with all CSV files in the directory"""
    csv_files_directory = os.path.join(csv_files_directory, "")
    filenames = glob.glob(csv_files_directory + '/*.csv', recursive=True)
    # Sort files using custom sorting key
    sorted_filenames = sorted(filenames, key=custom_sort_key)
    return sorted_filenames   # Return sorted filenames list

def readCSVFile(filename, row_num, skip_rows=0, delimiter=";"):
    """
    Reads a CSV file and returns the values from a specific column.
    :param file: The path to the CSV file.
    :param row_num: The index of the column from which to extract data.
    :param skip_rows: The number of rows to skip (0 for files with a single header, 9 for files with metadata).
    :param delimiter: The separator used in the CSV (default: ";").
    :return: A NumPy array with the extracted values.
    """
    values = []
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file, delimiter=delimiter)
            for _ in range(skip_rows):  # Jump unused lines (metadata + header)
                next(reader, None)
            for row in reader:
                try:
                    # Test if line has enough columns and if data fields are OK
                    if len(row) > row_num and row[row_num]:
                        values.append(float(row[row_num]))
                    else:
                        print(f"Skipping invalid or empty row in {file}: {row}")
                except ValueError:
                    print(f"Skipping invalid value in {file}: {row}")
    
    except FileNotFoundError:
        print(f"Error: File {filename} not found!")
        return np.array([])

    return np.array(values)

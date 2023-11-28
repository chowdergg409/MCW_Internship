import os
import csv

def list_folder_contents(folder_path):
    # Get a list of all files and subdirectories in the folder
    entries = os.listdir(folder_path)

    # Create a CSV file to store the entries
    csv_file_path = 'folder_contents.csv'

    # Check if the file already exists
    if os.path.exists(csv_file_path):
        print("CSV file already exists. Exiting.")
        return

    # Write the entries to the CSV file
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Entry'])

        for entry in entries:
            csv_writer.writerow([entry])

    print(f"CSV file '{csv_file_path}' created successfully.")

# Specify the folder path
folder_path = '/path/to/your/folder'

# Call the function to list folder contents and save to CSV
list_folder_contents(folder_path)

import csv
import os
import shutil

# Path to the CSV file
csv_file = 'more_samples_split.csv'

# Path to the folder where files will be organized
output_folder = 'more_splitted_test_organize/'

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Read the CSV file
with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        document_id = row['DocumentDetailID']
        file_url = row['DocumentS3URL']
        file_type = row['Type']
        file_path = row['FilePath']

        # Create a folder for the file type if it doesn't exist
        type_folder = os.path.join(output_folder, file_type)
        if not os.path.exists(type_folder):
            os.makedirs(type_folder)

        # Copy or move the file to the corresponding folder
        destination_path = os.path.join(type_folder, os.path.basename(file_path))
        shutil.copy2(file_path, destination_path)  # Use shutil.move() if you want to move instead of copy

        print(f"File {file_path} organized into folder {type_folder}.")

print("Organizing files complete.")

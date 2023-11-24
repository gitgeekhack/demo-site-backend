import os
import shutil

# Get the current directory
current_dir = '/Users/siddharthbhavsar/Documents/git/pareit-miscellaneous-scripts/siddharth/organized_files'

# Iterate over all subdirectories in the current directory
for root, dirs, files in os.walk(current_dir):
    for subdir in dirs:
        # Create a new subdirectory within each subdirectory
        new_subdir = os.path.join(root, subdir, 'splitted')
        os.makedirs(new_subdir, exist_ok=True)

        # Move the contents of the subdirectory to the new subdirectory
        subdir_path = os.path.join(root, subdir)
        for file_name in os.listdir(subdir_path):
            file_path = os.path.join(subdir_path, file_name)
            shutil.move(file_path, new_subdir)

print("Subdirectories and contents moved successfully!")

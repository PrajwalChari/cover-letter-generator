import os

# Directory containing the files
directory = "C:/Users/Prajwal Chari/Documents/Cover LEtter/test"

# Initialize counter
rename_count = 0

# Loop through each file in the directory
for filename in os.listdir(directory):
    # Check if '.mov' or '.mp4' is anywhere in the filename
    if '.mov' in filename.lower() or '.mp4' in filename.lower():
        # Find the first occurrence of '.mov' or '.mp4' and retain it
        if '.mov' in filename.lower():
            base_name = filename[:filename.lower().find('.mov') + 4]  # Retain ".mov"
        elif '.mp4' in filename.lower():
            base_name = filename[:filename.lower().find('.mp4') + 4]  # Retain ".mp4"
        
        # Build full paths
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, base_name)
        
        # Rename the file
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {base_name}")
        
        # Increment the counter
        rename_count += 1

# Print the total count of renamed files
print(f"Renaming complete! Total files renamed: {rename_count}")

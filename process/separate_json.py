import json
import os

# Path to the input JSON file
input_json_path = "/raid/data/yindusu/titan_wp3/datasets/java_time_split/test.json"

# Output directory to save the separated files
output_directory = "/raid/data/hhhuang/teamscale_testing/separated_data/java_time_split"

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Load the JSON data
with open(input_json_path, 'r') as json_file:
    data = json.load(json_file)

# Dictionary to collect entries by commit_URL
commit_entries = {}

# Separate entries by commit_URL
for entry in data:
    commit_url = entry.get("commit_URL")
    
    if commit_url:
        # Extract the commit name from the URL
        commit_name = commit_url.split('/')[-1]
        
        # Initialize the list for this commit if it doesn't exist, and append the entry
        if commit_name not in commit_entries:
            commit_entries[commit_name] = []
        commit_entries[commit_name].append(entry)
    else:
        print("Warning: Entry without commit_URL encountered and skipped.")

# Write each list of entries to its respective file
for commit_name, entries in commit_entries.items():
    output_file_path = os.path.join(output_directory, f"{commit_name}.json")
    
    # Save the list of entries to a single JSON file
    with open(output_file_path, 'w') as output_file:
        json.dump(entries, output_file, indent=4)
    
    print(f"Saved {len(entries)} entries to {output_file_path}")

print("All entries have been separated by commit_URL.")
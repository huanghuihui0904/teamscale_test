import json
import re
import os

# Directories
results_dir = "/raid/data/hhhuang/teamscale/teamscale_testing_files/teamscale_results"
true_results_dir = "/raid/data/hhhuang/teamscale/teamscale_testing_files/separated_data/java_time_split"
output_dir = "/raid/data/hhhuang/teamscale/teamscale_testing_files/compare_results"

# Initialize counters
total_matches = 0
matched_files_count = 0

# Process all JSON files in the results directory
for file_name in os.listdir(results_dir):
    if file_name.endswith(".json"):  # Process only JSON files
        result_path = os.path.join(results_dir, file_name)
        true_result_path = os.path.join(true_results_dir, file_name)
        output_file_path = os.path.join(output_dir, file_name)

        try:
            # Load result data
            with open(result_path, 'r') as result_file:
                result_data = json.load(result_file)

            # Load true result data
            with open(true_result_path, 'r') as true_result_file:
                true_result_data = json.load(true_result_file)

            # Iterate through each entry in the true result and append matched results
            processed_true_results = []

            for i, true_entry in enumerate(true_result_data):
                true_file_path = true_entry.get("file")

                if not true_file_path:
                    print(f"No 'file' field found in true result entry {i}. Skipping.")
                    continue

                print(f"Matching true result entry {i} with file path: {true_file_path}")

                # Match entries in the result file
                matches = [
                    entry for entry in result_data
                    if true_file_path in re.sub(r".*#", "", entry.get("file_path", ""))
                ]
                total_matches += len(matches)

                # Add matched results to the true entry
                true_entry["matched_result"] = matches
                processed_true_results.append(true_entry)

                if matches:
                    matched_files_count += 1
                    print(f"Found {len(matches)} matches for true result entry {i}.")
                else:
                    print(f"No matches found for true result entry {i}.")

            # Save the processed true results with matches or empty `matched_result`
            with open(output_file_path, 'w') as output_file:
                json.dump(processed_true_results, output_file, indent=4)

            print(f"Processed true results saved to {output_file_path}")

            # Print the JSON entry count
            print(f"Final JSON entry count in output file: {len(processed_true_results)}")
            print(f"Final JSON entry count in result_data: {len(result_data)}")
            print(f"Final JSON entry count in true_result_data: {len(true_result_data)}")

        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except KeyError as e:
            print(f"Key error: {e}")

# Summary
print(f"Total matches across all files: {total_matches}")
print(f"Total files with matches: {matched_files_count}")
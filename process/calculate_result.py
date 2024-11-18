import json
import re
import os

# Path to the directory containing JSON files
json_dir_path = "/raid/data/hhhuang/teamscale/teamscale_testing_files/compare_results"

def clean_text(text):
    """
    Clean the text by removing extra spaces, newline characters, and tabs.
    """
    return re.sub(r'\s+', ' ', text.strip())

# Initialize counters
total_true_positives = 0  # TP
total_false_negatives = 0  # FN
total_predictions = 0      # TP + FP

# Process each JSON file in the directory
for file_name in os.listdir(json_dir_path):
    if file_name.endswith(".json"):  # Process only JSON files
        file_path = os.path.join(json_dir_path, file_name)

        # Load the JSON file
        with open(file_path, "r") as file:
            data = json.load(file)

        # Ensure the data is a list (if the JSON contains multiple entries)
        if not isinstance(data, list):
            data = [data]

        # Initialize counters for the current file
        true_positives = 0
        false_negatives = 0
        predictions = 0

        for entry in data:
            function_content = clean_text(entry.get("function", ""))
            matched_results = entry.get("matched_result", [])
            entry_id = entry.get("id", "unknown")

            print(f"Checking entry ID: {entry_id} in file: {file_name}")
            found_match = False

            for result in matched_results:
                extracted_content = clean_text(result.get("extracted_content", ""))
                predictions += 1  # Every checked result is a prediction (TP + FP)
                if extracted_content in function_content:
                    print(f"Match found in function for extracted content in file: {file_name}")
                    true_positives += 1  # True Positive
                    found_match = True
                    break  # Stop checking other matched_results for this entry
                else:
                    print(f"No match found in function for extracted content in file: {file_name}")

            # If no match was found for the current entry, it counts as a False Negative
            if not found_match and matched_results:
                false_negatives += 1

        print(f"File: {file_name} - TP: {true_positives}, FN: {false_negatives}, Total Predictions: {predictions}")
        total_true_positives += true_positives
        total_false_negatives += false_negatives
        total_predictions += predictions

# Calculate precision and recall
precision = total_true_positives / total_predictions if total_predictions > 0 else 0
recall = total_true_positives / (total_true_positives + total_false_negatives) if (total_true_positives + total_false_negatives) > 0 else 0

print(f"Total True Positives (TP): {total_true_positives}")
print(f"Total False Negatives (FN): {total_false_negatives}")
print(f"Total Predictions (TP + FP): {total_predictions}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
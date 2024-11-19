import json
import os
import re

# Directories
results_dir = "/raid/data/hhhuang/teamscale/teamscale_testing_files/teamscale_results"
true_results_dir = "/raid/data/hhhuang/teamscale/teamscale_testing_files/separated_data/java_time_split"

# Initialize counters
total_matches = 0
matched_files_count = 0

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)
def clean_text(text):
    """
    Clean the text by removing extra spaces, newline characters, and tabs.
    """
    return re.sub(r'\s+', ' ', text.strip())

# Initialize counters
true_positive = 0  # TP
false_negative = 0  # FN
false_positive = 0  # FP
true_negative = 0  # TN
# Process all JSON files in the results directory
for file_name in os.listdir(results_dir):
    if file_name.endswith(".json"):  # Process only JSON files
        result_path = os.path.join(results_dir, file_name)
        true_result_path = os.path.join(true_results_dir, file_name)

        try:
            # Load result data
            with open(result_path, 'r') as result_file:
                result_data = json.load(result_file)

            # Load true result data
            with open(true_result_path, 'r') as true_result_file:
                true_result_data = json.load(true_result_file)


            # Compare `extracted_content` from each result entry with all functions in the true results
            for result_entry in result_data:
                extracted_content = clean_text(result_entry.get("extracted_content", ""))

                if not extracted_content:
                    print(f"No 'extracted_content' found in result entry. Skipping.")
                    continue

                # Check if `extracted_content` matches any function in the true results
                for true_entry in true_result_data:
                    function_content = clean_text(true_entry.get("function", ""))
                    label=true_entry.get("vulnerable", 0)
                    

                    prediction = int(extracted_content in function_content)

                    if prediction ==1 and label ==1:
                        true_positive +=1
                    elif prediction ==0 and label ==1:
                        false_negative +=1
                    elif prediction ==1 and label ==0:
                        false_positive +=1
                    elif prediction ==0 and label ==0:
                        true_negative +=1

        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except KeyError as e:
            print(f"Key error: {e}")


# Calculate precision, recall, and accuracy
precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0
accuracy = (true_positive + true_negative) / (true_positive + true_negative + false_positive + false_negative) if (true_positive + true_negative + false_positive + false_negative) > 0 else 0
f03_score = (1+0.3*0.3)*(precision*recall)/(0.3*0.3*precision+recall)
f1_score =  (2)*(precision*recall)/(1*precision+recall)
print(f"Total True Positives (TP): {true_positive}")
print(f"Total False Negatives (FN): {false_negative}")
print(f"Total False Positives (FP): {false_positive}")
print(f"Total True Negatives (TN): {true_negative}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"Accuracy: {accuracy:.4f}")
print(f"f03_score: {f03_score:.4f}")
print(f"f1_score: {f1_score:.4f}")
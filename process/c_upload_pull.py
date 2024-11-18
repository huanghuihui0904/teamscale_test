import os
import json
import time
from urllib.parse import urlparse
from teamscale_client.client import TeamscaleClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Step 1: Define Teamscale server details and credentials from environment variables
TEAMSCALE_SERVER_URL = os.getenv("TEAMSCALE_SERVER_URL")
USERNAME = os.getenv("USERNAME")
API_TOKEN = os.getenv("API_TOKEN")
PROJECT_ID = os.getenv("PROJECT_ID")

# Step 2: Initialize the Teamscale client
# Function to initialize the Teamscale client
def initialize_client():
    return TeamscaleClient(
        url=TEAMSCALE_SERVER_URL,
        username=USERNAME,
        access_token=API_TOKEN,
        project=PROJECT_ID
    )

# Directory to search for matching commit hash
root_base_dir = "/raid/data/hhhuang/teamscale/teamscale_testing_files/repos4/java_time_split"

# JSON file containing entries with file paths and commit URLs
json_file_path = "/raid/data/hhhuang/teamscale/teamscale_testing_files/separated_data/java_time_split/02b8792e6f4b829f0c1d87fcbf2d58b73458b938.json"

# Results JSON file
results_file_path = "teamscale_results.json"

# Failed findings JSON file
failed_findings_file_path = "failed_findings.json"

# Ensure results and failed findings files exist
for path in [results_file_path, failed_findings_file_path]:
    if not os.path.exists(path):
        with open(path, "w") as file:
            json.dump([], file)

# Function to append results to a JSON file
def append_to_json_file(file_path, data):
    try:
        with open(file_path, "r+") as file:
            # Load existing results
            existing_data = json.load(file)
            # Append the new data
            existing_data.append(data)
            # Write updated results back to the file
            file.seek(0)
            json.dump(existing_data, file, indent=2)
            file.truncate()  # Ensure old content is removed
    except Exception as e:
        print(f"Error updating file {file_path}: {e}")

# Function to convert finding objects into dictionaries
def serialize_finding(finding):
    return {
        "finding_id": getattr(finding, "finding_id", None),
        "findingTypeId": getattr(finding, "findingTypeId", None),
        "message": getattr(finding, "message", None),
        "startOffset": getattr(finding, "startOffset", None),
        "endOffset": getattr(finding, "endOffset", None),
        "startLine": getattr(finding, "startLine", None),
        "endLine": getattr(finding, "endLine", None),
        "identifier": getattr(finding, "identifier", None),
        "uniformPath": getattr(finding, "uniformPath", None),
        "findingProperties": getattr(finding, "findingProperties", None),
        "assessment": getattr(finding, "assessment", None)
    }

# Function to extract lines from a file
def extract_lines(file_path, start_line, end_line):
    """Extract lines from start_line to end_line (1-indexed) from the file."""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            return ''.join(lines[start_line - 1:end_line])
    except Exception as e:
        print(f"Error extracting lines from {file_path}: {e}")
        return None

# Function to submit and fetch findings with retries, including client reinitialization
def submit_and_fetch_findings(java_file_path, commit_hash, file_content, max_retries=10, delay=10):
    retries = 0
    while retries < max_retries:
        try:
            # Reinitialize the client
            client = initialize_client()
            print(f"Reinitialized Teamscale client (Attempt {retries + 1}/{max_retries}).")

            # Prepare the pre-commit data
            timestamp = datetime.now()
            precommit_data = {
                "deletedUniformPaths": [],
                "uniformPathToContentMap": {java_file_path: file_content}
            }

            # Resubmit the file for pre-commit analysis
            print(f"Uploading {java_file_path} for analysis...")
            response = client.upload_files_for_precommit_analysis(
                timestamp=timestamp,
                precommit_data=precommit_data
            )

            if response.status_code != 202:
                raise Exception(f"Failed to upload file {java_file_path}: {response.status_code} - {response.text}")

            print(f"File {java_file_path} upload accepted. Waiting for analysis to complete...")
            time.sleep(5)

            # Fetch findings
            print(f"Attempting to fetch findings for {java_file_path}...")
            added_findings, findings_in_changed_code, removed_findings = client.get_precommit_analysis_results()
            return added_findings, findings_in_changed_code, removed_findings

        except Exception as e:
            retries += 1
            print(f"Error: {e}. Retrying in {delay} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(delay)

    print(f"Failed to retrieve findings for {java_file_path} after {max_retries} attempts.")
    return None

# Step 3: Read the JSON file and process each entry
with open(json_file_path, 'r') as json_file:
    entries = json.load(json_file)



# Step 4: Process each entry
for entry in entries:
    try:
        # Extract the file path and commit URL
        java_file_path = entry.get("file")
        commit_url = entry.get("commit_URL")

        if not java_file_path or not commit_url:
            print("Missing 'file' or 'commit_URL' field in the entry. Skipping...")
            continue

        # Extract commit hash from the commit URL
        commit_hash = commit_url.split("/")[-1]

        # Check for matching directory
        matched_dir = None
        for subdir in os.listdir(root_base_dir):
            if f"#{commit_hash}" in subdir:
                matched_dir = subdir
                break

        if not matched_dir:
            print(f"No matching directory found for commit hash {commit_hash}. Skipping...")
            continue

        # Construct the file path
        base_dir = os.path.join(root_base_dir, matched_dir)
        local_file_path = os.path.join(base_dir, java_file_path)

        if not os.path.exists(local_file_path):
            print(f"File not found: {local_file_path}. Skipping...")
            continue

        # Read the file content
        with open(local_file_path, 'r') as file:
            file_content = file.read()

        # Submit and fetch findings
        findings = submit_and_fetch_findings(java_file_path, commit_hash, file_content)

        if findings is None:
            # Store in failed findings file
            failed_entry = {
                "file": java_file_path,
                "commit_hash": commit_hash,
                "error": "Analysis not finished after maximum retries"
            }
            append_to_json_file(failed_findings_file_path, failed_entry)
            print(f"Findings for {java_file_path} could not be retrieved. Stored in {failed_findings_file_path}")
            continue

        # Filter findings where assessment = "RED"
        added_findings, findings_in_changed_code, removed_findings = findings
        red_findings = []
        for finding in added_findings:
            if getattr(finding, "assessment", None) == "RED":
                serialized_finding = serialize_finding(finding)
                # Extract the content based on startLine and endLine
                start_line = serialized_finding.get("startLine")
                end_line = serialized_finding.get("endLine")
                extracted_content = extract_lines(local_file_path, start_line, end_line)
                if extracted_content is not None:
                    serialized_finding["extracted_content"] = extracted_content
                red_findings.append(serialized_finding)

        # Skip if no RED findings
        if not red_findings:
            print(f"No RED findings for {java_file_path}. Skipping storage...")
            continue

        # Append RED findings to the results file immediately
        findings_data = {
            "file": java_file_path,
            "commit_hash": commit_hash,
            "red_findings": red_findings,
        }
        append_to_json_file(results_file_path, findings_data)
        print(f"RED findings for file {java_file_path} appended to {results_file_path}")

    except Exception as e:
        print(f"An error occurred while processing {java_file_path}: {e}")
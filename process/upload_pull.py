import os
import json
import time
import logging
from teamscale_client.client import TeamscaleClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Teamscale configuration
TEAMSCALE_SERVER_URL = os.getenv("TEAMSCALE_SERVER_URL")
USERNAME = os.getenv("USERNAME")
API_TOKEN = os.getenv("API_TOKEN")
PROJECT_ID = os.getenv("PROJECT_ID")

# Root directory containing subdirectories
root_base_dir = "/raid/data/hhhuang/teamscale/teamscale_testing_files/repos4/java_time_split"

# Directory for storing results
results_dir = "/raid/data/hhhuang/teamscale/teamscale_testing_files/teamscale_results"
results_dir2="/raid/data/hhhuang/teamscale/teamscale_testing_files/teamscale_results2"

os.makedirs(results_dir, exist_ok=True)
os.makedirs(results_dir2, exist_ok=True)

# Configure logging
log_file = "process.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file,mode='w'),
    ]
)

# Initialize Teamscale client
def initialize_client():
    logging.info("Initializing Teamscale client...")
    return TeamscaleClient(
        url=TEAMSCALE_SERVER_URL,
        username=USERNAME,
        access_token=API_TOKEN,
        project=PROJECT_ID
    )

# Function to recursively collect all files in a directory
def get_all_files_in_directory(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    logging.info(f"Collected {len(file_paths)} files from directory: {directory}")
    return file_paths

# Read file content
def read_file_content(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None

# Extract lines from a file
def extract_lines(file_path, start_line, end_line):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            return ''.join(lines[start_line - 1:end_line])
    except Exception as e:
        logging.error(f"Error extracting lines from {file_path}: {e}")
        return None

def submit_and_fetch_findings_with_retries(batch_files, commit_id, max_retries=10, delay=10):
    """
    Submit a batch of files for pre-commit analysis, fetch findings, and retry the entire process if any part fails.
    """
    retries = 0
    while retries < max_retries:
        try:
            # Initialize the client
            client = initialize_client()
            logging.info(f"Initialized Teamscale client (Attempt {retries + 1}/{max_retries}) for commit {commit_id}.")

            # Prepare the pre-commit data
            timestamp = datetime.now()
            precommit_data = {
                "deletedUniformPaths": [],
                "uniformPathToContentMap": {  file_path.lstrip('/'): read_file_content(file_path) for file_path in batch_files}
            }

            # Filter out files with no content
            precommit_data["uniformPathToContentMap"] = {
                path: content
                for path, content in precommit_data["uniformPathToContentMap"].items()
                if content is not None
            }

            if not precommit_data["uniformPathToContentMap"]:
                logging.warning(f"No valid files to submit for commit {commit_id}. Skipping...")
                return None

            # Submit the batch for pre-commit analysis
            logging.info(f"Submitting batch of {len(precommit_data['uniformPathToContentMap'])} files for commit {commit_id}.")
            response = client.upload_files_for_precommit_analysis(
                timestamp=timestamp,
                precommit_data=precommit_data
            )

            if response.status_code != 202:
                raise Exception(f"Failed to submit batch for commit {commit_id}: {response.status_code} - {response.text}")

            logging.info(f"Batch submitted successfully for commit {commit_id}. Waiting for analysis to complete...")
            time.sleep(5)  # Wait before pulling findings

            # Fetch findings
            logging.info(f"Attempting to fetch findings for commit {commit_id}.")
            added_findings, findings_in_changed_code, removed_findings = client.get_precommit_analysis_results()
            logging.info(f"Findings fetched successfully for commit {commit_id}.")
            return added_findings, findings_in_changed_code, removed_findings

        except Exception as e:
            retries += 1
            logging.error(
                f"Error during submission or fetching findings for commit {commit_id} (Attempt {retries}/{max_retries}): {e}"
            )
            time.sleep(delay)

    logging.error(f"Failed to complete submission and retrieval after {max_retries} attempts for commit {commit_id}.")
    return None

# Store findings in a JSON file
def store_red_findings(commit_id, findings_data):
    output_file = os.path.join(results_dir, f"{commit_id}.json")
    try:
        with open(output_file, "w") as file:
            json.dump(findings_data, file, indent=2)
        logging.info(f"Findings stored in {output_file}")
    except Exception as e:
        logging.error(f"Error storing findings for commit {commit_id}: {e}")

def store_all_findings(commit_id, findings_data):
    output_file = os.path.join(results_dir2, f"{commit_id}.json")
    try:
        with open(output_file, "w") as file:
            json.dump(findings_data, file, indent=2)
        logging.info(f"Findings stored in {output_file}")
    except Exception as e:
        logging.error(f"Error storing findings for commit {commit_id}: {e}")

# Process subdirectories recursively
def process_subdirectories():
    for subdir in os.listdir(root_base_dir):
        subdir_path = os.path.join(root_base_dir, subdir)

        if not os.path.isdir(subdir_path):
            continue

        # Extract commit ID from subdir name
        commit_id = subdir.split("#")[-1]
        logging.info(f"Processing commit: {commit_id}")

        # Collect all files in the subdirectory recursively
        all_files = get_all_files_in_directory(subdir_path)

        if not all_files:
            logging.warning(f"No files found in {subdir_path}. Skipping...")
            continue

        # Submit and fetch findings
        findings = submit_and_fetch_findings_with_retries(all_files, commit_id)

        if findings:
            added_findings, findings_in_changed_code, removed_findings = findings
            red_findings = []
            all_findings = []

            # Process findings
            for finding in added_findings:
                # Extract common attributes for all findings
                start_line = getattr(finding, "startLine", None)
                end_line = getattr(finding, "endLine", None)
                file_path = getattr(finding, "uniformPath", None)
                assessment = getattr(finding, "assessment", None)
                file_path="/"+file_path

                # Extract content for the finding
                file_content = None
                if file_path and start_line and end_line:
                    file_content = extract_lines(file_path, start_line, end_line)

                # Prepare the finding data
                finding_data = {
                    "finding_id": getattr(finding, "finding_id", None),
                    "assessment": assessment,
                    "message": getattr(finding, "message", None),
                    "file_path": file_path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "extracted_content": file_content,
                }

                # Append to the all_findings list
                all_findings.append(finding_data)

                # Append to the red_findings list if assessment is RED
                if assessment == "RED":
                    red_findings.append(finding_data)

            # Store both RED findings and all findings
            store_red_findings(commit_id, red_findings)
            store_all_findings(commit_id, all_findings)
        else:
            logging.error(f"Failed to process {subdir_path}")
            failed_entry = {
                "directory": subdir_path,
                "commit_id": commit_id,
                "files_attempted": len(all_files),
                "error": "Batch submission or finding retrieval failed"
            }
            store_all_findings(f"failed_{commit_id}", failed_entry)

# Start processing
process_subdirectories()
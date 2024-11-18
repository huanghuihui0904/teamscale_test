import requests
from urllib.parse import urlparse
import os
import json
import logging
import base64  # For decoding base64 file content
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Directory containing JSON files
json_dir = "/raid/data/hhhuang/teamscale_testing_files/separated_data/java_time_split"
output_dir = "/raid/data/hhhuang/teamscale_testing_files/repos2/java_time_split"

# Load GitHub token from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

# Set up logging configuration
logging.basicConfig(
    filename='download_changed_java_files.log',  # Log file name
    level=logging.INFO,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
)

def fetch_changed_files(repo, commit_hash):
    """Fetch the list of changed files in the commit."""
    commit_url = f"https://api.github.com/repos/{repo}/commits/{commit_hash}"
    response = requests.get(commit_url, headers=headers)

    if response.status_code == 200:
        commit_data = response.json()
        if 'files' in commit_data:
            return commit_data['files']
        else:
            logging.error(f"No 'files' field in commit data for {commit_hash}.")
            return None
    else:
        logging.error(f"Failed to fetch commit details for {commit_hash}: {response.status_code} - {response.text}")
        return None

def download_file(repo, commit_hash, file_path):
    """Download a specific file from the commit."""
    file_url = f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={commit_hash}"
    try:
        response = requests.get(file_url, headers=headers)

        if response.status_code == 200:
            file_data = response.json()
            if 'content' in file_data and file_data['encoding'] == 'base64':
                # Decode base64 file content
                decoded_content = base64.b64decode(file_data['content']).decode('utf-8')

                # Define the output file path
                output_file_path = os.path.join(output_dir, f"{repo.replace('/', '@')}#{commit_hash}", file_path)
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

                # Write decoded content to the file
                with open(output_file_path, 'w') as output_file:
                    output_file.write(decoded_content)

                logging.info(f"Downloaded and saved file: {output_file_path}")
                return True
            else:
                logging.error(f"File {file_path} is not base64 encoded or 'content' field is missing.")
        else:
            logging.error(f"Failed to fetch file {file_path} from commit {commit_hash}: "
                          f"{response.status_code} - {response.text}")
        return False
    except Exception as e:
        logging.error(f"Exception occurred while downloading file {file_path} from commit {commit_hash}: {e}")
        return False

# Process each JSON file in the directory
for filename in os.listdir(json_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(json_dir, filename)

        # Load the JSON file and process its contents
        with open(filepath, "r") as json_file:
            try:
                data = json.load(json_file)
                if not isinstance(data, list):
                    logging.warning(f"File {filename} is not in the expected list format. Skipping...")
                    continue

                # for entry in data:
                entry = data[0]
                # Extract the "commit_URL" for each entry
                commit_url = entry.get("commit_URL")
                if not commit_url:
                    logging.warning(f"Missing 'commit_URL' in an entry of {filename}. Skipping entry...")
                    continue

                # Parse the commit URL to extract owner, repo, and commit hash
                parsed_url = urlparse(commit_url)
                path_parts = parsed_url.path.strip("/").split("/")
                if len(path_parts) < 4:
                    logging.error(f"Invalid commit URL format in {filename}: {commit_url}")
                    continue

                owner = path_parts[0]
                repo = path_parts[1]
                commit_hash = path_parts[3]
                full_repo_name = f"{owner}/{repo}"

                # Fetch the changed files in the commit
                logging.info(f"Fetching changed files for {commit_hash} in repository {full_repo_name}")
                changed_files = fetch_changed_files(full_repo_name, commit_hash)

                if changed_files:
                    # Download only .java files from the changed files
                    for file_info in changed_files:
                        if file_info['filename'].endswith('.java'):
                            download_file(full_repo_name, commit_hash, file_info['filename'])

                    logging.info(f"All changed .java files from commit {commit_hash} downloaded successfully.")
                else:
                    logging.error(f"No changed files found for commit {commit_hash}.")
            except Exception as e:
                logging.error(f"Exception occurred while processing file {filename}: {e}")
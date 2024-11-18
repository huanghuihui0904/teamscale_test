import requests
from urllib.parse import urlparse
import os
import json
import zipfile
import logging  # Import the logging module
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Directory containing JSON files
json_dir = "/raid/data/hhhuang/teamscale_testing/separated_data/java_time_split"
output_dir = "/raid/data/hhhuang/teamscale_testing/repos/java_time_split"

# Load GitHub token from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

# Set up logging configuration
logging.basicConfig(
    filename='download_repos.log',  # Log file name
    level=logging.INFO,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
)

def download_version_repo(repo, commit_hash):
    # GitHub API endpoint to get repository tags
    tags_url = f"https://api.github.com/repos/{repo}/tags"
    response = requests.get(tags_url, headers=headers)

    # Raise an exception if the tags couldn't be fetched
    if response.status_code != 200:
        logging.error(f"Failed to fetch tags: {response.status_code} - {response.text}")
        raise Exception(f"Failed to fetch tags: {response.status_code} - {response.text}")
    
    # Parse the response JSON to get the list of tags
    tags = response.json()
    for tag in tags:
        if 'name' in tag and 'zipball_url' in tag:
            tag_name = tag['name'].replace("/", "_")
            zipball_url = tag['zipball_url']
            logging.info(f"Found tag: {tag_name} with zipball URL: {zipball_url}")
            
            # Fetch the zipball file
            zip_response = requests.get(zipball_url, headers=headers)
            if zip_response.status_code == 200:
                zip_filename = f"{tag_name}.zip"
                
                # Save the zipball content to a local file
                with open(zip_filename, "wb") as zip_file:
                    zip_file.write(zip_response.content)
                logging.info(f"Downloaded zipball for tag {tag_name} as {zip_filename}")
                
                # Define the extraction directory
                extract_dir = os.path.join(output_dir, f"{repo.replace('/', '@')}#{commit_hash}#{tag_name}")
                
                # Skip extraction if directory already exists
                if os.path.exists(extract_dir):
                    logging.info(f"Directory {extract_dir} already exists, skipping extraction.")
                    os.remove(zip_filename)
                    return True
                
                # Unzip the downloaded file
                with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                logging.info(f"Extracted contents of {zip_filename} to {extract_dir}")

                # Clean up by deleting the zip file
                os.remove(zip_filename)
                logging.info(f"Removed temporary zip file {zip_filename}")
            else:
                logging.error(f"Failed to download zipball for tag {tag_name}: {zip_response.status_code}")
            return True  # Stop after the first matching tag
    
    return False

# Process each JSON file in the directory
for filename in os.listdir(json_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(json_dir, filename)
        
        # Load the JSON file and get the first entry
        with open(filepath, "r") as json_file:
            data = json.load(json_file)
            if not data:
                logging.warning(f"File {filename} is empty or not in the expected format.")
                continue
            
            # Read the first entry and extract the "commit_URL" property
            first_entry = data[0] if isinstance(data, list) else data
            commit_url = first_entry.get("commit_URL")
            if not commit_url:
                logging.warning(f"No 'commit_URL' found in the first entry of {filename}.")
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

            # Download the repository version associated with the commit
            logging.info(f"Processing commit {commit_hash} in repository {full_repo_name} from {filename}")
            version = download_version_repo(full_repo_name, commit_hash)

            # Log the result
            if version:
                logging.info(f"Repository for commit {commit_hash} downloaded and extracted successfully.")
            else:
                logging.info(f"No version tag found for commit {commit_hash} or its ancestors.")
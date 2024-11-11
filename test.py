import requests
from teamscale_client.client import TeamscaleClient
from teamscale_client.data import ProjectConfiguration, GitSourceCodeConnectorConfiguration
from teamscale_client.constants import ConnectorType
import time
from datetime import datetime

# Step 1: Define your Teamscale server details and credentials
TEAMSCALE_SERVER_URL = "http://10.0.104.40:8081"  # Replace with your Teamscale server URL
USERNAME = "admin"  # Replace with your Teamscale username
API_TOKEN = "erjIBjeSWjf4qiuFo72tlm1zwLfBlMzc"  # Replace with your Teamscale API token
PROJECT_ID = "your-project-id"


# # Step 2: Define repository configuration for the public project
repository_connector = GitSourceCodeConnectorConfiguration(
    connector_type=ConnectorType.GIT,  # Specify the connector type as Git
    included_file_names="**/*.java",  # Include all Java files (change based on your file type if needed)
    default_branch_name="main",  # Branch you want Teamscale to analyze
    account="huanghuihui0904",  # Set account to an empty string for public repositories
    repository_identifier="public-repo"  # Unique identifier for this repository in Teamscale
    # Optional parameters can be left as defaults
)


# Step 3: Define the project configuration with a Java-specific profile
project_config = ProjectConfiguration(
    name="Your Project Name",  # Display name for your project
    project_id=PROJECT_ID,  # Unique project ID, lowercase, no spaces
    profile="Java (default)",  # Set the profile to "java" or a Java-specific profile if available
    connectors=[repository_connector]  # Add repository connector to the project configuration
)

# # Step 4: Initialize the Teamscale client
# client = TeamscaleClient(
#     url=TEAMSCALE_SERVER_URL,
#     username=USERNAME,
#     access_token=API_TOKEN,
#     project=None  # No project specified yet, as we're creating a new one
# )

# # Step 5: Create the project in Teamscale
# try:
#     response = client.create_project(project_configuration=project_config)
#     if response.status_code in [200, 201]:  # Accept 201 as a success status for project creation
#         print("Project created successfully!")
#     else:
#         print(f"Failed to create project: {response.status_code} - {response.text}")
# except Exception as e:
#     print(f"An error occurred: {e}")



# Step 6: Upload the source code to Teamscale

client = TeamscaleClient(
    url=TEAMSCALE_SERVER_URL,
    username=USERNAME,
    access_token=API_TOKEN,
    project=PROJECT_ID
)
java_file_path = "src/main/java/org/folio/des/security/AuthService.java"
local_file_path = "/raid/data/hhhuang/teamscale_testing/src/main/java/org/folio/des/security/AuthService.java"  # Path to the file on your local system
timestamp = datetime.now()
message = "Uploading AuthService.java for analysis"

# Read the file content
with open(local_file_path, 'r') as file:
    file_content = file.read()

# Prepare the precommit data
# precommit_data = {
#     "deletedUniformPaths": [],  # No files are deleted in this example
#     "uniformPathToContentMap": {java_file_path: file_content}  # Map file path to its content
# }
# # Upload the file for pre-commit analysis
# try:
#     response = client.upload_files_for_precommit_analysis(
#         timestamp=timestamp,
#         precommit_data=precommit_data
#     )
#     if response.status_code == 202:
#         print("File upload accepted. Waiting for analysis to complete...")
#     else:
#         print(f"Failed to upload file: {response.status_code} - {response.text}")
# except Exception as e:
#     print(f"An error occurred while uploading the file: {e}")


# Step 7: Poll for findings 
try:
    # Wait for pre-commit analysis results
    added_findings, findings_in_changed_code, removed_findings = client.get_precommit_analysis_results()

    # Output findings for each category
    print("Added Findings:")
    for finding in added_findings:
        print(f"ID: {finding.finding_id}, Description: {finding.message}")

    print("\nFindings in Changed Code:")
    for finding in findings_in_changed_code:
        print(f"ID: {finding.finding_id}, Description: {finding.message}")

    print("\nRemoved Findings:")
    for finding in removed_findings:
        print(f"ID: {finding.finding_id}, Description: {finding.message}")

except Exception as e:
    print(f"An error occurred while retrieving pre-commit analysis results: {e}")
    

    
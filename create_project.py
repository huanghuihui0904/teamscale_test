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

# Step 4: Initialize the Teamscale client
client = TeamscaleClient(
    url=TEAMSCALE_SERVER_URL,
    username=USERNAME,
    access_token=API_TOKEN,
    project=None  # No project specified yet, as we're creating a new one
)

# Step 5: Create the project in Teamscale
try:
    response = client.create_project(project_configuration=project_config)
    if response.status_code in [200, 201]:  # Accept 201 as a success status for project creation
        print("Project created successfully!")
    else:
        print(f"Failed to create project: {response.status_code} - {response.text}")
except Exception as e:
    print(f"An error occurred: {e}")




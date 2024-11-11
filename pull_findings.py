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

# Step 6: Upload the source code to Teamscale

client = TeamscaleClient(
    url=TEAMSCALE_SERVER_URL,
    username=USERNAME,
    access_token=API_TOKEN,
    project=PROJECT_ID
)

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
    

    
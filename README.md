# AI Reporting Tool

This tool automates the generation of executive reports for engineering teams. It fetches project data from GitHub Projects, generates a narrative summary using Google's Gemini AI, and publishes the results to Google Sheets and Google Docs.

## Features

*   **Data Ingestion**: Queries GitHub GraphQL API for Project V2 items (Issues, PRs, Status).
*   **AI Analysis**: Uses Google Gemini 2.5 Flash to generate an executive summary (Achievements, Risks, Issues, Utilization).
*   **Reporting**:
    *   Appends metrics and summaries to a Google Sheet log.
    *   Appends formatted text reports to a specific Google Doc.

## Prerequisites

### 1. Python Environment
Ensure you have Python 3.x installed. This project uses Python, not Node.js, so we will use `pip` for dependency management.

### 2. Google Cloud Setup
*   Create a **Google Cloud Project**.
*   Enable the following APIs:
    *   Google Sheets API
    *   Google Drive API
    *   Google Docs API
*   Create a **Service Account** and download the JSON key file.
    *   *Note: You do not need to assign specific IAM roles (like Owner/Editor) to the Service Account in the Google Cloud Console. Access is granted via file sharing.*
*   Rename the key file to `service_account.json` and place it in the project root.
*   **Important**: Share your target Google Sheet and Google Doc with the `client_email` address found inside `service_account.json` (give it "Editor" access).

### 3. API Keys
You will need the following keys:
*   **GitHub Token**: A Personal Access Token (Classic) with `project` and `repo` scopes.
*   **Gemini API Key**: An API key from Google AI Studio.

## Installation

Install the required Python libraries:

```bash
pip install requests gspread oauth2client google-api-python-client httplib2
```

## Configuration

1.  Ensure `service_account.json` is in the root folder.
2.  Create or update `config.py` in the root folder with your specific IDs and keys. **Do not commit this file to version control.**

```python
# config.py
GITHUB_TOKEN = 'your_github_pat_here'
GEMINI_API_KEY = 'your_gemini_key_here'
PROJECT_ID = 'your_github_project_node_id'
SHEET_NAME = "Google Sheet Name"
DOC_NAME = "Google Doc Name"
```

## Usage

### Generating a Summary
To fetch data and generate the AI summary to the console:
```bash
python gitHubAISummary.py
```

### Writing to Docs and Sheets
To write the generated report to Google Docs and Sheets:
```bash
python writeToGoogleDoc.py
```

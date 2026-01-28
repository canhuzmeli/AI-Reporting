import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime

# pip install google-api-python-client httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2
import config

# --- CONFIGURATION ---

def write_to_sheets(summary_data):
    """Logs the executive summary and metrics into Google Sheets."""
    # Define the scope and authorize
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # You will need a 'service_account.json' file from Google Cloud Console
    creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
    client = gspread.authorize(creds)
    
    sheet = client.open(config.SHEET_NAME).worksheet("Engagement_Log")
    
    new_row = [
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Multi-Team",  # Type
        "Internal Product Teams", # Customer
        "85%", # Utilization Metric (Focus #3)
        "Active", # Status
        summary_data # The Gemini Narrative
    ]
    
    sheet.append_row(new_row)

def write_to_google_doc(text, document_name):
    """Finds a Google Doc by name and appends text to it.

    Note: You must share the Google Doc with the service account's email address,
    which can be found in your 'service_account.json' file.
    """
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    SCOPES = [
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/documents'
    ]

    try:
        # 1. Authenticate and build services using oauth2client
        creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
        http_auth = creds.authorize(httplib2.Http())
        drive_service = build('drive', 'v3', http=http_auth)
        docs_service = build('docs', 'v1', http=http_auth)

        # 2. Find the Google Doc by name to get its ID
        # The query searches for files with the exact name and the Google Docs mime type.
        query = f"name='{document_name}' and mimeType='application/vnd.google-apps.document'"
        response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = response.get('files', [])

        if not files:
            print(f"Error: No Google Doc found with the name '{document_name}'.")
            print("Please ensure the document exists and you have shared it with the service account email.")
            return

        # Assuming the first match is the correct one.
        doc_id = files[0].get('id')
        print(f"Found document '{files[0].get('name')}' with ID: {doc_id}")

        # 3. Append text to the document
        # First, get the document to find the end of the body.
        document = docs_service.documents().get(documentId=doc_id).execute()
        end_index = document.get('body').get('content')[-1].get('endIndex')

        # Prepare the request to insert text at the end of the document.
        # We insert at end_index - 1 to be just before the document's final newline.
        requests_body = {
            'requests': [
                {
                    'insertText': {
                        'location': {
                            'index': end_index - 1,
                        },
                        'text': text
                    }
                }
            ]
        }

        docs_service.documents().batchUpdate(
            documentId=doc_id, body=requests_body).execute()
        
        print(f"Successfully wrote to document: {document_name}")

    except HttpError as err:
        print(f"An API error occurred: {err}")
    except FileNotFoundError:
        print(f"Error: The service account key file '{SERVICE_ACCOUNT_FILE}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    # This is an example of how you might use these functions.
    # In a real scenario, you would uncomment and complete the logic.
    
    # 1. Fetch from GitHub (using logic from gitHubAISummary.py)
    # ... raw_data = fetch_github_project_data() ...
    
    # 2. Get Narrative from Gemini
    # ... summary = get_gemini_summary(raw_data) ...
    summary = "This is a test summary for the Google Doc." # Example data
    
    # 3. Save to Google Sheets
    #print("Logging to Google Sheets...")
    # write_to_sheets(summary) # Commented out for this example
    #print("Skipping sheet write for this example.")

    # 4. Save to Google Docs
    print("\nLogging to Google Docs...")
    doc_name = "Project Report" # The name of the Google Doc you want to write to
    doc_text = f"\n\n--- Report Generated on {datetime.now().strftime('%Y-%m-%d')} ---\n{summary}"
    write_to_google_doc(doc_text, doc_name)
    
    print("\nReport complete.")

if __name__ == "__main__":
    main()
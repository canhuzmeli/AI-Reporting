#pip install requests needed
import requests
import json
from datetime import datetime
import config

# --- CONFIGURATION ---


def fetch_github_project_data():
    """Fetches items and metadata from GitHub Project V2."""
    url = "https://api.github.com/graphql"
    
    # This query retrieves the last 40 items, their titles, bodies, and 'Status' field
    query = """
    query($id: ID!) {
      node(id: $id) {
        ... on ProjectV2 {
          items(first: 40) {
            nodes {
              updatedAt
              content {
                ... on PullRequest {
                  title
                  body
                  state
                  createdAt
                  updatedAt
                  mergedAt
                  author { login }
                  timelineItems(last: 20) {
                    nodes {
                      __typename
                      ... on IssueComment {
                        createdAt
                        author { login }
                        body
                      }
                      ... on PullRequestReview {
                        createdAt
                        author { login }
                        state
                        body
                      }
                      ... on ClosedEvent {
                        createdAt
                        actor { login }
                      }
                      ... on ReopenedEvent {
                        createdAt
                        actor { login }
                      }
                      ... on MergedEvent {
                        createdAt
                        actor { login }
                      }
                    }
                  }
                }
                ... on Issue {
                  title
                  body
                  state
                  createdAt
                  updatedAt
                  author { login }
                  timelineItems(last: 20) {
                    nodes {
                      __typename
                      ... on IssueComment {
                        createdAt
                        author { login }
                        body
                      }
                      ... on ClosedEvent {
                        createdAt
                        actor { login }
                      }
                      ... on ReopenedEvent {
                        createdAt
                        actor { login }
                      }
                    }
                  }
                }
              }
              fieldValueByName(name: "Status") {
                ... on ProjectV2ItemFieldSingleSelectValue { name }
              }
            }
          }
        }
      }
    }
    """
    

    headers = {"Authorization": f"Bearer {config.GITHUB_TOKEN}"}
    variables = {"id": config.PROJECT_ID}
    
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    response.raise_for_status()
    print(response.status_code)
    print(response.json())
    return response.json()

def get_gemini_summary(data):
    """Feeds the GitHub JSON to Gemini for an Executive Summary."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={config.GEMINI_API_KEY}"
    
    prompt = f"""
    Context: You are a CTO's reporting agent. You need to report on metrics. 
    
    Task: Review the following GitHub Project data and report on the metrics below. Do not provide qualitative information but only quantitative metrics. If the data is not sufficient to report on a specific metric, please indicate "Data Not Available" for that metric.
    1. Number of tasks finished in the last 2 weeks.
    2. Pull Request Cycle Time (average time from PR creation to merge/close).
    3. Work-in-Progress (WIP) Analysis.
    4. Performance Analysis per GitHub user.
    
    Raw Data: {json.dumps(data)}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    print(response.status_code)
    print(response.json())
    result = response.json()
    #TODO check the result to make sure it follows the structure mentioned in the prompt, otherwise prompt again
    return result['candidates'][0]['content']['parts'][0]['text']

def run_report():
    #TODO change this into a loop and use a project ID array to pass on to fetch_github_project_data, and then aggregate the data into a single report
    print(f"[{datetime.now()}] Fetching GitHub data...")
    raw_data = fetch_github_project_data()
    
    print(f"[{datetime.now()}] Generating AI summary...")

    summary = get_gemini_summary(raw_data)
    #TODO write the summary into a GoogleDoc using writeToGoogleDoc library

    #TODO send this to a Slack Webhook,
    print("\n--- EXECUTIVE REPORT ---\n")
    print(summary)

if __name__ == "__main__":
    run_report()
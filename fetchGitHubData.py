import requests
import json
from datetime import datetime, timedelta, timezone
import config

def fetch_github_project_data():
    """Fetches items and metadata from GitHub Project V2 updated in the last 2 weeks."""
    url = "https://api.github.com/graphql"
    
    # This query retrieves items with pagination to filter for the last 2 weeks
    query = """
    query($id: ID!, $after: String) {
      node(id: $id) {
        ... on ProjectV2 {
          items(first: 100, after: $after) {
            pageInfo {
              hasNextPage
              endCursor
            }
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
    
    all_items = []
    has_next_page = True
    cursor = None
    two_weeks_ago = datetime.now(timezone.utc) - timedelta(weeks=2)

    print(f"[{datetime.now()}] Fetching project items updated since {two_weeks_ago.date()}...")

    while has_next_page:
        variables = {"id": config.PROJECT_ID, "after": cursor}
        
        response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 'errors' in data:
            print("GraphQL Errors:", data['errors'])
            break
            
        items_data = data['data']['node']['items']
        for node in items_data['nodes']:
            # Parse GitHub timestamp (e.g., 2023-10-27T10:00:00Z)
            node_updated_at = datetime.strptime(node['updatedAt'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if node_updated_at >= two_weeks_ago:
                all_items.append(node)
        
        has_next_page = items_data['pageInfo']['hasNextPage']
        cursor = items_data['pageInfo']['endCursor']
        print(f"Fetched page. Total items so far: {len(all_items)}")
    
    # Construct a response structure similar to the original for compatibility
    result = {"data": {"node": {"items": {"nodes": all_items}}}}
    return result
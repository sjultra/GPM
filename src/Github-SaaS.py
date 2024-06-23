import requests
import csv
from datetime import datetime

# Constants
GITHUB_TOKEN = ''
ORG_NAME = 'sjultra'
GITHUB_API_URL = 'https://api.github.com'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def fetch_github_data(url):
    """ Helper function to fetch data from GitHub API """
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  #Raise an error for bad responses
    return response.json()

def get_organization_members(org_name):
    """ Fetches users from a given GitHub organization """
    url = f'{GITHUB_API_URL}/orgs/{org_name}/members'
    members = fetch_github_data(url)
    for member in members:
        member_detail_url = member['url']
        member_detail = fetch_github_data(member_detail_url)
        events_url = member_detail['events_url'].replace('{/privacy}', '')
        events = fetch_github_data(events_url)
        last_seen = events[0]['created_at'] if events else 'No recent activity'
        member['last_seen'] = last_seen
    return members

def count_github_actions(org_name, repo_name):
    """ Counts GitHub Actions workflows in a repository """
    workflows_url = f'{GITHUB_API_URL}/repos/{org_name}/{repo_name}/contents/.github/workflows'
    response = requests.get(workflows_url, headers=HEADERS)
    if response.status_code == 200:
        workflows = response.json()
        return len(workflows)  
    return 0

def get_repositories_and_branches(org_name):
    """ Fetches repositories and their branches + last commit and count of GitHub Actions workflows for each repo in an organization """
    url = f'{GITHUB_API_URL}/orgs/{org_name}/repos'
    repos = fetch_github_data(url)
    repo_data = []
    for repo in repos:
        branches_url = repo['branches_url'].replace('{/branch}', '')
        branches = fetch_github_data(branches_url)
        actions_count = count_github_actions(org_name, repo['name'])
        for branch in branches:
            commit_url = branch['commit']['url']
            commit_data = fetch_github_data(commit_url)
            last_commit_date = commit_data['commit']['committer']['date']
            repo_data.append([repo['name'], branch['name'], last_commit_date, actions_count])
    return repo_data

def write_to_csv(filename, data, headers):
    """ Writes data to a CSV file """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)


members = get_organization_members(ORG_NAME)
repositories = get_repositories_and_branches(ORG_NAME)


write_to_csv('organization_members.csv', [[member['login'], member.get('last_seen', 'No recent activity')] for member in members], ['Username', 'Last Seen'])
write_to_csv('repositories_and_branches.csv', repositories, ['Repository Name', 'Branch Name', 'Last Commit Date', 'GitHub Actions Count'])

print("Data has been written to CSV files.")

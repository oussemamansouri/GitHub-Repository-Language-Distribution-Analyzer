import os
import requests
from collections import defaultdict
import matplotlib.pyplot as plt
import time
from datetime import datetime

# GitHub REST API endpoint for repositories
url = 'https://api.github.com/search/repositories'

# Set up the authorization header
headers = {
    'Authorization': f'token {os.getenv("ACTION_TOKEN")}'
}

# Query parameters (searching for repositories with at least 1 star)
params = {
    'q': 'stars:>0',
    'sort': 'stars',
    'order': 'desc',
    'per_page': 100,  # Max number of repositories per request
    'page': 1  # Start at page 1
}

# Dictionary to count the number of repositories per language
language_counts = defaultdict(int)

# Function to check rate limit status
def check_rate_limit():
    response = requests.get('https://api.github.com/rate_limit', headers=headers)
    if response.status_code == 200:
        limits = response.json()['rate']
        return limits['remaining'], limits['reset']  # remaining requests and reset time
    else:
        print("Error checking rate limit:", response.status_code)
        return 0, 0

# Function to fetch repositories and count languages
def fetch_repositories(page):
    params['page'] = page  # Set the current page number
    response = requests.get(url, headers=headers, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        repositories = response.json()
        # Count the primary language for each repository
        for repo in repositories['items']:
            language = repo['language']
            if language:  # Some repositories may not have a primary language set
                language_counts[language] += 1
        return len(repositories['items'])  # Return the number of items fetched
    else:
        print(f"Error fetching repositories: {response.status_code}, {response.text}")
        return 0  # Return 0 if there's an error

# Fetch repositories across pages
page = 1
while True:
    remaining, reset_time = check_rate_limit()
    if remaining <= 1:  # If you're close to hitting the limit
        wait_time = reset_time - int(time.time()) + 1  # Calculate how long to wait
        print(f"Rate limit reached. Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
    
    print(f"Fetching page {page}...")
    num_repos = fetch_repositories(page)
    if num_repos == 0:  # Stop if no repositories were fetched
        break
    page += 1  # Move to the next page after each request

# Calculate total repositories
total_repositories = sum(language_counts.values())

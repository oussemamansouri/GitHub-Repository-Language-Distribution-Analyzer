import os
import requests
from collections import defaultdict
import time
from datetime import datetime

# GitHub REST API endpoint for repositories
url = 'https://api.github.com/search/repositories'

# Set up the authorization header
headers = {
    'Authorization': f'Bearer {os.getenv("GITHUB_TOKEN")}'
}

# Query parameters
params = {
    'q': 'stars:>0',
    'sort': 'stars',
    'order': 'desc',
    'per_page': 100,
    'page': 1
}

language_counts = defaultdict(int)

def check_rate_limit():
    response = requests.get('https://api.github.com/rate_limit', headers=headers)
    if response.status_code == 200:
        limits = response.json()['rate']
        return limits['remaining'], limits['reset']
    elif response.status_code == 401:
        print("Error checking rate limit: Unauthorized (401). Check GITHUB_TOKEN.")
    else:
        print(f"Error checking rate limit: {response.status_code}")
    return 0, int(time.time()) + 60  # Retry after 1 minute if there's an error

def fetch_repositories(page):
    params['page'] = page
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        repositories = response.json()
        for repo in repositories['items']:
            language = repo['language']
            if language:
                language_counts[language] += 1
        return len(repositories['items'])
    elif response.status_code == 403:
        print("Hit secondary rate limit. Waiting before retrying...")
        time.sleep(60)  # Wait 1 minute to respect the rate limit
        return fetch_repositories(page)  # Retry fetching the page
    else:
        print(f"Error fetching repositories: {response.status_code}, {response.text}")
        return 0

# Break down query by years to avoid the 1000 result limit
years = range(2020, datetime.now().year + 1)  # e.g., from 2020 to current year

for year in years:
    print(f"Fetching repositories created in {year}...")
    params['q'] = f'stars:>0 created:{year}-01-01..{year}-12-31'
    page = 1

    while True:
        remaining, reset_time = check_rate_limit()
        if remaining <= 1:
            wait_time = max(0, reset_time - int(time.time()) + 1)
            print(f"Rate limit reached. Waiting for {wait_time} seconds...")
            time.sleep(wait_time)

        print(f"Fetching page {page} for year {year}...")
        num_repos = fetch_repositories(page)
        if num_repos == 0 or (page * 100) >= 1000:  # Stop if no results or hit 1000 results limit
            break
        page += 1
        time.sleep(2)  # Add delay to avoid hitting secondary rate limits

total_repositories = sum(language_counts.values())
print(f"Total repositories processed: {total_repositories}")
print("Language distribution:")
for language, count in language_counts.items():
    print(f"{language}: {count}")

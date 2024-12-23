import os
import requests
from collections import defaultdict
import time
import matplotlib.pyplot as plt
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

page = 1
while True:
    remaining, reset_time = check_rate_limit()
    if remaining <= 1:
        wait_time = max(0, reset_time - int(time.time()) + 1)
        print(f"Rate limit reached. Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
    
    print(f"Fetching page {page}...")
    num_repos = fetch_repositories(page)
    if num_repos == 0:
        break
    page += 1
    time.sleep(2)  # Add a delay between requests to avoid secondary rate limits

total_repositories = sum(language_counts.values())
print(f"Total repositories processed: {total_repositories}")

# Create a bar chart image for language distribution
def create_bar_chart(language_counts):
    languages = list(language_counts.keys())
    counts = list(language_counts.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(languages, counts, color='skyblue')  # Create a vertical bar chart
    plt.ylabel('Number of Repositories')
    plt.title('Language Distribution in GitHub Repositories')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better visibility
    plt.tight_layout()
    plt.savefig('language_distribution_bar_chart.png')
    plt.close()

create_bar_chart(language_counts)

# Write the language distribution to README.md
with open('README.md', 'w') as readme:
    readme.write(f"# Language Distribution\n\n")
    readme.write(f"![Language Distribution Chart](language_distribution_bar_chart.png)\n\n")
    readme.write(f"Total repositories processed: {total_repositories}\n\n")
    readme.write("Language distribution:\n")
    
    # Create a single line of languages and counts
    language_line = ', '.join(f"{language}: {count}" for language, count in language_counts.items())
    readme.write(f"{language_line}\n")

    # Add a timestamp to force a commit
    readme.write(f"\n\n_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")

print("README.md has been updated with the latest language distribution and bar chart.")

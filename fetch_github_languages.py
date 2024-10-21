import os
import requests
from collections import defaultdict
import matplotlib.pyplot as plt
import time

# GitHub REST API endpoint for repositories
url = 'https://api.github.com/search/repositories'

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

# Retrieve the personal access token from environment variables
token = os.getenv('GITHUB_TOKEN')  # This will fetch the token from the environment

# Function to fetch repositories and count languages
def fetch_repositories(page):
    params['page'] = page  # Set the current page number
    headers = {'Authorization': f'token {token}'}  # Set the authentication header
    response = requests.get(url, params=params, headers=headers)
    
    # Check for rate limiting and handle it
    if response.status_code == 403:  # Rate limit exceeded
        print("Rate limit reached. Waiting for reset...")
        time.sleep(3600)  # Wait for 1 hour (3600 seconds) to reset the rate limit
        return fetch_repositories(page)  # Retry the same page after the wait

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
    print(f"Fetching page {page}...")
    num_repos = fetch_repositories(page)
    if num_repos == 0:  # Stop if no repositories were fetched
        break
    page += 1  # Move to the next page after each request

# Generate a Bar Chart from the language counts
def generate_bar_chart():
    languages = list(language_counts.keys())
    counts = list(language_counts.values())

    plt.figure(figsize=(12, 6))  # Set the figure size
    plt.bar(languages, counts, color='skyblue')
    plt.xticks(rotation=45, ha='right')  # Rotate x labels for better readability
    plt.title("Number of Repositories per Programming Language", pad=20)
    plt.xlabel("Programming Languages")
    plt.ylabel("Number of Repositories")
    plt.tight_layout()

    # Save the bar chart as a PNG image
    plt.savefig('language_distribution_bar_chart.png', bbox_inches='tight')
    plt.show()  # Show the bar chart
    plt.close()  # Close the figure window after showing it

# Generate and save the bar chart
generate_bar_chart()

# Save language statistics in a markdown format
with open('README.md', 'w') as f:
    # Writing the title and description for the README
    f.write("# GitHub Repository Language Distribution Analyzer\n")
    f.write("This project analyzes the most starred repositories on GitHub to determine the distribution of programming languages used. The findings are visualized in a bar chart and documented below.\n")
    f.write("![Language Distribution Bar Chart](language_distribution_bar_chart.png)\n")
    f.write("\n## Language Statistics\n")
    for language, count in language_counts.items():
        f.write(f"- **{language}**: {count} repositories\n")

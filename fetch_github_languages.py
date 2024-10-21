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

# Function to fetch repositories and count languages
def fetch_repositories(page):
    params['page'] = page  # Set the current page number
    response = requests.get(url, params=params)
    
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
    else:
        print(f"Error fetching repositories: {response.status_code}, {response.text}")

# Infinite loop to fetch repositories across all pages
page = 1
while page <= 5:  # Limit to first 5 pages (500 repos)
    print(f"Fetching page {page}...")
    fetch_repositories(page)
    page += 1  # Move to the next page after each request

# Generate a Pie Chart from the language counts
def generate_pie_chart():
    languages = list(language_counts.keys())
    counts = list(language_counts.values())

    plt.figure(figsize=(10, 7))
    plt.pie(counts, labels=languages, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title("Distribution of Programming Languages in Popular GitHub Repositories")
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.

    # Save the pie chart as a PNG image
    plt.savefig('language_distribution_pie_chart.png')
    plt.show()

# Generate and save the pie chart
generate_pie_chart()

# Save language statistics in a markdown format
with open('README.md', 'w') as f:
    f.write("# GitHub Language Distribution\n")
    f.write("![Language Distribution](language_distribution_pie_chart.png)\n")
    f.write("\n## Language Statistics\n")
    for language, count in language_counts.items():
        f.write(f"- **{language}**: {count} repositories\n")

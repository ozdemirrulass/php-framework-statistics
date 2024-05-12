import os
import requests
import matplotlib.pyplot as plt
from datetime import datetime
from itertools import cycle
import json

def get_repo_info(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        repo_info = response.json()
        stars = repo_info['stargazers_count']
        forks = repo_info['forks_count']
        return stars, forks
    else:
        return None, None

def generate_charts(frameworks):
    color_cycle = cycle(plt.cm.tab10.colors)
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    stars_values = []
    forks_values = []
    labels = []
    colors_dict = {}

    for framework in frameworks:
        owner = framework["owner"]
        repo = framework["repo"]
        stars, forks = get_repo_info(owner, repo)

        if stars is not None and forks is not None:
            labels.append(f'{owner}/{repo}')
            stars_values.append(stars)
            forks_values.append(forks)
            colors_dict[f'{owner}/{repo}'] = next(color_cycle)
        else:
            print(f"Unable to fetch information for {owner}/{repo}")

    # Create the directories if they don't exist
    directories = ["archive", "archive/charts"]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Generate chart for stars
    plt.figure(figsize=(12, 6))
    plt.bar(labels, stars_values, color=[colors_dict[label] for label in labels])
    plt.title(f'Stars Count for PHP Frameworks ({current_time})')
    plt.xlabel('Frameworks')
    plt.ylabel('Stars Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    stars_chart_filename = f'archive/charts/{current_time}_stars_count.png'
    plt.savefig(stars_chart_filename)

    # Generate chart for forks
    plt.figure(figsize=(12, 6))
    plt.bar(labels, forks_values, color=[colors_dict[label] for label in labels])
    plt.title(f'Forks Count for PHP Frameworks ({current_time})')
    plt.xlabel('Frameworks')
    plt.ylabel('Forks Count ')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    forks_chart_filename = f'archive/charts/{current_time}_forks_count.png'
    plt.savefig(forks_chart_filename)

    return stars_chart_filename, forks_chart_filename, current_time

def update_archive_json(data):
    filename = 'archive.json'

    # Check if the JSON file already exists
    try:
        with open(filename, 'r') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        json_data = {"php_framework_statistics": {"data": {}}}

    # Update JSON data with new timestamp and data
    json_data["php_framework_statistics"]["data"][current_time] = data

    # Write the updated JSON data back to the file
    with open(filename, 'w') as file:
        json.dump(json_data, file, indent=2)

if __name__ == "__main__":
    frameworks = [
        {"name": "Laravel", "owner": "laravel", "repo": "framework"},
        {"name": "Symfony", "owner": "symfony", "repo": "symfony"},
        {"name": "CodeIgniter", "owner": "bcit-ci", "repo": "codeigniter"},
        {"name": "Yii2", "owner": "yiisoft", "repo": "yii2"},
        {"name": "CakePHP", "owner": "cakephp", "repo": "cakephp"},
        {"name": "Slim", "owner": "slimphp", "repo": "Slim"},
        {"name": "Phalcon", "owner": "phalcon", "repo": "cphalcon"},
        {"name": "FuelPHP", "owner": "fuel", "repo": "fuel"}
    ]

    stars_chart, forks_chart, current_time = generate_charts(frameworks)

    # Write the Markdown content to the file
    with open("latest_stats.md", "w") as md_file:
        md_file.write(f"### Stars Count for PHP Frameworks\n\n")
        md_file.write(f"![Stars Chart](./{stars_chart})\n\n")
        md_file.write(f"### Forks Count for PHP Frameworks\n\n")
        md_file.write(f"![Forks Chart](./{forks_chart})\n\n")

    # Update or create the archive.json file
    update_archive_json({
        "chart_paths": {"stars_chart": stars_chart, "forks_chart": forks_chart},
        "frameworks": [
            {
                "name": framework["name"],
                "owner": framework["owner"],
                "repo": framework["repo"],
                "github": {
                    "stars_count": get_repo_info(framework["owner"], framework["repo"])[0],
                    "forks_count": get_repo_info(framework["owner"], framework["repo"])[1]
                }
            }
            for framework in frameworks
        ]
    })

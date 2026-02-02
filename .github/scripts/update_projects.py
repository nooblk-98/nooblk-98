#!/usr/bin/env python3
"""
GitHub Projects Fetcher and README Updater
Fetches public repositories and updates the README.md Featured Projects section
"""

import os
import re
import requests
from datetime import datetime

# Configuration
GITHUB_USERNAME = "nooblk-98"
GITHUB_API_URL = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
README_FILE = "README.md"

# Markers for the Featured Projects section
START_MARKER = "### 🚀 Notable Projects"
END_MARKER = "</td>\n<td width=\"50%\">"


def fetch_repositories():
    """Fetch public repositories from GitHub API"""
    try:
        headers = {}
        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        params = {
            "type": "public",
            "sort": "updated",
            "per_page": 100
        }
        
        response = requests.get(GITHUB_API_URL, headers=headers, params=params)
        response.raise_for_status()
        repos = response.json()
        
        # Filter out forked repos and sort by stars
        original_repos = [r for r in repos if not r["fork"]]
        sorted_repos = sorted(original_repos, key=lambda x: x["stargazers_count"], reverse=True)
        
        return sorted_repos
    except Exception as e:
        print(f"Error fetching repositories: {e}")
        return []


def format_projects_section(repos):
    """Format repositories into markdown table format"""
    # Take top repositories (limit to 10 for better display)
    top_repos = repos[:10]
    
    notable_projects = []
    featured_repos = []
    
    # Split into two columns
    mid_point = len(top_repos) // 2
    
    for i, repo in enumerate(top_repos):
        name = repo["name"]
        description = repo["description"] or "No description available"
        stars = repo["stargazers_count"]
        url = repo["html_url"]
        language = repo["language"] or "Various"
        
        # Truncate long descriptions
        if len(description) > 60:
            description = description[:57] + "..."
        
        if i < 4:  # First 4 for notable projects (left column)
            # Create a more descriptive title
            title = name.replace("-", " ").replace("_", " ").title()
            notable_projects.append(f"- **{title}** - {description}")
        else:  # Remaining for featured repos (right column)
            featured_repos.append(
                f"**[{name}]({url})**  \n"
                f"⭐ {stars} | 🔤 {language}  \n"
                f"_{description}_\n"
            )
    
    # Build the left column (Notable Projects)
    left_column = "\n".join(notable_projects) if notable_projects else "- More projects coming soon!"
    
    # Build the right column (Featured Repositories)
    right_column = "\n".join(featured_repos) if featured_repos else "_Check back soon for more projects!_"
    
    return left_column, right_column


def update_readme(left_content, right_content):
    """Update the README.md file with new projects"""
    try:
        with open(README_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the Featured Projects section
        pattern = r"(### 🚀 Notable Projects\n)(.*?)(\n\n</td>\n<td width=\"50%\">)\n\n(.*?)(\n\n</td>)"
        
        def replacer(match):
            return (
                f"{match.group(1)}"
                f"{left_content}"
                f"{match.group(3)}\n\n"
                f"### 📦 Featured Repositories\n"
                f"{right_content}"
                f"{match.group(5)}"
            )
        
        updated_content = re.sub(pattern, replacer, content, flags=re.DOTALL)
        
        # Write back to file
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print("✅ README.md updated successfully!")
        return True
    except Exception as e:
        print(f"❌ Error updating README: {e}")
        return False


def main():
    """Main execution function"""
    print(f"🔍 Fetching repositories for {GITHUB_USERNAME}...")
    repos = fetch_repositories()
    
    if not repos:
        print("⚠️ No repositories found or error occurred")
        return
    
    print(f"📊 Found {len(repos)} public repositories")
    
    print("📝 Formatting projects section...")
    left_content, right_content = format_projects_section(repos)
    
    print("💾 Updating README.md...")
    success = update_readme(left_content, right_content)
    
    if success:
        print(f"🎉 Update completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ Update failed")


if __name__ == "__main__":
    main()

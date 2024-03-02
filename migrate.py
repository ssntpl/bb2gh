import subprocess
import json
import os
import requests
from requests.auth import HTTPBasicAuth

# Your Bitbucket username and the app password you've created
bitbucket_username = 'BITBUCKET_USERNAME'
bitbucket_app_password = 'BITBUCKET_APP_PASSWORD'
bitbucket_workspace = 'BITBUCKET_WORKSPACE'

# Github token and workspace
github_token = 'GITHUB_TOKEN'
github_workspace = 'GITHUB_WORKSPACE'

# List Bitbucket repositories using basic authentication
def list_bitbucket_repos(url):
    # Use HTTPBasicAuth for basic authentication
    response = requests.get(url, auth=HTTPBasicAuth(bitbucket_username, bitbucket_app_password))
    if response.status_code == 200:
        # print(response.json())
        return response.json()
    else:
        print(f"Failed to fetch Bitbucket repositories. Status code: {response.status_code}, Response: {response.text}")
        return []

# Create GitHub repository
# def create_github_repo(repo_name):
#     url = "https://api.github.com/user/repos"
#     headers = {
#         "Authorization": f"token {github_token}",
#         "Accept": "application/vnd.github.v3+json"
#     }
#     data = {"name": repo_name}
#     response = requests.post(url, json=data, headers=headers)
#     if response.status_code == 201:
#         return response.json()['clone_url']
#     else:
#         print(f"Failed to create GitHub repository {repo_name}")
#         return None

# Main function to clone and push repos
def clone_and_push():
    url = f"https://api.bitbucket.org/2.0/repositories/{bitbucket_workspace}?page=8"
    repos = []
    while url:
        response = list_bitbucket_repos(url)
        for repo in response['values']:
            repo_name = repo['name']
            repo_slug = repo['slug']
            repo_description = repo['description']
            bitbucket_url = repo['links']['clone'][1]['href']
            repos.append({
                "name": repo_name,
                "slug": repo_slug,
                "description": repo_description,
                "http_url": repo['links']['clone'][0]['href'],
                "ssh_url": repo['links']['clone'][1]['href'],
                "project_key": repo['project']['key'],
                "project_name": repo['project']['name'],
                "created_on":repo['created_on'],
                "updated_on":repo['updated_on'],
                "size":repo['size'],
            })

            github_repo_name = f"{github_workspace}/{repo_slug}"
            github_url = f"https://github.com/{github_repo_name}.git"
            result = subprocess.run(["gh", "repo", "create", github_repo_name, "--private", "--description", repo_description], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0:
                print(f"\n\nStarted cloning and pushing {repo_name}({repo_slug}) to GitHub")
                # Clone the Bitbucket repo
                subprocess.run(["git", "clone", "--bare", bitbucket_url])
                # Change directory to the cloned repo
                os.chdir(repo_slug+".git")
                # Push to GitHub
                subprocess.run(["git", "push", "--mirror", github_url])
                # Change back to the original directory
                os.chdir("..")
                # Delete the cloned repo
                subprocess.run(["rm", "-rf", repo_slug+".git"])
                print(f"Successfully cloned and pushed {repo_name}({repo_slug}) to GitHub")
            else:
                print(f"\n\nFailed to create {repo_slug} on GitHub. {result.stderr.decode()}")

            # break
        # Get the next page URL
        url = response.get('next', None)
        # url = None

    # print(json.dumps(repos, indent=4))

if __name__ == "__main__":
    clone_and_push()

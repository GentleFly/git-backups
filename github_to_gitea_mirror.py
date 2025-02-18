#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script: Mirroring GitHub Repositories to Gitea
Author: DeepSeek (https://www.deepseek.com)
Created: 2023-10-10
Description: This script retrieves a list of repositories from a GitHub user and creates their mirrors in Gitea.
Version: 1.0
License: MIT License

Usage Example:
    python3 github_to_gitea_mirror.py
"""

# Import necessary libraries
import http.client
import json
import base64
import os

# GitHub credentials (from environment variables)
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # GitHub access token

# Gitea credentials (from environment variables)
GITEA_URL = os.getenv('GITEA_URL')  # For example, 'gitea.example.com'
GITEA_TOKEN = os.getenv('GITEA_TOKEN')  # Gitea access token

# GitHub username whose repositories are to be mirrored
GITHUB_TARGET_USERNAME = os.getenv('GITHUB_TARGET_USERNAME')

# Gitea organization name where repositories will be mirrored
GITEA_ORG_NAME = os.getenv('GITEA_ORG_NAME')

# Check if all required environment variables are set
if not all([GITHUB_USERNAME, GITHUB_TOKEN, GITEA_URL, GITEA_TOKEN, GITHUB_TARGET_USERNAME, GITEA_ORG_NAME]):
    raise ValueError("Not all required environment variables are set.")

# Encode credentials for Basic Auth (GitHub)
github_credentials = base64.b64encode(
    f"{GITHUB_USERNAME}:{GITHUB_TOKEN}".encode()
).decode()

# Function to get a list of repositories from GitHub
def get_github_repositories(username):
    conn = http.client.HTTPSConnection("api.github.com")
    headers = {
        "Authorization": f"Basic {github_credentials}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Gitea-Mirror-Script"  # Add User-Agent
    }
    repositories = []
    url = f"/users/{username}/repos"

    while url:
        conn.request("GET", url, headers=headers)
        response = conn.getresponse()
        if response.status == 200:
            data = json.loads(response.read().decode())
            repositories.extend(data)
            # Check for the next page
            link_header = response.getheader("Link", "")
            if 'rel="next"' in link_header:
                url = link_header.split(';')[0].strip('<>')
            else:
                url = None
        else:
            print(f"Error fetching repositories from GitHub: {response.status} - {response.read().decode()}")
            break

    conn.close()
    return repositories

# Function to check if a repository exists in Gitea (in an organization)
def gitea_repository_exists(org_name, repo_name):
    conn = http.client.HTTPSConnection(GITEA_URL)
    headers = {
        "Authorization": f"token {GITEA_TOKEN}",
        "Accept": "application/json"
    }
    conn.request("GET", f"/api/v1/repos/{org_name}/{repo_name}", headers=headers)
    response = conn.getresponse()
    conn.close()
    return response.status == 200

# Function to create a repository mirror in Gitea (in an organization)
def create_gitea_mirror(org_name, repo_name, repo_url):
    conn = http.client.HTTPSConnection(GITEA_URL)
    headers = {
        "Authorization": f"token {GITEA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "clone_addr": repo_url,  # Repository URL in GitHub
        "repo_name": repo_name,  # Repository name in Gitea
        "mirror": True,  # Create the repository as a mirror
        "private": True,  # Make the repository private (or False for public)
        "repo_owner": org_name,  # Repository owner (organization)
        "auth_username": GITHUB_USERNAME,  # GitHub username
        "auth_password": GITHUB_TOKEN,  # GitHub token
        "service": "git",  # Service type (git for GitHub)
        "mirror_interval": "24h"  # Sync interval
    })
    conn.request("POST", "/api/v1/repos/migrate", body=payload, headers=headers)
    response = conn.getresponse()
    if response.status == 201:
        print(f"Repository mirror '{repo_name}' successfully created in organization '{org_name}' in Gitea.")
    else:
        print(f"Error creating repository mirror '{repo_name}': {response.status} - {response.read().decode()}")
    conn.close()

# Get the list of repositories from GitHub
repositories = get_github_repositories(GITHUB_TARGET_USERNAME)

# Create repository mirrors in Gitea (in the organization)
for repo in repositories:
    repo_name = repo['name']
    repo_url = repo['clone_url']  # Clone URL (HTTPS)

    # Check if the repository exists in Gitea (in the organization)
    if gitea_repository_exists(GITEA_ORG_NAME, repo_name):
        print(f"Repository '{repo_name}' already exists in organization '{GITEA_ORG_NAME}' in Gitea. Skipping.")
    else:
        print(f"Creating repository mirror: {repo_name}")
        create_gitea_mirror(GITEA_ORG_NAME, repo_name, repo_url)


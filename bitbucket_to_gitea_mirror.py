#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script: Mirroring Repositories from Bitbucket to Gitea
Author: DeepSeek (https://www.deepseek.com)
Created: 2023-10-10
Description: This script retrieves a list of repositories from a Bitbucket user and creates their mirrors in Gitea.
Version: 1.0
License: MIT License

Usage Example:
    python3 bitbucket_to_gitea_mirror.py
"""

# Import necessary libraries
import http.client
import json
import base64
import os

# Bitbucket credentials (from environment variables)
BITBUCKET_USERNAME = os.getenv('BITBUCKET_USERNAME')
BITBUCKET_APP_PASSWORD = os.getenv('BITBUCKET_APP_PASSWORD')

# Gitea credentials (from environment variables)
GITEA_URL = os.getenv('GITEA_URL')  # For example, 'gitea.example.com'
GITEA_TOKEN = os.getenv('GITEA_TOKEN')  # Gitea access token

# Bitbucket username whose repositories need to be mirrored
BITBUCKET_TARGET_USERNAME = os.getenv('BITBUCKET_TARGET_USERNAME')

# Gitea organization name where repositories will be mirrored
GITEA_ORG_NAME = os.getenv('GITEA_ORG_NAME')

# Check if all required environment variables are set
if not all([BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD, GITEA_URL, GITEA_TOKEN, BITBUCKET_TARGET_USERNAME, GITEA_ORG_NAME]):
    raise ValueError("Not all required environment variables are set.")

# Encode Bitbucket credentials for Basic Auth
bitbucket_credentials = base64.b64encode(
    f"{BITBUCKET_USERNAME}:{BITBUCKET_APP_PASSWORD}".encode()
).decode()

# Function to get a list of repositories from Bitbucket
def get_bitbucket_repositories(username):
    conn = http.client.HTTPSConnection("api.bitbucket.org")
    headers = {
        "Authorization": f"Basic {bitbucket_credentials}",
        "Accept": "application/json"
    }
    repositories = []
    url = f"/2.0/repositories/{username}"

    while url:
        conn.request("GET", url, headers=headers)
        response = conn.getresponse()
        if response.status == 200:
            data = json.loads(response.read().decode())
            repositories.extend(data['values'])
            url = data.get('next')  # Move to the next page if available
        else:
            print(f"Error fetching repositories from Bitbucket: {response.status} - {response.read().decode()}")
            break

    conn.close()
    return repositories

# Function to check if a repository exists in Gitea (in the organization)
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

# Function to create a mirror repository in Gitea (in the organization)
def create_gitea_mirror(org_name, repo_name, repo_url):
    conn = http.client.HTTPSConnection(GITEA_URL)
    headers = {
        "Authorization": f"token {GITEA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "clone_addr": repo_url,  # Repository URL in Bitbucket
        "repo_name": repo_name,  # Repository name in Gitea
        "mirror": True,  # Create the repository as a mirror
        "private": True,  # Make the repository private (or False for public)
        "repo_owner": org_name,  # Repository owner (organization)
        "auth_username": BITBUCKET_USERNAME,  # Bitbucket login
        "auth_password": BITBUCKET_APP_PASSWORD,  # Bitbucket password
        "service": "git",  # Service type (git for Bitbucket)
        "mirror_interval": "24h"  # Synchronization interval
    })
    conn.request("POST", "/api/v1/repos/migrate", body=payload, headers=headers)
    response = conn.getresponse()
    if response.status == 201:
        print(f"Mirror repository '{repo_name}' successfully created in organization '{org_name}' in Gitea.")
    else:
        print(f"Error creating mirror repository '{repo_name}': {response.status} - {response.read().decode()}")
    conn.close()

# Get the list of repositories from Bitbucket
repositories = get_bitbucket_repositories(BITBUCKET_TARGET_USERNAME)

# Create mirror repositories in Gitea (in the organization)
for repo in repositories:
    repo_name = repo['name']
    repo_url = repo['links']['clone'][0]['href']  # Clone URL (HTTPS)

    # Check if the repository already exists in Gitea (in the organization)
    if gitea_repository_exists(GITEA_ORG_NAME, repo_name):
        print(f"Repository '{repo_name}' already exists in organization '{GITEA_ORG_NAME}' in Gitea. Skipping.")
    else:
        print(f"Creating mirror repository: {repo_name}")
        create_gitea_mirror(GITEA_ORG_NAME, repo_name, repo_url)


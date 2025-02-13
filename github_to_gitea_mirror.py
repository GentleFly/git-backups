#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script: Создание зеркал репозиториев из GitHub в Gitea
Author: DeepSeek (https://www.deepseek.com)
Created: 2023-10-10
Description: Скрипт получает список репозиториев пользователя на GitHub и создает их зеркала в Gitea.
Version: 1.0
License: MIT License

Пример использования:
    python3 github_to_gitea_mirror.py
"""

# Импорт необходимых библиотек
import http.client
import json
import base64
import os

# Учетные данные для GitHub (из переменных окружения)
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Токен доступа GitHub

# Учетные данные для Gitea (из переменных окружения)
GITEA_URL = os.getenv('GITEA_URL')  # Например, 'gitea.example.com'
GITEA_TOKEN = os.getenv('GITEA_TOKEN')  # Токен доступа Gitea

# Имя пользователя в GitHub, чьи репозитории нужно перенести
GITHUB_TARGET_USERNAME = os.getenv('GITHUB_TARGET_USERNAME')

# Имя организации в Gitea, куда будут перенесены репозитории
GITEA_ORG_NAME = os.getenv('GITEA_ORG_NAME')

# Проверка наличия обязательных переменных окружения
if not all([GITHUB_USERNAME, GITHUB_TOKEN, GITEA_URL, GITEA_TOKEN, GITHUB_TARGET_USERNAME, GITEA_ORG_NAME]):
    raise ValueError("Не все обязательные переменные окружения заданы.")

# Кодируем учетные данные для Basic Auth (GitHub)
github_credentials = base64.b64encode(
    f"{GITHUB_USERNAME}:{GITHUB_TOKEN}".encode()
).decode()

# Функция для получения списка репозиториев из GitHub
def get_github_repositories(username):
    conn = http.client.HTTPSConnection("api.github.com")
    headers = {
        "Authorization": f"Basic {github_credentials}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Gitea-Mirror-Script"  # Добавляем User-Agent
    }
    repositories = []
    url = f"/users/{username}/repos"

    while url:
        conn.request("GET", url, headers=headers)
        response = conn.getresponse()
        if response.status == 200:
            data = json.loads(response.read().decode())
            repositories.extend(data)
            # Проверяем наличие следующей страницы
            link_header = response.getheader("Link", "")
            if 'rel="next"' in link_header:
                url = link_header.split(';')[0].strip('<>')
            else:
                url = None
        else:
            print(f"Ошибка при получении репозиториев из GitHub: {response.status} - {response.read().decode()}")
            break

    conn.close()
    return repositories

# Функция для проверки существования репозитория в Gitea (в организации)
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

# Функция для создания зеркала репозитория в Gitea (в организации)
def create_gitea_mirror(org_name, repo_name, repo_url):
    conn = http.client.HTTPSConnection(GITEA_URL)
    headers = {
        "Authorization": f"token {GITEA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "clone_addr": repo_url,  # URL репозитория в GitHub
        "repo_name": repo_name,  # Имя репозитория в Gitea
        "mirror": True,  # Создать репозиторий как зеркало
        "private": True,  # Сделать репозиторий приватным (или False для публичного)
        "repo_owner": org_name,  # Владелец репозитория (организация)
        "auth_username": GITHUB_USERNAME,  # Логин для доступа к GitHub
        "auth_password": GITHUB_TOKEN,  # Токен для доступа к GitHub
        "service": "git",  # Тип сервиса (git для GitHub)
        "mirror_interval": "24h"  # Интервал синхронизации
    })
    conn.request("POST", "/api/v1/repos/migrate", body=payload, headers=headers)
    response = conn.getresponse()
    if response.status == 201:
        print(f"Зеркало репозитория '{repo_name}' успешно создано в организации '{org_name}' в Gitea.")
    else:
        print(f"Ошибка при создании зеркала репозитория '{repo_name}': {response.status} - {response.read().decode()}")
    conn.close()

# Получаем список репозиториев из GitHub
repositories = get_github_repositories(GITHUB_TARGET_USERNAME)

# Создаем зеркала репозиториев в Gitea (в организации)
for repo in repositories:
    repo_name = repo['name']
    repo_url = repo['clone_url']  # URL для клонирования (HTTPS)

    # Проверяем, существует ли репозиторий в Gitea (в организации)
    if gitea_repository_exists(GITEA_ORG_NAME, repo_name):
        print(f"Репозиторий '{repo_name}' уже существует в организации '{GITEA_ORG_NAME}' в Gitea. Пропускаем.")
    else:
        print(f"Создание зеркала репозитория: {repo_name}")
        create_gitea_mirror(GITEA_ORG_NAME, repo_name, repo_url)


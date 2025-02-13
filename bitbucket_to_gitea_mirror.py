#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script: Создание зеркал репозиториев из Bitbucket в Gitea
Author: DeepSeek (https://www.deepseek.com)
Created: 2023-10-10
Description: Скрипт получает список репозиториев пользователя на Bitbucket и создает их зеркала в Gitea.
Version: 1.0
License: MIT License

Пример использования:
    python3 bitbucket_to_gitea_mirror.py
"""

# Импорт необходимых библиотек
import http.client
import json
import base64
import os

# Учетные данные для Bitbucket (из переменных окружения)
BITBUCKET_USERNAME = os.getenv('BITBUCKET_USERNAME')
BITBUCKET_APP_PASSWORD = os.getenv('BITBUCKET_APP_PASSWORD')

# Учетные данные для Gitea (из переменных окружения)
GITEA_URL = os.getenv('GITEA_URL')  # Например, 'gitea.example.com'
GITEA_TOKEN = os.getenv('GITEA_TOKEN')  # Токен доступа Gitea

# Имя пользователя в Bitbucket, чьи репозитории нужно перенести
BITBUCKET_TARGET_USERNAME = os.getenv('BITBUCKET_TARGET_USERNAME')

# Имя организации в Gitea, куда будут перенесены репозитории
GITEA_ORG_NAME = os.getenv('GITEA_ORG_NAME')

# Проверка наличия обязательных переменных окружения
if not all([BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD, GITEA_URL, GITEA_TOKEN, BITBUCKET_TARGET_USERNAME, GITEA_ORG_NAME]):
    raise ValueError("Не все обязательные переменные окружения заданы.")

# Кодируем учетные данные для Basic Auth (Bitbucket)
bitbucket_credentials = base64.b64encode(
    f"{BITBUCKET_USERNAME}:{BITBUCKET_APP_PASSWORD}".encode()
).decode()

# Функция для получения списка репозиториев из Bitbucket
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
            url = data.get('next')  # Переход к следующей странице, если есть
        else:
            print(f"Ошибка при получении репозиториев из Bitbucket: {response.status} - {response.read().decode()}")
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
        "clone_addr": repo_url,  # URL репозитория в Bitbucket
        "repo_name": repo_name,  # Имя репозитория в Gitea
        "mirror": True,  # Создать репозиторий как зеркало
        "private": True,  # Сделать репозиторий приватным (или False для публичного)
        "repo_owner": org_name,  # Владелец репозитория (организация)
        "auth_username": BITBUCKET_USERNAME,  # Логин для доступа к Bitbucket
        "auth_password": BITBUCKET_APP_PASSWORD,  # Пароль для доступа к Bitbucket
        "service": "git",  # Тип сервиса (git для Bitbucket)
        "mirror_interval": "24h"  # Интервал синхронизации
    })
    conn.request("POST", "/api/v1/repos/migrate", body=payload, headers=headers)
    response = conn.getresponse()
    if response.status == 201:
        print(f"Зеркало репозитория '{repo_name}' успешно создано в организации '{org_name}' в Gitea.")
    else:
        print(f"Ошибка при создании зеркала репозитория '{repo_name}': {response.status} - {response.read().decode()}")
    conn.close()

# Получаем список репозиториев из Bitbucket
repositories = get_bitbucket_repositories(BITBUCKET_TARGET_USERNAME)

# Создаем зеркала репозиториев в Gitea (в организации)
for repo in repositories:
    repo_name = repo['name']
    repo_url = repo['links']['clone'][0]['href']  # URL для клонирования (HTTPS)

    # Проверяем, существует ли репозиторий в Gitea (в организации)
    if gitea_repository_exists(GITEA_ORG_NAME, repo_name):
        print(f"Репозиторий '{repo_name}' уже существует в организации '{GITEA_ORG_NAME}' в Gitea. Пропускаем.")
    else:
        print(f"Создание зеркала репозитория: {repo_name}")
        create_gitea_mirror(GITEA_ORG_NAME, repo_name, repo_url)


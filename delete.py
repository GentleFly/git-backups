#!/usr/bin/python
import http.client
import json

# Учетные данные для Gitea
GITEA_URL = 'gitea.gentlefly.org'  # Например, 'gitea.example.com'
GITEA_TOKEN = '54c54c0e9f299dcac91e9ad6f9c0f7748360113d'  # Токен доступа Gitea

# Имя пользователя или организации, чьи репозитории нужно удалить
TARGET_OWNER = 'Bitbucket'

# Функция для получения списка репозиториев
def get_gitea_repositories(owner):
    conn = http.client.HTTPSConnection(GITEA_URL)
    headers = {
        "Authorization": f"token {GITEA_TOKEN}",
        "Accept": "application/json"
    }
    url = f"/api/v1/users/{owner}/repos"
    conn.request("GET", url, headers=headers)
    response = conn.getresponse()
    if response.status == 200:
        data = json.loads(response.read().decode())
        conn.close()
        return data
    else:
        print(f"Ошибка при получении репозиториев: {response.status} - {response.read().decode()}")
        conn.close()
        return []

# Функция для удаления репозитория
def delete_gitea_repository(owner, repo_name):
    conn = http.client.HTTPSConnection(GITEA_URL)
    headers = {
        "Authorization": f"token {GITEA_TOKEN}"
    }
    conn.request("DELETE", f"/api/v1/repos/{owner}/{repo_name}", headers=headers)
    response = conn.getresponse()
    if response.status == 204:
        print(f"Репозиторий '{repo_name}' успешно удален.")
    else:
        print(f"Ошибка при удалении репозитория '{repo_name}': {response.status} - {response.read().decode()}")
    conn.close()

# Получаем список репозиториев
repositories = get_gitea_repositories(TARGET_OWNER)

# Удаляем все репозитории
for repo in repositories:
    repo_name = repo['name']
    print(f"Удаление репозитория: {repo_name}")
    delete_gitea_repository(TARGET_OWNER, repo_name)


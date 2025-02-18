
Automatic, periodical backup of git repositories from GitHub and Bitbucket to Gitea.

There is Python scripts:
* `./github_to_gitea_mirror.py`
* `./bitbucket_to_gitea_mirror.py`

Gitea Workflow YAML files:
* `.gitea/workflows/github.yaml`
* `.gitea/workflows/bitbucket.yaml`

# Gitea Actions

For use Gitea Workflow you need create Gitea Actions secrets and variables:

| Secrets                   | Description                                         |
|---------------------------|-----------------------------------------------------|
| USERNAME_GITHUB           | Your GitHub username                                |
| TOKEN_GITHUB              | Your GitHub token                                   |
| TARGET_USERNAME_GITHUB    | GitHub username who repositories will be back up    |
| USERNAME_BITBUCKET        | Your Bitbucket username                             |
| APP_PASSWORD_BITBUCKET    | Your Bitbucket token                                |
| TARGET_USERNAME_BITBUCKET | Bitbucket username who repositories will be back up |
| TOKEN_GITEA               | Your Gitea token                                    |
| EMAIL_TO                  | Recipient of the letter about errors                |
| SMTP_USERNAME             | Login SMTP on smtp.yandex.ru                        |
| SMTP_PASSWORD             | Pasword SMTP on smtp.yandex.ru                      |

| Variables              | Description                                                  |
|------------------------|--------------------------------------------------------------|
| URL_GITEA              | Gitea url                                                    |
| ORG_NAME_FOR_BITBUCKET | name of Gitea Organization for Bitbucket                     |
| ORG_NAME_FOR_GITHUB    | name of Gitea Organization for GitHub                        |
| SMTP_SERVER            | SMTP server address                                          |


# Manually use script

You can manually use Python script from command line, to automatically get a list of git repositories from GitHub or Bitbucket, and then generate mirrors in Gitea Organization.

How to use script:

* Set environment variables.
  ```bash
  export BITBUCKET_USERNAME="your_username_bitbucket"
  export BITBUCKET_APP_PASSWORD="your_app_password_bitbucket"
  export GITEA_URL="your_gitea_domain"
  export GITEA_TOKEN="your_gitea_token"
  export BITBUCKET_TARGET_USERNAME="username_bitbucket"
  export GITEA_ORG_NAME="org_gitea"
  ```
* Run the script.
  ```bash
  ./bitbucket_to_gitea_mirror.py
  ```


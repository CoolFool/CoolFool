import github.GithubException
from github import Github
from dotenv import load_dotenv
import os
import datetime
from string import Template
import urllib.request
import json

load_dotenv()
GH_TOKEN = os.environ["GH_TOKEN"]

now = datetime.datetime.now()
new_year = datetime.datetime(now.year, 1, 1)

gh = Github(login_or_token=GH_TOKEN)
me = gh.get_user()

variables = {
    "year": str(now.year),
}


def get_github_stats():
    total_commits = 0
    total_stargazers = 0
    # total_forks = 0
    for repo in me.get_repos():
        total_stargazers += repo.stargazers_count
        # total_forks += repo.forks_count
        if repo.private:
            repo_name = "Private Repository"
        else:
            repo_name = repo.name
        try:
            if repo.name.lower() == me.login.lower():
                commits = 0
                for i in repo.get_commits(author=me, since=new_year):
                    if "Automated Update for README.md" not in i.commit.message:
                        commits += 1
                print("{} commits in \"{}\" for {} since {}".format(commits, repo_name, me.login, new_year.year))
            else:
                commits = repo.get_commits(author=me, since=new_year).totalCount
                if commits > 0:
                    print("{} commits in \"{}\" for {} since {}".format(commits, repo_name, me.login, new_year.year))
            total_commits += commits
        except github.GithubException as err:
            print("Error occurred with code \"{}\" and message \"{}\" for repository \"{}\" "
                  "\n For more info visit {}".format(err.status, err.data["message"], repo_name,
                                                     err.data["documentation_url"]))
    return total_commits, total_stargazers


def get_os_stats():
    base_url = "https://archlinux.org/packages/search/json/?name={}"
    linux_zen_arch_package = base_url.format("linux-zen")
    plasma_desktop_arch_package = base_url.format("plasma-desktop")
    zsh_arch_package = base_url.format("zsh")
    linux_zen_version = json.loads(
        (urllib.request.urlopen(urllib.request.Request(linux_zen_arch_package)).read()).decode("utf-8"))["results"][0][
        "pkgver"]
    plasma_desktop_version = json.loads(
        (urllib.request.urlopen(urllib.request.Request(plasma_desktop_arch_package)).read()).decode("utf-8"))[
        "results"][0]["pkgver"]
    zsh_version = json.loads(
        (urllib.request.urlopen(urllib.request.Request(zsh_arch_package)).read()).decode("utf-8"))[
        "results"][0]["pkgver"]
    return plasma_desktop_version, linux_zen_version, zsh_version


def update_github_readme(template_vars):
    with open('readme_template.md', 'r') as template:
        src = Template(template.read())
        content = src.substitute(template_vars)
        try:
            profile_repo = me.get_repo(me.login)
            file = profile_repo.get_contents("README.md")
            if content != file.decoded_content.decode():
                profile_repo.update_file(path="README.md",
                                         message="Automated Update for {} at {} {}".format(file.name,
                                                                                           now.strftime("%c"),
                                                                                           now.astimezone().tzinfo),
                                         content=content, sha=file.sha)
                return "Successfully updated {}".format(file.name)
            else:
                return "No update required for {}".format(file.name)
        except github.GithubException as err:
            return err


if __name__ == "__main__":
    variables["commits"], variables["total_stars_earned"] = get_github_stats()
    variables["plasma_desktop_version"], variables["kernel_version"], variables["zsh_version"] = get_os_stats()
    # print(variables)
    print(update_github_readme(template_vars=variables))

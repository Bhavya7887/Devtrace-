import requests


class GitHubClient:

    BASE_URL = "https://api.github.com"

    def __init__(self, token=None):

        self.session = requests.Session()

        if token:
            self.session.headers.update({
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            })

    def get_repository(self, owner, repo):

        url = f"{self.BASE_URL}/repos/{owner}/{repo}"

        response = self.session.get(url)

        response.raise_for_status()

        return response.json()

    def get_commits(self, owner, repo, per_page=100):

        url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"

        response = self.session.get(
            url,
            params={"per_page": per_page}
        )

        response.raise_for_status()

        return response.json()

    def get_contents(self, owner, repo, path=""):

        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"

        response = self.session.get(url)

        response.raise_for_status()

        return response.json()
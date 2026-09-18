import requests


class FileAnalyzer:

    def __init__(self, github_client):
        self.github = github_client

    def analyze(self, owner, repo, path=""):

        contents = self.github.get_contents(owner, repo, path)

        files = []
        directories = []

        for item in contents:

            if item["type"] == "file":
                files.append({
                    "name": item["name"],
                    "path": item["path"],
                    "size": item["size"]
                })

            elif item["type"] == "dir":
                directories.append(item["path"])

        return {
            "files": files,
            "directories": directories,
            "total_files": len(files),
            "total_directories": len(directories)
        }
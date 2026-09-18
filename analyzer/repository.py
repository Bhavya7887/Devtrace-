class RepositoryAnalyzer:

    def __init__(self, repository):
        self.repository = repository

    def analyze(self):

        return {
            "name": self.repository.get("name"),
            "full_name": self.repository.get("full_name"),
            "description": self.repository.get("description"),
            "language": self.repository.get("language"),
            "stars": self.repository.get("stargazers_count"),
            "forks": self.repository.get("forks_count"),
            "open_issues": self.repository.get("open_issues_count"),
            "size": self.repository.get("size"),
            "created_at": self.repository.get("created_at"),
            "updated_at": self.repository.get("updated_at"),
        }
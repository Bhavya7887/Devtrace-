from collections import Counter


class CommitAnalyzer:

    def __init__(self, commits):
        self.commits = commits

    def analyze(self):

        authors = []

        for commit in self.commits:

            author = commit.get("commit", {}).get("author", {})

            name = author.get("name")

            if name:
                authors.append(name)

        author_counts = Counter(authors)

        return {
            "total_commits": len(self.commits),
            "contributors": len(author_counts),
            "top_contributors": author_counts.most_common(5)
        }
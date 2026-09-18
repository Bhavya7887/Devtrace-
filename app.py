from config import GITHUB_TOKEN

from github.client import GitHubClient
from analyzer.repository import RepositoryAnalyzer
from analyzer.commits import CommitAnalyzer
from analyzer.files import FileAnalyzer
from analyzer.risk import RiskAnalyzer


def main():

    owner = input("GitHub username: ").strip()
    repo = input("Repository name: ").strip()

    github = GitHubClient(GITHUB_TOKEN)

    print("\n[+] Fetching repository...")
    repository = github.get_repository(owner, repo)

    print("[+] Fetching commits...")
    commits = github.get_commits(owner, repo)

    print("[+] Scanning files...")
    file_data = FileAnalyzer(github).analyze(owner, repo)

    print("[+] Calculating risk...")
    risk_data = RiskAnalyzer(file_data["files"]).analyze()

    repository_analysis = RepositoryAnalyzer(repository).analyze()
    commit_analysis = CommitAnalyzer(commits).analyze()

    print("\n" + "=" * 55)
    print("                    DEVTRACE")
    print("=" * 55)

    print("\nREPOSITORY")

    print(f"Name           : {repository_analysis['full_name']}")
    print(f"Language       : {repository_analysis['language']}")
    print(f"Stars          : {repository_analysis['stars']}")
    print(f"Forks          : {repository_analysis['forks']}")
    print(f"Open Issues    : {repository_analysis['open_issues']}")

    print("\nDEVELOPMENT")

    print(f"Commits        : {commit_analysis['total_commits']}")
    print(f"Contributors   : {commit_analysis['contributors']}")

    print("\nCODEBASE")

    print(f"Files          : {file_data['total_files']}")
    print(f"Directories    : {file_data['total_directories']}")

    print("\nCODE RISK")

    for item in risk_data:
        print(
            f"  {item['path']:<35}"
            f"{item['risk']:<10}"
            f"{item['size']} bytes"
        )

    print("\nTOP CONTRIBUTORS")

    for name, count in commit_analysis["top_contributors"]:
        print(f"  {name:<25} {count} commits")

    print("\n" + "=" * 55)


if __name__ == "__main__":
    main()
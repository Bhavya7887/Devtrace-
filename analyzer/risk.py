import re


class RiskAnalyzer:

    SECRET_PATTERNS = [

        # API keys / tokens
        r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\'][^"\']+["\']',

        r'(?i)(access[_-]?token|auth[_-]?token)\s*[:=]\s*["\'][^"\']+["\']',

        # Passwords / secrets
        r'(?i)(password|passwd|pwd)\s*[:=]\s*["\'][^"\']+["\']',

        r'(?i)(secret|client[_-]?secret)\s*[:=]\s*["\'][^"\']+["\']',

        # GitHub token
        r'gh[pousr]_[A-Za-z0-9_]+',

        # AWS access key
        r'AKIA[0-9A-Z]{16}',

        # Generic bearer token
        r'(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*',
    ]

    def __init__(self, files, github_client=None, owner=None, repo=None):

        self.files = files
        self.github = github_client
        self.owner = owner
        self.repo = repo

    def analyze(self):

        results = []

        for file in self.files:

            path = file["path"]
            size = file["size"]

            findings = []
            score = 0

            # --------------------------------
            # LARGE FILE CHECK
            # --------------------------------

            if size > 10000:

                findings.append("Large file")
                score += 20

            elif size > 5000:

                findings.append("Moderately large file")
                score += 10

            # --------------------------------
            # FILE NAME CHECK
            # --------------------------------

            suspicious_names = [

                ".env",
                "config.py",
                "secrets.py",
                "secret.py",
                "credentials.py",
                "password.py"

            ]

            filename = path.split("/")[-1].lower()

            if filename in suspicious_names:

                findings.append("Sensitive filename")
                score += 35

            # --------------------------------
            # CODE CONTENT CHECK
            # --------------------------------

            content = ""

            if self.github and self.owner and self.repo:

                try:

                    data = self.github.get_contents(
                        self.owner,
                        self.repo,
                        path
                    )

                    # GitHub API returns file content encoded in base64
                    import base64

                    if isinstance(data, dict) and data.get("content"):

                        content = base64.b64decode(
                            data["content"]
                        ).decode(
                            "utf-8",
                            errors="ignore"
                        )

                except Exception:

                    content = ""

            # --------------------------------
            # SECRET DETECTION
            # --------------------------------

            for pattern in self.SECRET_PATTERNS:

                if re.search(pattern, content):

                    findings.append("Possible hardcoded secret")
                    score += 50

                    break

            # --------------------------------
            # TODO / FIXME
            # --------------------------------

            if re.search(r'(?i)\b(TODO|FIXME)\b', content):

                findings.append("TODO/FIXME detected")
                score += 5

            # --------------------------------
            # RISK LEVEL
            # --------------------------------

            if score >= 50:

                risk = "HIGH"

            elif score >= 20:

                risk = "MEDIUM"

            else:

                risk = "LOW"

            results.append({

                "path": path,
                "size": size,
                "risk": risk,
                "score": min(score, 100),
                "findings": findings

            })

        return results
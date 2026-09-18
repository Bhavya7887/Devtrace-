from django.db import models


class Report(models.Model):

    repository_name = models.CharField(max_length=255)
    repository_url = models.URLField()

    language = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    stars = models.IntegerField(default=0)
    forks = models.IntegerField(default=0)
    open_issues = models.IntegerField(default=0)

    total_commits = models.IntegerField(default=0)
    contributors = models.IntegerField(default=0)

    total_files = models.IntegerField(default=0)
    total_directories = models.IntegerField(default=0)

    repository_data = models.JSONField(default=dict)
    commit_data = models.JSONField(default=dict)
    file_data = models.JSONField(default=dict)
    risk_data = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.repository_name
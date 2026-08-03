from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    salary = models.PositiveIntegerField()
    description = models.TextField()
    required_skills = models.TextField()
    experience = models.CharField(max_length=100)
    job_type = models.CharField(
        max_length=50,
        choices=[
            ('Full Time','Full Time'),
            ('Part Time','Part Time'),
            ('Internship','Internship'),
            ('Remote','Remote')
        ]
    )
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_jobs")
    csv_index = models.PositiveIntegerField()
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "csv_index"], name="unique_saved_csv_job")]

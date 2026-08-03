from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    skills = models.TextField(blank=True)
    education = models.CharField(max_length=200, blank=True)
    secondary_school = models.CharField(max_length=200, blank=True)
    secondary_marks = models.CharField(max_length=30, blank=True)
    higher_secondary_school = models.CharField(max_length=200, blank=True)
    higher_secondary_marks = models.CharField(max_length=30, blank=True)
    university = models.CharField(max_length=200, blank=True)
    university_marks = models.CharField(max_length=30, blank=True)
    experience = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True, max_length=300)
    github_url = models.URLField(blank=True, max_length=300)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    cv_extracted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username

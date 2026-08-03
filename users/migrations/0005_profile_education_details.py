from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("users", "0004_profile_github_url_profile_linkedin_url")]
    operations = [
        migrations.AddField(model_name="profile", name="secondary_school", field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name="profile", name="secondary_marks", field=models.CharField(blank=True, max_length=30)),
        migrations.AddField(model_name="profile", name="higher_secondary_school", field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name="profile", name="higher_secondary_marks", field=models.CharField(blank=True, max_length=30)),
        migrations.AddField(model_name="profile", name="university", field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name="profile", name="university_marks", field=models.CharField(blank=True, max_length=30)),
    ]

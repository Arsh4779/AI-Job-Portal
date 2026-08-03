from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("users", "0005_profile_education_details")]
    operations = [
        migrations.AddField(
            model_name="profile",
            name="training",
            field=models.TextField(blank=True),
        ),
    ]

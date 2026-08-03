from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("jobs", "0001_initial")]
    operations = [migrations.CreateModel(name="SavedJob", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("csv_index", models.PositiveIntegerField()), ("saved_at", models.DateTimeField(auto_now_add=True)), ("user", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="saved_jobs", to=settings.AUTH_USER_MODEL))], options={"constraints": [models.UniqueConstraint(fields=("user", "csv_index"), name="unique_saved_csv_job")]})]

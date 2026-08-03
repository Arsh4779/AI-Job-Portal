from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("users", "0006_profile_training")]
    operations = [
        migrations.RemoveField(model_name="profile", name="training"),
    ]

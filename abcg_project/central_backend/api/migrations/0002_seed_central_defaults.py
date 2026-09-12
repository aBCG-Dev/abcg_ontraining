from django.db import migrations
from django.contrib.auth.models import User

def seed_defaults(apps, schema_editor):
    GlobalSettings = apps.get_model('api', 'GlobalSettings')
    
    # Create default study settings
    GlobalSettings.objects.get_or_create(
        name="Study Settings",
        defaults={
            "bmi_threshold": 18.0,
            "age_threshold": 60,
            "campaign_period": "Jan 2025 - Mar 2025"
        }
    )
    
    # Create default administrator user for login
    # User model must be imported using django's default User model because of auth framework
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "adminpassword")

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(seed_defaults),
    ]

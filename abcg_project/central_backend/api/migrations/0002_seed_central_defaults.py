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
    # Temporarily disconnect User post_save signal to prevent premature UserProfile creation
    # before later migrations add the 'role' column.
    from django.db.models.signals import post_save
    from django.contrib.auth.models import User
    try:
        from api.models import create_central_profile, save_central_profile
        post_save.disconnect(create_central_profile, sender=User)
        post_save.disconnect(save_central_profile, sender=User)
    except Exception:
        create_central_profile = None
        save_central_profile = None

    try:
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "adminpassword")
    finally:
        if create_central_profile:
            post_save.connect(create_central_profile, sender=User)
        if save_central_profile:
            post_save.connect(save_central_profile, sender=User)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(seed_defaults),
    ]

from django.db import migrations

def deactivate_child_symptoms(apps, schema_editor):
    Symptom = apps.get_model('questions', 'Symptom')
    Symptom.objects.filter(code__in=['fail_weight', 'decreased_activity']).update(is_active=False)

def reactivate_child_symptoms(apps, schema_editor):
    Symptom = apps.get_model('questions', 'Symptom')
    Symptom.objects.filter(code__in=['fail_weight', 'decreased_activity']).update(is_active=True)

class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0044_add_updated_at_to_participants'),
    ]

    operations = [
        migrations.RunPython(deactivate_child_symptoms, reactivate_child_symptoms),
    ]


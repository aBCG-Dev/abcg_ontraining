from django.db import migrations

def add_others_occupation(apps, schema_editor):
    Question = apps.get_model("questions", "Question")
    Option = apps.get_model("questions", "Option")
    q = Question.objects.filter(code="occupation").first()
    if q:
        Option.objects.get_or_create(
            question=q,
            code="others",
            defaults={"name": "Others", "display_order": 99, "is_active": True}
        )

def remove_others_occupation(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('questions', '0039_ineligibleindividual_government_id_name_and_more'),
    ]

    operations = [
        migrations.RunPython(add_others_occupation, remove_others_occupation),
    ]

from django.db import migrations

def seed_questions_and_options(apps, schema_editor):
    Question = apps.get_model('api', 'Question')
    Option = apps.get_model('api', 'Option')

    q_data = [
        ("sector", "Sector", 1, "radio", [
            ("public_sector", "Public Sector"),
            ("private_sector", "Private Sector")
        ]),
        ("case_finding_type", "Type of Case Finding", 1, "radio", [
            ("passive", "Passive (Routine programme)"),
            ("active", "Active (Active Case Finding)")
        ]),
        ("gender", "Gender", 2, "radio", [
            ("male", "Male"),
            ("female", "Female"),
            ("transgender", "Transgender")
        ]),
        ("demographic_area", "Demographic Area", 3, "select", [
            ("urban", "Urban"),
            ("rural", "Rural"),
            ("tribal", "Tribal")
        ]),
        ("marital_status", "Marital Status", 3, "select", [
            ("single", "Single"),
            ("married", "Married"),
            ("divorced", "Divorced"),
            ("widowed", "Widowed")
        ]),
        ("occupation", "Occupation", 3, "select", [
            ("teaching", "Teaching professional"),
            ("student", "Student"),
            ("self_employed", "Self employed"),
            ("homemaker", "Homemaker / housewife"),
            ("retired", "Retired"),
            ("unemployed", "Unemployed"),
            ("other", "Other")
        ]),
        ("socioeconomic_status", "Socio-economic Status", 3, "select", [
            ("apl", "APL"),
            ("bpl", "BPL")
        ]),
        ("hiv_status", "HIV Status", 4, "select", [
            ("unknown", "Unknown"),
            ("positive", "Positive"),
            ("reactive", "Reactive"),
            ("negative", "Non Reactive / Negative")
        ])
    ]

    for idx, (code, label, step, field_type, options_list) in enumerate(q_data):
        q_obj, created = Question.objects.get_or_create(
            code=code,
            defaults={
                "label": label,
                "step": step,
                "field_type": field_type,
                "display_order": idx
            }
        )
        if created:
            for opt_idx, (opt_code, opt_name) in enumerate(options_list):
                Option.objects.get_or_create(
                    question=q_obj,
                    code=opt_code,
                    defaults={
                        "name": opt_name,
                        "display_order": opt_idx
                    }
                )

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_question_option'),
    ]

    operations = [
        migrations.RunPython(seed_questions_and_options),
    ]

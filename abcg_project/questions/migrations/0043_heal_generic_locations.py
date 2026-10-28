from django.db import migrations
from django.db.models import Q

def heal_locations(apps, schema_editor):
    Participant = apps.get_model('questions', 'Participant')
    TptIndividual = apps.get_model('questions', 'TptIndividual')
    IneligibleIndividual = apps.get_model('questions', 'IneligibleIndividual')

    location_rules = [
        ("ABCG-AN-NEL-", "ACSR Medical college", "Andhra Pradesh", "Sri Potti Sriramulu Nellore", "NELLORE-1"),
        ("ABCG-AN-GUN-", "Guntur DTC", "Andhra Pradesh", "Guntur", "Guntur DTC"),
        ("ABCG-OD-BAR-", "Mayurbhanj", "Odisha", "Mayurbhanj", "Baripada_DTC"),
        ("ABCG-OD-URB-", "SCB", "Odisha", "Cuttack", "Urban_TU"),
        ("ABCG-TN-TIR-", "Avadi", "Tamil Nadu", "Tiruvallur", "Tiruvallur TU"),
        ("ABCG-KA-BEN-", "Bengaluru", "Karnataka", "Bengaluru", "Bengaluru TU"),
    ]

    for model in [Participant, TptIndividual, IneligibleIndividual]:
        generic_q = (
            Q(state__iexact="GLOBAL") |
            Q(district__iexact="ALL DISTRICTS") |
            Q(tb_unit__iexact="ALL TB UNITS") |
            Q(tb_unit__iexact="GLOBAL")
        )

        for prefix, fac, st, dist, tu in location_rules:
            filter_q = generic_q & (Q(study_id__startswith=prefix) | Q(facility__icontains=fac))
            model.objects.filter(filter_q).update(state=st, district=dist, tb_unit=tu)

class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0042_ineligibleindividual_consent_participant_consent_and_more'),
    ]

    operations = [
        migrations.RunPython(heal_locations, reverse_code=migrations.RunPython.noop),
    ]

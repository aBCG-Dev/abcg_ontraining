# Generated manually to update high-risk groups as requested by the user

from django.db import migrations

def update_risk_factors(apps, schema_editor):
    RiskFactor = apps.get_model('questions', 'RiskFactor')
    
    # 1. Update Elderly name
    RiskFactor.objects.filter(code='elderly').update(
        name="Individuals aged 60 years or above",
        is_target_hrg=True
    )
    
    # 2. Update Malnourished name
    RiskFactor.objects.filter(code='malnourished').update(
        name="Individuals with a Body Mass Index of less than 18 kg per sq.mts",
        is_target_hrg=True
    )
    
    # 3. Update Contact name
    RiskFactor.objects.filter(code='contact').update(
        name="Contacts of current TB patients as well as all those contacts of index TB cases enrolled in Ni-kshay from 1st January 2021",
        is_target_hrg=True
    )
    
    # 4. Update Diabetes name
    RiskFactor.objects.filter(code='diabetes').update(
        name="Diabetes (Self- reported).",
        is_target_hrg=True
    )
    
    # 5. Update Past TB name
    RiskFactor.objects.filter(code='past_tb').update(
        name="People who are reported to have at least one episode of TB in past 5 years.",
        is_target_hrg=True
    )
    
    # 6. Add or update Smoker RiskFactor
    smoker_rf, created = RiskFactor.objects.get_or_create(
        code='smoker',
        defaults={
            'name': "Individuals with a history of smoking tobacco (Current / Past User)- self reported",
            'is_target_hrg': True,
            'display_order': 6
        }
    )
    if not created:
        smoker_rf.name = "Individuals with a history of smoking tobacco (Current / Past User)- self reported"
        smoker_rf.is_target_hrg = True
        smoker_rf.save()

class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0029_devicesynclog'),
    ]

    operations = [
        migrations.RunPython(update_risk_factors),
    ]

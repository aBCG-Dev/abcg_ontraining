from django.db import migrations


def renumber_cohort(apps, schema_editor):
    Participant = apps.get_model('questions', 'Participant')
    TptIndividual = apps.get_model('questions', 'TptIndividual')
    IneligibleIndividual = apps.get_model('questions', 'IneligibleIndividual')
    NikshayRecord = apps.get_model('questions', 'NikshayRecord')

    # 1. Renumber Participants per TBU
    tbu_ids = list(Participant.objects.values_list('tbu_id', flat=True).distinct())
    for t_id in tbu_ids:
        if t_id is None:
            continue
        pts = list(Participant.objects.filter(tbu_id=t_id).order_by('date_enroll', 'id'))
        for seq, p in enumerate(pts, start=1):
            if not p.legacy_study_id:
                p.legacy_study_id = p.study_id
            if not p.legacy_screening_id:
                p.legacy_screening_id = p.screening_id or p.study_id
            st_id = p.state_id or 99
            dist_id = p.district_id or 999
            new_study_id = f"ABCG-{st_id}-{dist_id}-{t_id}-{seq:06d}"
            new_screening_id = f"SCREENED-{st_id}-{dist_id}-{t_id}-{seq:06d}"
            p.study_id = new_study_id
            p.screening_id = new_screening_id
            p.save()
            NikshayRecord.objects.filter(participant_id=p.id).update(
                study_id=new_study_id,
                screening_id=new_screening_id
            )

    # 2. Renumber TPT Individuals per TBU
    tbu_ids_tpt = list(TptIndividual.objects.values_list('tbu_id', flat=True).distinct())
    for t_id in tbu_ids_tpt:
        if t_id is None:
            continue
        tpts = list(TptIndividual.objects.filter(tbu_id=t_id).order_by('date_enroll', 'id'))
        for seq, t in enumerate(tpts, start=1):
            if not t.legacy_study_id:
                t.legacy_study_id = t.study_id
            if not t.legacy_screening_id:
                t.legacy_screening_id = t.screening_id or t.study_id
            st_id = t.state_id or 99
            dist_id = t.district_id or 999
            new_study_id = f"ABCG-{st_id}-{dist_id}-{t_id}-{seq:06d}"
            new_screening_id = f"SCREENED-{st_id}-{dist_id}-{t_id}-{seq:06d}"
            t.study_id = new_study_id
            t.screening_id = new_screening_id
            t.save()
            NikshayRecord.objects.filter(tpt_individual_id=t.id).update(
                study_id=new_study_id,
                screening_id=new_screening_id
            )

    # 3. Renumber Ineligible Individuals per TBU
    tbu_ids_inel = list(IneligibleIndividual.objects.values_list('tbu_id', flat=True).distinct())
    for t_id in tbu_ids_inel:
        if t_id is None:
            continue
        inels = list(IneligibleIndividual.objects.filter(tbu_id=t_id).order_by('date_enroll', 'id'))
        for seq, inel in enumerate(inels, start=1):
            if not inel.legacy_study_id:
                inel.legacy_study_id = inel.study_id
            if not inel.legacy_screening_id:
                inel.legacy_screening_id = inel.screening_id or inel.study_id
            st_id = inel.state_id or 99
            dist_id = inel.district_id or 999
            new_id = f"SCREENED-{st_id}-{dist_id}-{t_id}-{seq:06d}"
            inel.study_id = new_id
            inel.screening_id = new_id
            inel.save()
            NikshayRecord.objects.filter(ineligible_individual_id=inel.id).update(
                study_id=new_id,
                screening_id=new_id
            )


def reverse_renumber(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0048_ineligibleindividual_legacy_screening_id_and_more'),
    ]

    operations = [
        migrations.RunPython(renumber_cohort, reverse_renumber),
    ]

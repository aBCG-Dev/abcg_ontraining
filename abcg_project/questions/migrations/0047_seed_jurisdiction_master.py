from django.db import migrations


def seed_jurisdiction_master(apps, schema_editor):
    StudySite = apps.get_model("questions", "StudySite")
    Participant = apps.get_model("questions", "Participant")
    TptIndividual = apps.get_model("questions", "TptIndividual")
    IneligibleIndividual = apps.get_model("questions", "IneligibleIndividual")
    UserProfile = apps.get_model("questions", "UserProfile")

    from questions.locations_data import MASTER_JURISDICTION_RECORDS, lookup_jurisdiction_by_tbu

    # 1. Delete all Karnataka study sites (as per study requirement)
    StudySite.objects.filter(state__iexact="Karnataka").delete()

    # 2. Deduplicate and clean up StudySite rows (removes uppercase duplicates like JUNNARDEO when Junnardeo exists)
    for site in list(StudySite.objects.all()):
        match = lookup_jurisdiction_by_tbu(site.tb_unit, site.district, site.state)
        if not match:
            site.delete()
            continue

        canonical_name = match["tb_unit"]
        if site.tb_unit != canonical_name:
            if StudySite.objects.filter(tb_unit=canonical_name).exclude(pk=site.pk).exists():
                site.delete()
            else:
                site.state_id = match["state_id"]
                site.state = match["state"]
                site.district_id = match["district_id"]
                site.district = match["district"]
                site.tbu_id = match["tbu_id"]
                site.tb_unit = canonical_name
                site.is_active = True
                site.save()
        else:
            site.state_id = match["state_id"]
            site.state = match["state"]
            site.district_id = match["district_id"]
            site.district = match["district"]
            site.tbu_id = match["tbu_id"]
            site.is_active = True
            site.save()

    # 3. Ensure all 106 master study sites exist and are active
    for rec in MASTER_JURISDICTION_RECORDS:
        StudySite.objects.update_or_create(
            tb_unit=rec["tb_unit"],
            defaults={
                "state_id": rec["state_id"],
                "state": rec["state"],
                "district_id": rec["district_id"],
                "district": rec["district"],
                "tbu_id": rec["tbu_id"],
                "is_active": True,
            }
        )

    # 4. Remove any lingering unmapped or NULL rows
    StudySite.objects.filter(state_id__isnull=True).delete()

    # 5. Standardize and backfill Participant records (fixes casing and fills IDs)
    for p in Participant.objects.all():
        match = lookup_jurisdiction_by_tbu(p.tb_unit, p.district, p.state)
        if match:
            p.state_id = match["state_id"]
            p.state = match["state"]
            p.district_id = match["district_id"]
            p.district = match["district"]
            p.tbu_id = match["tbu_id"]
            p.tb_unit = match["tb_unit"]
            p.save()

    # 6. Standardize and backfill TptIndividual records
    for t in TptIndividual.objects.all():
        match = lookup_jurisdiction_by_tbu(t.tb_unit, t.district, t.state)
        if match:
            t.state_id = match["state_id"]
            t.state = match["state"]
            t.district_id = match["district_id"]
            t.district = match["district"]
            t.tbu_id = match["tbu_id"]
            t.tb_unit = match["tb_unit"]
            t.save()

    # 7. Standardize and backfill IneligibleIndividual records
    for i in IneligibleIndividual.objects.all():
        match = lookup_jurisdiction_by_tbu(i.tb_unit, i.district, i.state)
        if match:
            i.state_id = match["state_id"]
            i.state = match["state"]
            i.district_id = match["district_id"]
            i.district = match["district"]
            i.tbu_id = match["tbu_id"]
            i.tb_unit = match["tb_unit"]
            i.save()

    # 8. Standardize and backfill UserProfile records
    for up in UserProfile.objects.all():
        match = lookup_jurisdiction_by_tbu(up.tb_unit, up.district, up.state)
        if match:
            up.state_id = match["state_id"]
            up.state = match["state"]
            up.district_id = match["district_id"]
            up.district = match["district"]
            up.tbu_id = match["tbu_id"]
            up.tb_unit = match["tb_unit"]
            up.save()


def reverse_jurisdiction_master(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0046_alter_studysite_options_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_jurisdiction_master, reverse_jurisdiction_master),
    ]

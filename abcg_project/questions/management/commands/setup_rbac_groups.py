from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from questions.models import Participant, UserProfile

class Command(BaseCommand):
    help = "Initializes native Django Groups and maps model permissions."

    def handle(self, *args, **options):
        self.stdout.write("Initializing standard Django groups and permissions...")

        # 1. Get ContentType for Participant
        participant_ct = ContentType.objects.get_for_model(Participant)

        # 2. Get or create custom permissions
        custom_perms_data = [
            ("export_participant", "Can export participant registrations"),
            ("approve_reconciliation", "Can approve Nikshay reconciliation"),
            ("perform_bulk_sync", "Can perform bulk sync operations"),
            ("view_telemetry_logs", "Can view telemetry and audit logs"),
            ("doctor_review", "Can perform doctor diagnostic review"),
        ]

        custom_perms = {}
        for codename, name in custom_perms_data:
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=participant_ct,
                defaults={"name": name}
            )
            custom_perms[codename] = perm
            if created:
                self.stdout.write(f"Created custom permission: {codename}")

        # 3. Get standard model permissions
        std_perms = {}
        for action in ["add", "change", "delete", "view"]:
            codename = f"{action}_participant"
            try:
                std_perms[codename] = Permission.objects.get(
                    codename=codename,
                    content_type=participant_ct
                )
            except Permission.DoesNotExist:
                # If they do not exist yet, create them programmatically
                perm = Permission.objects.create(
                    codename=codename,
                    name=f"Can {action} participant",
                    content_type=participant_ct
                )
                std_perms[codename] = perm
                self.stdout.write(f"Created standard permission: {codename}")

        # Get UserProfile content type and permissions for Admin user management
        profile_ct = ContentType.objects.get_for_model(UserProfile)
        profile_perms = {}
        for action in ["add", "change", "delete", "view"]:
            codename = f"{action}_userprofile"
            perm, _ = Permission.objects.get_or_create(
                codename=codename,
                content_type=profile_ct,
                defaults={"name": f"Can {action} user profile"}
            )
            profile_perms[codename] = perm

        # 4. Initialize Groups
        group_assignments = {
            "Super Admin": list(std_perms.values()) + list(custom_perms.values()) + list(profile_perms.values()),
            "Admin": [
                std_perms["add_participant"],
                std_perms["change_participant"],
                std_perms["view_participant"],
                custom_perms["export_participant"],
                custom_perms["view_telemetry_logs"],
                profile_perms["add_userprofile"],
                profile_perms["change_userprofile"],
                profile_perms["view_userprofile"],
            ],
            "Nodal Officer": [
                std_perms["view_participant"],
                custom_perms["approve_reconciliation"],
                custom_perms["perform_bulk_sync"],
                custom_perms["view_telemetry_logs"],
            ],
            "Doctor": [
                std_perms["view_participant"],
                std_perms["change_participant"],
                custom_perms["doctor_review"],
            ],
            "Project Nurse": [
                std_perms["add_participant"],
                std_perms["change_participant"],
                std_perms["view_participant"],
                custom_perms["perform_bulk_sync"],
            ]
        }

        for group_name, perms in group_assignments.items():
            group, created = Group.objects.get_or_create(name=group_name)
            group.permissions.set(perms)
            group.save()
            action_str = "Created" if created else "Updated"
            self.stdout.write(f"{action_str} group: {group_name} with {len(perms)} permissions.")

        self.stdout.write(self.style.SUCCESS("Successfully setup all RBAC groups and permissions."))

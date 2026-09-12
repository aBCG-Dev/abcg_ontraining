"""
Management command to load default RBAC permissions into the database.

Usage:
    python manage.py load_rbac_permissions          # Load permissions
    python manage.py load_rbac_permissions --reset  # Clear and reload
    python manage.py load_rbac_permissions --list   # List all permissions
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from questions.models import RolePermission
from questions.decorators import DEFAULT_PERMISSIONS


class Command(BaseCommand):
    help = "Load default RBAC permissions into the RolePermission table"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Clear existing permissions and reload from defaults'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all permissions without saving to database'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each permission loaded'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        list_only = options.get('list', False)
        reset = options.get('reset', False)

        self.stdout.write(
            self.style.HTTP_INFO("=" * 60)
        )
        self.stdout.write(
            self.style.HTTP_INFO("RBAC Permission Loader")
        )
        self.stdout.write(
            self.style.HTTP_INFO("=" * 60)
        )

        existing_count = RolePermission.objects.count()
        self.stdout.write(
            f"\nExisting permissions in database: {existing_count}"
        )

        if reset:
            self.stdout.write(
                self.style.WARNING("\n[!] Resetting all permissions...")
            )
            RolePermission.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS("[OK] Cleared all existing permissions")
            )

        created_count = 0
        updated_count = 0
        total_count = 0
        permission_summary = {}

        self.stdout.write(
            self.style.HTTP_INFO("\nProcessing permissions from DEFAULT_PERMISSIONS...")
        )

        try:
            for role, modules in DEFAULT_PERMISSIONS.items():
                if role not in permission_summary:
                    permission_summary[role] = {'created': 0, 'updated': 0, 'total': 0}

                for module, actions in modules.items():
                    for action in actions:
                        total_count += 1
                        permission_summary[role]['total'] += 1

                        if list_only:
                            self.stdout.write(
                                f"  {role:20s} | {module:30s} | {action:20s} | ALLOWED"
                            )
                            continue

                        perm_obj, created = RolePermission.objects.get_or_create(
                            role=role,
                            module=module,
                            action=action,
                            defaults={'allowed': True}
                        )

                        if created:
                            created_count += 1
                            permission_summary[role]['created'] += 1
                            if verbose:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"  [+] Created: {role} -> {module} -> {action}"
                                    )
                                )
                        else:
                            if perm_obj.allowed is not True:
                                perm_obj.allowed = True
                                perm_obj.save()
                                updated_count += 1
                                permission_summary[role]['updated'] += 1
                            if verbose:
                                self.stdout.write(
                                    f"  [~] Already exists: {role} -> {module} -> {action}"
                                )

        except Exception as e:
            raise CommandError(
                self.style.ERROR(f"Error loading permissions: {str(e)}")
            )

        if list_only:
            self.stdout.write(
                self.style.SUCCESS(f"\n\nTotal permissions in DEFAULT_PERMISSIONS: {total_count}")
            )
            return

        self.stdout.write(
            self.style.HTTP_INFO("\n" + "=" * 60)
        )
        self.stdout.write(
            self.style.HTTP_INFO("SUMMARY BY ROLE")
        )
        self.stdout.write(
            self.style.HTTP_INFO("=" * 60)
        )

        for role in sorted(permission_summary.keys()):
            stats = permission_summary[role]
            self.stdout.write(
                f"\n{role:20s}: "
                f"Total={stats['total']:2d} | "
                f"Created={stats['created']:2d} | "
                f"Updated={stats['updated']:2d}"
            )

        self.stdout.write(
            self.style.HTTP_INFO("\n" + "=" * 60)
        )
        self.stdout.write(
            self.style.HTTP_INFO("OPERATION COMPLETE")
        )
        self.stdout.write(
            self.style.HTTP_INFO("=" * 60)
        )

        self.stdout.write(f"\nTotal permissions processed: {total_count}")
        self.stdout.write(f"New permissions created:     {created_count}")
        self.stdout.write(f"Existing permissions updated: {updated_count}")
        self.stdout.write(f"Total in database:           {RolePermission.objects.count()}")

        if created_count > 0 or updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS("\n[OK] RBAC permissions loaded successfully!")
            )
        else:
            self.stdout.write(
                self.style.WARNING("\n[!] No changes made (permissions already loaded)")
            )

        self.stdout.write("")

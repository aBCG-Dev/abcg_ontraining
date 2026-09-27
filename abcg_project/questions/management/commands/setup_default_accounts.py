from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from questions.models import UserProfile

DEFAULT_USERS = [
    {
        "username": "admin",
        "email": "admin@abcg.org",
        "password": "admin123",
        "full_name": "System Administrator",
        "role": "Super Admin",
        "is_superuser": True,
        "is_staff": True,
    },
    {
        "username": "staff",
        "email": "staff@abcg.org",
        "password": "staff123",
        "full_name": "Field Project Nurse",
        "role": "Project Nurse",
        "is_superuser": False,
        "is_staff": False,
    },
    {
        "username": "nodal",
        "email": "nodal@abcg.org",
        "password": "staff123",
        "full_name": "District Nodal Officer",
        "role": "Nodal Officer",
        "is_superuser": False,
        "is_staff": False,
    },
    {
        "username": "doctor_user",
        "email": "doctor@abcg.org",
        "password": "staff123",
        "full_name": "Study Medical Officer",
        "role": "Doctor",
        "is_superuser": False,
        "is_staff": False,
    },
]


class Command(BaseCommand):
    help = "Initializes default training and administrator user accounts if they do not already exist."

    def handle(self, *args, **options):
        self.stdout.write("Checking default user accounts...")
        for udata in DEFAULT_USERS:
            username = udata["username"]
            user = User.objects.filter(username=username).first()
            if not user:
                user = User.objects.create_user(
                    username=username,
                    email=udata["email"],
                    password=udata["password"],
                    is_superuser=udata.get("is_superuser", False),
                    is_staff=udata.get("is_staff", False),
                )
                self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))
            else:
                user.set_password(udata["password"])
                user.is_superuser = udata.get("is_superuser", False)
                user.is_staff = udata.get("is_staff", False)
                user.is_active = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Updated password & status for: {username}"))
            
            # Ensure profile exists and has role
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={"full_name": udata["full_name"], "role": udata["role"]}
            )
            profile.role = udata["role"]
            profile.full_name = udata["full_name"]
            profile.save()

        self.stdout.write(self.style.SUCCESS("All default accounts verified successfully."))

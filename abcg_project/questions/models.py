from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone




class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("Super Admin", "Super Admin"),
        ("Admin", "Admin"),
        ("Nodal Officer", "Nodal Officer"),
        ("Doctor", "Doctor"),
        ("Project Nurse", "Project Nurse"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="Project Nurse")
    state = models.CharField(max_length=100, default="Tamil Nadu")
    district = models.CharField(max_length=100, default="Tiruvallur")
    tb_unit = models.CharField(max_length=100, default="Tiruvallur TU")

    def __str__(self):
        return f"{self.user.username} Profile ({self.role})"


class AuditLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_actions")
    action = models.CharField(max_length=255)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_targets")
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.actor} - {self.action} on {self.target_user} at {self.timestamp}"


class RolePermission(models.Model):
    role = models.CharField(max_length=50, choices=UserProfile.ROLE_CHOICES)
    module = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    allowed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("role", "module", "action")

    def __str__(self):
        return f"{self.role} - {self.module} - {self.action}: {self.allowed}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, full_name=instance.get_full_name() or instance.username)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, "profile"):
        UserProfile.objects.create(user=instance, full_name=instance.get_full_name() or instance.username)
    instance.profile.save()


@receiver(post_save, sender=UserProfile)
def sync_user_groups(sender, instance, **kwargs):
    """
    Automatically synchronize native Django Group memberships whenever UserProfile.role is updated.
    If role is Super Admin, sets is_superuser and is_staff to True.
    """
    user = instance.user
    role = instance.role
    if role:
        from django.contrib.auth.models import Group
        # Get or create group
        group, _ = Group.objects.get_or_create(name=role)
        # Clear other role groups
        all_roles = ["Super Admin", "Admin", "Nodal Officer", "Doctor", "Project Nurse"]
        for r in all_roles:
            if r != role:
                try:
                    g = Group.objects.get(name=r)
                    user.groups.remove(g)
                except Group.DoesNotExist:
                    pass
        user.groups.add(group)
        
        # Super Admin updates
        if role == "Super Admin":
            if not user.is_superuser or not user.is_staff:
                User.objects.filter(pk=user.pk).update(is_superuser=True, is_staff=True)
        else:
            if user.is_superuser or user.is_staff:
                User.objects.filter(pk=user.pk).update(is_superuser=False, is_staff=False)


class Participant(models.Model):
    CLASSIFICATION_CHOICES = [
        ("Case", "Case"),
        ("Control", "Control"),
        ("Pending", "Pending"),
        ("Not Eligible", "Not Eligible"),
        ("TPT+BCG", "TPT+BCG"),
        ("Excluded", "Excluded"),
    ]

    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    dob = models.DateField(null=True, blank=True)
    secondary_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    full_name = models.CharField(max_length=250)
    study_id = models.CharField(max_length=50, unique=True)
    screening_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    nikshay_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    reconciliation_status = models.CharField(max_length=50, default="UNRECONCILED", db_index=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    date_enroll = models.DateField()
    
    # Geography & Campaign wash-out details
    state = models.CharField(max_length=100, default="Tamil Nadu")
    district = models.CharField(max_length=100, default="Tiruvallur")
    tb_unit = models.CharField(max_length=100, default="Tiruvallur TU")
    facility = models.CharField(max_length=100, default="Local Clinic")
    village = models.CharField(max_length=150, default="")
    pincode = models.CharField(max_length=20, default="")
    demographic_area = models.CharField(max_length=100, default="Unknown")
    campaign_completion_date = models.DateField(null=True, blank=True)

    # New Sector & additional details fields
    sector = models.CharField(max_length=50, default="Public Sector")
    case_finding_type = models.CharField(max_length=100, blank=True, null=True)
    private_facility = models.CharField(max_length=150, blank=True, null=True)
    public_phi = models.CharField(max_length=150, blank=True, null=True)
    father_husband_name = models.CharField(max_length=150, blank=True, null=True)
    secondary_phone_1 = models.CharField(max_length=15, blank=True, null=True)
    secondary_phone_2 = models.CharField(max_length=15, blank=True, null=True)
    secondary_phone_3 = models.CharField(max_length=15, blank=True, null=True)
    taluka_block = models.CharField(max_length=150, blank=True, null=True)
    landmark = models.CharField(max_length=250, blank=True, null=True)
    
    # Contact Person Details
    contact_person_name = models.CharField(max_length=150, blank=True, null=True)
    contact_person_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_person_address = models.TextField(blank=True, null=True)
    
    # Informant Details
    informant_name = models.CharField(max_length=150, blank=True, null=True)
    informant_designation = models.CharField(max_length=150, blank=True, null=True)

    # PTB Screening & Testing fields
    ptb_screened = models.BooleanField(default=False)
    ptb_test_registered = models.BooleanField(default=False)
    ptb_test_type = models.CharField(max_length=100, blank=True, null=True)
    ptb_test_result = models.CharField(max_length=100, blank=True, null=True)
    ptb_test_date = models.DateField(blank=True, null=True)
    ptb_test_facility = models.CharField(max_length=150, blank=True, null=True)
    ptb_test_details = models.TextField(default="{}")
    
    # EPTB Screening fields
    eptb_screened = models.BooleanField(default=False)
    eptb_details = models.TextField(default="{}")
    
    # New Socio-Demographics
    marital_status = models.CharField(max_length=50, default="Unknown")
    occupation = models.CharField(max_length=150, default="Unknown")
    socioeconomic_status = models.CharField(max_length=50, default="Unknown")
    questionnaire_answers = models.TextField(default="{}")
    
    # Symptoms & Clinical Risk Profiles
    symptoms = models.TextField(default="")
    risk_factors = models.TextField(default="")
    hiv_status = models.CharField(max_length=50, default="Unknown")
    
    # Clinical Risk Parameters (HRG Checklist)
    weight_kg = models.FloatField(default=0.0)
    height_cm = models.FloatField(default=0.0)
    bmi = models.FloatField(default=0.0)
    
    past_tb = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    smoker = models.BooleanField(default=False)
    close_contact = models.BooleanField(default=False)
    
    # TPT questions fields
    tpt_undergone = models.CharField(max_length=20, default="No")
    tpt_status = models.CharField(max_length=50, blank=True, null=True)
    tpt_contact_known = models.CharField(max_length=20, blank=True, null=True)
    tpt_history = models.CharField(max_length=100, blank=True, null=True)
    tpt_start_date = models.DateField(blank=True, null=True)
    tpt_end_date = models.DateField(blank=True, null=True)
    tpt_duration_months = models.IntegerField(blank=True, null=True)
    tpt_regimen = models.CharField(max_length=250, blank=True, null=True)
    tpt_risk_factor = models.CharField(max_length=250, blank=True, null=True)

    # BCG Vaccine Evidence Grade
    bcg_evidence = models.CharField(max_length=100, default="No evidence")
    
    # Eligibility Gates Results
    eligible = models.BooleanField(default=True)
    eligible_bcg_campaign = models.BooleanField(default=False, verbose_name="Eligible for BCG vaccine during campaign period")
    bcg_eligibility_criteria = models.TextField(blank=True, null=True, verbose_name="Eligibility Criteria for Adult BCG Vaccination")
    match_hrg = models.CharField(max_length=500, blank=True, null=True) # Assigned primary HRG group
    
    # BCG Vaccine Verification Step 7 Details
    bcg_status = models.CharField(max_length=50, default="No") # "No", "Yes (Verified via Registry)", "Yes (Manually Verified)"
    bcg_beneficiary_id = models.CharField(max_length=100, blank=True, null=True)
    bcg_ben_mobile_number = models.CharField(max_length=50, blank=True, null=True)
    bcg_ben_gender = models.CharField(max_length=50, blank=True, null=True)
    bcg_date = models.CharField(max_length=50, blank=True, null=True)
    bcg_registration_mode = models.CharField(max_length=100, blank=True, null=True)
    bcg_dob = models.CharField(max_length=50, blank=True, null=True)
    bcg_age = models.IntegerField(blank=True, null=True)
    bcg_vaccination_status = models.CharField(max_length=50, blank=True, null=True)
    bcg_first_name = models.CharField(max_length=150, blank=True, null=True)
    bcg_last_name = models.CharField(max_length=150, blank=True, null=True)
    bcg_site_id = models.CharField(max_length=50, blank=True, null=True)
    bcg_approved_by = models.CharField(max_length=50, blank=True, null=True)
    bcg_beneficiary_type_name = models.CharField(max_length=250, blank=True, null=True)
    bcg_pincode = models.CharField(max_length=20, blank=True, null=True)
    bcg_address = models.TextField(blank=True, null=True)
    bcg_facility_id = models.CharField(max_length=50, blank=True, null=True)
    bcg_scar = models.CharField(max_length=20, blank=True, null=True)
    bcg_scar_file = models.FileField(upload_to="bcg_scar_records/", blank=True, null=True)
    bcg_has_record = models.CharField(max_length=20, blank=True, null=True)
    bcg_record_file = models.FileField(upload_to="bcg_records/", blank=True, null=True)
    cxr_record_file = models.FileField(upload_to="cxr_records/", blank=True, null=True)
    
    # Legacy fields for backward compatibility
    bcg_vaccination_date = models.DateField(blank=True, null=True)
    bcg_vaccine_name = models.CharField(max_length=100, default="BCG")
    bcg_batch_number = models.CharField(max_length=100, blank=True, null=True)
    bcg_facility = models.CharField(max_length=250, blank=True, null=True)

    # Classification
    classification = models.CharField(max_length=25, choices=CLASSIFICATION_CHOICES, default="Pending")
    classification_reason = models.TextField(blank=True, default="")
    
    # Sync metadata
    synced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_participants")

    def __str__(self):
        return f"{self.full_name} ({self.study_id})"


class Symptom(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.name


class RiskFactor(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)
    is_target_hrg = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.name


class Question(models.Model):
    FIELD_TYPE_CHOICES = [
        ("radio", "Radio buttons"),
        ("select", "Dropdown list"),
    ]

    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=250)
    step = models.IntegerField(default=1)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default="select")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["step", "display_order", "id"]

    def __str__(self):
        return f"Step {self.step}: {self.label} ({self.code})"


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=250)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]
        unique_together = ("question", "code")

    def __str__(self):
        return f"{self.question.label} - {self.name}"


class BcgVaccination(models.Model):
    beneficiary_id = models.CharField(max_length=100, unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True, default="")
    last_name = models.CharField(max_length=150, blank=True, default="")
    beneficiary_gender = models.CharField(max_length=50, blank=True, default="")
    ben_gender = models.CharField(max_length=50, blank=True, default="")
    age = models.IntegerField(null=True, blank=True)
    ben_mobile_number = models.CharField(max_length=50, blank=True, default="")
    dob = models.CharField(max_length=50, blank=True, default="")
    date = models.CharField(max_length=50, blank=True, default="")
    registration_mode = models.CharField(max_length=100, blank=True, default="")
    vaccination_status = models.CharField(max_length=50, blank=True, default="")
    beneficiary_type_name = models.CharField(max_length=250, blank=True, default="")
    pincode = models.CharField(max_length=20, blank=True, default="")
    address = models.TextField(blank=True, default="")
    facility_id = models.CharField(max_length=50, blank=True, default="")
    site_id = models.CharField(max_length=50, blank=True, default="")
    approved_by = models.CharField(max_length=50, blank=True, default="")
    date_created = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.beneficiary_id})"


class TptIndividual(models.Model):
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    dob = models.DateField(null=True, blank=True)
    secondary_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    full_name = models.CharField(max_length=250)
    study_id = models.CharField(max_length=50, unique=True)
    screening_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    nikshay_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    reconciliation_status = models.CharField(max_length=50, default="UNRECONCILED", db_index=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    date_enroll = models.DateField()
    
    # Geography & Campaign wash-out details
    state = models.CharField(max_length=100, default="Tamil Nadu")
    district = models.CharField(max_length=100, default="Tiruvallur")
    tb_unit = models.CharField(max_length=100, default="Tiruvallur TU")
    facility = models.CharField(max_length=100, default="Local Clinic")
    village = models.CharField(max_length=150, default="")
    pincode = models.CharField(max_length=20, default="")
    demographic_area = models.CharField(max_length=100, default="Unknown")
    campaign_completion_date = models.DateField(null=True, blank=True)

    # New Sector & additional details fields
    sector = models.CharField(max_length=50, default="Public Sector")
    case_finding_type = models.CharField(max_length=100, blank=True, null=True)
    private_facility = models.CharField(max_length=150, blank=True, null=True)
    public_phi = models.CharField(max_length=150, blank=True, null=True)
    father_husband_name = models.CharField(max_length=150, blank=True, null=True)
    secondary_phone_1 = models.CharField(max_length=15, blank=True, null=True)
    secondary_phone_2 = models.CharField(max_length=15, blank=True, null=True)
    secondary_phone_3 = models.CharField(max_length=15, blank=True, null=True)
    taluka_block = models.CharField(max_length=150, blank=True, null=True)
    landmark = models.CharField(max_length=250, blank=True, null=True)
    
    # Contact Person Details
    contact_person_name = models.CharField(max_length=150, blank=True, null=True)
    contact_person_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_person_address = models.TextField(blank=True, null=True)
    
    # Informant Details
    informant_name = models.CharField(max_length=150, blank=True, null=True)
    informant_designation = models.CharField(max_length=150, blank=True, null=True)

    # PTB Screening & Testing fields
    ptb_screened = models.BooleanField(default=False)
    ptb_test_registered = models.BooleanField(default=False)
    ptb_test_type = models.CharField(max_length=100, blank=True, null=True)
    ptb_test_result = models.CharField(max_length=100, blank=True, null=True)
    ptb_test_date = models.DateField(blank=True, null=True)
    ptb_test_facility = models.CharField(max_length=150, blank=True, null=True)
    ptb_test_details = models.TextField(default="{}")
    
    # EPTB Screening fields
    eptb_screened = models.BooleanField(default=False)
    eptb_details = models.TextField(default="{}")
    
    # New Socio-Demographics
    marital_status = models.CharField(max_length=50, default="Unknown")
    occupation = models.CharField(max_length=150, default="Unknown")
    socioeconomic_status = models.CharField(max_length=50, default="Unknown")
    questionnaire_answers = models.TextField(default="{}")
    
    # Symptoms & Clinical Risk Profiles
    symptoms = models.TextField(default="")
    risk_factors = models.TextField(default="")
    hiv_status = models.CharField(max_length=50, default="Unknown")
    
    # Clinical Risk Parameters (HRG Checklist)
    weight_kg = models.FloatField(default=0.0)
    height_cm = models.FloatField(default=0.0)
    bmi = models.FloatField(default=0.0)
    
    past_tb = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    smoker = models.BooleanField(default=False)
    close_contact = models.BooleanField(default=False)
    
    # TPT questions fields
    tpt_undergone = models.CharField(max_length=20, default="No")
    tpt_status = models.CharField(max_length=50, blank=True, null=True)
    tpt_contact_known = models.CharField(max_length=20, blank=True, null=True)
    tpt_history = models.CharField(max_length=100, blank=True, null=True)
    tpt_start_date = models.DateField(blank=True, null=True)
    tpt_end_date = models.DateField(blank=True, null=True)
    tpt_duration_months = models.IntegerField(blank=True, null=True)
    tpt_regimen = models.CharField(max_length=250, blank=True, null=True)
    tpt_risk_factor = models.CharField(max_length=250, blank=True, null=True)

    # BCG Vaccine Evidence Grade
    bcg_evidence = models.CharField(max_length=100, default="No evidence")
    
    # Eligibility Gates Results
    eligible = models.BooleanField(default=True)
    eligible_bcg_campaign = models.BooleanField(default=False, verbose_name="Eligible for BCG vaccine during campaign period")
    bcg_eligibility_criteria = models.TextField(blank=True, null=True, verbose_name="Eligibility Criteria for Adult BCG Vaccination")
    match_hrg = models.CharField(max_length=500, blank=True, null=True) # Assigned primary HRG group
    
    # BCG Vaccine Verification Step 7 Details
    bcg_status = models.CharField(max_length=50, default="No") # "No", "Yes (Verified via Registry)", "Yes (Manually Verified)"
    bcg_beneficiary_id = models.CharField(max_length=100, blank=True, null=True)
    bcg_ben_mobile_number = models.CharField(max_length=50, blank=True, null=True)
    bcg_ben_gender = models.CharField(max_length=50, blank=True, null=True)
    bcg_date = models.CharField(max_length=50, blank=True, null=True)
    bcg_registration_mode = models.CharField(max_length=100, blank=True, null=True)
    bcg_dob = models.CharField(max_length=50, blank=True, null=True)
    bcg_age = models.IntegerField(blank=True, null=True)
    bcg_vaccination_status = models.CharField(max_length=50, blank=True, null=True)
    bcg_first_name = models.CharField(max_length=150, blank=True, null=True)
    bcg_last_name = models.CharField(max_length=150, blank=True, null=True)
    bcg_site_id = models.CharField(max_length=50, blank=True, null=True)
    bcg_approved_by = models.CharField(max_length=50, blank=True, null=True)
    bcg_beneficiary_type_name = models.CharField(max_length=250, blank=True, null=True)
    bcg_pincode = models.CharField(max_length=20, blank=True, null=True)
    bcg_address = models.TextField(blank=True, null=True)
    bcg_facility_id = models.CharField(max_length=50, blank=True, null=True)
    bcg_scar = models.CharField(max_length=20, blank=True, null=True)
    bcg_scar_file = models.FileField(upload_to="bcg_scar_records/", blank=True, null=True)
    bcg_has_record = models.CharField(max_length=20, blank=True, null=True)
    bcg_record_file = models.FileField(upload_to="bcg_records/", blank=True, null=True)
    cxr_record_file = models.FileField(upload_to="cxr_records/", blank=True, null=True)
    
    # Legacy fields for backward compatibility
    bcg_vaccination_date = models.DateField(blank=True, null=True)
    bcg_vaccine_name = models.CharField(max_length=100, default="BCG")
    bcg_batch_number = models.CharField(max_length=100, blank=True, null=True)
    bcg_facility = models.CharField(max_length=250, blank=True, null=True)

    # Classification
    classification = models.CharField(max_length=25, default="TPT+BCG")
    classification_reason = models.TextField(blank=True, default="")
    
    # Sync metadata
    synced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_tpt_individuals")

    def __str__(self):
        return f"[TPT] {self.full_name} ({self.study_id})"


class IneligibleIndividual(models.Model):
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    dob = models.DateField(null=True, blank=True)
    secondary_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    full_name = models.CharField(max_length=250)
    study_id = models.CharField(max_length=50, unique=True)
    screening_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    nikshay_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    reconciliation_status = models.CharField(max_length=50, default="UNRECONCILED", db_index=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    date_enroll = models.DateField()
    
    # Geography & Campaign wash-out details
    state = models.CharField(max_length=100, default="Tamil Nadu")
    district = models.CharField(max_length=100, default="Tiruvallur")
    tb_unit = models.CharField(max_length=100, default="Tiruvallur TU")
    facility = models.CharField(max_length=100, default="Local Clinic")
    village = models.CharField(max_length=150, default="")
    pincode = models.CharField(max_length=20, default="")
    demographic_area = models.CharField(max_length=100, default="Unknown")
    campaign_completion_date = models.DateField(null=True, blank=True)

    # New Sector & additional details fields
    sector = models.CharField(max_length=50, default="Public Sector")
    case_finding_type = models.CharField(max_length=100, blank=True, null=True)
    private_facility = models.CharField(max_length=150, blank=True, null=True)
    public_phi = models.CharField(max_length=150, blank=True, null=True)
    father_husband_name = models.CharField(max_length=150, blank=True, null=True)
    secondary_phone_1 = models.CharField(max_length=15, blank=True, null=True)
    secondary_phone_2 = models.CharField(max_length=15, blank=True, null=True)
    secondary_phone_3 = models.CharField(max_length=15, blank=True, null=True)
    taluka_block = models.CharField(max_length=150, blank=True, null=True)
    landmark = models.CharField(max_length=250, blank=True, null=True)
    
    # Contact Person Details
    contact_person_name = models.CharField(max_length=150, blank=True, null=True)
    contact_person_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_person_address = models.TextField(blank=True, null=True)
    
    # Informant Details
    informant_name = models.CharField(max_length=150, blank=True, null=True)
    informant_designation = models.CharField(max_length=150, blank=True, null=True)

    # PTB Screening & Testing fields
    ptb_screened = models.BooleanField(default=False)
    ptb_test_registered = models.BooleanField(default=False)
    ptb_test_type = models.CharField(max_length=100, blank=True, null=True)
    ptb_test_result = models.CharField(max_length=100, blank=True, null=True)
    ptb_test_date = models.DateField(blank=True, null=True)
    ptb_test_facility = models.CharField(max_length=150, blank=True, null=True)
    ptb_test_details = models.TextField(default="{}")
    
    # EPTB Screening fields
    eptb_screened = models.BooleanField(default=False)
    eptb_details = models.TextField(default="{}")
    
    # New Socio-Demographics
    marital_status = models.CharField(max_length=50, default="Unknown")
    occupation = models.CharField(max_length=150, default="Unknown")
    socioeconomic_status = models.CharField(max_length=50, default="Unknown")
    questionnaire_answers = models.TextField(default="{}")
    
    # Symptoms & Clinical Risk Profiles
    symptoms = models.TextField(default="")
    risk_factors = models.TextField(default="")
    hiv_status = models.CharField(max_length=50, default="Unknown")
    
    # Clinical Risk Parameters (HRG Checklist)
    weight_kg = models.FloatField(default=0.0)
    height_cm = models.FloatField(default=0.0)
    bmi = models.FloatField(default=0.0)
    
    past_tb = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    smoker = models.BooleanField(default=False)
    close_contact = models.BooleanField(default=False)
    
    # TPT questions fields
    tpt_undergone = models.CharField(max_length=20, default="No")
    tpt_status = models.CharField(max_length=50, blank=True, null=True)
    tpt_contact_known = models.CharField(max_length=20, blank=True, null=True)
    tpt_history = models.CharField(max_length=100, blank=True, null=True)
    tpt_start_date = models.DateField(blank=True, null=True)
    tpt_end_date = models.DateField(blank=True, null=True)
    tpt_duration_months = models.IntegerField(blank=True, null=True)
    tpt_regimen = models.CharField(max_length=250, blank=True, null=True)
    tpt_risk_factor = models.CharField(max_length=250, blank=True, null=True)

    # BCG Vaccine Evidence Grade
    bcg_evidence = models.CharField(max_length=100, default="No evidence")
    
    # Eligibility Gates Results
    eligible = models.BooleanField(default=False)
    eligible_bcg_campaign = models.BooleanField(default=False, verbose_name="Eligible for BCG vaccine during campaign period")
    bcg_eligibility_criteria = models.TextField(blank=True, null=True, verbose_name="Eligibility Criteria for Adult BCG Vaccination")
    match_hrg = models.CharField(max_length=500, blank=True, null=True) # Assigned primary HRG group
    
    # BCG Vaccine Verification Step 7 Details
    bcg_status = models.CharField(max_length=50, default="No") # "No", "Yes (Verified via Registry)", "Yes (Manually Verified)"
    bcg_beneficiary_id = models.CharField(max_length=100, blank=True, null=True)
    bcg_ben_mobile_number = models.CharField(max_length=50, blank=True, null=True)
    bcg_ben_gender = models.CharField(max_length=50, blank=True, null=True)
    bcg_date = models.CharField(max_length=50, blank=True, null=True)
    bcg_registration_mode = models.CharField(max_length=100, blank=True, null=True)
    bcg_dob = models.CharField(max_length=50, blank=True, null=True)
    bcg_age = models.IntegerField(blank=True, null=True)
    bcg_vaccination_status = models.CharField(max_length=50, blank=True, null=True)
    bcg_first_name = models.CharField(max_length=150, blank=True, null=True)
    bcg_last_name = models.CharField(max_length=150, blank=True, null=True)
    bcg_site_id = models.CharField(max_length=50, blank=True, null=True)
    bcg_approved_by = models.CharField(max_length=50, blank=True, null=True)
    bcg_beneficiary_type_name = models.CharField(max_length=250, blank=True, null=True)
    bcg_pincode = models.CharField(max_length=20, blank=True, null=True)
    bcg_address = models.TextField(blank=True, null=True)
    bcg_facility_id = models.CharField(max_length=50, blank=True, null=True)
    bcg_scar = models.CharField(max_length=20, blank=True, null=True)
    bcg_scar_file = models.FileField(upload_to="bcg_scar_records/", blank=True, null=True)
    bcg_has_record = models.CharField(max_length=20, blank=True, null=True)
    bcg_record_file = models.FileField(upload_to="bcg_records/", blank=True, null=True)
    cxr_record_file = models.FileField(upload_to="cxr_records/", blank=True, null=True)
    
    # Legacy fields for backward compatibility
    bcg_vaccination_date = models.DateField(blank=True, null=True)
    bcg_vaccine_name = models.CharField(max_length=100, default="BCG")
    bcg_batch_number = models.CharField(max_length=100, blank=True, null=True)
    bcg_facility = models.CharField(max_length=250, blank=True, null=True)

    # Classification
    classification = models.CharField(max_length=25, default="Not Eligible")
    classification_reason = models.TextField(blank=True, default="")
    
    # Sync metadata
    synced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_ineligible_individuals")

    def __str__(self):
        return f"[INELIGIBLE] {self.full_name} ({self.study_id})"


class DeviceSyncLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sync_logs")
    timestamp = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    battery_level = models.IntegerField(null=True, blank=True)
    battery_charging = models.BooleanField(default=False)
    pending_count = models.IntegerField(default=0)
    synced_count = models.IntegerField(default=0)
    device_user_agent = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Sync by {self.user.username} at {self.timestamp}"


class NikshayRecord(models.Model):
    """
    Dedicated table storing all Nikshay IDs and participant linkage.
    Ensures Nikshay ID is preserved permanently across all user logins,
    cohort reclassifications, and jurisdictional boundaries.
    """
    COHORT_CHOICES = [
        ("Participant", "Participant"),
        ("TPT", "TPT Individual"),
        ("Ineligible", "Ineligible Individual"),
    ]

    nikshay_id = models.CharField(max_length=100, db_index=True)
    study_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    screening_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)

    # Optional references to cohort models (set null on delete to preserve historical Nikshay mapping)
    participant = models.ForeignKey("Participant", on_delete=models.SET_NULL, null=True, blank=True, related_name="nikshay_records")
    tpt_individual = models.ForeignKey("TptIndividual", on_delete=models.SET_NULL, null=True, blank=True, related_name="nikshay_records")
    ineligible_individual = models.ForeignKey("IneligibleIndividual", on_delete=models.SET_NULL, null=True, blank=True, related_name="nikshay_records")
    cohort = models.CharField(max_length=50, choices=COHORT_CHOICES, default="Participant")

    # Demographic snapshot for persistence across logins and cohort movements
    full_name = models.CharField(max_length=250, blank=True, default="")
    contact_number = models.CharField(max_length=20, blank=True, default="")
    gender = models.CharField(max_length=20, blank=True, default="")
    age = models.IntegerField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)

    # Geographic jurisdiction
    state = models.CharField(max_length=100, blank=True, default="")
    district = models.CharField(max_length=100, blank=True, default="")
    tb_unit = models.CharField(max_length=100, blank=True, default="")

    # Audit & tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_nikshay_records")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=50, default="Personal Details Form")

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Nikshay Record"
        verbose_name_plural = "Nikshay Records"

    def __str__(self):
        return f"{self.nikshay_id} - {self.full_name} ({self.study_id or self.screening_id or 'No Study ID'})"


def sync_nikshay_record(obj, nikshay_id, user=None):
    """
    Saves or updates Nikshay ID and participant metadata in the dedicated NikshayRecord table,
    ensuring that the Nikshay ID is preserved across all logins, cohort movements, and updates.
    """
    if not nikshay_id:
        return None

    study_id = getattr(obj, "study_id", "")
    screening_id = getattr(obj, "screening_id", "")

    rec = None
    if study_id:
        rec = NikshayRecord.objects.filter(study_id=study_id).first()
    if not rec and screening_id:
        rec = NikshayRecord.objects.filter(screening_id=screening_id).first()
    if not rec and nikshay_id and study_id:
        rec = NikshayRecord.objects.filter(nikshay_id=nikshay_id, study_id=study_id).first()
    if not rec:
        rec = NikshayRecord(study_id=study_id, screening_id=screening_id)

    rec.nikshay_id = str(nikshay_id).strip()
    rec.study_id = study_id
    rec.screening_id = screening_id
    rec.full_name = (getattr(obj, "full_name", "") or f"{getattr(obj, 'first_name', '')} {getattr(obj, 'last_name', '')}".strip()) or ""
    rec.contact_number = getattr(obj, "contact_number", "") or ""
    rec.gender = getattr(obj, "gender", "") or ""
    rec.age = getattr(obj, "age", None)
    rec.dob = getattr(obj, "dob", None)
    rec.state = getattr(obj, "state", "") or ""
    rec.district = getattr(obj, "district", "") or ""
    rec.tb_unit = getattr(obj, "tb_unit", "") or ""

    if user and not rec.created_by:
        rec.created_by = user
    elif getattr(obj, "created_by", None) and not rec.created_by:
        rec.created_by = obj.created_by

    if isinstance(obj, Participant):
        rec.participant = obj
        rec.tpt_individual = None
        rec.ineligible_individual = None
        rec.cohort = "Participant"
    elif isinstance(obj, TptIndividual):
        rec.tpt_individual = obj
        rec.participant = None
        rec.ineligible_individual = None
        rec.cohort = "TPT"
    elif isinstance(obj, IneligibleIndividual):
        rec.ineligible_individual = obj
        rec.participant = None
        rec.tpt_individual = None
        rec.cohort = "Ineligible"

    rec.save()
    return rec


@receiver(post_save, sender=Participant)
def auto_sync_participant_nikshay(sender, instance, **kwargs):
    if instance.nikshay_id:
        sync_nikshay_record(instance, instance.nikshay_id, getattr(instance, "created_by", None))


@receiver(post_save, sender=TptIndividual)
def auto_sync_tpt_nikshay(sender, instance, **kwargs):
    if instance.nikshay_id:
        sync_nikshay_record(instance, instance.nikshay_id, getattr(instance, "created_by", None))


@receiver(post_save, sender=IneligibleIndividual)
def auto_sync_ineligible_nikshay(sender, instance, **kwargs):
    if instance.nikshay_id:
        sync_nikshay_record(instance, instance.nikshay_id, getattr(instance, "created_by", None))




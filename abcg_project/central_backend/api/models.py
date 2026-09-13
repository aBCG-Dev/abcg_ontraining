from django.db import models
from django.contrib.auth.models import User

class GlobalSettings(models.Model):
    """
    Holds configurations that stakeholders might request changes to.
    Updating these changes values globally in the Rules Engine without code deployments!
    """
    name = models.CharField(max_length=100, default="Study Settings")
    bmi_threshold = models.FloatField(default=18.0, help_text="Malnutrition BMI threshold (participants below this are eligible)")
    age_threshold = models.IntegerField(default=60, help_text="Elderly age threshold (participants at or above this are eligible)")
    campaign_period = models.CharField(max_length=250, default="Jan 2025 - Mar 2025", help_text="Campaign period description")

    class Meta:
        verbose_name = "Global Setting"
        verbose_name_plural = "Global Settings"

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Investigator metadata linked to their geographic jurisdiction.
    """
    ROLE_CHOICES = [
        ("Super Admin", "Super Admin"),
        ("Admin", "Admin"),
        ("Nodal Officer", "Nodal Officer"),
        ("Doctor", "Doctor"),
        ("Field Investigator", "Field Investigator"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="central_profile")
    full_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="Field Investigator")
    state = models.CharField(max_length=100, default="Tamil Nadu")
    district = models.CharField(max_length=100, default="Tiruvallur")
    tb_unit = models.CharField(max_length=100, default="Tiruvallur TU")

    def __str__(self):
        return f"{self.user.username} Profile ({self.role})"


class AuditLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="central_audit_actions")
    action = models.CharField(max_length=255)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="central_audit_targets")
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.actor} - {self.action} on {self.target_user} at {self.timestamp}"


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_central_profile(sender, instance, created, **kwargs):
    if created:
        try:
            UserProfile.objects.create(user=instance, full_name=instance.get_full_name() or instance.username)
        except Exception:
            pass

@receiver(post_save, sender=User)
def save_central_profile(sender, instance, **kwargs):
    try:
        if not hasattr(instance, "central_profile"):
            UserProfile.objects.create(user=instance, full_name=instance.get_full_name() or instance.username)
        else:
            instance.central_profile.save()
    except Exception:
        pass


class Participant(models.Model):
    """
    Aggegated record containing clinical screening, demographics, and outcomes.
    """
    study_id = models.CharField(max_length=50, unique=True, db_index=True)
    nikshay_id = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    full_name = models.CharField(max_length=250)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    date_enroll = models.DateField()
    
    # Geography
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    tb_unit = models.CharField(max_length=100)
    facility = models.CharField(max_length=150, blank=True, default="Local Clinic")
    village = models.CharField(max_length=150, blank=True, default="")
    pincode = models.CharField(max_length=20, blank=True, default="")
    demographic_area = models.CharField(max_length=100, default="Unknown")
    
    # Additional geography & campaign details
    secondary_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    campaign_completion_date = models.DateField(null=True, blank=True)
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

    # Contact Person & Informant Details
    contact_person_name = models.CharField(max_length=150, blank=True, null=True)
    contact_person_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_person_address = models.TextField(blank=True, null=True)
    informant_name = models.CharField(max_length=150, blank=True, null=True)
    informant_designation = models.CharField(max_length=150, blank=True, null=True)

    # Screening checks
    ptb_screened = models.BooleanField(default=False)
    ptb_test_registered = models.BooleanField(default=False)
    ptb_test_type = models.CharField(max_length=100, blank=True, null=True)
    ptb_test_result = models.CharField(max_length=100, blank=True, null=True)
    ptb_test_date = models.DateField(blank=True, null=True)
    ptb_test_facility = models.CharField(max_length=150, blank=True, null=True)
    ptb_test_details = models.TextField(default="{}")
    eptb_screened = models.BooleanField(default=False)
    marital_status = models.CharField(max_length=50, default="Unknown")
    occupation = models.CharField(max_length=150, default="Unknown")
    socioeconomic_status = models.CharField(max_length=50, default="Unknown")
    
    # Clinical metrics
    height_cm = models.FloatField(default=0.0)
    weight_kg = models.FloatField(default=0.0)
    bmi = models.FloatField(default=0.0)
    
    # Comorbidities & Risks
    symptoms = models.TextField(default="")
    risk_factors = models.TextField(default="")
    hiv_status = models.CharField(max_length=50, default="Unknown")
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
    
    # Verification details
    bcg_evidence = models.CharField(max_length=100, default="No evidence")
    bcg_status = models.CharField(max_length=50, default="No")
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
    bcg_has_record = models.CharField(max_length=20, blank=True, null=True)
    
    # File attachments saved on 2 TB disk
    bcg_scar_file = models.FileField(upload_to="bcg_scar_records/", blank=True, null=True)
    bcg_record_file = models.FileField(upload_to="bcg_records/", blank=True, null=True)
    cxr_record_file = models.FileField(upload_to="cxr_records/", blank=True, null=True)
    
    # Legacy fields
    bcg_vaccination_date = models.DateField(blank=True, null=True)
    bcg_vaccine_name = models.CharField(max_length=100, default="BCG")
    bcg_batch_number = models.CharField(max_length=100, blank=True, null=True)
    bcg_facility = models.CharField(max_length=250, blank=True, null=True)
    
    # Questionnaire JSON representation
    questionnaire_answers = models.TextField(default="{}")
    eptb_details = models.TextField(default="{}")
    ptb_test_details = models.TextField(default="{}")
    
    # Eligibility checks outcomes
    eligible = models.BooleanField(default=True)
    eligible_bcg_campaign = models.BooleanField(default=False)
    bcg_eligibility_criteria = models.TextField(blank=True, null=True)
    match_hrg = models.CharField(max_length=500, blank=True, null=True)
    classification = models.CharField(max_length=25, default="Pending")
    classification_reason = models.TextField(blank=True, default="")
    
    # Telemetry & Sync Receipt
    sync_receipt_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    sync_verified_at = models.DateTimeField(null=True, blank=True)
    media_checksums = models.TextField(blank=True, default="{}")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    client_app_version = models.CharField(max_length=50, default="1.0.0")

    def __str__(self):
        return f"{self.full_name} ({self.study_id}) - {self.classification}"


class TptIndividual(models.Model):
    """
    Exploratory cohort of TPT + BCG participants.
    """
    study_id = models.CharField(max_length=50, unique=True, db_index=True)
    nikshay_id = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    full_name = models.CharField(max_length=250)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    date_enroll = models.DateField()
    
    # Geography & details
    state = models.CharField(max_length=100, default="Tamil Nadu")
    district = models.CharField(max_length=100, default="Tiruvallur")
    tb_unit = models.CharField(max_length=100, default="Tiruvallur TU")
    facility = models.CharField(max_length=100, blank=True, default="Local Clinic")
    village = models.CharField(max_length=150, default="")
    pincode = models.CharField(max_length=20, default="")
    demographic_area = models.CharField(max_length=100, default="Unknown")
    campaign_completion_date = models.DateField(null=True, blank=True)
    
    secondary_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
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
    
    # TPT questions
    tpt_undergone = models.CharField(max_length=20, default="Yes")
    tpt_status = models.CharField(max_length=50, blank=True, null=True)
    tpt_contact_known = models.CharField(max_length=20, blank=True, null=True)
    tpt_history = models.CharField(max_length=100, blank=True, null=True)
    tpt_start_date = models.DateField(blank=True, null=True)
    tpt_end_date = models.DateField(blank=True, null=True)
    tpt_duration_months = models.IntegerField(blank=True, null=True)
    tpt_regimen = models.CharField(max_length=250, blank=True, null=True)
    tpt_risk_factor = models.CharField(max_length=250, blank=True, null=True)
    # Media & Verification Attachments
    bcg_scar = models.CharField(max_length=20, blank=True, null=True)
    bcg_has_record = models.CharField(max_length=20, blank=True, null=True)
    bcg_scar_file = models.FileField(upload_to="bcg_scar_records/", blank=True, null=True)
    bcg_record_file = models.FileField(upload_to="bcg_records/", blank=True, null=True)
    cxr_record_file = models.FileField(upload_to="cxr_records/", blank=True, null=True)
    sync_receipt_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    sync_verified_at = models.DateTimeField(null=True, blank=True)
    media_checksums = models.TextField(blank=True, default="{}")
    
    classification = models.CharField(max_length=25, default="TPT+BCG")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.study_id}) - TPT"


class IneligibleIndividual(models.Model):
    """
    Participants who screened out of eligibility gates.
    """
    study_id = models.CharField(max_length=50, unique=True, db_index=True)
    nikshay_id = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    full_name = models.CharField(max_length=250)
    age = models.IntegerField()
    gender = models.CharField(max_length=20, default="Unknown")
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    date_enroll = models.DateField()
    
    # Geography & details
    state = models.CharField(max_length=100, default="Tamil Nadu")
    district = models.CharField(max_length=100, default="Tiruvallur")
    tb_unit = models.CharField(max_length=100, default="Tiruvallur TU")
    facility = models.CharField(max_length=100, blank=True, default="Local Clinic")
    village = models.CharField(max_length=150, default="")
    pincode = models.CharField(max_length=20, default="")
    demographic_area = models.CharField(max_length=100, default="Unknown")
    campaign_completion_date = models.DateField(null=True, blank=True)
    
    secondary_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
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
    
    # Media & Verification Attachments
    bcg_scar = models.CharField(max_length=20, blank=True, null=True)
    bcg_has_record = models.CharField(max_length=20, blank=True, null=True)
    bcg_scar_file = models.FileField(upload_to="bcg_scar_records/", blank=True, null=True)
    bcg_record_file = models.FileField(upload_to="bcg_records/", blank=True, null=True)
    cxr_record_file = models.FileField(upload_to="cxr_records/", blank=True, null=True)
    sync_receipt_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    sync_verified_at = models.DateTimeField(null=True, blank=True)
    media_checksums = models.TextField(blank=True, default="{}")

    classification = models.CharField(max_length=25, default="Not Eligible")
    classification_reason = models.TextField(blank=True, default="")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.study_id}) - Ineligible"


class DeviceSyncLog(models.Model):
    """
    Silent telemetry sync auditing.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    battery_level = models.IntegerField(null=True, blank=True)
    battery_charging = models.BooleanField(default=False)
    pending_count = models.IntegerField(default=0)
    synced_count = models.IntegerField(default=0)
    device_user_agent = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sync event by {self.user.username if self.user else 'Unknown'} at {self.timestamp}"


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


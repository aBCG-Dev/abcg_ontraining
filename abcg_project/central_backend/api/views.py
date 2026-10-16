import uuid
import hashlib
import json
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from .models import Participant, TptIndividual, IneligibleIndividual, DeviceSyncLog, Question
from .serializers import BulkSyncPayloadSerializer, QuestionSerializer
from .eligibility import RulesEngine
from .permissions import HasRolePermission

def compute_file_sha256(file_obj):
    """Computes SHA-256 hash of an uploaded file."""
    hasher = hashlib.sha256()
    for chunk in file_obj.chunks():
        hasher.update(chunk)
    file_obj.seek(0)
    return hasher.hexdigest()

class CentralObtainAuthToken(ObtainAuthToken):
    """
    Endpoint for field investigators to login and retrieve token.
    """
    permission_classes = [AllowAny]


class BulkSyncView(APIView):
    """
    Idempotent bulk synchronization ingestion API.
    Processes batches of participant records and silent device telemetry,
    generating verifiable receipt tokens for field staff.
    """
    permission_classes = [HasRolePermission]
    allowed_roles = ['Super Admin', 'Admin', 'Field Investigator']
    
    def post(self, request):
        serializer = BulkSyncPayloadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        validated_data = serializer.validated_data
        synced_participants = []
        synced_tpt = []
        synced_ineligible = []
        receipts = {}
        now = timezone.now()
        
        # 1. Ingest Participants
        for p_data in validated_data.get("participants", []):
            study_id = p_data.get("study_id")
            receipt_id = f"REC-P-{uuid.uuid4().hex[:10].upper()}"
            
            # Server-side validation of eligibility metrics (fail-safe audit)
            eligible, match_hrg, reason = RulesEngine.evaluate_eligibility(p_data)
            classification, classification_reason = RulesEngine.evaluate_classification(p_data)
            
            # Print audit warning if client-side classification differs from server-side re-evaluation
            client_class = p_data.get("classification")
            client_reason = p_data.get("classification_reason")
            if client_class != classification:
                print(f"[AUDIT WARNING] Classification mismatch for study_id={study_id}: Client={client_class}, Server={classification}")
            
            # If record was clinically confirmed on the field (Case, Control, Excluded, TPT+BCG), do not degrade to Pending
            final_class = classification
            final_reason = classification_reason
            if client_class in ["Case", "Control", "Excluded", "TPT+BCG"] and classification == "Pending":
                final_class = client_class
                final_reason = client_reason or classification_reason

            # Check if study_id exists or if participant is a duplicate entry
            from .deduplication import ParticipantDeduplicator
            dedup_p = ParticipantDeduplicator(model_class=Participant)
            target_study_id = study_id
            
            existing_match = Participant.objects.filter(study_id=study_id).first()
            if not existing_match:
                is_dup, match_rec, tier, reason = dedup_p.check_candidate_duplicate(
                    first_name=p_data.get("first_name", ""),
                    last_name=p_data.get("last_name", ""),
                    full_name=p_data.get("full_name", ""),
                    contact_number=p_data.get("contact_number", ""),
                    nikshay_id=p_data.get("nikshay_id", ""),
                    dob=p_data.get("dob"),
                    age=p_data.get("age"),
                    gender=p_data.get("gender", "")
                )
                if is_dup and match_rec:
                    existing_match = match_rec
                    target_study_id = match_rec.study_id

            participant_obj, created = Participant.objects.update_or_create(
                study_id=target_study_id,
                defaults={
                    **p_data,
                    "study_id": target_study_id,
                    "eligible": eligible,
                    "match_hrg": match_hrg,
                    "classification": final_class,
                    "classification_reason": final_reason,
                    "sync_receipt_id": receipt_id,
                    "sync_verified_at": now,
                    "uploaded_by": request.user
                }
            )
            synced_participants.append(target_study_id)
            receipts[study_id] = {
                "receipt_id": receipt_id,
                "verified_at": now.isoformat(),
                "cohort": "Participant",
                "study_id": target_study_id
            }
            
        # 2. Ingest TPT Individuals
        dedup_t = ParticipantDeduplicator(model_class=TptIndividual)
        for t_data in validated_data.get("tpt_individuals", []):
            study_id = t_data.get("study_id")
            receipt_id = f"REC-T-{uuid.uuid4().hex[:10].upper()}"
            target_study_id = study_id
            
            existing_match = TptIndividual.objects.filter(study_id=study_id).first()
            if not existing_match:
                is_dup, match_rec, tier, reason = dedup_t.check_candidate_duplicate(
                    first_name=t_data.get("first_name", ""),
                    last_name=t_data.get("last_name", ""),
                    full_name=t_data.get("full_name", ""),
                    contact_number=t_data.get("contact_number", ""),
                    nikshay_id=t_data.get("nikshay_id", ""),
                    dob=t_data.get("dob"),
                    age=t_data.get("age"),
                    gender=t_data.get("gender", "")
                )
                if is_dup and match_rec:
                    target_study_id = match_rec.study_id

            tpt_obj, created = TptIndividual.objects.update_or_create(
                study_id=target_study_id,
                defaults={
                    **t_data,
                    "study_id": target_study_id,
                    "sync_receipt_id": receipt_id,
                    "sync_verified_at": now,
                    "uploaded_by": request.user
                }
            )
            synced_tpt.append(target_study_id)
            receipts[study_id] = {
                "receipt_id": receipt_id,
                "verified_at": now.isoformat(),
                "cohort": "TPT",
                "study_id": target_study_id
            }
            
        # 3. Ingest Ineligible Individuals
        dedup_i = ParticipantDeduplicator(model_class=IneligibleIndividual)
        for i_data in validated_data.get("ineligible_individuals", []):
            study_id = i_data.get("study_id")
            receipt_id = f"REC-I-{uuid.uuid4().hex[:10].upper()}"
            target_study_id = study_id
            
            existing_match = IneligibleIndividual.objects.filter(study_id=study_id).first()
            if not existing_match:
                is_dup, match_rec, tier, reason = dedup_i.check_candidate_duplicate(
                    first_name=i_data.get("first_name", ""),
                    last_name=i_data.get("last_name", ""),
                    full_name=i_data.get("full_name", ""),
                    contact_number=i_data.get("contact_number", ""),
                    nikshay_id=i_data.get("nikshay_id", ""),
                    dob=i_data.get("dob"),
                    age=i_data.get("age"),
                    gender=i_data.get("gender", "")
                )
                if is_dup and match_rec:
                    target_study_id = match_rec.study_id

            ineligible_obj, created = IneligibleIndividual.objects.update_or_create(
                study_id=target_study_id,
                defaults={
                    **i_data,
                    "study_id": target_study_id,
                    "sync_receipt_id": receipt_id,
                    "sync_verified_at": now,
                    "uploaded_by": request.user
                }
            )
            synced_ineligible.append(target_study_id)
            receipts[study_id] = {
                "receipt_id": receipt_id,
                "verified_at": now.isoformat(),
                "cohort": "Ineligible",
                "study_id": target_study_id
            }
            
        # 4. Ingest Telemetry Log
        telemetry_data = validated_data.get("telemetry")
        if telemetry_data:
            DeviceSyncLog.objects.create(
                user=request.user,
                latitude=telemetry_data.get("latitude"),
                longitude=telemetry_data.get("longitude"),
                battery_level=telemetry_data.get("battery_level"),
                battery_charging=telemetry_data.get("battery_charging"),
                synced_count=len(synced_participants) + len(synced_tpt) + len(synced_ineligible),
                device_user_agent=telemetry_data.get("device_user_agent")
            )
            
        return Response({
            "status": "success",
            "participants": synced_participants,
            "tpt_individuals": synced_tpt,
            "ineligible_individuals": synced_ineligible,
            "receipts": receipts,
            "synced_at": now.isoformat()
        }, status=status.HTTP_200_OK)


class MediaUploadView(APIView):
    """
    Ingest file uploads (BCG scar photo, vaccination record card, Chest X-Rays)
    across all cohorts (Participant, TptIndividual, IneligibleIndividual).
    Computes SHA-256 checksums, verifies file sizes, and returns a verified delivery receipt.
    """
    permission_classes = [HasRolePermission]
    allowed_roles = ['Super Admin', 'Admin', 'Field Investigator']
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        study_id = request.data.get("study_id")
        if not study_id:
            return Response({"error": "study_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Look up across all three cohorts
        target_obj = (
            Participant.objects.filter(study_id=study_id).first() or
            TptIndividual.objects.filter(study_id=study_id).first() or
            IneligibleIndividual.objects.filter(study_id=study_id).first()
        )
        if not target_obj:
            return Response({"error": f"Participant or individual with study_id '{study_id}' does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
        # Extract files
        bcg_scar = request.FILES.get("bcg_scar_file")
        bcg_record = request.FILES.get("bcg_record_file")
        cxr_record = request.FILES.get("cxr_record_file")
        
        if not (bcg_scar or bcg_record or cxr_record):
            return Response({"error": "No files provided in request"}, status=status.HTTP_400_BAD_REQUEST)
            
        checksums = {}
        now = timezone.now()
        receipt_id = f"REC-MED-{uuid.uuid4().hex[:10].upper()}"
        
        if bcg_scar:
            target_obj.bcg_scar_file = bcg_scar
            checksums["bcg_scar_file"] = {
                "sha256": compute_file_sha256(bcg_scar),
                "size_bytes": bcg_scar.size,
                "name": bcg_scar.name,
            }
        if bcg_record:
            target_obj.bcg_record_file = bcg_record
            checksums["bcg_record_file"] = {
                "sha256": compute_file_sha256(bcg_record),
                "size_bytes": bcg_record.size,
                "name": bcg_record.name,
            }
        if cxr_record:
            target_obj.cxr_record_file = cxr_record
            checksums["cxr_record_file"] = {
                "sha256": compute_file_sha256(cxr_record),
                "size_bytes": cxr_record.size,
                "name": cxr_record.name,
            }
            
        # Update existing checksums if any
        existing_checksums = {}
        if target_obj.media_checksums:
            try:
                existing_checksums = json.loads(target_obj.media_checksums)
            except (json.JSONDecodeError, TypeError):
                existing_checksums = {}
        existing_checksums.update(checksums)
        
        target_obj.media_checksums = json.dumps(existing_checksums)
        target_obj.sync_receipt_id = receipt_id
        target_obj.sync_verified_at = now
        target_obj.save()
        
        return Response({
            "status": "success",
            "receipt_id": receipt_id,
            "study_id": study_id,
            "cohort": target_obj.__class__.__name__,
            "files_received": list(checksums.keys()),
            "checksums": checksums,
            "verified_at": now.isoformat(),
            "message": f"Files uploaded and verified successfully for {study_id}"
        }, status=status.HTTP_200_OK)


class QuestionListView(APIView):
    """
    API endpoint to fetch the list of dynamic questions and options.
    Allows clients to pull dynamic survey questionnaire schemas.
    """
    permission_classes = [HasRolePermission]
    allowed_roles = ['Super Admin', 'Admin', 'Nodal Officer', 'Doctor', 'Field Investigator']

    def get(self, request):
        questions = Question.objects.filter(is_active=True).prefetch_related('options')
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

class CentralObtainAuthToken(ObtainAuthToken):
    """
    Endpoint for field investigators to login and retrieve token.
    """
    permission_classes = [AllowAny]


class BulkSyncView(APIView):
    """
    Idempotent bulk synchronization ingestion API.
    Processes batches of participant records and silent device telemetry.
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
        
        # 1. Ingest Participants
        for p_data in validated_data.get("participants", []):
            study_id = p_data.get("study_id")
            
            # Server-side validation of eligibility metrics (fail-safe audit)
            eligible, match_hrg, reason = RulesEngine.evaluate_eligibility(p_data)
            classification, classification_reason = RulesEngine.evaluate_classification(p_data)
            
            # Print audit warning if client-side classification differs from server-side re-evaluation
            client_class = p_data.get("classification")
            if client_class != classification:
                print(f"[AUDIT WARNING] Classification mismatch for study_id={study_id}: Client={client_class}, Server={classification}")
            
            participant_obj, created = Participant.objects.update_or_create(
                study_id=study_id,
                defaults={
                    **p_data,
                    "eligible": eligible,
                    "match_hrg": match_hrg,
                    "classification": classification,
                    "classification_reason": classification_reason,
                    "uploaded_by": request.user
                }
            )
            synced_participants.append(study_id)
            
        # 2. Ingest TPT Individuals
        for t_data in validated_data.get("tpt_individuals", []):
            study_id = t_data.get("study_id")
            tpt_obj, created = TptIndividual.objects.update_or_create(
                study_id=study_id,
                defaults={
                    **t_data,
                    "uploaded_by": request.user
                }
            )
            synced_tpt.append(study_id)
            
        # 3. Ingest Ineligible Individuals
        for i_data in validated_data.get("ineligible_individuals", []):
            study_id = i_data.get("study_id")
            ineligible_obj, created = IneligibleIndividual.objects.update_or_create(
                study_id=study_id,
                defaults={
                    **i_data,
                    "uploaded_by": request.user
                }
            )
            synced_ineligible.append(study_id)
            
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
            "ineligible_individuals": synced_ineligible
        }, status=status.HTTP_200_OK)


class MediaUploadView(APIView):
    """
    Ingest file uploads (Chest X-Rays, BCG cards) and links them to the participant.
    Saves them directly in the server's 2 TB local disk storage pools.
    """
    permission_classes = [HasRolePermission]
    allowed_roles = ['Super Admin', 'Admin', 'Field Investigator']
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        study_id = request.data.get("study_id")
        if not study_id:
            return Response({"error": "study_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            participant = Participant.objects.get(study_id=study_id)
        except Participant.DoesNotExist:
            return Response({"error": f"Participant with study_id {study_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
        # Extract files
        bcg_scar = request.FILES.get("bcg_scar_file")
        bcg_record = request.FILES.get("bcg_record_file")
        cxr_record = request.FILES.get("cxr_record_file")
        
        updated = False
        if bcg_scar:
            participant.bcg_scar_file = bcg_scar
            updated = True
        if bcg_record:
            participant.bcg_record_file = bcg_record
            updated = True
        if cxr_record:
            participant.cxr_record_file = cxr_record
            updated = True
            
        if updated:
            participant.save()
            return Response({"status": "success", "message": f"Files uploaded successfully for {study_id}"}, status=status.HTTP_200_OK)
            
        return Response({"error": "No files provided in request"}, status=status.HTTP_400_BAD_REQUEST)


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


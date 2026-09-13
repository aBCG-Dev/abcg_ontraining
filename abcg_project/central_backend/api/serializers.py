from rest_framework import serializers
from .models import Participant, TptIndividual, IneligibleIndividual, DeviceSyncLog, Question, Option

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        exclude = ('uploaded_by', 'uploaded_at', 'bcg_scar_file', 'bcg_record_file', 'cxr_record_file')


class TptIndividualSerializer(serializers.ModelSerializer):
    class Meta:
        model = TptIndividual
        exclude = ('uploaded_by', 'uploaded_at', 'bcg_scar_file', 'bcg_record_file', 'cxr_record_file')


class IneligibleIndividualSerializer(serializers.ModelSerializer):
    class Meta:
        model = IneligibleIndividual
        exclude = ('uploaded_by', 'uploaded_at', 'bcg_scar_file', 'bcg_record_file', 'cxr_record_file')


class DeviceSyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceSyncLog
        exclude = ('user', 'timestamp')


class BulkSyncPayloadSerializer(serializers.Serializer):
    participants = ParticipantSerializer(many=True, required=False, default=[])
    tpt_individuals = TptIndividualSerializer(many=True, required=False, default=[])
    ineligible_individuals = IneligibleIndividualSerializer(many=True, required=False, default=[])
    telemetry = DeviceSyncLogSerializer(required=False, allow_null=True)


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('code', 'name', 'display_order', 'is_active')


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('code', 'label', 'step', 'field_type', 'display_order', 'is_active', 'options')


# emotion_analysis/serializers.py
from rest_framework import serializers

class EmotionAnalysisRequestSerializer(serializers.Serializer):
    url = serializers.URLField()

class EmotionAnalysisResponseSerializer(serializers.Serializer):
    source_name = serializers.CharField()
    prosody_emotions = serializers.ListField(child=serializers.DictField())
    burst_emotions = serializers.ListField(child=serializers.DictField())

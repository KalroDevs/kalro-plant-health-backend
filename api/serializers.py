from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

# ============================================================================
# Base Serializers
# ============================================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ['id', 'name', 'scientific_name', 'category', 'description', 
                  'image', 'icon', 'growing_season_start', 'growing_season_end',
                  'average_yield_kg_per_ha', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CropListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    class Meta:
        model = Crop
        fields = ['id', 'name', 'category', 'icon']


class ClassificationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificationCategory
        fields = ['id', 'name', 'category_type', 'description', 'icon', 
                  'color_code', 'display_order', 'is_active']
        read_only_fields = ['id']


# ============================================================================
# Pest and Disease Serializers
# ============================================================================

class PestDiseaseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PestDiseaseImage
        fields = ['id', 'image_type', 'image', 'caption', 'order']


class PestDiseaseListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color_code', read_only=True)
    severity_color = serializers.SerializerMethodField()
    
    class Meta:
        model = PestDisease
        fields = ['id', 'name', 'scientific_name', 'category_name', 'category_color',
                  'issue_type', 'severity', 'severity_color', 'damage_type', 
                  'is_emerging', 'main_image']
    
    def get_severity_color(self, obj):
        return obj.get_severity_color()


class PestDiseaseDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single object views"""
    category = ClassificationCategorySerializer(read_only=True)
    affects_crops = CropSerializer(many=True, read_only=True)
    additional_images = PestDiseaseImageSerializer(many=True, read_only=True)
    symptoms_list = serializers.SerializerMethodField()
    control_methods_list = serializers.SerializerMethodField()
    prevention_methods_list = serializers.SerializerMethodField()
    severity_color = serializers.SerializerMethodField()
    
    class Meta:
        model = PestDisease
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_symptoms_list(self, obj):
        return obj.get_symptoms_list()
    
    def get_control_methods_list(self, obj):
        return obj.get_control_methods_list()
    
    def get_prevention_methods_list(self, obj):
        return obj.get_prevention_methods_list()
    
    def get_severity_color(self, obj):
        return obj.get_severity_color()


class PestDiseaseCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating pests and diseases"""
    class Meta:
        model = PestDisease
        fields = '__all__'
    
    def create(self, validated_data):
        return PestDisease.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ============================================================================
# Outbreak Serializers
# ============================================================================

class OutbreakReportSerializer(serializers.ModelSerializer):
    pest_disease_name = serializers.CharField(source='pest_disease.name', read_only=True)
    county_name = serializers.CharField(source='county.name', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.username', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.username', read_only=True)
    
    class Meta:
        model = OutbreakReport
        fields = ['id', 'pest_disease', 'pest_disease_name', 'county', 'county_name',
                  'location', 'report_date', 'severity', 'status', 'affected_area_ha',
                  'estimated_loss', 'reported_by', 'reported_by_name', 'reporter_name',
                  'description', 'verification_notes', 'verified_by', 'verified_by_name',
                  'verified_date', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class OutbreakReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutbreakReport
        fields = ['pest_disease', 'county', 'location', 'severity', 
                  'affected_area_ha', 'estimated_loss', 'description']


# ============================================================================
# County Serializers
# ============================================================================

class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = ['id', 'name', 'code', 'region', 'population', 'area_km2']


# ============================================================================
# Management Practice Serializers
# ============================================================================

class ManagementPracticeSerializer(serializers.ModelSerializer):
    crops = CropSerializer(many=True, read_only=True)
    targets = PestDiseaseListSerializer(many=True, read_only=True)
    
    class Meta:
        model = ManagementPractice
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ManagementPracticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementPractice
        fields = ['id', 'name', 'category', 'description', 'effectiveness_rating', 
                  'is_organic', 'is_recommended']


# ============================================================================
# Early Warning Serializers
# ============================================================================

class EarlyWarningAlertSerializer(serializers.ModelSerializer):
    pest_disease_name = serializers.CharField(source='pest_disease.name', read_only=True)
    affected_counties = CountySerializer(many=True, read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.username', read_only=True)
    is_current = serializers.SerializerMethodField()
    
    class Meta:
        model = EarlyWarningAlert
        fields = ['id', 'title', 'description', 'alert_level', 'pest_disease',
                  'pest_disease_name', 'affected_counties', 'start_date', 'end_date',
                  'issued_at', 'recommended_actions', 'issued_by', 'issued_by_name',
                  'source', 'is_active', 'is_current']
        read_only_fields = ['id', 'issued_at']
    
    def get_is_current(self, obj):
        return obj.is_current()


# ============================================================================
# User Dashboard Serializers
# ============================================================================

class UserDashboardSerializer(serializers.ModelSerializer):
    saved_pests_diseases = PestDiseaseListSerializer(many=True, read_only=True)
    saved_management_practices = ManagementPracticeListSerializer(many=True, read_only=True)
    favorite_crops = CropListSerializer(many=True, read_only=True)
    favorite_counties = CountySerializer(many=True, read_only=True)
    
    class Meta:
        model = UserDashboard
        fields = ['id', 'user', 'saved_pests_diseases', 'saved_management_practices',
                  'favorite_crops', 'favorite_counties', 'receive_alerts',
                  'alert_frequency', 'created_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# Resource Serializers
# ============================================================================

class ResourceSerializer(serializers.ModelSerializer):
    related_pests_diseases = PestDiseaseListSerializer(many=True, read_only=True)
    related_crops = CropListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'resource_type', 'file', 'url',
                  'thumbnail', 'duration', 'language', 'view_count', 'download_count',
                  'is_featured', 'related_pests_diseases', 'related_crops']
        read_only_fields = ['id', 'view_count', 'download_count', 'created_at']


# ============================================================================
# Search and Feedback Serializers
# ============================================================================

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'search_query', 'search_filters', 'results_count', 
                  'clicked_result', 'created_at']
        read_only_fields = ['id', 'created_at']


class FeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    pest_disease_name = serializers.CharField(source='pest_disease.name', read_only=True)
    
    class Meta:
        model = Feedback
        fields = ['id', 'user', 'user_name', 'pest_disease', 'pest_disease_name',
                  'feedback_type', 'comment', 'user_rating', 'page_url', 
                  'created_at', 'is_resolved']
        read_only_fields = ['id', 'created_at']


# ============================================================================
# Statistics Serializer
# ============================================================================

class StatisticsSerializer(serializers.Serializer):
    total_pests = serializers.IntegerField()
    total_diseases = serializers.IntegerField()
    total_crops = serializers.IntegerField()
    active_outbreaks = serializers.IntegerField()
    recent_alerts = serializers.IntegerField()
    total_resources = serializers.IntegerField()
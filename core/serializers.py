from rest_framework import serializers
from .models import *

class PestCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PestCategory
        fields = ['id', 'name', 'slug', 'description', 'icon', 'order', 'is_active']

class EconomicImportanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicImportance
        fields = ['id', 'title', 'content', 'image', 'order']

class IdentificationImportanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentificationImportance
        fields = ['id', 'title', 'content', 'image', 'order']

class IPMPrincipleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPMPrinciple
        fields = ['id', 'title', 'content', 'icon', 'order']

class PesticideUseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PesticideUse
        fields = ['id', 'title', 'content', 'best_practices', 'precautions', 'order']

class NutrientDeficiencySerializer(serializers.ModelSerializer):
    deficiency_type_display = serializers.CharField(source='get_deficiency_type_display', read_only=True)
    
    class Meta:
        model = NutrientDeficiency
        fields = ['id', 'name', 'deficiency_type', 'deficiency_type_display', 'symptoms', 
                  'causes', 'management', 'image']

class EnvironmentalFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalFactor
        fields = ['id', 'name', 'description', 'effects', 'management', 'image']

class PestImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PestImage
        fields = ['id', 'image', 'caption', 'is_primary', 'order']

class DiseaseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiseaseImage
        fields = ['id', 'image', 'caption', 'is_primary', 'order']

class PestSerializer(serializers.ModelSerializer):
    pest_type_display = serializers.CharField(source='get_pest_type_display', read_only=True)
    images = PestImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Pest
        fields = ['id', 'name', 'slug', 'pest_type', 'pest_type_display', 'category', 
                  'category_name', 'scientific_name', 'description', 'about', 'identification',
                  'symptoms', 'management', 'lifecycle', 'host_range', 'image', 'images',
                  'is_active', 'created_at', 'updated_at']

class DiseaseSerializer(serializers.ModelSerializer):
    disease_type_display = serializers.CharField(source='get_disease_type_display', read_only=True)
    images = DiseaseImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Disease
        fields = ['id', 'name', 'slug', 'disease_type', 'disease_type_display', 'category',
                  'category_name', 'scientific_name', 'description', 'about', 'identification',
                  'symptoms', 'management', 'disease_cycle', 'favorable_conditions', 'image',
                  'images', 'is_active', 'created_at', 'updated_at']

class CropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crop
        fields = ['id', 'name', 'slug', 'scientific_name', 'family', 'description',
                  'economic_importance', 'growing_regions', 'image', 'is_active',
                  'created_at', 'updated_at']

class CropPestSerializer(serializers.ModelSerializer):
    pest = PestSerializer(read_only=True)
    pest_id = serializers.PrimaryKeyRelatedField(queryset=Pest.objects.all(), source='pest', write_only=True)
    
    class Meta:
        model = CropPest
        fields = ['id', 'crop', 'pest', 'pest_id', 'description', 'damage_symptoms', 'management_measures']

class CropDiseaseSerializer(serializers.ModelSerializer):
    disease = DiseaseSerializer(read_only=True)
    disease_id = serializers.PrimaryKeyRelatedField(queryset=Disease.objects.all(), source='disease', write_only=True)
    
    class Meta:
        model = CropDisease
        fields = ['id', 'crop', 'disease', 'disease_id', 'description', 'damage_symptoms', 'management_measures']

class CropDetailSerializer(CropSerializer):
    crop_pests = CropPestSerializer(many=True, read_only=True)
    crop_diseases = CropDiseaseSerializer(many=True, read_only=True)
    
    class Meta(CropSerializer.Meta):
        fields = CropSerializer.Meta.fields + ['crop_pests', 'crop_diseases']

class ControlMethodSerializer(serializers.ModelSerializer):
    method_type_display = serializers.CharField(source='get_method_type_display', read_only=True)
    
    class Meta:
        model = ControlMethod
        fields = ['id', 'name', 'method_type', 'method_type_display', 'description',
                  'application', 'advantages', 'disadvantages', 'pests', 'diseases']
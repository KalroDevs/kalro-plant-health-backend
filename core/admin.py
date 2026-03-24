from django.contrib import admin
from django.utils.html import format_html
from .models import *

class BaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(EconomicImportance)
class EconomicImportanceAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']
    search_fields = ['title', 'content']

@admin.register(IdentificationImportance)
class IdentificationImportanceAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']
    search_fields = ['title', 'content']

@admin.register(IPMPrinciple)
class IPMPrincipleAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']
    search_fields = ['title', 'content']

@admin.register(PesticideUse)
class PesticideUseAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    list_editable = ['order']
    search_fields = ['title', 'content']

@admin.register(NutrientDeficiency)
class NutrientDeficiencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'deficiency_type']
    list_filter = ['deficiency_type']
    search_fields = ['name', 'symptoms']

@admin.register(EnvironmentalFactor)
class EnvironmentalFactorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']

@admin.register(PestCategory)
class PestCategoryAdmin(BaseAdmin):
    list_display = ['name', 'order', 'is_active']
    list_editable = ['order']

class PestImageInline(admin.TabularInline):
    model = PestImage
    extra = 1
    fields = ['image', 'caption', 'is_primary', 'order']

class CropPestInline(admin.TabularInline):
    model = CropPest
    extra = 1
    fields = ['crop', 'description', 'damage_symptoms', 'management_measures']

@admin.register(Pest)
class PestAdmin(BaseAdmin):
    list_display = ['name', 'pest_type', 'category', 'is_active']
    list_filter = ['pest_type', 'category', 'is_active']
    inlines = [PestImageInline, CropPestInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'pest_type', 'category', 'scientific_name', 'description', 'is_active')
        }),
        ('Detailed Information', {
            'fields': ('about', 'identification', 'symptoms', 'management')
        }),
        ('Additional Information', {
            'fields': ('lifecycle', 'host_range', 'image')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

class DiseaseImageInline(admin.TabularInline):
    model = DiseaseImage
    extra = 1
    fields = ['image', 'caption', 'is_primary', 'order']

class CropDiseaseInline(admin.TabularInline):
    model = CropDisease
    extra = 1
    fields = ['crop', 'description', 'damage_symptoms', 'management_measures']

@admin.register(Disease)
class DiseaseAdmin(BaseAdmin):
    list_display = ['name', 'disease_type', 'category', 'is_active']
    list_filter = ['disease_type', 'category', 'is_active']
    inlines = [DiseaseImageInline, CropDiseaseInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'disease_type', 'category', 'scientific_name', 'description', 'is_active')
        }),
        ('Detailed Information', {
            'fields': ('about', 'identification', 'symptoms', 'management')
        }),
        ('Additional Information', {
            'fields': ('disease_cycle', 'favorable_conditions', 'image')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Crop)
class CropAdmin(BaseAdmin):
    list_display = ['name', 'family', 'is_active']
    list_filter = ['family', 'is_active']
    search_fields = ['name', 'scientific_name', 'family']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'scientific_name', 'family', 'description', 'is_active')
        }),
        ('Agricultural Information', {
            'fields': ('economic_importance', 'growing_regions')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CropPestInline, CropDiseaseInline]

@admin.register(ControlMethod)
class ControlMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'method_type']
    list_filter = ['method_type']
    search_fields = ['name', 'description']
    filter_horizontal = ['pests', 'diseases']

@admin.register(PestImage)
class PestImageAdmin(admin.ModelAdmin):
    list_display = ['pest', 'thumbnail', 'is_primary', 'order']
    list_filter = ['is_primary', 'pest']
    list_editable = ['is_primary', 'order']
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = 'Preview'

@admin.register(DiseaseImage)
class DiseaseImageAdmin(admin.ModelAdmin):
    list_display = ['disease', 'thumbnail', 'is_primary', 'order']
    list_filter = ['is_primary', 'disease']
    list_editable = ['is_primary', 'order']
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = 'Preview'
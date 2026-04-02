from django.contrib import admin
from django.utils.html import format_html
from .models import *

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'scientific_name']
    list_editable = ['is_active']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'scientific_name', 'category', 'description', 'icon')
        }),
        ('Growing Information', {
            'fields': ('growing_season_start', 'growing_season_end', 'average_yield_kg_per_ha')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Metadata', {
            'fields': ('is_active',)
        }),
    )


@admin.register(ClassificationCategory)
class ClassificationCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'display_order', 'is_active']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['display_order', 'is_active']


@admin.register(PestDisease)
class PestDiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'issue_type', 'severity', 'is_emerging', 'is_active']
    list_filter = ['category', 'issue_type', 'severity', 'is_emerging', 'is_active']
    search_fields = ['name', 'scientific_name', 'local_names']
    filter_horizontal = ['affects_crops']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'scientific_name', 'local_names', 'category', 'issue_type')
        }),
        ('Severity and Damage', {
            'fields': ('severity', 'damage_type', 'description')
        }),
        ('Symptoms and Control', {
            'fields': ('symptoms', 'control_methods', 'prevention_methods')
        }),
        ('Impact and Distribution', {
            'fields': ('economic_impact', 'yield_loss_percentage_min', 'yield_loss_percentage_max', 
                      'distribution_kenya', 'global_distribution', 'seasonal_pattern')
        }),
        ('Biology and Transmission', {
            'fields': ('life_cycle_days', 'is_vector', 'vector_for')
        }),
        ('Media', {
            'fields': ('main_image', 'symptom_image', 'damage_image')
        }),
        ('Relationships', {
            'fields': ('affects_crops',)
        }),
        ('Metadata', {
            'fields': ('is_active', 'is_emerging')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('created_at', 'updated_at')
        return ()


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'region']
    search_fields = ['name', 'code']
    list_filter = ['region']


@admin.register(OutbreakReport)
class OutbreakReportAdmin(admin.ModelAdmin):
    list_display = ['pest_disease', 'county', 'severity', 'status', 'report_date']
    list_filter = ['severity', 'status', 'county', 'report_date']
    search_fields = ['pest_disease__name', 'location', 'reporter_name']
    date_hierarchy = 'report_date'
    
    fieldsets = (
        ('Outbreak Details', {
            'fields': ('pest_disease', 'county', 'location', 'report_date', 'severity', 'status')
        }),
        ('Impact Assessment', {
            'fields': ('affected_area_ha', 'estimated_loss')
        }),
        ('Reporting Information', {
            'fields': ('reported_by', 'reporter_name', 'reporter_contact', 'description')
        }),
        ('Verification', {
            'fields': ('verification_notes', 'verified_by', 'verified_date')
        }),
    )


@admin.register(ManagementPractice)
class ManagementPracticeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_organic', 'is_recommended']
    list_filter = ['category', 'is_organic', 'is_recommended']
    search_fields = ['name', 'description']
    filter_horizontal = ['crops', 'targets']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Application', {
            'fields': ('application_method', 'timing', 'frequency')
        }),
        ('Effectiveness and Costs', {
            'fields': ('effectiveness_rating', 'estimated_cost_kes', 'cost_per_unit')
        }),
        ('Safety', {
            'fields': ('safety_precautions', 'reentry_interval_days')
        }),
        ('Metadata', {
            'fields': ('is_organic', 'is_recommended', 'source')
        }),
        ('Relationships', {
            'fields': ('crops', 'targets')
        }),
    )


@admin.register(EarlyWarningAlert)
class EarlyWarningAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_level', 'start_date', 'end_date', 'is_active']
    list_filter = ['alert_level', 'is_active', 'start_date']
    search_fields = ['title', 'description']
    filter_horizontal = ['affected_counties']
    date_hierarchy = 'issued_at'


@admin.register(UserDashboard)
class UserDashboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'receive_alerts', 'alert_frequency', 'created_at']
    list_filter = ['receive_alerts', 'alert_frequency']
    search_fields = ['user__username', 'user__email']
    filter_horizontal = ['saved_pests_diseases', 'saved_management_practices', 
                        'favorite_crops', 'favorite_counties']


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['search_query', 'user', 'results_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['search_query', 'user__username', 'session_id']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['feedback_type', 'user', 'pest_disease', 'user_rating', 'created_at']
    list_filter = ['feedback_type', 'is_resolved', 'created_at']
    search_fields = ['comment', 'user__username']
    date_hierarchy = 'created_at'


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'language', 'view_count', 'is_featured']
    list_filter = ['resource_type', 'language', 'is_featured', 'is_published']
    search_fields = ['title', 'description']
    filter_horizontal = ['related_pests_diseases', 'related_crops']
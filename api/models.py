from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.urls import reverse

# ============================================================================
# Core Models
# ============================================================================

class Crop(models.Model):
    """Model for agricultural crops"""
    
    CROP_CATEGORIES = [
        ('cereal', 'Cereal'),
        ('legume', 'Legume'),
        ('vegetable', 'Vegetable'),
        ('tuber', 'Tuber/Root Crop'),
        ('fruit', 'Fruit'),
        ('cash-crop', 'Cash Crop'),
        ('oil-crop', 'Oil Crop'),
        ('fiber', 'Fiber Crop'),
    ]
    
    name = models.CharField(max_length=100, unique=True, db_index=True)
    scientific_name = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CROP_CATEGORIES, db_index=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='crops/', blank=True, null=True)
    icon = models.CharField(max_length=10, blank=True, help_text="Emoji icon for display")
    
    # Growing information
    growing_season_start = models.CharField(max_length=50, blank=True)
    growing_season_end = models.CharField(max_length=50, blank=True)
    average_yield_kg_per_ha = models.FloatField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('crop-detail', args=[self.id])


class ClassificationCategory(models.Model):
    """Main classification categories for crop health issues"""
    
    CATEGORY_TYPES = [
        ('invertebrate-pests', 'Invertebrate Pests'),
        ('diseases', 'Plant Diseases'),
        ('vertebrate-pests', 'Vertebrate Pests'),
        ('abiotic', 'Abiotic Causes'),
        ('invasive-alien', 'Invasive Alien Species'),
        ('post-harvest', 'Post-Harvest Damage'),
        ('weeds', 'Weed Competition'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=50, choices=CATEGORY_TYPES, unique=True, db_index=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    color_code = models.CharField(max_length=7, default='#6c757d', help_text="Hex color code")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = "Classification Categories"
    
    def __str__(self):
        return self.name


class PestDisease(models.Model):
    """Main model for pests, diseases, and other crop health issues"""
    
    SEVERITY_LEVELS = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    DAMAGE_TYPES = [
        ('direct', 'Direct Damage'),
        ('indirect', 'Indirect Damage'),
        ('both', 'Both Direct and Indirect'),
    ]
    
    ISSUE_TYPES = [
        ('insect', 'Insect Pest'),
        ('mite', 'Mite'),
        ('nematode', 'Nematode'),
        ('fungal', 'Fungal Disease'),
        ('bacterial', 'Bacterial Disease'),
        ('viral', 'Viral Disease'),
        ('vertebrate', 'Vertebrate Pest'),
        ('abiotic', 'Abiotic Stress'),
        ('weed', 'Weed'),
        ('invasive', 'Invasive Species'),
        ('post-harvest', 'Post-Harvest Issue'),
    ]
    
    # Basic information
    name = models.CharField(max_length=200, unique=True, db_index=True)
    scientific_name = models.CharField(max_length=300, blank=True, null=True)
    local_names = models.CharField(max_length=500, blank=True, help_text="Comma-separated local names")
    
    # Classification
    category = models.ForeignKey(ClassificationCategory, on_delete=models.CASCADE, related_name='issues')
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPES, db_index=True)
    
    # Severity and damage
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, db_index=True)
    damage_type = models.CharField(max_length=20, choices=DAMAGE_TYPES, default='direct')
    
    # Description
    description = models.TextField()
    symptoms = models.TextField(help_text="Detailed symptoms with bullet points")
    
    # Control and prevention
    control_methods = models.TextField(help_text="Control methods (cultural, biological, chemical)")
    prevention_methods = models.TextField(help_text="Prevention strategies")
    
    # Impact information
    economic_impact = models.TextField(blank=True, help_text="Economic impact description")
    yield_loss_percentage_min = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    yield_loss_percentage_max = models.FloatField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Distribution
    distribution_kenya = models.TextField(help_text="Distribution across Kenyan counties/regions")
    global_distribution = models.TextField(blank=True)
    
    # Seasonal patterns
    seasonal_pattern = models.CharField(max_length=500, blank=True, help_text="When is this issue most prevalent")
    
    # Images
    main_image = models.ImageField(upload_to='pests_diseases/', blank=True, null=True)
    symptom_image = models.ImageField(upload_to='pests_diseases/symptoms/', blank=True, null=True)
    damage_image = models.ImageField(upload_to='pests_diseases/damage/', blank=True, null=True)
    
    # Life cycle (for pests)
    life_cycle_days = models.IntegerField(blank=True, null=True, help_text="Average life cycle in days")
    
    # Vector information
    is_vector = models.BooleanField(default=False, help_text="Does this pest transmit diseases?")
    vector_for = models.TextField(blank=True, help_text="What diseases does it transmit?")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_emerging = models.BooleanField(default=False, help_text="Is this an emerging threat?")
    
    # Relationships
    affects_crops = models.ManyToManyField(Crop, related_name='pests_diseases', blank=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'severity']),
            models.Index(fields=['issue_type', 'category']),
            models.Index(fields=['is_active', 'is_emerging']),
        ]
        verbose_name_plural = "Pests and Diseases"
    
    def __str__(self):
        return self.name
    
    def get_severity_color(self):
        colors = {
            'high': '#dc3545',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        return colors.get(self.severity, '#6c757d')
    
    def get_symptoms_list(self):
        return [s.strip() for s in self.symptoms.split('\n') if s.strip()]
    
    def get_control_methods_list(self):
        return [c.strip() for c in self.control_methods.split('\n') if c.strip()]
    
    def get_prevention_methods_list(self):
        return [p.strip() for p in self.prevention_methods.split('\n') if p.strip()]


class PestDiseaseImage(models.Model):
    """Additional images for pests and diseases"""
    
    IMAGE_TYPES = [
        ('adult', 'Adult Stage'),
        ('larva', 'Larva/Nymph'),
        ('egg', 'Egg Stage'),
        ('symptom', 'Symptom'),
        ('damage', 'Damage'),
        ('control', 'Control Method'),
    ]
    
    pest_disease = models.ForeignKey(PestDisease, on_delete=models.CASCADE, related_name='additional_images')
    image_type = models.CharField(max_length=50, choices=IMAGE_TYPES)
    image = models.ImageField(upload_to='pests_diseases/additional/')
    caption = models.CharField(max_length=500, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']


class County(models.Model):
    """Kenyan counties for regional data"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    region = models.CharField(max_length=100, blank=True)
    population = models.BigIntegerField(blank=True, null=True)
    area_km2 = models.FloatField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Counties"
    
    def __str__(self):
        return self.name


class OutbreakReport(models.Model):
    """Reports of pest/disease outbreaks in specific areas"""
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('severe', 'Severe'),
    ]
    
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('confirmed', 'Confirmed'),
        ('contained', 'Contained'),
        ('ongoing', 'Ongoing'),
        ('resolved', 'Resolved'),
    ]
    
    pest_disease = models.ForeignKey(PestDisease, on_delete=models.CASCADE, related_name='outbreaks')
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='outbreaks')
    location = models.CharField(max_length=300, blank=True, help_text="Specific location/ward")
    
    # Outbreak details
    report_date = models.DateTimeField(default=timezone.now)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    
    # Area affected
    affected_area_ha = models.FloatField(blank=True, null=True, help_text="Affected area in hectares")
    estimated_loss = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Estimated loss in KES")
    
    # Reported by
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    reporter_name = models.CharField(max_length=200, blank=True)
    reporter_contact = models.CharField(max_length=100, blank=True)
    
    # Additional info
    description = models.TextField(blank=True)
    verification_notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_reports')
    verified_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-report_date']
        indexes = [
            models.Index(fields=['pest_disease', 'county']),
            models.Index(fields=['report_date', 'severity']),
        ]
    
    def __str__(self):
        return f"{self.pest_disease.name} - {self.county.name} ({self.report_date.date()})"


class ManagementPractice(models.Model):
    """Best management practices for different crops and issues"""
    
    PRACTICE_CATEGORIES = [
        ('cultural', 'Cultural Practice'),
        ('biological', 'Biological Control'),
        ('chemical', 'Chemical Control'),
        ('physical', 'Physical Control'),
        ('integrated', 'Integrated Pest Management'),
        ('preventive', 'Preventive Measure'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=50, choices=PRACTICE_CATEGORIES)
    description = models.TextField()
    
    # Application details
    application_method = models.CharField(max_length=500, blank=True)
    timing = models.CharField(max_length=500, help_text="When to apply this practice")
    frequency = models.CharField(max_length=200, blank=True, help_text="How often to apply")
    
    # Effectiveness
    effectiveness_rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True)
    
    # Costs
    estimated_cost_kes = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_per_unit = models.CharField(max_length=100, blank=True, help_text="e.g., per acre, per hectare")
    
    # Safety
    safety_precautions = models.TextField(blank=True)
    reentry_interval_days = models.IntegerField(blank=True, null=True, help_text="Days before re-entry after application")
    
    # Relationships
    crops = models.ManyToManyField(Crop, related_name='management_practices', blank=True)
    targets = models.ManyToManyField(PestDisease, related_name='management_practices', blank=True)
    
    # Metadata
    is_organic = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=True)
    source = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class EarlyWarningAlert(models.Model):
    """Early warning alerts for pest/disease outbreaks"""
    
    ALERT_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    alert_level = models.CharField(max_length=20, choices=ALERT_LEVELS, db_index=True)
    
    pest_disease = models.ForeignKey(PestDisease, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    affected_counties = models.ManyToManyField(County, related_name='alerts', blank=True)
    
    # Timing
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    issued_at = models.DateTimeField(auto_now_add=True)
    
    # Actions
    recommended_actions = models.TextField()
    
    # Source
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=300, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['alert_level', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return self.title
    
    def is_current(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date


class UserDashboard(models.Model):
    """User's saved items and preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard')
    saved_pests_diseases = models.ManyToManyField(PestDisease, related_name='saved_by', blank=True)
    saved_management_practices = models.ManyToManyField(ManagementPractice, related_name='saved_by', blank=True)
    
    # Preferences
    favorite_crops = models.ManyToManyField(Crop, related_name='favorite_of', blank=True)
    favorite_counties = models.ManyToManyField(County, related_name='favorite_of', blank=True)
    
    # Notification settings
    receive_alerts = models.BooleanField(default=True)
    alert_frequency = models.CharField(max_length=50, default='daily', choices=[
        ('instant', 'Instant'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Dashboard"


class SearchHistory(models.Model):
    """User search history for analytics"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches', null=True, blank=True)
    session_id = models.CharField(max_length=100, db_index=True)
    
    search_query = models.CharField(max_length=500)
    search_filters = models.JSONField(default=dict, help_text="Stores search filters as JSON")
    
    results_count = models.IntegerField(default=0)
    clicked_result = models.CharField(max_length=300, blank=True, null=True)
    
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_id', 'created_at']),
        ]
        verbose_name_plural = "Search Histories"
    
    def __str__(self):
        return f"Search: {self.search_query[:50]} ({self.created_at.date()})"


class Feedback(models.Model):
    """User feedback on information quality"""
    
    FEEDBACK_TYPES = [
        ('helpful', 'Helpful'),
        ('not_helpful', 'Not Helpful'),
        ('inaccurate', 'Inaccurate'),
        ('outdated', 'Outdated'),
        ('suggestion', 'Suggestion'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback')
    pest_disease = models.ForeignKey(PestDisease, on_delete=models.CASCADE, related_name='feedback', null=True, blank=True)
    
    feedback_type = models.CharField(max_length=50, choices=FEEDBACK_TYPES)
    comment = models.TextField(blank=True)
    
    # Metadata
    page_url = models.CharField(max_length=500, blank=True)
    user_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.feedback_type} - {self.created_at.date()}"


class Resource(models.Model):
    """Additional resources like PDFs, videos, etc."""
    
    RESOURCE_TYPES = [
        ('pdf', 'PDF Document'),
        ('video', 'Video Tutorial'),
        ('article', 'Article'),
        ('infographic', 'Infographic'),
        ('tool', 'Interactive Tool'),
    ]
    
    title = models.CharField(max_length=300)
    description = models.TextField()
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    
    # File or URL
    file = models.FileField(upload_to='resources/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='resources/thumbnails/', blank=True, null=True)
    
    # Relationships
    related_pests_diseases = models.ManyToManyField(PestDisease, related_name='resources', blank=True)
    related_crops = models.ManyToManyField(Crop, related_name='resources', blank=True)
    
    # Metadata
    duration = models.CharField(max_length=50, blank=True, help_text="For videos: e.g., '10:30'")
    file_size = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=50, default='English')
    
    # Usage stats
    view_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
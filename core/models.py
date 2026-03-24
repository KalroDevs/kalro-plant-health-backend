from django.db import models
from django.utils.text import slugify
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class PestCategory(BaseModel):
    """Categories of crop pests/diseases"""
    icon = models.CharField(max_length=100, blank=True, help_text="FontAwesome icon class")
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Pest Categories"
        ordering = ['order', 'name']

class EconomicImportance(models.Model):
    """Economic importance of crops pest and disease"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='economic_importance/', blank=True, null=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class IdentificationImportance(models.Model):
    """Importance of appropriate identification"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='identification_importance/', blank=True, null=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class IPMPrinciple(models.Model):
    """Principles and components of integrated pest management (IPM)"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    icon = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class PesticideUse(models.Model):
    """Responsible use of pesticides in IPM"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    best_practices = models.TextField(blank=True)
    precautions = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class NutrientDeficiency(models.Model):
    """Nutrient Deficiencies and Other Environmental Factors"""
    DEFICIENCY_TYPES = [
        ('N', 'Nitrogen'),
        ('P', 'Phosphorus'),
        ('K', 'Potassium'),
        ('Mg', 'Magnesium'),
        ('Ca', 'Calcium'),
        ('Fe', 'Iron'),
        ('Zn', 'Zinc'),
        ('Other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    deficiency_type = models.CharField(max_length=10, choices=DEFICIENCY_TYPES)
    symptoms = models.TextField()
    causes = models.TextField()
    management = models.TextField()
    image = models.ImageField(upload_to='nutrient_deficiencies/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_deficiency_type_display()} Deficiency - {self.name}"

class EnvironmentalFactor(models.Model):
    """Other environmental factors affecting plant health"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    effects = models.TextField()
    management = models.TextField()
    image = models.ImageField(upload_to='environmental_factors/', blank=True, null=True)
    
    def __str__(self):
        return self.name

class Crop(BaseModel):
    """Crop/Plant model"""
    scientific_name = models.CharField(max_length=200, blank=True)
    family = models.CharField(max_length=100, blank=True)
    economic_importance = models.TextField(blank=True)
    growing_regions = models.TextField(blank=True)
    image = models.ImageField(upload_to='crops/', blank=True, null=True)
    
    class Meta:
        ordering = ['name']

class Pest(BaseModel):
    """Pest model (including vertebrate pests)"""
    PEST_TYPES = [
        ('insect', 'Insect Pest'),
        ('mite', 'Mite'),
        ('nematode', 'Nematode'),
        ('vertebrate', 'Vertebrate Pest'),
        ('other', 'Other'),
    ]
    
    pest_type = models.CharField(max_length=20, choices=PEST_TYPES, default='insect')
    category = models.ForeignKey(PestCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='pests')
    scientific_name = models.CharField(max_length=200, blank=True)
    about = models.TextField(help_text="About the pest")
    identification = models.TextField(help_text="How to identify the pest")
    symptoms = models.TextField(help_text="Symptoms of infestation")
    management = models.TextField(help_text="Management measures")
    lifecycle = models.TextField(blank=True)
    host_range = models.TextField(blank=True)
    image = models.ImageField(upload_to='pests/', blank=True, null=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.get_pest_type_display()}: {self.name}"

class Disease(BaseModel):
    """Disease model"""
    DISEASE_TYPES = [
        ('fungal', 'Fungal Disease'),
        ('bacterial', 'Bacterial Disease'),
        ('viral', 'Viral Disease'),
        ('other', 'Other'),
    ]
    
    disease_type = models.CharField(max_length=20, choices=DISEASE_TYPES, default='fungal')
    category = models.ForeignKey(PestCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='diseases')
    scientific_name = models.CharField(max_length=200, blank=True)
    about = models.TextField(help_text="About the disease")
    identification = models.TextField(help_text="How to identify the disease")
    symptoms = models.TextField(help_text="Symptoms of infestation")
    management = models.TextField(help_text="Management measures")
    disease_cycle = models.TextField(blank=True)
    favorable_conditions = models.TextField(blank=True)
    image = models.ImageField(upload_to='diseases/', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Diseases"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.get_disease_type_display()}: {self.name}"

class PestImage(models.Model):
    """Images for pests"""
    pest = models.ForeignKey(Pest, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='pests/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.pest.name} - {self.caption or 'Image'}"

class DiseaseImage(models.Model):
    """Images for diseases"""
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='diseases/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.disease.name} - {self.caption or 'Image'}"

class CropPest(models.Model):
    """Many-to-many relationship between crops and pests with additional info"""
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='crop_pests')
    pest = models.ForeignKey(Pest, on_delete=models.CASCADE, related_name='crop_pests')
    description = models.TextField(blank=True, help_text="Specific description for this crop-pest relationship")
    damage_symptoms = models.TextField(blank=True, help_text="Damage/Symptoms specific to this crop")
    management_measures = models.TextField(blank=True, help_text="Management measures specific to this crop")
    
    class Meta:
        unique_together = ['crop', 'pest']
    
    def __str__(self):
        return f"{self.crop.name} - {self.pest.name}"

class CropDisease(models.Model):
    """Many-to-many relationship between crops and diseases with additional info"""
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='crop_diseases')
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='crop_diseases')
    description = models.TextField(blank=True, help_text="Specific description for this crop-disease relationship")
    damage_symptoms = models.TextField(blank=True, help_text="Damage/Symptoms specific to this crop")
    management_measures = models.TextField(blank=True, help_text="Management measures specific to this crop")
    
    class Meta:
        unique_together = ['crop', 'disease']
    
    def __str__(self):
        return f"{self.crop.name} - {self.disease.name}"

class VertebratePest(Pest):
    """Specific model for vertebrate pests with additional fields"""
    class Meta:
        proxy = True
    
    def save(self, *args, **kwargs):
        self.pest_type = 'vertebrate'
        super().save(*args, **kwargs)

class ControlMethod(models.Model):
    """Control methods for pests and diseases"""
    METHOD_TYPES = [
        ('cultural', 'Cultural Control'),
        ('biological', 'Biological Control'),
        ('mechanical', 'Mechanical Control'),
        ('chemical', 'Chemical Control'),
        ('integrated', 'Integrated Control'),
    ]
    
    name = models.CharField(max_length=200)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    description = models.TextField()
    application = models.TextField()
    advantages = models.TextField(blank=True)
    disadvantages = models.TextField(blank=True)
    pests = models.ManyToManyField(Pest, blank=True, related_name='control_methods')
    diseases = models.ManyToManyField(Disease, blank=True, related_name='control_methods')
    
    def __str__(self):
        return f"{self.get_method_type_display()}: {self.name}"
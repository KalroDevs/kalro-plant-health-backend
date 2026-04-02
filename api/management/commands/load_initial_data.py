from django.core.management.base import BaseCommand
from api.models import *

class Command(BaseCommand):
    help = 'Load initial data for crop protection database'
    
    def handle(self, *args, **options):
        # Create classification categories
        categories = [
            {'category_type': 'invertebrate-pests', 'name': 'Invertebrate Pests', 
             'description': 'Insects and mites that damage crops', 'color_code': '#dc3545', 'display_order': 1},
            {'category_type': 'diseases', 'name': 'Plant Diseases', 
             'description': 'Fungal, viral, and bacterial diseases', 'color_code': '#fd7e14', 'display_order': 2},
            {'category_type': 'vertebrate-pests', 'name': 'Vertebrate Pests', 
             'description': 'Rodents, birds, and mammals', 'color_code': '#20c997', 'display_order': 3},
            {'category_type': 'abiotic', 'name': 'Abiotic Causes', 
             'description': 'Environmental and nutritional stresses', 'color_code': '#17a2b8', 'display_order': 4},
            {'category_type': 'invasive-alien', 'name': 'Invasive Species', 
             'description': 'Emerging exotic threats', 'color_code': '#e83e8c', 'display_order': 5},
            {'category_type': 'post-harvest', 'name': 'Post-Harvest', 
             'description': 'Storage and handling issues', 'color_code': '#6f42c1', 'display_order': 6},
            {'category_type': 'weeds', 'name': 'Weeds', 
             'description': 'Competitive plants', 'color_code': '#28a745', 'display_order': 7},
        ]
        
        for cat in categories:
            obj, created = ClassificationCategory.objects.get_or_create(
                category_type=cat['category_type'],
                defaults=cat
            )
            self.stdout.write(f"{'Created' if created else 'Already exists'} category: {obj.name}")
        
        # Create Kenyan counties (simplified - add all 47 counties)
        counties = [
            ('Nairobi', 'NBO', 'Central'),
            ('Kiambu', 'KMB', 'Central'),
            ('Nakuru', 'NKR', 'Rift Valley'),
            ('Kisumu', 'KSM', 'Nyanza'),
            ('Mombasa', 'MBS', 'Coast'),
            # Add all 47 counties...
        ]
        
        for name, code, region in counties:
            obj, created = County.objects.get_or_create(
                code=code,
                defaults={'name': name, 'region': region}
            )
        
        # Create major crops
        crops = [
            ('Maize', 'cereal', 'Zea mays'),
            ('Tomato', 'vegetable', 'Solanum lycopersicum'),
            ('Common Bean', 'legume', 'Phaseolus vulgaris'),
            ('Potato', 'tuber', 'Solanum tuberosum'),
            ('Coffee', 'cash-crop', 'Coffea arabica'),
        ]
        
        for name, category, scientific in crops:
            obj, created = Crop.objects.get_or_create(
                name=name,
                defaults={'category': category, 'scientific_name': scientific}
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded initial data'))
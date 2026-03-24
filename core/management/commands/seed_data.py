from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import *
class Command(BaseCommand):
    help = 'Seed initial data for KALRO Plant Health'
    
    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Create pest categories
        categories = [
            {'name': 'Insects', 'description': 'Insect pests affecting crops', 'icon': 'fa-bug', 'order': 1},
            {'name': 'Mites', 'description': 'Mite pests', 'icon': 'fa-spider', 'order': 2},
            {'name': 'Nematodes', 'description': 'Nematode pests', 'icon': 'fa-worm', 'order': 3},
            {'name': 'Fungal Diseases', 'description': 'Fungal diseases', 'icon': 'fa-mushroom', 'order': 4},
            {'name': 'Bacterial Diseases', 'description': 'Bacterial diseases', 'icon': 'fa-bacteria', 'order': 5},
            {'name': 'Viral Diseases', 'description': 'Viral diseases', 'icon': 'fa-virus', 'order': 6},
            {'name': 'Vertebrate Pests', 'description': 'Vertebrate pests including birds and monkeys', 'icon': 'fa-paw', 'order': 7},
        ]
        
        for cat in categories:
            PestCategory.objects.get_or_create(
                name=cat['name'],
                defaults={
                    'description': cat['description'],
                    'icon': cat['icon'],
                    'order': cat['order']
                }
            )
        
        # Create economic importance entries
        economic_entries = [
            {
                'title': 'Food Security',
                'content': 'Pests and diseases significantly impact food security by reducing crop yields and quality. In Kenya, major crops like maize, beans, and vegetables face threats from various pests leading to substantial losses.',
                'order': 1
            },
            {
                'title': 'Economic Losses',
                'content': 'Annual losses due to pests and diseases in Kenya are estimated at billions of shillings. This affects farmers\' income, employment in agriculture sector, and the overall economy.',
                'order': 2
            },
            {
                'title': 'Export Markets',
                'content': 'Pest and disease infestations can restrict access to international markets due to quarantine restrictions. Maintaining pest-free status is crucial for export crops like coffee, tea, and horticultural products.',
                'order': 3
            },
        ]
        
        for entry in economic_entries:
            EconomicImportance.objects.get_or_create(
                title=entry['title'],
                defaults=entry
            )
        
        # Create IPM principles
        ipm_principles = [
            {
                'title': 'Prevention',
                'content': 'Prevent pest problems through cultural practices, resistant varieties, and maintaining plant health.',
                'icon': 'fa-shield-alt',
                'order': 1
            },
            {
                'title': 'Monitoring',
                'content': 'Regular scouting and monitoring to identify pests and determine if control measures are needed.',
                'icon': 'fa-eye',
                'order': 2
            },
            {
                'title': 'Action Thresholds',
                'content': 'Establish economic thresholds to determine when control measures are justified.',
                'icon': 'fa-chart-line',
                'order': 3
            },
            {
                'title': 'Integrated Control',
                'content': 'Combine biological, cultural, mechanical, and chemical control methods for sustainable management.',
                'icon': 'fa-chart-line',
                'order': 4
            },
        ]
        
        for principle in ipm_principles:
            IPMPrinciple.objects.get_or_create(
                title=principle['title'],
                defaults=principle
            )
        
        # Create pesticide use guidelines
        pesticide_use = {
            'title': 'Responsible Pesticide Use',
            'content': 'Pesticides should be used as a last resort in IPM programs, following all safety guidelines and regulations.',
            'best_practices': '• Use recommended pesticides only\n• Apply at correct dosage\n• Rotate pesticides to prevent resistance\n• Follow safety intervals before harvest',
            'precautions': '• Wear protective clothing\n• Avoid spraying during windy conditions\n• Keep away from water sources\n• Store safely away from children and food',
            'order': 1
        }
        
        PesticideUse.objects.get_or_create(
            title=pesticide_use['title'],
            defaults=pesticide_use
        )
        
        # Create sample crops
        crops = [
            {
                'name': 'Maize',
                'scientific_name': 'Zea mays',
                'family': 'Poaceae',
                'description': 'Maize is the most important cereal crop in Kenya, serving as a staple food for millions of Kenyans.',
                'economic_importance': 'Maize accounts for over 40% of the total cropped area in Kenya and is the main source of food and income for smallholder farmers.',
                'growing_regions': 'Rift Valley, Western, Eastern, Central, and Coast regions'
            },
            {
                'name': 'Beans',
                'scientific_name': 'Phaseolus vulgaris',
                'family': 'Fabaceae',
                'description': 'Beans are a major source of protein for many Kenyan households.',
                'economic_importance': 'Beans are the second most important food crop after maize, providing essential protein and income.',
                'growing_regions': 'All agricultural regions of Kenya'
            },
            {
                'name': 'Tomato',
                'scientific_name': 'Solanum lycopersicum',
                'family': 'Solanaceae',
                'description': 'Tomatoes are one of the most important vegetable crops in Kenya.',
                'economic_importance': 'Tomatoes generate significant income for smallholder farmers and contribute to food security.',
                'growing_regions': 'Kirinyaga, Kiambu, Meru, and other vegetable-growing areas'
            },
        ]
        
        for crop_data in crops:
            Crop.objects.get_or_create(
                name=crop_data['name'],
                defaults=crop_data
            )
        
        # Create sample pests
        pests = [
            {
                'name': 'Fall Armyworm',
                'pest_type': 'insect',
                'scientific_name': 'Spodoptera frugiperda',
                'description': 'An invasive pest that attacks maize and other crops.',
                'about': 'Fall armyworm is a destructive pest that originated in the Americas and has spread to Africa.',
                'identification': 'Larvae have a distinctive inverted Y on the head, adult moths have white hindwings and mottled forewings.',
                'symptoms': 'Leaf damage, whorl damage, and frass (excrement) in the whorl.',
                'management': 'Early planting, regular scouting, use of biopesticides, and chemical control when thresholds are exceeded.',
                'host_range': 'Maize, sorghum, millet, rice, and over 80 other plant species.'
            },
            {
                'name': 'Birds (Quelea quelea)',
                'pest_type': 'vertebrate',
                'scientific_name': 'Quelea quelea',
                'description': 'Red-billed quelea birds that cause significant damage to cereal crops.',
                'about': 'Quelea birds are considered the most destructive bird pest in Africa, forming massive flocks.',
                'identification': 'Small finch-like birds, males have red bills and pink to red plumage during breeding season.',
                'symptoms': 'Large flocks descending on fields, stripping grains from heads, causing significant yield loss.',
                'management': 'Scaring devices, bird netting, coordinated control operations, and planting of less susceptible varieties.',
                'host_range': 'Maize, sorghum, wheat, millet, and other cereal grains.'
            },
            {
                'name': 'Monkeys',
                'pest_type': 'vertebrate',
                'scientific_name': 'Cercopithecus spp.',
                'description': 'Monkeys that raid farms and cause significant crop damage.',
                'about': 'Various monkey species, particularly vervet and Sykes monkeys, raid farms near forest edges.',
                'identification': 'Medium-sized primates with gray or brown fur, long tails, and agile movements.',
                'symptoms': 'Crop raiding, fruit and vegetable damage, broken branches, and trampling of plants.',
                'management': 'Physical barriers like electric fences, guard animals, scare tactics, and community-based management approaches.',
                'host_range': 'Maize, bananas, fruits, vegetables, and various other crops.'
            },
        ]
        
        for pest_data in pests:
            Pest.objects.get_or_create(
                name=pest_data['name'],
                defaults=pest_data
            )
        
        # Create sample diseases
        diseases = [
            {
                'name': 'Maize Lethal Necrosis',
                'disease_type': 'viral',
                'scientific_name': 'Maize lethal necrosis virus complex',
                'description': 'A devastating viral disease affecting maize.',
                'about': 'MLN is caused by a combination of two viruses: Maize chlorotic mottle virus and Sugarcane mosaic virus.',
                'identification': 'Chlorotic mottling, leaf necrosis, stunting, and sometimes plant death.',
                'symptoms': 'Yellowing, stunting, dead tissue on leaves, and reduced ear formation.',
                'management': 'Use of resistant varieties, crop rotation, removal of infected plants, and controlling insect vectors.',
                'favorable_conditions': 'Presence of insect vectors, continuous maize cropping, and warm conditions.'
            },
            {
                'name': 'Tomato Bacterial Wilt',
                'disease_type': 'bacterial',
                'scientific_name': 'Ralstonia solanacearum',
                'description': 'A bacterial disease that causes rapid wilting and death of tomato plants.',
                'about': 'Bacterial wilt is a soil-borne disease that affects many solanaceous crops.',
                'identification': 'Sudden wilting of leaves, vascular discoloration, and bacterial ooze from cut stems.',
                'symptoms': 'Wilting, stunting, yellowing, and eventual plant death.',
                'management': 'Crop rotation, use of resistant varieties, soil solarization, and avoiding injury to roots.',
                'favorable_conditions': 'Warm, moist soils, and continuous cropping of susceptible plants.'
            },
        ]
        
        for disease_data in diseases:
            Disease.objects.get_or_create(
                name=disease_data['name'],
                defaults=disease_data
            )
        
        # Create control methods
        control_methods = [
            {
                'name': 'Biological Control with Natural Enemies',
                'method_type': 'biological',
                'description': 'Use of natural predators, parasitoids, and pathogens to control pests.',
                'application': 'Introduce or conserve natural enemies in the farming system.',
                'advantages': 'Environmentally friendly, sustainable, and reduces chemical use.',
                'disadvantages': 'May be slower to act and requires knowledge of beneficial organisms.'
            },
            {
                'name': 'Crop Rotation',
                'method_type': 'cultural',
                'description': 'Alternating different crops in the same field across seasons.',
                'application': 'Rotate crops from different families to break pest and disease cycles.',
                'advantages': 'Reduces pest build-up, improves soil health, and manages nutrient depletion.',
                'disadvantages': 'May require planning and may not be suitable for all farming systems.'
            },
        ]
        
        for control_data in control_methods:
            ControlMethod.objects.get_or_create(
                name=control_data['name'],
                defaults=control_data
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded initial data'))
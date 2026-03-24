from rest_framework import viewsets, generics, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import *
from .serializers import *

class EconomicImportanceViewSet(viewsets.ModelViewSet):
    queryset = EconomicImportance.objects.all()
    serializer_class = EconomicImportanceSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order']
    ordering = ['order']

class IdentificationImportanceViewSet(viewsets.ModelViewSet):
    queryset = IdentificationImportance.objects.all()
    serializer_class = IdentificationImportanceSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order']
    ordering = ['order']

class IPMPrincipleViewSet(viewsets.ModelViewSet):
    queryset = IPMPrinciple.objects.all()
    serializer_class = IPMPrincipleSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order']
    ordering = ['order']

class PesticideUseViewSet(viewsets.ModelViewSet):
    queryset = PesticideUse.objects.all()
    serializer_class = PesticideUseSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order']
    ordering = ['order']

class NutrientDeficiencyViewSet(viewsets.ModelViewSet):
    queryset = NutrientDeficiency.objects.all()
    serializer_class = NutrientDeficiencySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['deficiency_type']
    search_fields = ['name', 'symptoms']

class EnvironmentalFactorViewSet(viewsets.ModelViewSet):
    queryset = EnvironmentalFactor.objects.all()
    serializer_class = EnvironmentalFactorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class PestCategoryViewSet(viewsets.ModelViewSet):
    queryset = PestCategory.objects.filter(is_active=True)
    serializer_class = PestCategorySerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order']
    ordering = ['order']

class PestViewSet(viewsets.ModelViewSet):
    queryset = Pest.objects.filter(is_active=True)
    serializer_class = PestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pest_type', 'category']
    search_fields = ['name', 'scientific_name', 'description', 'about', 'identification']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def crops(self, request, pk=None):
        pest = self.get_object()
        crops = Crop.objects.filter(crop_pests__pest=pest)
        serializer = CropSerializer(crops, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        pest_type = request.query_params.get('type')
        if pest_type:
            pests = self.queryset.filter(pest_type=pest_type)
            serializer = self.get_serializer(pests, many=True)
            return Response(serializer.data)
        return Response({'error': 'Please specify pest type'}, status=400)
    
    @action(detail=False, methods=['get'])
    def vertebrate(self, request):
        pests = self.queryset.filter(pest_type='vertebrate')
        serializer = self.get_serializer(pests, many=True)
        return Response(serializer.data)

class DiseaseViewSet(viewsets.ModelViewSet):
    queryset = Disease.objects.filter(is_active=True)
    serializer_class = DiseaseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['disease_type', 'category']
    search_fields = ['name', 'scientific_name', 'description', 'about', 'identification']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def crops(self, request, pk=None):
        disease = self.get_object()
        crops = Crop.objects.filter(crop_diseases__disease=disease)
        serializer = CropSerializer(crops, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        disease_type = request.query_params.get('type')
        if disease_type:
            diseases = self.queryset.filter(disease_type=disease_type)
            serializer = self.get_serializer(diseases, many=True)
            return Response(serializer.data)
        return Response({'error': 'Please specify disease type'}, status=400)

class CropViewSet(viewsets.ModelViewSet):
    queryset = Crop.objects.filter(is_active=True)
    serializer_class = CropSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'scientific_name', 'family', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CropDetailSerializer
        return CropSerializer
    
    @action(detail=True, methods=['get'])
    def pests(self, request, pk=None):
        crop = self.get_object()
        pests = Pest.objects.filter(crop_pests__crop=crop)
        serializer = PestSerializer(pests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def diseases(self, request, pk=None):
        crop = self.get_object()
        diseases = Disease.objects.filter(crop_diseases__crop=crop)
        serializer = DiseaseSerializer(diseases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def pest_details(self, request, pk=None):
        crop = self.get_object()
        crop_pests = CropPest.objects.filter(crop=crop).select_related('pest')
        serializer = CropPestSerializer(crop_pests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def disease_details(self, request, pk=None):
        crop = self.get_object()
        crop_diseases = CropDisease.objects.filter(crop=crop).select_related('disease')
        serializer = CropDiseaseSerializer(crop_diseases, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search_by_name(self, request):
        query = request.query_params.get('q', '')
        crops = self.queryset.filter(Q(name__icontains=query) | Q(scientific_name__icontains=query))
        serializer = self.get_serializer(crops, many=True)
        return Response(serializer.data)

class CropPestViewSet(viewsets.ModelViewSet):
    queryset = CropPest.objects.all()
    serializer_class = CropPestSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['crop', 'pest']

class CropDiseaseViewSet(viewsets.ModelViewSet):
    queryset = CropDisease.objects.all()
    serializer_class = CropDiseaseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['crop', 'disease']

class ControlMethodViewSet(viewsets.ModelViewSet):
    queryset = ControlMethod.objects.all()
    serializer_class = ControlMethodSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['method_type']
    search_fields = ['name', 'description']
    
    @action(detail=False, methods=['get'])
    def for_pest(self, request):
        pest_id = request.query_params.get('pest_id')
        if pest_id:
            methods = self.queryset.filter(pests__id=pest_id)
            serializer = self.get_serializer(methods, many=True)
            return Response(serializer.data)
        return Response({'error': 'Please specify pest_id'}, status=400)
    
    @action(detail=False, methods=['get'])
    def for_disease(self, request):
        disease_id = request.query_params.get('disease_id')
        if disease_id:
            methods = self.queryset.filter(diseases__id=disease_id)
            serializer = self.get_serializer(methods, many=True)
            return Response(serializer.data)
        return Response({'error': 'Please specify disease_id'}, status=400)

class DashboardView(generics.GenericAPIView):
    """Dashboard view with statistics and overview"""
    
    def get(self, request):
        data = {
            'total_crops': Crop.objects.filter(is_active=True).count(),
            'total_pests': Pest.objects.filter(is_active=True).count(),
            'total_diseases': Disease.objects.filter(is_active=True).count(),
            'pests_by_type': {
                pest_type: Pest.objects.filter(pest_type=pest_type, is_active=True).count()
                for pest_type, _ in Pest.PEST_TYPES
            },
            'diseases_by_type': {
                disease_type: Disease.objects.filter(disease_type=disease_type, is_active=True).count()
                for disease_type, _ in Disease.DISEASE_TYPES
            },
            'recent_crops': CropSerializer(Crop.objects.filter(is_active=True)[:5], many=True).data,
            'recent_pests': PestSerializer(Pest.objects.filter(is_active=True)[:5], many=True).data,
            'recent_diseases': DiseaseSerializer(Disease.objects.filter(is_active=True)[:5], many=True).data,
        }
        return Response(data)
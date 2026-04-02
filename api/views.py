from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from .filters import PestDiseaseFilter

# ============================================================================
# Custom Pagination
# ============================================================================

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class for API endpoints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargeResultsSetPagination(PageNumberPagination):
    """Larger pagination for admin/bulk operations"""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500


# ============================================================================
# Crop ViewSet
# ============================================================================

class CropViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Crop operations.
    
    Provides CRUD operations for crops including:
    - List all crops
    - Get crop details
    - Create/Update/Delete crops (admin only)
    - Get pests/diseases affecting a crop
    - Get management practices for a crop
    """
    queryset = Crop.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'scientific_name', 'description']
    ordering_fields = ['name', 'category', 'created_at']
    ordering = ['name']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CropListSerializer
        return CropSerializer
    
    @action(detail=True, methods=['get'])
    def pests_diseases(self, request, pk=None):
        """
        Get all pests and diseases that affect this crop.
        """
        crop = self.get_object()
        pests_diseases = crop.pests_diseases.filter(is_active=True)
        
        # Apply additional filters if provided
        severity = request.query_params.get('severity')
        issue_type = request.query_params.get('issue_type')
        
        if severity:
            pests_diseases = pests_diseases.filter(severity=severity)
        if issue_type:
            pests_diseases = pests_diseases.filter(issue_type=issue_type)
        
        page = self.paginate_queryset(pests_diseases)
        if page is not None:
            serializer = PestDiseaseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PestDiseaseListSerializer(pests_diseases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def management_practices(self, request, pk=None):
        """
        Get management practices recommended for this crop.
        """
        crop = self.get_object()
        practices = crop.management_practices.filter(is_recommended=True)
        
        # Filter by practice category
        category = request.query_params.get('category')
        if category:
            practices = practices.filter(category=category)
        
        serializer = ManagementPracticeListSerializer(practices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get crops grouped by category.
        """
        categories = Crop.CROP_CATEGORIES
        result = {}
        
        for category_code, category_name in categories:
            crops = self.queryset.filter(category=category_code)
            if crops.exists():
                serializer = CropListSerializer(crops, many=True)
                result[category_name] = serializer.data
        
        return Response(result)


# ============================================================================
# Classification Category ViewSet
# ============================================================================

class ClassificationCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Classification Categories.
    
    Manages the main categories of crop health issues including:
    - Invertebrate Pests
    - Plant Diseases
    - Vertebrate Pests
    - Abiotic Causes
    - Invasive Species
    - Post-Harvest Issues
    - Weeds
    """
    queryset = ClassificationCategory.objects.filter(is_active=True)
    serializer_class = ClassificationCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category_type']
    search_fields = ['name', 'description']
    ordering_fields = ['display_order', 'name']
    ordering = ['display_order', 'name']
    
    @action(detail=True, methods=['get'])
    def issues(self, request, pk=None):
        """
        Get all pests/diseases in this category.
        """
        category = self.get_object()
        issues = category.issues.filter(is_active=True)
        
        # Paginate results
        page = self.paginate_queryset(issues)
        if page is not None:
            serializer = PestDiseaseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PestDiseaseListSerializer(issues, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get statistics for this category.
        """
        category = self.get_object()
        issues = category.issues.filter(is_active=True)
        
        stats = {
            'total_issues': issues.count(),
            'by_severity': {
                'high': issues.filter(severity='high').count(),
                'medium': issues.filter(severity='medium').count(),
                'low': issues.filter(severity='low').count(),
            },
            'by_issue_type': {},
        }
        
        # Count by issue type
        for issue_type, _ in PestDisease.ISSUE_TYPES:
            count = issues.filter(issue_type=issue_type).count()
            if count > 0:
                stats['by_issue_type'][issue_type] = count
        
        return Response(stats)


# ============================================================================
# Pest and Disease ViewSet
# ============================================================================

class PestDiseaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Pest and Disease operations.
    
    Comprehensive management of pests and diseases including:
    - List all pests/diseases with filtering
    - Get detailed information about specific issues
    - Get management practices
    - Get outbreak reports
    - Get related resources
    - Filter by various criteria
    """
    queryset = PestDisease.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PestDiseaseFilter
    search_fields = ['name', 'scientific_name', 'local_names', 'description', 'symptoms']
    ordering_fields = ['name', 'severity', 'created_at', 'updated_at']
    ordering = ['name']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PestDiseaseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PestDiseaseCreateUpdateSerializer
        return PestDiseaseDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get detailed information about a specific pest/disease.
        Includes all related data like symptoms, control methods, etc.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Add additional context
        data = serializer.data
        data['related_outbreaks'] = OutbreakReportSerializer(
            instance.outbreaks.filter(status__in=['confirmed', 'ongoing'])[:5], 
            many=True
        ).data
        data['related_resources'] = ResourceSerializer(
            instance.resources.filter(is_published=True)[:3], 
            many=True
        ).data
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def management_practices(self, request, pk=None):
        """
        Get management practices for this pest/disease.
        """
        pest = self.get_object()
        practices = pest.management_practices.filter(is_recommended=True)
        
        # Filter by practice category
        category = request.query_params.get('category')
        if category:
            practices = practices.filter(category=category)
        
        serializer = ManagementPracticeListSerializer(practices, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def outbreaks(self, request, pk=None):
        """
        Get outbreak reports for this pest/disease.
        """
        pest = self.get_object()
        outbreaks = pest.outbreaks.all()
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            outbreaks = outbreaks.filter(status=status_filter)
        
        # Filter by county
        county_id = request.query_params.get('county_id')
        if county_id:
            outbreaks = outbreaks.filter(county_id=county_id)
        
        # Paginate results
        page = self.paginate_queryset(outbreaks)
        if page is not None:
            serializer = OutbreakReportSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OutbreakReportSerializer(outbreaks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        """
        Get resources for this pest/disease.
        """
        pest = self.get_object()
        resources = pest.resources.filter(is_published=True)
        
        # Filter by resource type
        resource_type = request.query_params.get('resource_type')
        if resource_type:
            resources = resources.filter(resource_type=resource_type)
        
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def emerging(self, request):
        """
        Get all emerging threats.
        """
        emerging = self.queryset.filter(is_emerging=True)
        
        # Paginate results
        page = self.paginate_queryset(emerging)
        if page is not None:
            serializer = PestDiseaseListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PestDiseaseListSerializer(emerging, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_severity(self, request):
        """
        Get pests/diseases grouped by severity.
        """
        result = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for severity in ['high', 'medium', 'low']:
            queryset = self.queryset.filter(severity=severity)
            serializer = PestDiseaseListSerializer(queryset, many=True)
            result[severity] = serializer.data
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def by_crop(self, request):
        """
        Get pests/diseases by crop.
        """
        crop_id = request.query_params.get('crop_id')
        if not crop_id:
            return Response(
                {'error': 'crop_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            crop = Crop.objects.get(id=crop_id)
            pests_diseases = crop.pests_diseases.filter(is_active=True)
            serializer = PestDiseaseListSerializer(pests_diseases, many=True)
            return Response(serializer.data)
        except Crop.DoesNotExist:
            return Response(
                {'error': 'Crop not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get statistics for pests and diseases.
        """
        stats = {
            'total': self.queryset.count(),
            'by_type': {},
            'by_severity': {
                'high': self.queryset.filter(severity='high').count(),
                'medium': self.queryset.filter(severity='medium').count(),
                'low': self.queryset.filter(severity='low').count(),
            },
            'by_damage_type': {
                'direct': self.queryset.filter(damage_type='direct').count(),
                'indirect': self.queryset.filter(damage_type='indirect').count(),
                'both': self.queryset.filter(damage_type='both').count(),
            },
            'emerging': self.queryset.filter(is_emerging=True).count(),
        }
        
        # Count by issue type
        for issue_type, label in PestDisease.ISSUE_TYPES:
            count = self.queryset.filter(issue_type=issue_type).count()
            if count > 0:
                stats['by_type'][label] = count
        
        return Response(stats)
    

    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        """
        Get all images for a specific pest/disease.
        """
        pest = self.get_object()
        images = pest.additional_images.all()
        serializer = PestDiseaseImageSerializer(images, many=True)
        return Response(serializer.data)


# ============================================================================
# County ViewSet
# ============================================================================

class CountyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for County operations.
    
    Manages Kenyan counties including:
    - List all counties
    - Get county details
    - Get outbreaks in a county
    - Get active alerts for a county
    """
    queryset = County.objects.all()
    serializer_class = CountySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'region']
    filterset_fields = ['region']
    ordering_fields = ['name', 'region']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def outbreaks(self, request, pk=None):
        """
        Get outbreak reports in this county.
        """
        county = self.get_object()
        outbreaks = county.outbreaks.all()
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            outbreaks = outbreaks.filter(status=status_filter)
        
        # Filter by pest/disease
        pest_id = request.query_params.get('pest_id')
        if pest_id:
            outbreaks = outbreaks.filter(pest_disease_id=pest_id)
        
        # Paginate results
        page = self.paginate_queryset(outbreaks)
        if page is not None:
            serializer = OutbreakReportSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OutbreakReportSerializer(outbreaks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """
        Get active early warning alerts for this county.
        """
        county = self.get_object()
        now = timezone.now()
        alerts = EarlyWarningAlert.objects.filter(
            affected_counties=county,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
        
        serializer = EarlyWarningAlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get agricultural statistics for this county.
        """
        county = self.get_object()
        
        stats = {
            'county_name': county.name,
            'total_outbreaks': county.outbreaks.count(),
            'active_outbreaks': county.outbreaks.filter(status__in=['confirmed', 'ongoing']).count(),
            'recent_alerts': county.alerts.filter(is_active=True).count(),
            'top_pests': [],
        }
        
        # Get top pests in this county
        top_pests = county.outbreaks.values('pest_disease__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        stats['top_pests'] = list(top_pests)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def by_region(self, request):
        """
        Get counties grouped by region.
        """
        regions = County.objects.values_list('region', flat=True).distinct()
        result = {}
        
        for region in regions:
            if region:
                counties = self.queryset.filter(region=region)
                serializer = CountySerializer(counties, many=True)
                result[region] = serializer.data
        
        return Response(result)


# ============================================================================
# Outbreak Report ViewSet
# ============================================================================

class OutbreakReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Outbreak Reports.
    
    Manages pest/disease outbreak reports including:
    - Report new outbreaks
    - Track outbreak status
    - Filter by pest, county, severity, status
    - Verify and update reports
    """
    queryset = OutbreakReport.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pest_disease', 'county', 'severity', 'status']
    search_fields = ['location', 'description', 'reporter_name']
    ordering_fields = ['report_date', 'severity', 'created_at']
    ordering = ['-report_date']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OutbreakReportCreateSerializer
        return OutbreakReportSerializer
    
    def perform_create(self, serializer):
        """Create a new outbreak report."""
        serializer.save(
            reported_by=self.request.user if self.request.user.is_authenticated else None
        )
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify an outbreak report (admin only).
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin privileges required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        outbreak = self.get_object()
        outbreak.status = 'confirmed'
        outbreak.verified_by = request.user
        outbreak.verified_date = timezone.now()
        outbreak.verification_notes = request.data.get('verification_notes', '')
        outbreak.save()
        
        serializer = self.get_serializer(outbreak)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Mark an outbreak as resolved.
        """
        outbreak = self.get_object()
        outbreak.status = 'resolved'
        outbreak.save()
        
        serializer = self.get_serializer(outbreak)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent outbreak reports (last 30 days).
        """
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_outbreaks = self.queryset.filter(report_date__gte=thirty_days_ago)
        
        page = self.paginate_queryset(recent_outbreaks)
        if page is not None:
            serializer = OutbreakReportSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OutbreakReportSerializer(recent_outbreaks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get active outbreaks (confirmed or ongoing).
        """
        active_outbreaks = self.queryset.filter(status__in=['confirmed', 'ongoing'])
        
        page = self.paginate_queryset(active_outbreaks)
        if page is not None:
            serializer = OutbreakReportSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OutbreakReportSerializer(active_outbreaks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get outbreak statistics.
        """
        stats = {
            'total_reports': self.queryset.count(),
            'active_outbreaks': self.queryset.filter(status__in=['confirmed', 'ongoing']).count(),
            'by_severity': {},
            'by_status': {},
            'most_affected_counties': [],
            'most_common_pests': [],
        }
        
        # Count by severity
        for severity, _ in OutbreakReport.SEVERITY_LEVELS:
            stats['by_severity'][severity] = self.queryset.filter(severity=severity).count()
        
        # Count by status
        for status, _ in OutbreakReport.STATUS_CHOICES:
            stats['by_status'][status] = self.queryset.filter(status=status).count()
        
        # Most affected counties
        top_counties = self.queryset.values('county__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        stats['most_affected_counties'] = list(top_counties)
        
        # Most common pests
        top_pests = self.queryset.values('pest_disease__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        stats['most_common_pests'] = list(top_pests)
        
        return Response(stats)


# ============================================================================
# Management Practice ViewSet
# ============================================================================

class ManagementPracticeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Management Practices.
    
    Manages agricultural management practices including:
    - Cultural practices
    - Biological control
    - Chemical control
    - Physical control
    - IPM strategies
    - Preventive measures
    """
    queryset = ManagementPractice.objects.filter(is_recommended=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_organic', 'is_recommended']
    search_fields = ['name', 'description', 'application_method']
    ordering_fields = ['name', 'effectiveness_rating', 'estimated_cost_kes']
    ordering = ['category', 'name']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ManagementPracticeListSerializer
        return ManagementPracticeSerializer
    
    @action(detail=False, methods=['get'])
    def by_crop(self, request):
        """
        Get management practices by crop.
        """
        crop_id = request.query_params.get('crop_id')
        if not crop_id:
            return Response(
                {'error': 'crop_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            crop = Crop.objects.get(id=crop_id)
            practices = crop.management_practices.filter(is_recommended=True)
            serializer = ManagementPracticeListSerializer(practices, many=True)
            return Response(serializer.data)
        except Crop.DoesNotExist:
            return Response(
                {'error': 'Crop not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def by_pest(self, request):
        """
        Get management practices by pest/disease.
        """
        pest_id = request.query_params.get('pest_id')
        if not pest_id:
            return Response(
                {'error': 'pest_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pest = PestDisease.objects.get(id=pest_id)
            practices = pest.management_practices.filter(is_recommended=True)
            serializer = ManagementPracticeListSerializer(practices, many=True)
            return Response(serializer.data)
        except PestDisease.DoesNotExist:
            return Response(
                {'error': 'Pest/Disease not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def organic(self, request):
        """
        Get organic management practices only.
        """
        organic_practices = self.queryset.filter(is_organic=True)
        
        page = self.paginate_queryset(organic_practices)
        if page is not None:
            serializer = ManagementPracticeListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ManagementPracticeListSerializer(organic_practices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_effectiveness(self, request):
        """
        Get management practices sorted by effectiveness rating.
        """
        min_rating = request.query_params.get('min_rating', 0)
        practices = self.queryset.filter(effectiveness_rating__gte=min_rating).order_by('-effectiveness_rating')
        
        serializer = ManagementPracticeListSerializer(practices, many=True)
        return Response(serializer.data)


# ============================================================================
# Early Warning Alert ViewSet
# ============================================================================

class EarlyWarningAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Early Warning Alerts.
    
    Manages early warning alerts for pest/disease outbreaks including:
    - Create and publish alerts
    - Get current active alerts
    - Filter alerts by county, severity, pest
    - Alert expiration and deactivation
    """
    queryset = EarlyWarningAlert.objects.filter(is_active=True)
    serializer_class = EarlyWarningAlertSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['alert_level', 'is_active', 'pest_disease']
    search_fields = ['title', 'description', 'recommended_actions']
    ordering_fields = ['issued_at', 'start_date', 'end_date']
    ordering = ['-issued_at']
    pagination_class = StandardResultsSetPagination
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get current active alerts.
        """
        now = timezone.now()
        current_alerts = self.queryset.filter(
            start_date__lte=now,
            end_date__gte=now
        )
        
        page = self.paginate_queryset(current_alerts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(current_alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_county(self, request):
        """
        Get alerts by county.
        """
        county_id = request.query_params.get('county_id')
        if not county_id:
            return Response(
                {'error': 'county_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            county = County.objects.get(id=county_id)
            alerts = self.queryset.filter(affected_counties=county)
            
            serializer = self.get_serializer(alerts, many=True)
            return Response(serializer.data)
        except County.DoesNotExist:
            return Response(
                {'error': 'County not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """
        Get critical level alerts only.
        """
        critical_alerts = self.queryset.filter(alert_level='critical')
        
        serializer = self.get_serializer(critical_alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Deactivate an alert (admin only).
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin privileges required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        alert = self.get_object()
        alert.is_active = False
        alert.save()
        
        return Response({'message': 'Alert deactivated successfully'})


# ============================================================================
# User Dashboard ViewSet
# ============================================================================

class UserDashboardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User Dashboard.
    
    Manages user-specific dashboard data including:
    - Saved pests/diseases
    - Saved management practices
    - Favorite crops and counties
    - Notification preferences
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserDashboardSerializer
    
    def get_queryset(self):
        return UserDashboard.objects.filter(user=self.request.user)
    
    def get_object(self):
        obj, created = UserDashboard.objects.get_or_create(user=self.request.user)
        return obj
    
    def list(self, request, *args, **kwargs):
        """Get the current user's dashboard."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def save_pest(self, request):
        """
        Save a pest/disease to the user's dashboard.
        """
        dashboard = self.get_object()
        pest_id = request.data.get('pest_id')
        
        if not pest_id:
            return Response(
                {'error': 'pest_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pest = PestDisease.objects.get(id=pest_id)
            dashboard.saved_pests_diseases.add(pest)
            return Response(
                {'message': f'{pest.name} saved successfully'},
                status=status.HTTP_200_OK
            )
        except PestDisease.DoesNotExist:
            return Response(
                {'error': 'Pest/Disease not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def remove_pest(self, request):
        """
        Remove a pest/disease from the user's dashboard.
        """
        dashboard = self.get_object()
        pest_id = request.data.get('pest_id')
        
        if not pest_id:
            return Response(
                {'error': 'pest_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pest = PestDisease.objects.get(id=pest_id)
            dashboard.saved_pests_diseases.remove(pest)
            return Response(
                {'message': f'{pest.name} removed successfully'},
                status=status.HTTP_200_OK
            )
        except PestDisease.DoesNotExist:
            return Response(
                {'error': 'Pest/Disease not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def save_practice(self, request):
        """
        Save a management practice to the user's dashboard.
        """
        dashboard = self.get_object()
        practice_id = request.data.get('practice_id')
        
        if not practice_id:
            return Response(
                {'error': 'practice_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            practice = ManagementPractice.objects.get(id=practice_id)
            dashboard.saved_management_practices.add(practice)
            return Response(
                {'message': f'{practice.name} saved successfully'},
                status=status.HTTP_200_OK
            )
        except ManagementPractice.DoesNotExist:
            return Response(
                {'error': 'Management practice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def add_favorite_crop(self, request):
        """
        Add a crop to the user's favorites.
        """
        dashboard = self.get_object()
        crop_id = request.data.get('crop_id')
        
        if not crop_id:
            return Response(
                {'error': 'crop_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            crop = Crop.objects.get(id=crop_id)
            dashboard.favorite_crops.add(crop)
            return Response(
                {'message': f'{crop.name} added to favorites'},
                status=status.HTTP_200_OK
            )
        except Crop.DoesNotExist:
            return Response(
                {'error': 'Crop not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def update_preferences(self, request):
        """
        Update notification preferences.
        """
        dashboard = self.get_object()
        
        receive_alerts = request.data.get('receive_alerts')
        alert_frequency = request.data.get('alert_frequency')
        
        if receive_alerts is not None:
            dashboard.receive_alerts = receive_alerts
        if alert_frequency:
            dashboard.alert_frequency = alert_frequency
        
        dashboard.save()
        
        return Response(
            {'message': 'Preferences updated successfully'},
            status=status.HTTP_200_OK
        )


# ============================================================================
# Resource ViewSet
# ============================================================================

class ResourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Resources.
    
    Manages educational resources including:
    - PDF documents
    - Video tutorials
    - Articles
    - Infographics
    - Interactive tools
    """
    queryset = Resource.objects.filter(is_published=True)
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type', 'language', 'is_featured', 'is_published']
    search_fields = ['title', 'description']
    ordering_fields = ['view_count', 'download_count', 'created_at']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination
    
    def retrieve(self, request, *args, **kwargs):
        """Get a resource and increment view count."""
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured resources.
        """
        featured = self.queryset.filter(is_featured=True)[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get resources grouped by type.
        """
        resource_type = request.query_params.get('type')
        if resource_type:
            resources = self.queryset.filter(resource_type=resource_type)
            serializer = self.get_serializer(resources, many=True)
            return Response(serializer.data)
        
        # Group by type
        result = {}
        for type_code, type_label in Resource.RESOURCE_TYPES:
            resources = self.queryset.filter(resource_type=type_code)
            if resources.exists():
                serializer = self.get_serializer(resources, many=True)
                result[type_label] = serializer.data
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def track_download(self, request, pk=None):
        """
        Track resource downloads.
        """
        resource = self.get_object()
        resource.download_count += 1
        resource.save()
        
        return Response({'download_count': resource.download_count})


# ============================================================================
# Search History ViewSet
# ============================================================================

class SearchHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Search History.
    
    Manages user search history including:
    - Track search queries
    - Store search filters
    - Record result counts
    - Analytics for user behavior
    """
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SearchHistory.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """
        Clear all search history for the current user.
        """
        self.get_queryset().delete()
        return Response(
            {'message': 'Search history cleared successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def popular_searches(self, request):
        """
        Get popular searches across all users.
        """
        popular = SearchHistory.objects.values('search_query').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response(popular)


# ============================================================================
# Feedback ViewSet
# ============================================================================

class FeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Feedback.
    
    Manages user feedback including:
    - Submit feedback on information quality
    - Rate helpfulness of content
    - Report inaccuracies or outdated information
    - Suggestions for improvement
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Feedback.objects.all()
        return Feedback.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_feedback(self, request):
        """
        Get feedback submitted by the current user.
        """
        feedback = self.get_queryset()
        serializer = self.get_serializer(feedback, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Mark feedback as resolved (admin only).
        """
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin privileges required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        feedback = self.get_object()
        feedback.is_resolved = True
        feedback.save()
        
        return Response({'message': 'Feedback marked as resolved'})


# ============================================================================
# Public API Views (Search and Statistics)
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    """
    Global search endpoint for pests and diseases.
    
    Query Parameters:
    - q: Search query string
    - crop: Filter by crop ID
    - category: Filter by category type
    - issue_type: Filter by issue type
    - severity: Filter by severity (high, medium, low)
    - page: Page number for pagination
    - page_size: Number of results per page
    """
    query = request.query_params.get('q', '')
    crop = request.query_params.get('crop', None)
    category = request.query_params.get('category', None)
    issue_type = request.query_params.get('issue_type', None)
    severity = request.query_params.get('severity', None)
    
    # Start with all active pests/diseases
    queryset = PestDisease.objects.filter(is_active=True)
    
    # Apply filters
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(scientific_name__icontains=query) |
            Q(local_names__icontains=query) |
            Q(description__icontains=query) |
            Q(symptoms__icontains=query)
        )
    
    if crop:
        try:
            queryset = queryset.filter(affects_crops__id=crop)
        except ValueError:
            pass
    
    if category:
        queryset = queryset.filter(category__category_type=category)
    
    if issue_type:
        queryset = queryset.filter(issue_type=issue_type)
    
    if severity:
        queryset = queryset.filter(severity=severity)
    
    # Order by relevance
    if query:
        queryset = queryset.annotate(
            relevance=Count('name')
        ).order_by('-relevance', 'name')
    else:
        queryset = queryset.order_by('name')
    
    # Save search history if user is authenticated
    if request.user.is_authenticated:
        SearchHistory.objects.create(
            user=request.user,
            search_query=query or 'global search',
            search_filters={
                'crop': crop,
                'category': category,
                'issue_type': issue_type,
                'severity': severity
            },
            results_count=queryset.count()
        )
    
    # Paginate results
    paginator = StandardResultsSetPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = PestDiseaseListSerializer(paginated_queryset, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def statistics(request):
    """
    Get platform-wide statistics.
    
    Returns:
    - Total counts of pests, diseases, crops, etc.
    - Top pests by outbreak frequency
    - Recent outbreaks
    - Active alerts
    """
    stats = {
        'total_pests': PestDisease.objects.filter(
            issue_type__in=['insect', 'mite', 'nematode'], 
            is_active=True
        ).count(),
        'total_diseases': PestDisease.objects.filter(
            issue_type__in=['fungal', 'bacterial', 'viral'], 
            is_active=True
        ).count(),
        'total_crops': Crop.objects.filter(is_active=True).count(),
        'active_outbreaks': OutbreakReport.objects.filter(
            status__in=['confirmed', 'ongoing']
        ).count(),
        'recent_alerts': EarlyWarningAlert.objects.filter(
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
            is_active=True
        ).count(),
        'total_resources': Resource.objects.filter(is_published=True).count(),
        'total_counties': County.objects.count(),
    }
    
    # Get top pests by outbreak count
    top_pests = PestDisease.objects.annotate(
        outbreak_count=Count('outbreaks')
    ).filter(outbreak_count__gt=0).order_by('-outbreak_count')[:5]
    
    stats['top_pests'] = PestDiseaseListSerializer(top_pests, many=True).data
    
    # Get recent outbreaks (last 30 days)
    recent_outbreaks = OutbreakReport.objects.filter(
        report_date__gte=timezone.now() - timezone.timedelta(days=30)
    )[:10]
    stats['recent_outbreaks'] = OutbreakReportSerializer(recent_outbreaks, many=True).data
    
    # Get critical alerts
    critical_alerts = EarlyWarningAlert.objects.filter(
        alert_level='critical',
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )[:5]
    stats['critical_alerts'] = EarlyWarningAlertSerializer(critical_alerts, many=True).data
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_stats(request):
    """
    Get statistics for dashboard widgets.
    
    Returns:
    - Pests/diseases grouped by severity
    - Outbreaks grouped by region
    - Recent activity metrics
    """
    stats = {
        'pests_by_severity': {
            'high': PestDisease.objects.filter(severity='high', is_active=True).count(),
            'medium': PestDisease.objects.filter(severity='medium', is_active=True).count(),
            'low': PestDisease.objects.filter(severity='low', is_active=True).count(),
        },
        'outbreaks_by_region': {},
        'recent_activity': {
            'new_outbreaks_last_week': OutbreakReport.objects.filter(
                report_date__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            'new_alerts_last_week': EarlyWarningAlert.objects.filter(
                issued_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            'new_resources_last_month': Resource.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30),
                is_published=True
            ).count(),
        }
    }
    
    # Get outbreaks by region
    regions = County.objects.exclude(region__isnull=True).exclude(region='').values_list('region', flat=True).distinct()
    for region in regions:
        if region:
            count = OutbreakReport.objects.filter(
                county__region=region,
                status__in=['confirmed', 'ongoing']
            ).count()
            stats['outbreaks_by_region'][region] = count
    
    # Add top affected counties
    top_counties = OutbreakReport.objects.filter(
        status__in=['confirmed', 'ongoing']
    ).values('county__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    stats['top_affected_counties'] = list(top_counties)
    
    return Response(stats)
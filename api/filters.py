import django_filters
from .models import PestDisease

class PestDiseaseFilter(django_filters.FilterSet):
    """Advanced filtering for PestDisease model"""
    
    min_severity = django_filters.ChoiceFilter(choices=PestDisease.SEVERITY_LEVELS, method='filter_min_severity')
    crops = django_filters.NumberFilter(field_name='affects_crops__id', lookup_expr='exact')
    category_type = django_filters.CharFilter(field_name='category__category_type', lookup_expr='exact')
    name_contains = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = PestDisease
        fields = {
            'severity': ['exact'],
            'issue_type': ['exact'],
            'damage_type': ['exact'],
            'is_emerging': ['exact'],
            'is_active': ['exact'],
        }
    
    def filter_min_severity(self, queryset, name, value):
        severity_order = {'low': 1, 'medium': 2, 'high': 3}
        if value:
            min_order = severity_order.get(value, 0)
            filtered_ids = []
            for obj in queryset:
                if severity_order.get(obj.severity, 0) >= min_order:
                    filtered_ids.append(obj.id)
            return queryset.filter(id__in=filtered_ids)
        return queryset
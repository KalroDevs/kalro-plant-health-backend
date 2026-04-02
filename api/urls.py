from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router
router = DefaultRouter()
router.register(r'crops', views.CropViewSet)
router.register(r'categories', views.ClassificationCategoryViewSet)
router.register(r'pests-diseases', views.PestDiseaseViewSet)
router.register(r'counties', views.CountyViewSet)
router.register(r'outbreaks', views.OutbreakReportViewSet)
router.register(r'management-practices', views.ManagementPracticeViewSet)
router.register(r'alerts', views.EarlyWarningAlertViewSet)
router.register(r'dashboard', views.UserDashboardViewSet, basename='dashboard')
router.register(r'resources', views.ResourceViewSet)
# Fixed: Added basename for SearchHistoryViewSet since it doesn't have a queryset attribute
router.register(r'search-history', views.SearchHistoryViewSet, basename='search-history')
router.register(r'feedback', views.FeedbackViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.search, name='search'),
    path('statistics/', views.statistics, name='statistics'),
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
]
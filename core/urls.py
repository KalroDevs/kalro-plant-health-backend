from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'economic-importance', views.EconomicImportanceViewSet)
router.register(r'identification-importance', views.IdentificationImportanceViewSet)
router.register(r'ipm-principles', views.IPMPrincipleViewSet)
router.register(r'pesticide-use', views.PesticideUseViewSet)
router.register(r'nutrient-deficiencies', views.NutrientDeficiencyViewSet)
router.register(r'environmental-factors', views.EnvironmentalFactorViewSet)
router.register(r'pest-categories', views.PestCategoryViewSet)
router.register(r'pests', views.PestViewSet)
router.register(r'diseases', views.DiseaseViewSet)
router.register(r'crops', views.CropViewSet)
router.register(r'crop-pests', views.CropPestViewSet)
router.register(r'crop-diseases', views.CropDiseaseViewSet)
router.register(r'control-methods', views.ControlMethodViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
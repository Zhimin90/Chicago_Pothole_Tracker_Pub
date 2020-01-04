from rest_framework import routers
from django.urls import path
from .api import T_PotholesViewSet
from . import views

router = routers.DefaultRouter()
router.register('api/world', T_PotholesViewSet, 'T_Potholes')
urlpatterns = [router.urls[0],
    path('api/geojson_density_map', views.get_density_map, name='geojson_densty_map')]
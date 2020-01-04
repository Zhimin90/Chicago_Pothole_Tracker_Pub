from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from django.core.serializers import serialize
from world.models import WorldBorder, T_Potholes, Density_Map
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from datetime import datetime
import ast

# Create your views here.
def get_density_map(request):
    try:
        getBound = ast.literal_eval(request.GET["Bounds"])
        bound = Polygon.from_bbox((getBound['_ne']['lng'],  getBound['_ne']['lat'], getBound['_sw']['lng'], getBound['_sw']['lat']))
        #print(bound)
    except:
        print("no parameters")
        bound = Polygon.from_bbox((-87.65797272125538,  41.95381335885449, -87.63888550483443, 41.97115012250981))
    #bound = Polygon.from_bbox((-87.65797272125538,  41.95381335885449, -87.63888550483443, 41.97115012250981))
    query = Density_Map.objects.filter(poly_coordinate__within = bound).filter(end_date__date__gte = datetime(2018, 11, 11), )
    geojson = serialize('geojson', query,  fields=('density','start_date','end_date', 'poly_coordinate'))
    return(HttpResponse(geojson))



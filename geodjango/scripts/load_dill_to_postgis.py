import os
import pandas as pd
import numpy as np
from world.models import Density_Map
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
import dill
import geopandas as gpd
from shapely.geometry import Polygon

CSV_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'

def run():

    f_in = open(CSV_PATH +'gdf_dissolved_2020.pkl', "rb")
    gdf_dissolved = dill.load(f_in)
    f_in.close()


    def applyInsert(geometry,start_d,end_d,density):
        geometry = GEOSGeometry(str(geometry))
        
        insert_row = Density_Map(start_date = start_d, end_date = end_d, poly_coordinate = geometry, density = density)
        insert_row.save()
    
    Density_Map.objects.all().delete()
    gdf_dissolved.apply(lambda row: applyInsert(row.geometry, row.start_date, row.end_date, row.density), axis=1)
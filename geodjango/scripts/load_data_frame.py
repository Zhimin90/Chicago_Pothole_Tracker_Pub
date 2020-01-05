import pandas as pd
from world.models import Density_Map
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from ast import literal_eval
import json

def run():
    Density_Map.objects.all().delete()
    filename = 'C:\\Users\\Zhimin90\\Documents\\CPT\\Geopandas\\2017-11-11_4_test.geojson'
    f = open(filename, 'r')
    geo_dict = json.load(f)

    for row in geo_dict['features']:
        geometry = GEOSGeometry(str(row['geometry']))
        start_d = row['properties']['start_date']
        end_d = row['properties']['end_date']
        density = row['properties']['density']
        
        insert_row = Density_Map(start_date = start_d, end_date = end_d, poly_coordinate = geometry, density = density)
        insert_row.save()
    '''
    df = pd.read_csv("C:\\Users\\Zhimin90\\Documents\\CPT\\CSV\\2017-11-11_4frames_test",converters={"poly_coordinate": literal_eval})

    Density_Map.objects.all().delete()

    for index, row in df.iterrows():
        #print((row['poly_coordinate'][0], row['poly_coordinate'][1], row['poly_coordinate'][3], row['poly_coordinate'][2],row['poly_coordinate'][0]))
        insert_row = Density_Map(start_date = row['start_date'],  end_date = row['end_date'], poly_coordinate = Polygon( ((row['poly_coordinate'][0][0], row['poly_coordinate'][0][1]), (row['poly_coordinate'][1][0], row['poly_coordinate'][1][1]), (row['poly_coordinate'][3][0], row['poly_coordinate'][3][1]), (row['poly_coordinate'][2][0], row['poly_coordinate'][2][1]), (row['poly_coordinate'][0][0], row['poly_coordinate'][0][1])) ), density = row['density'])
        insert_row.save()'''
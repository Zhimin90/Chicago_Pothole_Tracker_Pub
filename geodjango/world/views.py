from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from django.core.serializers import serialize
from world.models import WorldBorder, T_Potholes, Density_Map
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from datetime import datetime
import ast
import tensorflow as tf
import geopandas as gpd
import dill
import os
import pandas as pd
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from sodapy import Socrata


# Create your views here.
def get_density_map(request):
    print("got request")
    try:
        getBound = ast.literal_eval(request.GET["Bounds"])
        bound = Polygon.from_bbox((getBound['_ne']['lng'],  getBound['_ne']['lat'], getBound['_sw']['lng'], getBound['_sw']['lat']))
        print(bound)
    except:
        print("no parameters")
        bound = Polygon.from_bbox((-87.65797272125538,  41.95381335885449, -87.63888550483443, 41.97115012250981))
    #bound = Polygon.from_bbox((-87.65797272125538,  41.95381335885449, -87.63888550483443, 41.97115012250981))
    query = Density_Map.objects.filter(poly_coordinate__bboverlaps = bound).filter(end_date__date__gte = datetime(2018, 11, 10))
    #query = Density_Map.objects.filter(end_date__date__gte = datetime(2018, 11, 10), )
    #print(query)
    print("Serializing")
    geojson = serialize('geojson', query, geometry_field='poly_coordinate', fields=('density','start_date','end_date'))
    print("Done Serializing")
    return(HttpResponse(geojson))

def load_data_frame(request):
    print("loading DataFrame")

def get_points(request):
    print("getting raw points")
    previous_30days_date = (pd.datetime.now()- timedelta(days=30)).strftime('%Y-%m-%d')
    client = Socrata("data.cityofchicago.org", None)
    results = client.get("wqdh-9gek",order="request_date DESC",where="request_date > \"" + str(previous_30days_date)+"\"", limit=100000)

    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    test_df = results_df
    test_df.columns = pd.Series(test_df.columns).apply(lambda x: x.upper()).values
    xbound = (-87.9361,-87.5245)
    ybound = (41.6447,42.023)
    test_df = test_df[test_df.LATITUDE.notna()].sort_values(['REQUEST_DATE','COMPLETION_DATE'], ascending=[0,0])
    test_df['REQUEST_DATE'] = pd.to_datetime(test_df['REQUEST_DATE'])
    test_df['COMPLETION_DATE'] = pd.to_datetime(test_df['COMPLETION_DATE'])
    test_df['LATITUDE'] = pd.to_numeric(test_df['LATITUDE'])
    test_df['LONGITUDE'] = pd.to_numeric(test_df['LONGITUDE'])
    df = test_df
    map_arr = []
    interval_int = 30 #use 30 days data to predict next 7 days
    series_range = 7 #days
    time_interval = timedelta(days=interval_int)
    date_start = min(df['REQUEST_DATE'])
    date_end = max(df['REQUEST_DATE'])

    geo_price_map = df[['REQUEST_DATE', 'COMPLETION_DATE','LATITUDE', 'LONGITUDE']]
    filter1a = pd.to_numeric(geo_price_map["LONGITUDE"]) > xbound[0]
    filter1b = pd.to_numeric(geo_price_map["LONGITUDE"]) < xbound[1]
    filter1c = pd.to_numeric(geo_price_map["LATITUDE"]) > ybound[0]
    filter1d = pd.to_numeric(geo_price_map["LATITUDE"]) < ybound[1]
    print("sum of remaining is: " + str(sum(filter1a&filter1b&filter1c&filter1d)))
    geo_price_map = geo_price_map[filter1a&filter1b&filter1c&filter1d]

    for int_cur_date in range(0, 7, int(series_range)):
        geo_price_map_filtered = geo_price_map[geo_price_map['LONGITUDE'].notnull()]
        
        filter2 = geo_price_map_filtered['REQUEST_DATE'] > (date_end - timedelta(days=int_cur_date+interval_int))
        filter3 = geo_price_map_filtered['REQUEST_DATE'] <= (date_end -  timedelta(days=int_cur_date))
        
        print(date_end - timedelta(days=int_cur_date+interval_int))
        print(date_end -  timedelta(days=int_cur_date))
        
        geo_price_map_filtered = geo_price_map_filtered.where(filter2 & filter3)
        print("pothole count: " + str(len(geo_price_map_filtered.notnull().index)))
        print("_"*20)
        map_arr.append(geo_price_map_filtered)

    map_arr.reverse()

    last_30days_df = map_arr[-1]

    '''CSV_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
    f_in = open(CSV_PATH +'last_30days_df.pkl', "rb")
    df = dill.load(f_in)
    f_in.close()
    print(df) '''
    #serialize date first
    df['REQUEST_DATE'] = df['REQUEST_DATE'].dt.strftime(
        '%Y-%m-%d')
    df['COMPLETION_DATE'] = df['COMPLETION_DATE'].dt.strftime(
        '%Y-%m-%d')
        
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.LONGITUDE, df.LATITUDE))
    return(HttpResponse(gdf.to_json()))



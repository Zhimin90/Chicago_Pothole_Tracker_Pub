from apscheduler.schedulers.blocking import BlockingScheduler
import os
from world.models import Density_Map
from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
from sodapy import Socrata
import dill
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from KDEpy import FFTKDE, NaiveKDE
import rasterio
from rasterio.transform import Affine
from shapely.geometry import shape
from shapely.geometry import Polygon
from rasterio import features
import geopandas as gp
import dill

CSV_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'

def run():
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
    """
    last_30days_df = map_arr[-1]

    f = open(CSV_PATH +'last_30days_df.pkl', "wb")
    dill.dump(last_30days_df, file=f)
    f.close()
    """

    pothole_count = []
    for df in map_arr:
        pothole_count.append(df.count())

    def get_kde( x, y, xmin, xmax, ymin, ymax, xx, yy, positions):

        values = np.array([x, y]).T
        #values = values.reshape(values.shape[1], values.shape[0])
        #print("values is: " + str(values))
        #grid, points = get_kernel(values)
        points = get_kernel(values, positions)
        #kernel.set_bandwidth(bw_method=kernel.factor / 30.)
        f = np.reshape(points, xx.shape)
        #print(points.shape)
        #print(grid)
        #return grid, f
        return f

    def get_kernel(data, positions):
        #print(data.shape)
        #print(data)
        estimator = FFTKDE(kernel='gaussian', norm=2, bw=0.001)
        #grid, points = estimator.fit(data, weights=None).evaluate(grid_size)
        points = estimator.fit(data, weights=None).evaluate(positions)
        #grid, points = estimator.fit(data, weights=None).evaluate(grid_size)
        #kernel = gaussian_kde(dataset=values, bw_method="silverman" )
        #return grid, points
        return points

    grid_size = 1000
    density_matrix_t_series = []
    # Define the borders
    x = [-87.9361,-87.5245]
    y = [41.6447,42.023]
    deltaX = (max(x) - min(x))/10
    deltaY = (max(y) - min(y))/10
    xmin = min(x) - deltaX
    xmax = max(x) + deltaX
    ymin = min(y) - deltaY
    ymax = max(y) + deltaY

    xx, yy = np.mgrid[xmin:xmax:(grid_size*1j), ymin:ymax:(grid_size*1j)]
    positions = np.dstack([xx.ravel(), yy.ravel()])
    positions = positions.reshape(positions.shape[1], positions.shape[2])
    grid_matrix = positions

    for i, df in enumerate(map_arr):
        if df["LONGITUDE"].count() > 400:
            #grid, points = get_kde(df["LONGITUDE"].dropna().to_numpy(), df["LATITUDE"].dropna().to_numpy() , xmin, xmax, ymin, ymax, xx, yy, positions)
            points = get_kde(df["LONGITUDE"].dropna().to_numpy(), df["LATITUDE"].dropna().to_numpy() , xmin, xmax, ymin, ymax, xx, yy, positions)
            density_matrix_t_series.append(points)
            print("@" + str(i))

    s = round(len(density_matrix_t_series)*0)
    f_in = open(CSV_PATH +'Scalers_2020.pkl', "rb")
    scaler,scaler2 = dill.load(f_in)
    f_in.close()

    dm_series_np = np.array(density_matrix_t_series[s:])
    flattened_matrix_np = np.reshape(dm_series_np, (dm_series_np.shape[0]*dm_series_np.shape[1], dm_series_np.shape[2]))

    normalized_matrices_test = scaler2.transform(scaler.transform(flattened_matrix_np))
    y_test2 = normalized_matrices_test

    import tensorflow.keras as keras
    from tensorflow.keras.utils import get_file

    Model_Weight_URL = os.environ.get('Model_Weight_URL')
    weights_path = get_file(
            'TensorFlowModel_2020_train_save_my_weights.h5',
            Model_Weight_URL)

    with open(CSV_PATH + 'TensorFlowModel_2020_train_save_model_config.json') as json_file:
            json_config = json_file.read()
    model = keras.models.model_from_json(json_config)
    model.load_weights(weights_path)
    #model.load_weights(CSV_PATH + 'TensorFlowModel_2020_train_save_my_weights.h5')

    Last_time_frame = y_test2
    pred = model.predict(np.reshape(Last_time_frame,(Last_time_frame.shape[0],1,Last_time_frame.shape[1])))
    data = scaler.inverse_transform(scaler2.inverse_transform(pred))
    data_reshaped = data.reshape((int(data.shape[0]/data.shape[1]), data.shape[1], data.shape[1]))
    print(data_reshaped.shape)
    start_frame_date = min(map_arr[-1]['REQUEST_DATE'][map_arr[-1]['REQUEST_DATE'].notna()])
    end_frame_date = max(map_arr[-1]['REQUEST_DATE'][map_arr[-1]['REQUEST_DATE'].notna()])
    time_shift = 7 #days

    offset = yy.shape[0]
    print("offset = yy.shape[0]" + str(offset))
    xx = xx.ravel()
    yy = yy.ravel()
    xdelta = abs(xx[1] - xx[1+offset])
    ydelta = abs(yy[0] - yy[1+offset])
    print("xdelta"+str(xdelta))
    print("ydelta"+str(ydelta))
    columns = [ 'start_date', 'end_date', 'poly_coordinate', 'density']

    Matrix = np.rot90(np.flip(data_reshaped[0],1))
    max_density = np.max(Matrix)
    min_density = np.min(Matrix)
    Matrix = ((Matrix-min_density).astype(int)*10/(max_density - min_density)).astype('int32')
    Z = Matrix*25
    transform = rasterio.transform.from_bounds(min(xx), max(yy), max(xx), min(yy), Z.shape[1], Z.shape[0])

    results = ({'properties': {'raster_val': v}, 'geometry': s,'start_date':pd.to_datetime(start_frame_date) + timedelta(days=(time_shift*(1))),'end_date':pd.to_datetime(end_frame_date) + timedelta(days=(time_shift*(1)))}
            for i, (s, v)
            in enumerate(rasterio.features.shapes(Z,transform=transform)))

    geoms = list(results)
    gpd_polygonized_raster  = gp.GeoDataFrame.from_features(geoms)
    gpd_polygonized_raster["geometry"] = gpd_polygonized_raster["geometry"].simplify(0)
    gpd_polygonized_raster['start_date'] = pd.to_datetime(start_frame_date) + timedelta(days=(time_shift*(1)))
    gpd_polygonized_raster['end_date'] = pd.to_datetime(end_frame_date) + timedelta(days=(time_shift*(1)))
    gpd_polygonized_raster.rename(columns={'raster_val': 'density'}, inplace=True)

    f = open(CSV_PATH +'gdf_dissolved_2020.pkl', "wb")
    dill.dump(gpd_polygonized_raster, file=f)
    f.close()

    def applyInsert(geometry,start_d,end_d,density):
        geometry = GEOSGeometry(str(geometry))
        
        insert_row = Density_Map(start_date = start_d, end_date = end_d, poly_coordinate = geometry, density = density)
        insert_row.save()
    
    Density_Map.objects.all().delete()
    gpd_polygonized_raster.apply(lambda row: applyInsert(row.geometry, row.start_date, row.end_date, row.density), axis=1)


sched = BlockingScheduler()
@sched.scheduled_job('interval', minutes=25)
def timed_job():
    run()
    print('This job is run every 25 minute.')

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=0)
def scheduled_job():
    run()
    print('This job is run every weekday at midnight 12am.')

sched.start()
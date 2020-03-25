import os
import pandas as pd
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
import tensorflow.keras as keras
import geopandas as gpd
from shapely.geometry import Polygon

CSV_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'

def run():

    client = Socrata("data.cityofchicago.org", None)
    results = client.get("wqdh-9gek",order="request_date DESC", limit=100000)

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


    for int_cur_date in range(0, (date_end - date_start).days - interval_int, int(series_range)):
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

    for i, df in enumerate(map_arr[-5:]):
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
    x_test = normalized_matrices_test[0:-normalized_matrices_test.shape[1]].copy()
    y_test = normalized_matrices_test[normalized_matrices_test.shape[1]-1:-1].copy()

    x_test2 = np.reshape(x_test, (x_test.shape[0], 1, x_test.shape[1]))
    y_test2 = y_test 

    with open(CSV_PATH + 'TensorFlowModel_2020_train_save_model_config.json') as json_file:
        json_config = json_file.read()
    model = keras.models.model_from_json(json_config)
    model.load_weights(CSV_PATH + 'TensorFlowModel_2020_train_save_my_weights.h5')

    def predictor(model, data_in, grid, start_frame_date, end_frame_date, time_shift):
        xx, yy = grid
        offset = yy.shape[0]
        print("offset = yy.shape[0]" + str(offset))
        xx = xx.ravel()
        yy = yy.ravel()
        xdelta = abs(xx[1] - xx[1+offset])
        ydelta = abs(yy[0] - yy[1+offset])
        print("xdelta"+str(xdelta))
        print("ydelta"+str(ydelta))
        columns = [ 'start_date', 'end_date', 'poly_coordinate', 'density']
        
        pred = model.predict(data_in)
        data = scaler.inverse_transform(scaler2.inverse_transform(pred))
        data_reshaped = data.reshape((int(data.shape[0]/data.shape[1]), data.shape[1], data.shape[1]))
        print(data_reshaped.shape)
        #each cell is a density estimate from KDE that that has been aggregated by number of potholes over time
        #This time interval of density cell is input frame time + timeshift the target frame in the model that has shifted forward by
        
        row_dict = {'start_date' : None, 'end_date' : None, 'poly_coordinate': None, 'density': 0}
        #append = pd.DataFrame(columns=columns)
        dict_list = []
        for t, matrix in enumerate(data_reshaped):
            xy_matrix = np.flip(np.rot90(matrix),0)
            print(xy_matrix.shape)
            row_dict['start_date'] = pd.to_datetime(start_frame_date) + timedelta(days=(time_shift*(t+1)))
            row_dict['end_date'] = pd.to_datetime(end_frame_date) + timedelta(days=(time_shift*(t+1)))
            
            for i, row in enumerate(xy_matrix):
                for j, cell in enumerate(row):
                    pos_index = i + j*xy_matrix.shape[1]
                    #generate density cell (square) polycoordinate [[cxmin,cymin],[cxmax, cymin],[cxmin, cymax],[cxmax, cymax]]
                    row_dict['poly_coordinate'] = [[xx[pos_index],yy[pos_index]],[xx[pos_index]+xdelta,yy[pos_index]],[xx[pos_index]+xdelta,yy[pos_index]+ydelta], [xx[pos_index],yy[pos_index]+ydelta]]
                    row_dict['density'] = cell
                    dict_list.append(row_dict.copy())

        return pd.DataFrame(dict_list)

    Last_time_frame = y_test2[-(y_test2.shape[1]+1):-1]
    start_frame_date = min(map_arr[-1]['REQUEST_DATE'][map_arr[-1]['REQUEST_DATE'].notna()])
    end_frame_date = max(map_arr[-1]['REQUEST_DATE'][map_arr[-1]['REQUEST_DATE'].notna()])
    time_shift = 7 #days
    dataframe = predictor(model,np.reshape(Last_time_frame,(Last_time_frame.shape[0],1,Last_time_frame.shape[1])), (xx, yy), start_frame_date, end_frame_date, time_shift)

    df = dataframe
    max_density = max(df.density.astype(int))
    min_density = min(df.density.astype(int))
    df["int_density"] = (df.density.astype(int)*25/(max_density - min_density)).astype(int)

    list = []
    for index, row in df.iterrows():
        list.append( [row['start_date'],  row['end_date'],Polygon( row['poly_coordinate']), row['density'], row['int_density']] )

    gdf = gpd.GeoDataFrame(list, columns =['start_date','end_date', 'geometry', 'density', 'int_density'])
    xmin, ymin, xmax, ymax = gdf.total_bounds

    grid_size = 10
    xgrid = np.arange(xmin, xmax, (xmax-xmin)/grid_size)
    ygrid = np.arange(ymin, ymax, (ymax-ymin)/grid_size)
    print(xgrid,ygrid)

    c = 0
    gdf["zone"] = None
    for row in xgrid:
        for col in ygrid:
            boundbox = Polygon([[row,col],[row+(xmax-xmin)/grid_size,col],[row+(xmax-xmin)/grid_size,col+(ymax-ymin)/grid_size],[row,col+(ymax-ymin)/grid_size],[row,col]])
            bb_df = gpd.GeoSeries(boundbox)
            bool_within_bb = gdf.geometry.intersects(boundbox)
            index_within_bb = gdf[bool_within_bb].index
            gdf.iloc[index_within_bb,5] = c
            c+=1
            print(c)
            print("count rows within count: " + str(len(index_within_bb)))
            print("-"*25)

    gdf_dissolved = gdf.dissolve(by=['int_density','zone'])
    gdf_dissolved['geometry'] = gdf_dissolved['geometry'].simplify(0)
    
    f = open(CSV_PATH +'gdf_dissolved_2020.pkl', "wb")
    dill.dump(gdf_dissolved, file=f)
    f.close()

    def applyInsert(geometry,start_d,end_d,density):
        geometry = GEOSGeometry(str(geometry))
        
        insert_row = Density_Map(start_date = start_d, end_date = end_d, poly_coordinate = geometry, density = density)
        insert_row.save()
    
    Density_Map.objects.all().delete()
    gdf_dissolved.apply(lambda row: applyInsert(row.geometry, row.start_date, row.end_date, row.density), axis=1)
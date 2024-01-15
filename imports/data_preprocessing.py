import pandas as pd

from helper_functions import split_datetime

def merge_data(data, client, historical_weather,
        forecast_weather, electricity_prices, gas_prices, weather_station_to_county_mapping):
    '''
        This function merges all given DataFrames on the train or test data.
        The function checks first if the data_block_id is included in the data.
        parameter: all DataFrames we want to merge
        return: merged DataFrame
    '''
    has_dbid = False
    if "data_block_id" in data.columns:
        has_dbid = True

    merge_parameter = []
    if has_dbid:
        merge_parameter = ["data_block_id"]

    # Datatype conversion
    client.date = pd.to_datetime(client.date)

    ## Electricity Prices Data
    electricity_prices.forecast_date = pd.to_datetime(electricity_prices.forecast_date)
    electricity_prices.origin_date = pd.to_datetime(electricity_prices.origin_date)

    ## Forecast Weather Data
    forecast_weather.origin_datetime = pd.to_datetime(forecast_weather.origin_datetime)
    forecast_weather.forecast_datetime = pd.to_datetime(forecast_weather.forecast_datetime)

    ## Gas Prices Data
    gas_prices.forecast_date = pd.to_datetime(gas_prices.forecast_date)
    gas_prices.origin_date = pd.to_datetime(gas_prices.origin_date)

    ## Historical Weather Data
    historical_weather.datetime = pd.to_datetime(historical_weather.datetime)

    weather_station_to_county_mapping.latitude = weather_station_to_county_mapping.latitude.round(1)
    weather_station_to_county_mapping.longitude = weather_station_to_county_mapping.longitude.round(1)

    # round lat and long to avoid mismatching due to different accuracy
    historical_weather.latitude = historical_weather.latitude.astype("float").round(1)
    historical_weather.longitude = historical_weather.longitude.astype("float").round(1)

    # append '_client' to merged columns
    client.columns = [f"{column}_client" if column not in ['data_block_id', 'county', 'is_business', 'product_type'] else column for column in client.columns]
    # append _gas_prices to columns
    gas_prices.columns = [f"{column}_gas_prices" if column != 'data_block_id' else column for column in gas_prices.columns]
    # append electricity_prices to column names
    electricity_prices.columns = [f"{column}_electricity_prices" if column not in ['time_of_day','data_block_id'] else column for column in electricity_prices.columns]

    if "datetime" in data.columns:
        data.datetime = pd.to_datetime(data.datetime, format='%Y-%m-%d %H:%M:%S')
    else:
       data.prediction_datetime = pd.to_datetime(data.prediction_datetime, format='%Y-%m-%d %H:%M:%S')
       data["datetime"] = data["prediction_datetime"]

    #### Data Merging 

    ### Merge Client
    merge_on = ['county', 'is_business', 'product_type'] + merge_parameter
    merged_df = pd.merge(data, client, on=merge_on, how='left')

    ### Merge Gas Prices
    if has_dbid: 
        merged_df = pd.merge(merged_df, gas_prices, on=['data_block_id'], how='left')
    else:
        merged_df["lowest_price_per_mwh_gas_prices"] = gas_prices.lowest_price_per_mwh_gas_prices.min()
        merged_df["highest_price_per_mwh_gas_prices"] = gas_prices.highest_price_per_mwh_gas_prices.max()

    ### Merge Electricity Prices
    # add time column for merging with electricity data
    merged_df['time_of_day'] = merged_df['datetime'].dt.time
    # Merge electricity prices
    # the prices are available hourly -> create new column with time 
    electricity_prices['time_of_day'] = electricity_prices.forecast_date_electricity_prices.dt.time

    ### Merge Electricity Prices
    merge_on = ['time_of_day'] + merge_parameter
    # merge electricity_prices
    merged_df = pd.merge(merged_df, electricity_prices, on = merge_on, how='left')

    ### Merge Historical Weather   
    # get county and county_name from weather_station_to_county_mapping (merge on latitude and longitude)
    # merge historical weather to get counties
    merged_hist_weather = pd.merge(historical_weather, weather_station_to_county_mapping, on=['latitude', 'longitude'], how='left')
    # get time of day
    merged_hist_weather['time_of_day'] = merged_hist_weather['datetime'].dt.time

    # aggregate by county and time (summarize weather stations for same county)
    group_by = ['county', 'time_of_day', 'datetime'] + merge_parameter
    merged_hist_weather = merged_hist_weather.groupby(group_by).mean(numeric_only=True).reset_index()

    # append _hist_weather to column names
    merged_hist_weather.columns = [f"{column}_hist_weather" if column not in ['county', 'time_of_day','data_block_id'] else column for column in merged_hist_weather.columns]

    # merge to merged_df
    merge_on = ['time_of_day', 'county'] + merge_parameter
    merged_df = pd.merge(merged_df, merged_hist_weather, on=merge_on, how='left')

    ### Merge Forecast Weather

    #round lat and long
    forecast_weather.latitude = forecast_weather.latitude.astype("float").round(1)
    forecast_weather.longitude = forecast_weather.longitude.astype("float").round(1)

    # merge to get counties
    merged_forecast_weather = pd.merge(forecast_weather, weather_station_to_county_mapping, on=['latitude', 'longitude'], how='left')
    # merged_forecast_weather['time_of_day'] = merged_forecast_weather.

    # # aggregate for duplicate locations
    group_by = ['county', 'forecast_datetime'] + merge_parameter
    merged_forecast_weather = merged_forecast_weather.groupby(group_by).mean(numeric_only=True).reset_index()

    # append forecast_weather to column names
    merged_forecast_weather.columns = [f"{column}_forecast_weather" if column not in ['county', 'forecast_datetime','data_block_id'] else column for column in merged_forecast_weather.columns]

    # merge forecast_weather
    merge_on_left = ['datetime', 'county'] + merge_parameter
    merge_on_right = ['forecast_datetime', 'county'] + merge_parameter
    merged_df = pd.merge(merged_df, merged_forecast_weather, left_on=merge_on_left, right_on=merge_on_right, how='left')

    
    # split datetime into meaningful features of int types
    merged_df = split_datetime(merged_df)
    
    # mapping days of the week names and converting to categorical variable  ----- not working!!!!!???
    if 'day_of_week' in merged_df.columns:
        weekday_map = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'
        }
        merged_df['day_of_week'] = merged_df['day_of_week'].map(weekday_map).astype('category')
    
    # encode categories to category datetype
    merged_df['county'] = merged_df['county'].astype('category')
    merged_df['product_type'] = merged_df['product_type'].astype('category')

    merged_df['hour'] = merged_df['hour'].astype('category')

    return merged_df


def remove_col(merged_df, col_list=[]):        
    ### Drop Colums for modelling 
    # # model is not able to handle datetime
    model_df = merged_df.drop(merged_df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, EET]', "object"]).columns, axis=1)

    drop_columns = [
    'hours_ahead_forecast_weather',
    'row_id',
    'prediction_unit_id',
    'longitude_hist_weather',
    'longitude_forecast_weather',
    'latitude_hist_weather',
    'latitude_forecast_weather',
    'data_block_id'
    ] + col_list
    
    model_df.drop(drop_columns, axis=1, inplace=True)

    # drop na from target
    model_df.dropna(subset=['target'], inplace=True)    

    return model_df
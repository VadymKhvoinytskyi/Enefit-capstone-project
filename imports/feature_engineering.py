import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def add_daylight_col(merged_df):
    sunset = {1: 15, 2: 17, 3: 18, 4: 20, 5: 21, 6: 22, 7: 22, 8: 21, 9: 19, 10: 18, 11: 15, 12: 15}
    sunrise = {1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 9}
    merged_df["daylight"] = (merged_df["hour"].astype("int") >= merged_df["month"].apply(lambda x: sunrise[x])) & (merged_df["hour"].astype("int") <  merged_df["month"].apply(lambda x: sunset[x]))
    return merged_df

def add_capacity_col(merged_df):
    # Add new feature 'capacity_per_eic'
    merged_df["capacity_per_eic"] = np.round(merged_df["installed_capacity_client"] / merged_df["eic_count_client"], 2)
    merged_df["squared_capacity_client"] = merged_df["installed_capacity_client"].pow(2)
    #merged_df[["efficiency"]] = merged_df[["target"]][merged_df["installed_capacity_client"].notnull()] / merged_df[["installed_capacity_client"]][merged_df["installed_capacity_client"].notnull()]
    merged_df.drop("installed_capacity_client", axis=1, inplace=True)
    return merged_df

def basic_improvements(df):

    # Tryouts that dit not improve the results
    # dropping is_business: WORSE results
    # df_exp.drop('is_business', inplace=True, axis=1)
    # df_exp.drop(['county'], inplace=True, axis=1)


    # STEP 1: Improvement
    # dropping these two (assumption: cloudcover_total_hist_weather contains that info): slight improvements
    df.drop(['rain_hist_weather', 'snowfall_hist_weather'], inplace=True, axis=1)
    df.drop(['cloudcover_mid_hist_weather', 'cloudcover_high_hist_weather'], inplace=True, axis=1)


    # STEP 2: Improvment
    # Create a new column as the sum of the two columns representing cloud cover: better MAE for train
    # (but MAE train/test difference slightly larger)
    df['sum_column'] = df['cloudcover_total_hist_weather'] * df['diffuse_radiation_hist_weather']
    # Drop the original columns
    df.drop(['cloudcover_total_hist_weather', 'diffuse_radiation_hist_weather'], axis=1, inplace=True)

    # STEP 3: Improvement
    # Create a new column as the product of temperature_forecast_weather and dewpoint_forecast_weather
    df['temp_dew'] = df['temperature_forecast_weather'] * df['dewpoint_forecast_weather']
    # Drop the original columns
    df.drop(['temperature_forecast_weather', 'dewpoint_forecast_weather'], axis=1, inplace=True)

    return df


def add_public_holiday_col(merged_df):
    import requests

    # Set URL as url
    url = 'https://openholidaysapi.org/PublicHolidays?' # for public holidays

    parameters = {
        'countryIsoCode': 'EE', # not EST, thanks google.....
        'languageIsoCode': 'EN',
        'validFrom': '2021-09-01',
        'validTo': '2023-05-31'
    }
    # in terminal:
    #url = curl -X GET 'https://openholidaysapi.org/PublicHolidays?countryIsoCode=EST&languageIsoCode=EN&validFrom=2021-09-01&validTo=2023-05-31' -H 'accept: text/json' 

    # get request
    r = requests.get(url, parameters)

    # unpack nested json (name is nested)
    ee_holidays = pd.json_normalize(r.json(), sep='_',
                                    record_path='name',
                                    record_prefix='name_',
                                    meta=['id',
                                        'startDate', 'endDate',
                                        'type', 'nationwide'])

    # convert dates to datetimes
    ee_holidays['startDate'] = pd.to_datetime(ee_holidays['startDate'])
    ee_holidays['endDate'] = pd.to_datetime(ee_holidays['endDate'])

    # add datetime column to merged_df 
    merged_df['dateTime'] = pd.to_datetime(merged_df['year'].astype(str) + merged_df['day_of_year'].astype(str), format='%Y%j')

    # Check if dateTime appears in the range of startDate and endDate in ee_holidays
    # and add new is_public_holiday column
    merged_df['is_public_holiday'] = merged_df['dateTime'].between(ee_holidays['startDate'].min(), ee_holidays['endDate'].max()) & \
        merged_df['dateTime'].isin(ee_holidays['startDate']) | merged_df['dateTime'].isin(ee_holidays['endDate'])

    # remove dateTime column again
    merged_df.drop(columns='dateTime', axis=1, inplace=True)

    return merged_df



def add_school_holiday_col(merged_df):
    # doesn't recognize holidays between start and end date?
    import requests

    # Set URL as url
    url = 'https://openholidaysapi.org/SchoolHolidays?' # for public holidays

    parameters = {
        'countryIsoCode': 'EE', # not EST, thanks google.....
        'languageIsoCode': 'EN',
        'validFrom': '2021-09-01',
        'validTo': '2023-05-31'
    }
    # in terminal:
    #url = curl -X GET 'https://openholidaysapi.org/SchoolHolidays?countryIsoCode=EST&languageIsoCode=EN&validFrom=2021-09-01&validTo=2023-05-31' -H 'accept: text/json' 

    # get request
    r = requests.get(url, parameters)

    # unpack nested json (name is nested)
    ee_holidays = pd.json_normalize(r.json(), sep='_',
                                    record_path='name',
                                    record_prefix='name_',
                                    meta=['id',
                                        'startDate', 'endDate',
                                        'type', 'nationwide'])

    # convert dates to datetimes
    ee_holidays['startDate'] = pd.to_datetime(ee_holidays['startDate'])
    ee_holidays['endDate'] = pd.to_datetime(ee_holidays['endDate'])

    # add datetime column to merged_df 
    merged_df['dateTime'] = pd.to_datetime(merged_df['year'].astype(str) + merged_df['day_of_year'].astype(str), format='%Y%j')

    # Check if dateTime appears in the range of startDate and endDate in ee_holidays
    # and add new is_public_holiday column
    merged_df['is_school_holiday'] = merged_df['dateTime'].between(ee_holidays['startDate'].min(), ee_holidays['endDate'].max()) & \
        merged_df['dateTime'].isin(ee_holidays['startDate']) | merged_df['dateTime'].isin(ee_holidays['endDate'])

    # remove dateTime column again
    merged_df.drop(columns='dateTime', axis=1, inplace=True)

    return merged_df


def add_shifted_target(df:pd.DataFrame)->pd.DataFrame:
    # reintroduce the datetime column for merging
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day_of_month', 'hour']].rename(columns={'day_of_month' : 'day'}),format='%Y:%m:%d:%h')
    # make copy of the needed columns
    shifted_df = df[['county', 'is_business', 'product_type', 'is_consumption','datetime', 'target']].copy()
    # rename the target as shifted_target - that is the new column we want to add
    shifted_df.rename(columns={'target' : 'shifted_target'}, inplace=True)
    # shift the datetime by two days for our helper df
    shifted_df["datetime"] = shifted_df["datetime"] + pd.Timedelta(2, unit="days")
    # merge the shifted df to our original df - match the target of today to the day two days ahead 
    df = pd.merge(df, shifted_df, on= ['county', 'is_business', 'product_type', 'is_consumption','datetime'], how='left')
    # drop the datetime column again
    df.drop("datetime", axis=1, inplace=True)
    return df


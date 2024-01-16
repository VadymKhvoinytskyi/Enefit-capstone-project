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
    copy()

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
    df['sum_column'] = df_exp['cloudcover_total_hist_weather'] * df_exp['diffuse_radiation_hist_weather']
    # Drop the original columns
    df.drop(['cloudcover_total_hist_weather', 'diffuse_radiation_hist_weather'], axis=1, inplace=True)

    # STEP 3: Improvement
    # Create a new column as the product of temperature_forecast_weather and dewpoint_forecast_weather
    df['temp_dew'] = df_exp['temperature_forecast_weather'] * df_exp['dewpoint_forecast_weather']
    # Drop the original columns
    df.drop(['temperature_forecast_weather', 'dewpoint_forecast_weather'], axis=1, inplace=True)

    return df

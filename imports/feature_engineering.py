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
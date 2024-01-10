def split_datetime(data, col="datetime"):
    # Adding columns for date & time
    data['year']    = data[col].dt.year
    # data['quarter'] = data[col].dt.quarter
    data['month']   = data[col].dt.month
    data['week']    = data[col].dt.isocalendar().week
    data['hour']    = data[col].dt.hour 

    data['day_of_year']  = data[col].dt.day_of_year
    data['day_of_month'] = data[col].dt.day
    data['day_of_week']  = data[col].dt.day_of_week

    return data
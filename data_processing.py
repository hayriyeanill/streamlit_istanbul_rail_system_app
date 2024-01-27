"This module contains data cleaning and date processing."

import pandas as pd
import numpy as np


def analyze_null_values_line_frames(data: pd.DataFrame):
    """Analyze the null values in line frames"""
    lines = (data['line'].unique()).tolist()
    for line in lines:
        line_frame = data[data['line'] == line]
        if line_frame.isnull().sum().sum() > 0:
            print(line)
            print(line_frame.shape)
            print(line_frame.isnull().sum())
            

def drop_null_values_line_frames(data: pd.DataFrame):
    """Drop rows where station name is null in data frame."""
    print("Before dropping NaN values:", data.shape)
    data.dropna(subset=['station_name'], inplace=True)
    print("After dropping NaN values:", data.shape)


def process_date_features(data: pd.DataFrame):
    """Parse"""
    data.rename(columns={'transaction_year': 'year',
                        'transaction_month': 'month',
                        'transaction_day': 'day'}, inplace=True)

    data['date'] = pd.to_datetime(data[['year', 'month', 'day']],
                                format='%Y-%m-%d')
    data['month'] = data['date'].dt.month_name()
    data['week'] = data['date'].dt.isocalendar().week
    data['week_number'] = (data['date'].dt.day - 1) // 7 + 1
    data['day_of_week'] = data['date'].dt.day_name()
    data['weekend_status'] =  np.where(data['date'].dt.weekday > 4, 1, 0)
    return data


def data_processing(data: pd.DataFrame):
    """Apply data processing to data frame."""
    drop_null_values_line_frames(data)
    data = process_date_features(data)
    return data
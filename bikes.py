import pandas as pd
import numpy as np

from datetime import datetime
from os import listdir, getcwd
from os.path import isfile, join, dirname


class Bikes:

    @staticmethod
    def retrieve_data():
        path = getcwd() + '/data_hourly/'

        all_files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]

        df = pd.DataFrame()
        df = pd.concat((pd.read_csv(f, encoding='utf8', engine='python', sep=';', index_col=0) for f in all_files))
        df['total_slots'] = df.empty_slots + df.free_bikes
        df['usage_ratio'] = df.empty_slots / df.total_slots
        df['datetime'] = pd.DatetimeIndex(df['timestamp'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['weekday'] = df['datetime'].apply(lambda x: x.weekday())
        df = df.drop('extra', axis=1)
        print(df.info())
        #Extract stations, min and max dates
        stations = pd.DataFrame(df[:255], columns=['id', 'name', 'latitude', 'longitude'])
        min_date = min(df['timestamp'])
        max_date = max(df['timestamp'])
        return df, stations, min_date, max_date

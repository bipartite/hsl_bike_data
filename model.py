import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from pandas.plotting import autocorrelation_plot
from bikes import Bikes


df, stations, min_date, max_date = Bikes.retrieve_data()

grouped_df = df.groupby(['weekday', df.timestamp.dt.hour]).apply(pd.DataFrame.sort_values, 'usage_ratio', ascending=False)
# sorted_df = pd.DataFrame(grouped_df.mean().reset_index())

# g = sorted_df['usage_ratio'].groupby(level=0, group_keys=False)
# res = g.apply(lambda x: x.order(ascending=False))
print(grouped_df.loc[(grouped_df.weekday == 0) & (grouped_df.timestamp.dt.hour == 0), ['name', 'usage_ratio']])

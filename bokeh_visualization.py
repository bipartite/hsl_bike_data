import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

from os import listdir
from os.path import isfile, join, dirname
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, Div, HoverTool
from bokeh.models.widgets import Slider, Select, TextInput, DateRangeSlider
from bokeh.io import curdoc
from bokeh.models.annotations import Title
from bokeh.models.callbacks import CustomJS

from bikes import Bikes

df, stations, min_date, max_date = Bikes.retrieve_data()
stations_names = stations.name.tolist()

path = os.getcwd()
filename = "bike_meter.html"

desc = Div(text=open(join(path, filename)).read(), width=800)

axis_map = {
    "empty_slots": "empty_slots",
    "free_bikes": "free_bikes",
    "total_slots": "total_slots",
    "usage_ratio": "usage_ratio"
}

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[]))
source_mon = ColumnDataSource(data=dict(time=[], y_value=[]))
source_tue = ColumnDataSource(data=dict(time=[], y_value=[]))
source_wed = ColumnDataSource(data=dict(time=[], y_value=[]))
source_thu = ColumnDataSource(data=dict(time=[], y_value=[]))
source_fri = ColumnDataSource(data=dict(time=[], y_value=[]))
source_sat = ColumnDataSource(data=dict(time=[], y_value=[]))
source_sun = ColumnDataSource(data=dict(time=[], y_value=[]))


# Create Input controls
station_name = Select(title="Select station", value="Varsapuistikko", options=stations_names)
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="empty_slots")
date_range_slider = DateRangeSlider(title="Date Range: ", start=min_date, end=max_date, value=(min_date, max_date), step=1)


p = figure(x_axis_type="datetime", plot_height=300, plot_width=500, title="", tools="", toolbar_location=None)
p_mon = figure(plot_height=200, plot_width=400, toolbar_location=None, tools="")
p_tue = figure(plot_height=200, plot_width=400, toolbar_location=None, tools="")
p_wed = figure(plot_height=200, plot_width=400, toolbar_location=None, tools="")
p_thu = figure(plot_height=200, plot_width=400, toolbar_location=None, tools="")
p_fri = figure(plot_height=200, plot_width=400, toolbar_location=None, tools="")
p_sat = figure(plot_height=200, plot_width=400, toolbar_location=None, tools="")
p_sun = figure(plot_height=200, plot_width=400, toolbar_location=None, tools="")


p.step(x='x', y='y', source=source, line_width=2, mode="center")
p_mon.line(x='time', y='y_value', source=source_mon, line_width=2)
p_tue.line(x='time', y='y_value', source=source_tue, line_width=2)
p_wed.line(x='time', y='y_value', source=source_wed, line_width=2)
p_thu.line(x='time', y='y_value', source=source_thu, line_width=2)
p_fri.line(x='time', y='y_value', source=source_fri, line_width=2)
p_sat.line(x='time', y='y_value', source=source_sat, line_width=2)
p_sun.line(x='time', y='y_value', source=source_sun, line_width=2)

def select_station():
    station_val = station_name.value
    date_start, date_end = date_range_slider.value_as_datetime
    selected = df[(df.name == station_val)
                & (df['timestamp'].map(lambda x: x >= date_start))
                & (df['timestamp'].map(lambda x: x <= date_end))]
    selected.set_index('datetime', inplace=True)
    selected = selected.sort_index()

    print(selected.head())
    return selected, station_val


def update():
    selected, station = select_station()
    x_name = 'timestamp'
    y_name = axis_map[y_axis.value]

    p_mon.title.text = y_name + ' on mondays'
    p_tue.title.text = y_name + ' on tuesdays'
    p_wed.title.text = y_name + ' on wednesdays'
    p_thu.title.text = y_name + ' on thursdays'
    p_fri.title.text = y_name + ' on fridays'
    p_sat.title.text = y_name + ' on saturdays'
    p_sun.title.text = y_name + ' on sundays'

    p.yaxis.axis_label = y_axis.value

    bikes_hourly_mon = selected[selected.timestamp.dt.weekday == 0].groupby([selected.timestamp.dt.hour])[y_name].mean()
    bikes_hourly_tue = selected[selected.timestamp.dt.weekday == 1].groupby([selected.timestamp.dt.hour])[y_name].mean()
    bikes_hourly_wed = selected[selected.timestamp.dt.weekday == 2].groupby([selected.timestamp.dt.hour])[y_name].mean()
    bikes_hourly_thu = selected[selected.timestamp.dt.weekday == 3].groupby([selected.timestamp.dt.hour])[y_name].mean()
    bikes_hourly_fri = selected[selected.timestamp.dt.weekday == 4].groupby([selected.timestamp.dt.hour])[y_name].mean()
    bikes_hourly_sat = selected[selected.timestamp.dt.weekday == 5].groupby([selected.timestamp.dt.hour])[y_name].mean()
    bikes_hourly_sun = selected[selected.timestamp.dt.weekday == 6].groupby([selected.timestamp.dt.hour])[y_name].mean()

    source.data = dict(
        x=selected[x_name],
        y=selected[y_name]
    )
    source_mon.data = dict(
        time=bikes_hourly_mon.index,
        y_value=bikes_hourly_mon
    )
    source_tue.data = dict(
        time=bikes_hourly_tue.index,
        y_value=bikes_hourly_tue
    )
    source_wed.data = dict(
        time=bikes_hourly_wed.index,
        y_value=bikes_hourly_wed
    )
    source_thu.data = dict(
        time=bikes_hourly_thu.index,
        y_value=bikes_hourly_thu
    )
    source_fri.data = dict(
        time=bikes_hourly_fri.index,
        y_value=bikes_hourly_fri
    )
    source_sat.data = dict(
        time=bikes_hourly_sat.index,
        y_value=bikes_hourly_sat
    )
    source_sun.data = dict(
        time=bikes_hourly_sun.index,
        y_value=bikes_hourly_sun
    )


controls = [station_name, y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed' # 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [p_mon, p_sat, p, inputs],
    [p_tue, p_sun],
    [p_wed],
    [p_thu],
    [p_fri]
], sizing_mode=sizing_mode)

update()

curdoc().add_root(l)
curdoc().title = "Stations"
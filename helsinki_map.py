import fiona
from mpl_toolkits.basemap import Basemap
import pandas as pd
from shapely.geometry import Polygon, Point, MultiPoint, MultiPolygon
from shapely.prepared import prep
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
from descartes import PolygonPatch

from bikes import Bikes

data, stations, min_date, max_date = Bikes.retrieve_data()

def points_per_poly(poly, points):
    poly = prep(poly)
    return int(len(list(filter(poly.contains, points))))

def create_map():
    shp = fiona.open("./Kaupunginosajako/KaupunginosajakoPolygon_WGS84.shp") # helsinki districts shapefile
    coords = shp.bounds         # Extract the bound coordinates from the shapefile
    shp.close()

    fig, ax = plt.subplots(figsize=(8,8))  # figure and axis objects
    m = Basemap(
        projection='tmerc', ellps='WGS84', # set transverse mercator proj. and ellipsoid
        lon_0=(coords[0] + coords[2]) / 2, # longitude center
        lat_0=(coords[1] + coords[3]) / 2, # latitude center
        llcrnrlon=coords[0],    # left lower corner
        llcrnrlat=coords[1],
        urcrnrlon=coords[2],    # upper right corner
        urcrnrlat=coords[3] ,
        resolution='c',  suppress_ticks=True
        )

    m.readshapefile("./Kaupunginosajako/KaupunginosajakoPolygon_WGS84", name='helsinki', drawbounds=True, color='blue')

    df_map = pd.DataFrame( {
        "poly": [Polygon(xy) for xy in m.helsinki],
        "district": [x["nimi_fi"] for x in m.helsinki_info ]
        })
    df_map["area_km"] = df_map["poly"].map(lambda x: x.area / 1000)

    map_points = [Point(m(x,y)) for x,y
                    in zip(stations.longitude, stations.latitude)] # Convert Data Points to projection, then to Shapely
    all_points = MultiPoint(map_points)
    district_poly = prep(MultiPolygon(list(df_map.poly.values )))
    all_points = list(filter(district_poly.contains, all_points)) # Select only points within map boundaries

    df_map["bikes_count"] = df_map.poly.apply(points_per_poly, args=(all_points,) )
    df_map["bikes_per_area"] = df_map.bikes_count / df_map.area_km
    df_map.patch = df_map.poly.map(lambda x: PolygonPatch(x))
    pc = PatchCollection(df_map.patch, match_original=False, zorder=2)

    pc.set(array=df_map.bikes_per_area.values, cmap='Reds') # impose color map onto patch collection
    fig.colorbar(pc, label="Bike density")  # Draw Colorbar and display the measure
    ax.add_collection(pc)                   # add patchcollection to axis

    centroids = df_map["poly"].map(lambda x: x.centroid) # get center of each polygon
    for i, (point, label) in enumerate(zip(centroids, df_map.district)):
        if df_map.loc[i, "bikes_per_area"] > df_map.bikes_per_area.quantile(0.05):
            ax.text(point.x, point.y, label, ha='center', size=8) # plot text in center

    plt.show()

def main():
    create_map()

if __name__ == '__main__':
    main()
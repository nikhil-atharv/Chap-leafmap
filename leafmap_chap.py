import leafmap.foliumap as leafmap

import geopandas
import os

gpd_file_path = os.path.join('Chapurapalli/Boundary.gpkg')

boundary = geopandas.read_file(gpd_file_path)
roi = boundary.geometry
print(boundary.crs)
geom = boundary.geometry.unary_union.__geo_interface__

import pystac_client
import planetary_computer

catalog = pystac_client.Client.open(
    url = "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier = planetary_computer.sign_inplace
)

search = catalog.search(
    collections=['sentinel-2-l2a'],
    datetime='2025-03-01/2025-03-30',
    query={'eo:cloud_cover': {'lt': 5}},
    intersects = geom,
    sortby='eo:cloud_cover'
)

items = search.get_all_items()
selected_image = items[0]

import xrspatial
import rioxarray
import xarray
import stackstac
import rasterio

stacked = stackstac.stack(selected_image, epsg=4326)
clipped = stacked.rio.clip(roi)
clipped_med = clipped.median('time', keep_attrs=True)
clipped2 = clipped_med.sel(band = ['B01'])
clipped2.rio.to_raster('clipped_chap.tif')

raster = rioxarray.open_rasterio('clipped_chap.tif')

import folium
import localtileserver

m = leafmap.Map()
m.add_basemap("HYBRID")

m.add_raster(raster)

m.to_streamlit()





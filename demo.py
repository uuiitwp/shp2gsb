# coding:utf-8
from shp2gsb import shp2gsb

"""
指定shp中改正字段
To spacify the shapefile grid-shift fields
"""

shp2gsb.DB_NE = "DB_东北"
shp2gsb.DB_NW = "DB_西北"
shp2gsb.DB_SE = "DB_东南"
shp2gsb.DB_SW = "DB_西南"
shp2gsb.DL_NE = "DL_东北"
shp2gsb.DL_NW = "DL_西北"
shp2gsb.DL_SE = "DL_东南"
shp2gsb.DL_SW = "DL_西南"


# shp2gsb.write(grid_shift_shapefile, gsb_file_output_path)
shp2gsb.write(r'c:\grid.shp', r'c:\a.gsb')


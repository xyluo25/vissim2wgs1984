# -*- coding:utf-8 -*-
##############################################################
# Created Date: Sunday, February 18th 2024
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################
from __future__ import absolute_import
from vissim2geojson import vissim2wgs1984

file_inpx = "./vissim_data/xl_002.inpx"
file_fhz = "./vissim_data/xl_002_001.fhz"
file_fzp = "./vissim_data/xl_002_001.fzp"
file_folder = "./vissim_data"

# prepare map reference data from Vissim
x_refmap = -9772791.018
y_refmap = 5317836.791
x_refnet = 0
y_refnet = 0

# for covert fzp files, if you don't need to convert fzp file, leave these value to default values.
x_col_name = "POS"
y_col_name = "POSLAT"

# using vissim folder as input path, will generate four files: inpx.geojson, fzp.geojson, fzp.csv, fhz.csv.
# all result files will save to the same folder as the input folder.
vissim = vissim2wgs1984(file_folder, x_refmap, y_refmap, x_refnet, y_refnet, x_col_name, y_col_name)

vissim.main()
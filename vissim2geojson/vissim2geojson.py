# -*- coding:utf-8 -*-
##############################################################
# Created Date: Tuesday, June 14th 2022
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################

import contextlib
import pandas as pd
import xml.etree.ElementTree as ET
from geojson import MultiLineString, Feature, FeatureCollection, dump
import warnings
from geopandas import GeoDataFrame
from shapely.geometry import Point
from os import listdir
from os.path import isfile, join, isdir
import math

from pyufunc import get_filenames_by_ext, func_running_time
from pathlib import Path


class vissim2wgs1984:
    """A tool to convert vissim files to geojson and csv.
    specifically:
        convert .inpx file to geojson file
        convert .fzp file to geojson and csv files
        convert .fhz file to csv file

    Args:
        vissim_file_path (str): the folder or file path to the vissim file
        x_refmap (float, optional): coordinates of the reference point of the background map(Mercator). Defaults to -9772674.016.
        y_refmap (float, optional): coordinates of the reference point of the background map(Mercator). Defaults to 5317775.409.
        x_refnet (int, optional): coordinates of the reference point of the network(Cartesian Vissim System). Defaults to 0.
        y_refnet (int, optional): coordinates of the reference point of the network(Cartesian Vissim System). Defaults to 0.
        x_col_name (str, optional): the longitude column name in fzp file to convert fzp file to geojson. Defaults to "POS".
        y_col_name (str, optional): the latitude column name in fzp file to convert fzp file to geojson. Defaults to "POSLAT".

    Methods:
        vissim_fzp(path_vissim_fzp: str, x_col_name: str = "POS", y_col_name: str = "POSLAT") -> None:
            Convert .fzp file to geojson and csv files.

        dataframe2geojson() -> None:
            Convert dataframe to geojson.

        vissim_fhz(path_vissim_fhz: str) -> None:
            Convert .fhz file to csv file.

        main() -> None:
            Main function to convert vissim files to geojson and csv.

    """

    print("Please check and correctly input x_refmap, y_refmap, x_refnet and y_refnet from your vissim software!")

    def __init__(self,
                 vissim_file_path: str,
                 x_refmap: float = -9772674.016,
                 y_refmap: float = 5317775.409,
                 x_refnet: float = 0,
                 y_refnet: float = 0,
                 x_col_name: str = "POS",
                 y_col_name: str = "POSLAT"):

        # TDD: test the inputs of the vissim2geojson
        assert isinstance(vissim_file_path, str), "The input vissim_file_path should be a string."
        assert isdir(vissim_file_path), "The input vissim_file_path should be a folder."

        self.vissim_file_path = self.__allFiles(vissim_file_path)
        print("Input files: ", self.vissim_file_path)

        self.x_refmap = x_refmap
        self.y_refmap = y_refmap
        self.x_refnet = x_refnet
        self.y_refnet = y_refnet
        self.x_col_name = x_col_name
        self.y_col_name = y_col_name

        # The class automatically return files in certain folder
        # self.main()

    # This return all files in a folder or subfolder or single file
    def __allFiles(self, path: str, view_files=False) -> list:

        # files = []

        # def readFiles(path):
        #     if isfile(path):
        #         files.append(path)
        #     elif isdir(path):
        #         for f in listdir(path):
        #             if isfile(join(path, f)):
        #                 files.append(join(path, f))
        #             if isdir(join(path, f)):
        #                 readFiles(join(path, f))
        #     else:
        #         print("Invalid Input Path!")
        #     return files
        file_names = [Path(each_path) for each_path in get_filenames_by_ext(path, file_ext="*")]

        if view_files:
            print(file_names)
        return file_names

    def __vissim2wgs1984(self, x_vissim: float, y_vissim: float) -> list:

        # ##This is a function that transfer a single vissim x,y coordinate date into wgs1984 x,y format######

        # Local coordinates in PTV Vissim use a cartesian coordinate system with a reference to a background position in Mercator coordinates.

        # coordinates of the point to be converted(Cartesian Vissim System)
        # x_vissim , y_vissim = -0.255, 39.368

        # coordinates of the reference point of the network(Cartesian Vissim System)
        # x_refnet, y_refnet = -56.556, -2.045

        # coordinates of the reference point of the background map(Mercator)
        # x_refmap, y_refmap = -9772199.101, 5317834.498

        Pi = 3.14159265358979  # vissim system
        Pi_this = 3.14159265358979323846264338  # our detailed pi
        EarthRadius = 6378137  # vissim system earth radius

        # CorrectionFactorMercator, the correction factor is required for transforming the latitude of a sphere(Mercator) to the WGS 84 ellipse.
        CorrectionFactorMercator = 1.001120232
        # CorrectionFactorMercator = 1.0011202320000001

        # LatitudeRefPointMap  # WGS84 latitude coordinate for the reference point map.  Base map -> Network Setting -> Display
        LatitudeRefPointMap = (
            2 * math.atan(math.exp(CorrectionFactorMercator * self.y_refmap / EarthRadius)) - Pi_this / 2) / (Pi_this / 180)

        LocalScale = 1 / math.cos(LatitudeRefPointMap * Pi_this / 180)

        # MercatorXFront  #Mercator coordinate X of the front of the vehicle
        MercatorX = (x_vissim - self.x_refnet) * \
            LocalScale + self.x_refmap
        MercatorY = (y_vissim - self.y_refnet) * \
            LocalScale + self.y_refmap

        a_cor = CorrectionFactorMercator
        r = EarthRadius
        # a_cor and r represents ???   经度
        Longitude = a_cor * MercatorX / (Pi * r / 180)
        Latitude = (2 * math.atan(math.exp(CorrectionFactorMercator *
                                           MercatorY / EarthRadius)) - Pi / 2) / (Pi / 180)  # 维度

        return [Longitude, Latitude]

    def __get_link(self, path_vissim_inpx: str) -> list:
        with open(path_vissim_inpx, "r") as f:
            xmlstring = f.read()
        f.close()

        tree = ET.ElementTree(ET.fromstring(xmlstring))
        root = tree.getroot()
        return root.findall("links")[0]

    def __link_vissim2wgs(self):
        link_data = []
        link_data1 = []  # original x,   y multistring data
        link_data2 = []  # transfered x, y multistring data

        for i in range(len(self.link)):
            temp = []
            temp1 = []  # original single x,   y data
            temp2 = []  # transfered single x, y data
            for j in range(len(self.link[i])):
                for k in range(len(self.link[i][j])):
                    with contextlib.suppress(Exception):
                        for m in range(len(self.link[i][j][k])):
                            temp.extend((self.link[i][j][k][m].attrib["x"], self.link[i][j][k][m].attrib["y"], self.link[i][j][k][m].attrib["zOffset"]))
                            temp1.append((float(self.link[i][j][k][m].attrib["x"]), float(self.link[i][j][k][m].attrib["y"])))
                            temp2.append(self.__vissim2wgs1984(float(self.link[i][j][k][m].attrib["x"]), float(self.link[i][j][k][m].attrib["y"])))
                    with contextlib.suppress(Exception):
                        temp.append(self.link[i][j][k].attrib["width"])
            link_data.append(temp)
            link_data1.append(temp1)  # link original
            link_data2.append(temp2)  # link transfered
        # df = pd.DataFrame(link_data)
        return link_data, link_data1, link_data2


    @func_running_time
    def vissim_fzp(self, path_vissim_fzp: str, x_col_name: str = "POS", y_col_name: str = "POSLAT") -> None:
        df_fzp = ""
        with open(path_vissim_fzp, 'rb') as ff:
            df_fzp = pd.DataFrame(ff.readlines())
        ff.close()
        fzp_date = str(df_fzp.iloc[3, :])  # Get the vissim running time(date)

        start_fzp = next((i for i in range(len(df_fzp)) if str(df_fzp.iloc[i, 0])[3:10] == "VEHICLE"), 0)

        # fzp file starts from start_fzp(row 28)
        vissim_fzpdata = df_fzp.iloc[start_fzp:]
        fzp_data = pd.DataFrame([str(jj).split(';') for jj in vissim_fzpdata.iloc[:, 0]])

        columns_pre = []
        columns_pre = list(fzp_data.iloc[0])
        for i in columns_pre:
            if "\\r\\n'" in i:
                columns_pre[columns_pre.index(i)] = i[:-5]

        fzp_data.columns = columns_pre

        fzp_data = fzp_data.iloc[1:]
        fzp_data = fzp_data.reset_index(drop=True)
        fzp_data.iloc[:, 0] = [i.split("'")[1] for i in fzp_data.iloc[:, 0]]

        fzp_data.iloc[:, 0] = fzp_data.iloc[:, 0].astype(float)

        fzp_data["datetime"] = pd.to_datetime(fzp_date.split("\\")[0].split(
            "Date: ")[1]) + pd.to_timedelta(fzp_data.iloc[:, 0], unit='s')

        fzp_data[y_col_name] = fzp_data[y_col_name].apply(lambda x: x[:-5])
        # print(fzp_data.head(10))

        for coor in range(len(fzp_data[x_col_name])):
            # "COORDREARX"
            with contextlib.suppress(Exception):
                fzp_data.loc[coor, f"{x_col_name}_wgs"], fzp_data.loc[coor, f"{y_col_name}_wgs"] = self.__vissim2wgs1984(float(fzp_data.loc[coor, x_col_name]), float(fzp_data.loc[coor, y_col_name]))

        self.fzp_data = fzp_data
        self.x_col_name_lonlat = f"{x_col_name}_wgs"
        self.y_col_name_lonlat = f"{y_col_name}_wgs"

    @func_running_time
    def dataframe2geojson(self) -> None:
        df = self.fzp_data
        geometry = [Point(xy) for xy in zip(df[self.x_col_name_lonlat], df[self.y_col_name_lonlat])]
        # http: //www.spatialreference.org/ref/epsg/2263/

        geo_df = GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)  # geometry=geometry
        geo_df.to_file(self.output_filename, driver="GeoJSON")
        df.to_csv(self.output_filename, index=False)
        # geo_df.to_file(driver='ESRI Shapefile', filename='data.shp')

    @func_running_time
    def vissim_fhz(self, path_vissim_fhz: str) -> None:

        with open(path_vissim_fhz, 'rb') as f:
            df_fhz = pd.DataFrame(f.readlines())
        f.close()
        fhz_date = str(df_fhz.iloc[5, :])
        start_fhz = next((i for i in range(len(df_fhz)) if str(df_fhz.iloc[i, :])[11:15] == "Time"), 0)

        vissim_fhzdata = df_fhz.iloc[start_fhz:]  # fhz file starts from row 8
        fhz_data = pd.DataFrame([str(jj).split(';') for jj in vissim_fhzdata.iloc[:, 0]])
        fhz_data.columns = fhz_data.iloc[0]
        fhz_data = fhz_data.iloc[1:]
        fhz_data = fhz_data.reset_index(drop=True)
        for j in range(len(fhz_data.iloc[:, 0])):
            fhz_data.iloc[j, 0] = str(fhz_data.iloc[j, 0]).split("'")[1]

        fhz_data.iloc[:, 0] = fhz_data.iloc[:, 0].astype(float)
        fhz_data["datetime"] = pd.to_datetime(fhz_date.split("Name")[0].split(
            "Date:")[1].lstrip()) + pd.to_timedelta(fhz_data.iloc[:, 0], unit="s")

        self.fhz_data = fhz_data

    @func_running_time
    def main(self):
        # #####save geojson data to geojson file ######

        for i in self.vissim_file_path:
            if i.suffix == ".inpx":
                print("############## Begin to process inpx file! ######################\n")
                self.output_filename = i.with_suffix(".geojson")
                self.link = self.__get_link(i)
                self.vissimLayer, self.vissim_xy, self.wgs1984_lonlat = self.__link_vissim2wgs()

                self.__multilines = MultiLineString([[(3.75, 9.25), (-130.95, 1.52)], [(
                    23.15, -34.25), (-1.35, -4.65), (3.45, 77.95)]])  # doctest: +ELLIPSIS

                self.__multilines["coordinates"] = self.wgs1984_lonlat
                feature = Feature(geometry=self.__multilines)
                feature_collection = FeatureCollection([feature])
                with open(self.output_filename, 'w') as f:
                    dump(feature_collection, f)
                    # f.write(str(self.__multilines))
                f.close()
                print(f"\nSuccessfully Save inpx file to geojson: {self.output_filename}\n")

            elif i.suffix == ".fzp":
                print("############## Begin to process fzp file! ######################\n")
                self.output_filename = i.with_suffix(".geojson")
                self.vissim_fzp(i, self.x_col_name, self.y_col_name)
                self.dataframe2geojson()
                print(f"Successfully Save fzp file to geojson: {self.output_filename}\n")

            elif i.suffix == ".fhz":
                print("############## Begin to process fhz file! ######################\n")
                self.output_filename = i.with_suffix(".csv")
                self.vissim_fhz(i)
                self.fhz_data.to_csv(
                    self.output_filename, header=True, index=False, encoding="utf_8_sig")

                # df.to_csv(self.output_filename,header=False,index = False,encoding="utf_8_sig")
                print(f"Successfully Save fhz file to: {self.output_filename}\n", "fhz file is a vissim output file don't need to transfer to geojson\n")

            else:
                print(f"Invalid Input File or Folder: {str(i)}.")
                # warnings.warn(f"Invalid Input File or Folder: {str(i)}.")
        return None

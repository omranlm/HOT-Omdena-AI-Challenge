import glob
import math
import os
import re


def main():
    for i in range(5):

        path = f"{i+1}/*?.png"
        print("\033[1m" + f"Performing rasterizing on folder {i+1}" + "\033[0m")

        # labels converter
        cmd = label_converter(
            i + 1
        )  # start on compiling commands to georeference and rasterize tiles in entire folder to
        # be executed in batch files

        for tiles in glob.glob(path):

            fname = tiles.replace(".png", "")
            split = re.split("-", tiles)
            x = int(split[1])
            y = int(split[2])
            z = int(split[3].replace(".png", ""))
            print(x, y, z)
            # lon, lat = tiletolatlon(x, y, z)
            # print(f"Long: {lon}, Lat: {lat}")

            name = list(fname)
            name[0] = f"{i+1}\After"
            name = "".join(name)
            print(name)

            # get minimum and maximum lat and lon in degrees
            lon_min, lat_min = tiletolatlon(x, y + 1, z)
            lon_max, lat_max = tiletolatlon(x + 1, y, z)
            print(lon_min, lat_min)
            print(lon_max, lat_max)

            # conversion to espg3857
            x_min, y_min = ConvertCoor(lon_min, lat_min)
            x_max, y_max = ConvertCoor(lon_max, lat_max)

            # the following lines can be uncomented to view bounding box
            # print(x_min, y_min)
            # print(x_max, y_max)

            # clipping of tile into geojson
            clip = clipping(x_min, y_min, x_max, y_max, name, i + 1)
            cmd += "&" + clip

            # generate raster of tile image
            ras = raster(x_min, y_min, x_max, y_max, name)
            cmd += "&" + ras

            # convert tiff to png
            co = tifftopng(name)
            cmd += "&" + co

            print()

        print("\033[1m" + f"Commands for rasterizing on folder {i+1}" + "\033[0m")
        # print(cmd)    #complete command to georeference and rasterize entire folders
        # saves joint commands into batch files that can be executed
        with open(f"{i+1}commands.bat", "w") as f:
            f.write(cmd)

        print()
        print()


def tiletolatlon(xtile, ytile, zoom):
    """
    conversion of tile values to lon and lat in degrees"""
    n = 2.0**zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = lat_rad * 180.0 / math.pi
    return lon_deg, lat_deg


def ConvertCoor(lon, lat):

    """
    Converts lat lon  in degrees to epsg 3857"""

    lonInEPSG3857 = lon * 20037508.34 / 180
    latInEPSG3857 = (
        math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    ) * (20037508.34 / 180)

    # print("{0},{1}".format(lonInEPSG3857,latInEPSG3857))
    return lonInEPSG3857, latInEPSG3857


def clipping(xmin, ymin, xmax, ymax, fname):
    clip = f"ogr2ogr -clipsrc {xmin} {ymin} {xmax} {ymax} {fname} -f GeoJSON {fname}.geojson labels.geojson"
    os.system(clip)
    #! clip
    print(clip)


def raster(xmin, ymin, xmax, ymax, fname):
    raster = f"gdal_rasterize -burn 255 -burn 255 -burn 255 -ts 256 256 -te {xmin} {ymin} {xmax} {ymax} {fname}.geojson\
    {fname}.tiff"
    os.system(raster)
    print(raster)


def label_converter(n):  # conversion of geojson files
    conv = f"ogr2ogr -s_srs EPSG:4326 -t_srs EPSG:3857 -f GeoJSON {n}/labels_rep.geojson {n}/labels.geojson"
    os.system(conv)
    # print(conv)
    return conv


def tifftopng(fname):
    conv = f"gdal_translate -ot Byte -of PNG -scale -co worldfile=yes {fname}.tif {fname}-burned.png"
    print(conv)


main()

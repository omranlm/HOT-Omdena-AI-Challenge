import json
import logging
import math
import os
import sys

import osm2geojson
import requests

work_dir = ".."
os.chdir(work_dir)
gdal_path = 'C:/"Program Files"/"QGIS 3.26.3"/bin/'

logger = logging.getLogger("generate_osm_data")
logging.basicConfig(level=logging.DEBUG)


def query_overpass(lat_min, lon_min, lat_max, lon_max, time_out=50):
    """
    Querying the Overpass-API for generating labels of Openstreetmap buildings.
    Installation of package osm2geojson is necessary (with pip).
    Parallel installation of gdal breaks the osm2geojson package(?).

    Args:
        lat_min (float): Minimum latitude of the bounding box in WGS84 coordinates (decimal degree)
        lon_min (float): Minimum longitude of the bounding box in WGS84 coordinates (decimal degree)
        lat_max (float): Maximum latitude of the bounding box in WGS84 coordinates (decimal degree)
        lon_max (float): Maximum longitude of the bounding box in WGS84 coordinates (decimal degree)
        time_out (int): Timeout for querying the Overpass-API (default 50)

    """
    logger.info("start function query_overpass")
    bbox = str(lat_min) + "," + str(lon_min) + "," + str(lat_max) + "," + str(lon_max)
    timeout = time_out
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:{timeout}];
    (
        way["building"]({bbox});
        relation["building"]({bbox});
    );
    out geom;
    """

    logger.info("requesting the overpass-api")
    logger.debug(overpass_query)
    response = requests.get(overpass_url, params={"data": overpass_query})
    try:
        response_json = response.json()
    except ValueError:
        logger.error("error while requesting the overpass-api")
        logger.error(sys.exc_info())
        return

    logger.info("converting json file to geojson")
    geojson = osm2geojson.json2geojson(response_json)

    logger.info("saving geojson file to folder")
    with open(tilename + ".geojson", "w", encoding="utf-8") as file:
        json.dump(geojson, file)

    if os.path.exists(tilename + "_3857.geojson"):
        os.remove(tilename + "_3857.geojson")

    logger.info("projecting the geojson file form EPSG:4326 to EPSG:3857")
    ogr2ogr = (
        gdal_path
        + f"ogr2ogr -s_srs EPSG:4326 -t_srs EPSG:3857 \
        -f GeoJSON {tilename}_3857.geojson {tilename}.geojson"
    )
    logger.debug(ogr2ogr)
    os.system(ogr2ogr)

    # (in mercator units, not DD)
    logger.info("rasterize labels from geojson to tif")
    gdal_rasterize = (
        gdal_path
        + f"gdal_rasterize -q -burn 1 -ot Byte -tr 1 1 \
        {tilename}_3857.geojson {tilename}_3857.tif"
    )
    logger.debug(gdal_rasterize)
    os.system(gdal_rasterize)

    logger.info("end function query_overpass")
    return


def deg2num(lat_deg, lon_deg, zoom=19):
    """
    Calculating tile number based on latitude and longitude in degrees.
    Further information: https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Implementations.

    Args:
        lat_deg (float): Latitude in WGS84 coordinates (decimal degree)
        lon_deg (float): Longitude in WGS84 coordinates (decimal degree)
        zoom (int): Zoom level (default 19)

    Returns:
        xtile (int): Number of the horizontal tile
        ytile (int): Number of the vertical tile

    """
    lat_rad = math.radians(lat_deg)
    n = 2.0**zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)

    return (xtile, ytile)


def setup_logging():
    """
    Setup of the logfile.

    """
    file_handler = logging.FileHandler("generate_training_data.log", mode="a")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)d: %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


if __name__ == "__main__":
    # Test cases:
    # 41.88883634691523, 12.501153945922852, 41.89438706550483, 12.510209083557129 # Rome
    # 19.324508067213333, -99.16281223297119, 19.352651384874918, -99.12659168243408 # Mexiko City
    # -22.99171103584478, -43.25338840484619, -22.984846657733844, -43.244333267211914 # Rio de Janeiro
    # -22.91695450249122, -43.19472312927246, -22.903217810692396, -43.176612854003906 # Rio de Janeiro 2
    # -26.137254698472045, 28.10577392578125, -26.083690063014146, 28.17821502685547 # Johannesburg

    xmin, ymin = deg2num(-26.137254698472045, 28.10577392578125, 19)
    tilename = str(xmin) + "_" + str(ymin)
    if not os.path.exists(work_dir + "/" + tilename):
        os.mkdir(tilename)
        os.chdir(work_dir + "/" + tilename)
        os.mkdir("osm")
        os.mkdir("oam")

    setup_logging()

    os.chdir(work_dir + "/" + tilename + "/osm")
    query_overpass(
        -26.137254698472045, 28.10577392578125, -26.083690063014146, 28.17821502685547
    )  # Johannesburg

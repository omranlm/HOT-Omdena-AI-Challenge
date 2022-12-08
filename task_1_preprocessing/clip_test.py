import math
import re
from typing import Tuple

import geopandas
from shapely.geometry import Polygon


def get_bounding_box(filename: str) -> str:
    """Get the four corners of the OAM image as coordinates.

    This function gives us the limiting values that we will pass to
    the GDAL commands. We need to make sure that the raster image
    that we're generating have the same dimension as the original image.
    Hence, we'll need to fetch these extrema values.

    Returns:
        x_min, y_max, x_max, y_min: This is the format the -a_ullr
            flag of GDAL expects.
    """
    _, *tile_info = re.split("-", filename)
    x_tile, y_tile, zoom = map(int, tile_info)
    top_left = num2deg(x_tile, y_tile, zoom)
    bottom_right = num2deg(x_tile + 1, y_tile + 1, zoom)

    return [*top_left, *bottom_right]


def num2deg(x_tile: int, y_tile: int, zoom: int) -> Tuple[float, float]:
    """Convert tile numbers to EPSG:4326 coordinates.

    Convert tile numbers to the WGS84 latitude/longitude coordinates
    (in degrees) of the upper left corner of the tile.

    Args:
        x_tile: Tile X coordinate
        y_tile: Tile Y coordinate
        zoom: Level of detail

    Returns:
        A tuple (longitude, latitude) in degrees.
    """
    n = 2.0**zoom
    lon_deg = x_tile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
    lat_deg = math.degrees(lat_rad)

    return lon_deg, lat_deg


file_stem = "OAM-319295-270960-19"
x_min, y_max, x_max, y_min = get_bounding_box(file_stem)

gdf = geopandas.read_file("labels.geojson").set_crs("EPSG:4326")
polygon = Polygon([(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)])
gdf.clip(polygon).to_crs("EPSG:3857").to_file("output.geojson")

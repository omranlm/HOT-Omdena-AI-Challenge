import math
import os
import re
from glob import glob
from typing import Tuple, List

import numpy as np
from PIL import Image
from tensorflow import keras

IMAGE_SIZE = 256


def open_images(paths: List[str]) -> np.ndarray:
    """Open images from some given paths."""
    images = []
    for path in paths:
        image = keras.preprocessing.image.load_img(
            path, target_size=(IMAGE_SIZE, IMAGE_SIZE)
        )
        image = np.array(image.getdata()).reshape(IMAGE_SIZE, IMAGE_SIZE, 3) / 255.0
        images.append(image)

    return np.array(images)


def save_mask(mask: np.ndarray, filename: str) -> None:
    """Save the mask array to the specified location."""
    reshaped_mask = mask.reshape((IMAGE_SIZE, IMAGE_SIZE)) * 255
    result = Image.fromarray(reshaped_mask.astype(np.uint8))
    result.save(filename)


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
    bounding_box = [*top_left, *bottom_right]

    return "".join([f"{x} " for x in bounding_box])


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
    n = 2.0 ** zoom
    lon_deg = x_tile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
    lat_deg = math.degrees(lat_rad)

    return lon_deg, lat_deg


def remove_files(pattern: str) -> None:
    """Remove files matching a wildcard."""
    files = glob(pattern)
    for file in files:
        os.remove(file)

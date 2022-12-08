import os
from glob import glob
from pathlib import Path

from .utils import get_bounding_box


def georeference(input_path: str, is_mask=False) -> None:
    """Perform georeferencing.

    The EPSG:4326 coordinate system is used ('WGS 84', coordinates in degrees).

    Args:
        input_path: Path of the directory where the input data are stored.
        is_mask: Whether the image is binary or not.
    """
    for path in glob(f"{input_path}/*.png"):
        filename = Path(path).stem
        bounding_box = get_bounding_box(filename)
        process_image = f"""
            gdal_translate \
                -b 1 {'' if is_mask else '-b 2 -b 3'} \
                -a_ullr {bounding_box} \
                -a_srs EPSG:4326 \
                {input_path}/{filename}.png \
                {input_path}/{filename}.tif
        """
        os.system(process_image)

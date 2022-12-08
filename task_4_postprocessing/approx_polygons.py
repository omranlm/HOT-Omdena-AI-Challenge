import os
from pathlib import Path

import cv2
import numpy as np
from geopandas import GeoSeries
from shapely.geometry import Polygon


def vectorize(path):
    mask = cv2.imread(path)
    contours = get_contours(mask)

    polygons = []
    for contour in contours:
        try:
            polygons.append(Polygon(contour))
        except:
            ...

    gs = GeoSeries(polygons).set_crs("EPSG:4326")
    gs.to_file(f"test.geojson")


def get_contours(mask):
    gray_mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    eroded_mask = erode(gray_mask)
    contours, _ = cv2.findContours(
        eroded_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    simplified_contours = simplify_contours(contours)
    scaled_contours = scale_contour(simplified_contours, 1.2)
    squeezed_contours = map(np.squeeze, scaled_contours)

    return squeezed_contours


def erode(mask):
    _, thresh = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
    thresh_eroded_1 = cv2.erode(
        thresh, np.ones((5, 5), np.uint8), cv2.BORDER_CONSTANT, iterations=1
    )
    thresh_eroded_2 = cv2.erode(
        thresh_eroded_1, np.ones((3, 3), np.uint8), cv2.BORDER_CONSTANT, iterations=2
    )
    thresh_eroded_3 = cv2.erode(
        thresh_eroded_2, np.ones((2, 2), np.uint8), cv2.BORDER_CONSTANT, iterations=3
    )

    return thresh_eroded_3


def simplify_contours(contours, max_corners=6):
    simplified_contours = []

    for contour in contours:
        if len(contour) < 4:
            continue

        epsilon = 0.0008 * cv2.arcLength(contour, True)
        while True:
            epsilon *= 2
            new_contour = cv2.approxPolyDP(contour, epsilon, True)
            if len(new_contour) <= max_corners:
                simplified_contours.append(new_contour)
                break

    return simplified_contours


def scale_contour(contours, scale):
    scaled_contours = []

    for contour in contours:
        M = cv2.moments(contour)
        cx = int(M["m10"] / (M["m00"] + 0.0000001))
        cy = int(M["m01"] / (M["m00"] + 0.0000001))

        contour_norm = contour - [cx, cy]
        scaled_contour = contour_norm * scale
        scaled_contour = scaled_contour + [cx, cy]
        scaled_contour = scaled_contour.astype(np.int32)
        scaled_contours.append(scaled_contour)

    return scaled_contours


if __name__ == "__main__":
    vectorize("labels.tif")

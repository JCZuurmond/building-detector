from typing import (
    List,
    Tuple,
)

import osgeo
from pyproj import (
    Proj,
    transform,
)


def get_layer_extent(layer: osgeo.ogr.Layer) -> Tuple[int, int, int, int]:
    """
    Get the layer extent.

    Parameters
    ----------
    layer : osgeo.ogr.Layer
        An osgeo layer.

    Returns
    -------
    Tuple[int, int, int, int] : The extent of the layer (xmin, xmax, ymin,
    ymax).
    """
    extents = [feat.GetGeometryRef().GetEnvelope() for feat in layer]
    if not any(extents):
        return None, None, None, None
    xmin, xmax, ymin, ymax = zip(*extents)
    return min(xmin), max(xmax), min(ymin), max(ymax)


def wgs84_to_rd_new(*points: Tuple[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Convert WGS84 (EPSG:4326) coordinates to RD new (EPSG:28892).

    Parameters
    ----------
    *points : Tuple[Tuple[int, int]]
        The points (lon, lat)

    Returns
    -------
    Tuple[Tuple[int, int]] : The points converted to the RD new coordinate
    system.
    """
    wgs84_projection = Proj('EPSG:4326')
    rd_new_projection = Proj('EPSG:28992')

    # The transformation expects a (lat, lon) coordinate and returns a (x, y)
    # coordinate. Though lat is the y coordinate and lon he x coordinate.
    return [transform(wgs84_projection, rd_new_projection, *point[::-1])
            for point in points]


def get_bbox_width_height(bbox: List[float]) -> Tuple[float]:
    """
    Get the width and height of a bounding box (xmin, ymin, xmax, ymax).

    Parameters
    ----------
    bbox : List[float]
        The bounding box (xmin, ymin, xmax, ymax).

    Returns
    -------
    Tuple[float] : The width and height of the bounding box.
    """
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

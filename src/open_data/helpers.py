from typing import Tuple

import osgeo


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

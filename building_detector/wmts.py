from io import BytesIO

import requests
from PIL import Image

from .helpers import gps_to_tile


def get_wmts_tile_from_coordinate(coordinate, wmts_base, layer, zoom=0):
    """
    Gets an tile from the WMTS service given the coordinate.

    Parameters
    ----------
    coordinate : Tuple(float, float)
        The gps coordinate.
    wmts_base : str
        The base of th WMTS url.
    layer : str
        The layer to query in the WMTS service.
    zoom : int (default: 0)
        The zoom level

    Returns
    -------
    PIL.image : The tile (as PIL image).
    """
    tile_col, tile_row = gps_to_tile(*coordinate, zoom=zoom)

    params = (
        ('layer', layer),
        ('style', 'default'),
        ('tilematrixset', 'EPSG:3857'),
        ('Service', 'WMTS'),
        ('Request', 'GetTile'),
        ('Version', '1.0.0'),
        ('Format', 'image/png'),
        ('TileMatrix', '%02d' % zoom),
        ('TileCol', tile_col),
        ('TileRow', tile_row),
    )

    response = requests.get(wmts_base, params=params)

    # BytesIO is an in memory file
    image_bytes = BytesIO()
    image_bytes.write(response.content)
    image = Image.open(image_bytes)

    return image

import math
from io import BytesIO

import requests
from PIL import Image


def gps_to_tile(lat, lon, zoom):
    """
    Convert gps coordinate to tile number.

    Parameters
    ----------
    lat : float
        The latitude of the coordinate.
    lon : float
        The longitude of the coordinate.
    zoom : int
        Zoom level.

    Returns
    -------
    Tuple(int, int) : The tile (column, row) index.

    Source
    ------
    https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Tile_numbers_to_lon..2Flat._2
    """
    n = 2.0 ** zoom
    lat_rad = math.radians(lat)
    sec = (1 / math.cos(lat_rad))

    tile_col = (lon + 180.0) / 360.0 * n
    tile_row = (1.0 - math.log(math.tan(lat_rad) + sec) / math.pi) / 2.0 * n

    return int(tile_col), int(tile_row)


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

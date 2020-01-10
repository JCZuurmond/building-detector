import argparse
import logging
import time
from pathlib import Path

import requests
from owslib.wmts import WebMapTileService
from tqdm import tqdm

from building_detector import helpers


def mkdir_isdir(path: Path):
    if not path.exists():
        path.mkdir()
    if not path.is_dir():
        raise ValueError(f'{path} should be a directory')


def download(
        wmts_url: str,
        layer_name: str,
        data_dir: Path,
        zoom: int):
    """
    Download the Actueel_orth25 layer from the pdok WMTS. The following
    subdirectory will be created in `data_dir`:

        <data dir>/Actueel_orth25/<zoom level>

    Parameters
    ---------
    wmts_url : str
        The url to the WMTS.
    layer_name : str
        The layer name.
    data_dir : Path
        Directory in which the jpg's are saved.
    zoom : int
        The zoom level of the layer.

    Link
    ----
    https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wmts
    """
    logger = logging.getLogger(__name__)
    logger.info('scraping wmts: %s', wmts_url)
    logger.info('layer: %s', layer_name)
    logger.info('data_dir: %s', data_dir)
    logger.info('zoom: %s', zoom)

    layer_dir = data_dir / layer_name
    zoom_dir = layer_dir / f'{zoom:02d}'

    for d in data_dir, layer_dir, zoom_dir:
        mkdir_isdir(d)

    wmts = WebMapTileService(wmts_url, version='1.1.1')
    bbox = helpers.Bbox(*wmts.contents[layer_name].boundingBoxWGS84)
    # TODO: For now only download data around Amsterdam
    bbox = helpers.Bbox(
        xmin=100000,
        ymin=460000,
        xmax=140000,
        ymax=500000,
    )
    cols, rows = zip(*[
        helpers.wgs84_to_tile_number(*point, zoom)
        for point in bbox.rdnew_to_wgs84()
    ])

    pbar = tqdm(
        ((col, row) for col in range(*cols) for row in range(*rows, -1)),
        total=(cols[1] - cols[0]) * (rows[0] - rows[1]),
    )
    for col, row in pbar:
        logger.debug('col=%s, row=%s', col, row)
        pbar.set_postfix(row=row, col=col)
        tile_file = zoom_dir / f'{col}_{row}.jpg'
        if tile_file.exists():
            continue

        try_ = 0
        while try_ < 10:
            time.sleep(0.1)
            try:
                tile = wmts.gettile(
                    layer=layer_name,
                    tilematrixset='EPSG:3857',
                    tilematrix=f'{zoom:02d}',
                    row=row,
                    column=col,
                    format="image/png"
                )
            except requests.exceptions.ReadTimeout:
                logger.info('Got timeout')
                try_ += 1
            finally:
                tile_file.write_bytes(tile.read())
                break


def main():
    """Download Actueel_orth25."""
    parser = argparse.ArgumentParser(
        description='Download the Actueel_orth25 layer from PDOk.'
    )
    parser.add_argument(
        'wmts',
        type=str,
        help='the wmts link, e.g. https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wmts'
    )
    parser.add_argument(
        'layer',
        type=str,
        help='layer_name, e.g. Actueel_ortho25'
    )
    parser.add_argument(
        'data_dir',
        type=str,
        help='data directory'
    )
    parser.add_argument(
        '--zoom',
        type=int,
        help='zoom level',
        default=19,
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='verbose log statements',
        default=False,
    )
    args = parser.parse_args()

    logging.basicConfig(
        format=('[%(funcName)s:%(lineno)d] - %(message)s'),
        level=logging.DEBUG if args.verbose else logging.INFO
    )

    download(args.wmts, args.layer, Path(args.data_dir), args.zoom)


if __name__ == "__main__":
    main()

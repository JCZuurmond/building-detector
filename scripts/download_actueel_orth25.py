import argparse
from pathlib import Path

from owslib.wmts import WebMapTileService
from tqdm import tqdm

from building_detector import helpers


def mkdir_isdir(path: Path):
    if not path.exists():
        path.mkdir()
    if not path.is_dir():
        raise ValueError(f'{path} should be a directory')


def download(data_dir: Path, zoom: int):
    """
    Download the Actueel_orth25 layer from the pdok WMTS. The following
    subdirectory will be created in `data_dir`:

        <data dir>/Actueel_orth25/<zoom level>

    Parameters
    ---------
    data_dir : Path
        Directory in which the jpg's are saved.
    zoom : int
        The zoom level of the layer.

    Link
    ----
    https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wmts
    """
    wmts_url = 'https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wmts'
    layer_name = 'Actueel_ortho25'

    layer_dir = data_dir / layer_name
    zoom_dir = layer_dir / f'{zoom:02d}'

    for d in data_dir, layer_dir, zoom_dir:
        mkdir_isdir(d)

    wmts = WebMapTileService(wmts_url, version='1.1.1')
    bbox = helpers.Bbox(*wmts.contents[layer_name].boundingBoxWGS84)
    cols, rows = zip(*[
        helpers.wgs84_to_tile_number(*point, zoom)
        for point in bbox
    ])

    pbar = tqdm(
        ((col, row) for col in range(*cols) for row in range(*rows, -1)),
        total=(cols[1] - cols[0]) * (rows[0] - rows[1]),
    )
    for col, row in pbar:
        pbar.set_postfix(row=row, col=col)
        tile = wmts.gettile(
            layer=layer_name,
            tilematrixset='EPSG:3857',
            tilematrix=f'{zoom:02d}',
            row=row,
            column=col,
            format="image/jpeg"
        )

        tile_file = zoom_dir / f'{col}_{row}.jpg'
        tile_file.write_bytes(tile.read())


def main():
    """Download Actueel_orth25."""
    parser = argparse.ArgumentParser(
        description='Download the Actueel_orth25 layer from PDOk.'
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
    args = parser.parse_args()
    download(Path(args.data_dir), args.zoom)


if __name__ == "__main__":
    main()

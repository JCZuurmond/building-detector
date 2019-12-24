import argparse
import tempfile
from itertools import chain
from pathlib import Path

import geopandas as gpd
import pandas as pd
from owslib.wfs import WebFeatureService

from building_detector import helpers


def get_features_gen(
    wfs: WebFeatureService,
    maxfeatures: int = 1000,
    **wfs_kwargs
) -> gpd.geodataframe.GeoDataFrame:
    """
    Generator to get all features from a certain wfs request.

    Parameters
    ----------
    wfs : WebFeatureService
        The WFS service to download from.
    maxfeatures : int, optional (default : 1000)
        The maximum number of features to download each time.
    **wfs_kwargs
        Kwargs to be passed to the WFS request.

    Returns
    -------
    gpd.geodataframe.GeoDataFrame : The features.
    """
    wfs_kwargs = {
        **wfs_kwargs,
        **dict(maxfeatures=maxfeatures, startindex=0)
    }
    tmp_file = tempfile.NamedTemporaryFile(suffix='.gml').name

    while True:
        response = wfs.getfeature(**wfs_kwargs)

        with open(tmp_file, 'wb') as f:
            f.write(response.read())

        out = gpd.read_file(tmp_file, driver='GML')
        yield out

        if out.shape[0] == maxfeatures:
            wfs_kwargs['startindex'] += maxfeatures
        else:
            break


def download(data_dir: Path, gml_path: Path = None) -> None:
    """
    Download the BAG data.

    Parameters
    ----------
    data_dir : Path
        The data directory to save the features in
    gml_path : Path (default : None)
        The path to an gml file used to bound the download
    """
    wfs_url = 'https://geodata.nationaalgeoregister.nl/bag/wfs/v1_1'
    layer_name = 'bag:pand'

    bbox = None
    if gml_path is not None:
        envelope = gpd.read_file(gml_path).envelope
        bbox = tuple(chain(*helpers.Bbox.from_poly(envelope[0])))

    wfs = WebFeatureService(wfs_url, version='2.0.0')
    features = pd.concat(get_features_gen(wfs, typename=layer_name, bbox=bbox))

    layer_name = layer_name.replace(':', '_')
    if gml_path is not None:
        out_file = data_dir / f'{layer_name}_{gml_path.stem}.gml'
    else:
        out_file = data_dir / f'{layer_name}.gml'

    features.to_file(out_file, driver='GML')


def main():
    """Download BAG."""
    parser = argparse.ArgumentParser(
        description='Download the BAG layer from PDOk.'
    )
    parser.add_argument(
        'data_dir',
        type=str,
        help='data directory'
    )
    parser.add_argument(
        '--gml',
        type=str,
        help='GML file with poly to use as bounding box.',
        default=None,
    )
    args = parser.parse_args()
    download(Path(args.data_dir), args.gml)


if __name__ == "__main__":
    main()

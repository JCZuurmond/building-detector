from typing import (
    List,
    Tuple,
    Union,
)

import osgeo
from pyproj import (
    Proj,
    transform,
)


class Point:
    """
    A point.

    Attributes
    ----------
    x : float
        The x-coordinate.
    y : float
        The y-coordinate.
    """

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point(x={self.x!r}, y={self.y})'

    def __str__(self):
        return f'{self.x},{self.y}'


class Bbox:
    """
    A bounding box.

    Attributes
    ----------
    xmin : float
        The minimum x coordinate.
    ymin : float
        The minimum y coordinate.
    xmin : float
        The maximum x coordinate.
    ymin : float
        The maximum y coordinate.
    """

    def __init__(self, xmin: float, ymin: float, xmax: float, ymax: float):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def __contains__(self, other):
        if isinstance(other, tuple):
            if not len(other) == 2:
                raise ValueError('Expected tuple of length two.')
            other = Point(*other)

        if isinstance(other, Bbox):
            return all(p in self for p in self)
        elif isinstance(other, Point):
            return (
                (self.xmin <= other.x <= self.xmax) and
                (self.ymin <= other.y <= self.ymax)
            )
        else:
            raise NotImplementedError(
                f'This method is not implemented for type {type(other)}.'
            )

    def __getitem__(self, key: Union[int, str]):
        if isinstance(key, int):
            if key >= len(self):
                raise IndexError('Bbox index out of range.')
            points = (self.lower_left,
                      self.lower_right,
                      self.upper_left,
                      self.upper_right)
            return points[key]
        else:
            return getattr(self, key)

    def __len__(self):
        return 4

    def __repr__(self):
        return (
            f'BBox(xmin={self.xmin!r}, ymin={self.ymin!r}, '
            f'xmax={self.xmax!r}, ymax={self.ymax!r})'
        )

    @classmethod
    def from_points(cls, point_min: Point, point_max: Point):
        """
        Create a bounding box from two points.

        Parameters
        ----------
        point_min : Point
            The minimum coordinate.
        point_max : Point
            The maximum coordinate.

        Returns
        -------
        The bounding box.
        """
        return cls(xmin=point_min.x,
                   ymin=point_min.y,
                   xmax=point_max.x,
                   ymax=point_max.y)

    @property
    def width(self) -> float:
        """The bounding box width."""
        return self.xmax - self.xmin

    @property
    def height(self) -> float:
        """The bounding height."""
        return self.ymax - self.ymin

    @property
    def center(self) -> float:
        """The bounding box center."""
        return Point(self.xmin + 0.5 * self.width,
                     self.ymin + 0.5 * self.height)

    @property
    def lower_left(self) -> Point:
        """Lower left coordinate of the bounding box."""
        return Point(self.xmin, self.ymin)

    @property
    def lower_right(self) -> Point:
        """Lower right coordinate of the bounding box."""
        return Point(self.xmax, self.ymin)

    @property
    def upper_left(self) -> Point:
        """Upper left coordinate of the bounding box."""
        return Point(self.xmin, self.ymax)

    @property
    def upper_right(self) -> Point:
        """Upper right coordinate of the bounding box."""
        return Point(self.xmax, self.ymax)


def get_layer_bbox(layer: osgeo.ogr.Layer) -> Bbox:
    """
    Get the layer bounding box.

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
    if any(extents):
        xmin, xmax, ymin, ymax = zip(*extents)
        return Bbox(min(xmin), max(xmax), min(ymin), max(ymax))


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


def get_gml_layer(path: str) -> osgeo.ogr.Layer:
    """
    Get GML layer form file.

    Parameters
    ----------
    path : str
        The path to the gml file.

    Returns
    -------
    osgeo.ogr.Layer : The (first) layer in the gml.
    """
    driver = ogr.GetDriverByName('GML')
    gml = driver.Open(path)
    return gml.GetLayer()

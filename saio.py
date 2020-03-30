"""
SQLAlchemyIO (saio): Module hack for autoloading table definitions

## Usage

After

  ```python
  import saio
  saio.register_schema("model_draft", engine)
  ````

one can import table declarations easily using

  ```python
  from saio.model_draft import lis_charging_poi as LisChargingPoi
  ```

Note that `ipython` and Jupyter Notebook, allow using `<TAB>` to auto-complete
table names.

## Implementation details

`saio.register_schema` instantiates a declarative base using

  ```python
  from sqlalchemy.ext.declarative import declarative_base
  Base = declarative_base(bind=engine)
  # The Base can be imported using from saio.model_draft import Base
  ```

and then whenever one imports any table from `saio.model_draft`, ie. by calling
`from saio.model_draft import lis_charging_poi as LisChargingPoi`, saio does
approximately

  ```python
  class LisChargingPoi(Base):
      __tablename__ =  'lis_charging_poi'
      __table_args__ = {'schema': 'model_draft', 'autoload': True}
  ```
"""

__copyright__   = "© Reiner Lemoine Institut"
__license__     = "MIT"
__url__         = "https://github.com/coroa/saio/blob/master/saio.py"
__author__      = "coroa"

import sqlalchemy as sa
import sqlalchemy.ext.declarative
import sqlalchemy.engine.reflection

import warnings
from types import ModuleType

import logging
logger = logging.getLogger(__name__)

def memoize(func):
    cache = {}
    def memoizer(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return memoizer

class SchemaInspectorModule(ModuleType):
    __all__ = ()  # to make help() happy
    __package__ = __name__

    __path__ = []
    __file__ = __file__

    def __init__(self, modulepath, moduledoc, schema, engine):
        super().__init__(modulepath, moduledoc)

        assert isinstance(engine, sa.engine.Engine)

        self.schema = schema
        self.engine = engine
        self.Base = sa.ext.declarative.declarative_base(bind=engine)
        self.Meta = self.Base.metadata

    @memoize
    def __dir__(self):
        insp = sa.engine.reflection.Inspector.from_engine(self.engine)
        return insp.get_table_names(self.schema) + insp.get_view_names(self.schema)

    @memoize
    def __getattr__(self, name):
        # IPython queries several strange attributes, which should not become tables
        # if tblname.startswith("_ipython") or tblname.startswith("_repr"):
        #     raise AttributeError(tblname)

        # Idea for treating views from https://hultner.se/quickbits/2017-10-23-postgresql-reflection-views-python-sqlalchemy.html

        tab = sa.Table(name, self.Meta, autoload=True, schema=self.schema)
        attrs = {'__module__': self.__name__,
                 '__table__': tab}
        if not tab.primary_key:
            first_col = next(iter(tab.columns))
            logger.warning(f"Reflection was unable to determine primary key (normal for views), assuming: {first_col}")
            attrs['__mapper_args__'] = {'primary_key': [first_col]}

        return type(name, (self.Base,), attrs)

del ModuleType
del memoize

def register_schema(schema, engine):
    import sys

    module = SchemaInspectorModule(f"{__name__}.{schema}", "", schema, engine)
    # Make `from saio.{schema} import {table}` work
    sys.modules[module.__name__] = module

    # We could register the schema module in the saio module, as well
    #setattr(sys.modules[__name__], schema, module)

try:
    import pandas as pd
    has_pandas = True
except ImportError:
    has_pandas = False

try:
    import geopandas as gpd
    import shapely.wkb
    import shapely.geos
    has_geopandas = True
except ImportError:
    has_geopandas = False

def as_pandas(query, index_col=None, coerce_float=True, params=None,
              geometry='geom', crs=None, hex_encoded=True):
    """
    Import a query into a pandas DataFrame or a geopandas GeoDataFrame

    Arguments
    ---------
    query : sqlalchemy.orm.query.Query

    index_col : string or list of strings, optional, default: None
        Column(s) to set as index(MultiIndex).

    coerce_float : boolean, default: True
        Attempts to convert values of non-string, non-numeric objects (like
        decimal.Decimal) to floating point. Useful for SQL result sets.

    params : list, tuple or dict, optional, default: None
        List of parameters to pass to execute method.  The syntax used
        to pass parameters is database driver dependent. Check your
        database driver documentation for which of the five syntax styles,
        described in PEP 249's paramstyle, is supported.
        Eg. for psycopg2, uses %(name)s so use params={'name' : 'value'}

    geometry : string, default: "geom"
        Column name to convert to shapely geometries

    crs : dict|string|None, default: None
        CRS to use for the returned GeoDataFrame; if None, CRS is determined
        from the SRID of the first geometry.

    hex_encoded : bool, optional, default: True
        Whether the geometry is in a hex-encoded string. Default is True,
        standard for postGIS. Use hex_encoded=False for sqlite databases.

    Note
    ----
    Adapted from geopandas' read_postgis function.

    Usage
    -----
    import saio
    saio.register_schema("boundaries", engine)
    from saio.boundaries import bkg_vg250_2_lan as BkgLan
    df = saio.as_pandas(session.query(BkgLan.geom))
    df.plot()
    """
    assert has_pandas, "Pandas failed to import. Please check your installation!"

    df = pd.read_sql_query(query.statement, query.session.bind,
                           index_col=index_col, coerce_float=coerce_float,
                           params=params)

    if geometry not in df:
        return df

    if not has_geopandas:
        warnings.warn("GeoPandas failed to import. Geometry column is left as WKB.")
        return df

    obj = next((s for s in df[geometry] if s is not None), None)
    if obj is not None:
        if isinstance(obj, bytes):
            load_geom = lambda s: shapely.wkb.loads(s, hex=hex_encoded)
        else:
            load_geom = lambda s: shapely.wkb.loads(str(s), hex=hex_encoded)

        srid = getattr(obj, 'srid', -1)
        if srid == -1:
            srid = shapely.geos.lgeos.GEOSGetSRID(load_geom(obj)._geom)

        if crs is None and srid != 0:
            crs = dict(init="epsg:{}".format(srid))

        df[geometry] = df[geometry].map(lambda s: load_geom(s) if s is not None else None)

    return gpd.GeoDataFrame(df, crs=crs, geometry=geometry)

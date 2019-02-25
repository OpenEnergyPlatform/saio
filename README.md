# SQLAlchemyIO (saio)

Module hack for autoloading table definitions.

Also provides a helper function `as_pandas` to read an `sqlalchemy.orm.query.Query` into a (Geo)Pandas dataframe.

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

The helper function `as_pandas` reads a query into a GeoDataFrame:
```python
saio.register_schema("boundaries", engine)

from saio.boundaries import bkg_vg250_2_lan as BkgLan
df = saio.as_pandas(session.query(BkgLan))
df.plot()
```

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

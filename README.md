# SQLAlchemyIO (saio)

Module hack for autoloading table definitions

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

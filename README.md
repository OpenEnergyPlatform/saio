# SQLAlchemyIO (saio): Module hack for autoloading table definitions

After
```python
import saio
saio.register_schema("model_draft", engine)
```
the table declaration for `lis_charging_poi`
```python
class LisChargingPoi(Base):
    __tablename__ =  'lis_charging_poi'
    __table_args__ = {'schema': 'model_draft', 'autoload': True}
```
is auto-generated and loaded by accessing
```python
saio.model_draft.LisChargingPoi
```
or importing
```python
from saio.model_draft import LisChargingPoi
```

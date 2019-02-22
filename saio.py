## Copyright Jonas Hoersch (RLI)

## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
SQLAlchemyIO (saio): Module hack for autoloading table definitions

## Usage

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
  saio.model_draft.Base = declarative_base(bind=engine)
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
import sqlalchemy as sa
import sqlalchemy.ext.declarative

from types import ModuleType

class SchemaInspectorModule(ModuleType):
    __all__ = ()  # to make help() happy
    __package__ = __name__

    __path__ = []
    __file__ = __file__

    def __init__(self, modulepath, moduledoc, schema, engine):
        super().__init__(modulepath, moduledoc)

        self.schema = schema
        assert isinstance(engine, sa.engine.Engine)
        self.Base = sa.ext.declarative.declarative_base(bind=engine)
        self.tables = engine.table_names(schema=schema)
        self.klasses = {}

    def __dir__(self):
        return self.tables

    def __getattr__(self, tblname):
        if tblname in self.klasses:
            return self.klasses[tblname]
        elif tblname in self.tables:
            __package__ = self.__package__
            klass = type(tblname,
                         (self.Base,),
                         {'__module__': self.__name__,
                          '__tablename__': tblname,
                          '__table_args__': {'schema': self.schema, 'autoload': True}})
            self.klasses[tblname] = klass
            return klass
        else:
            raise AttributeError(tblname)

del ModuleType

def register_schema(schema, engine):
    import sys

    module = SchemaInspectorModule(f"{__name__}.{schema}", "", schema, engine)
    # Make `from saio.{schema} import {table}` work
    sys.modules[module.__name__] = module
    setattr(sys.modules[__name__], schema, module)

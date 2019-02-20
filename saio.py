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

After

  ```python
  import saio
  saio.register_schema("model_draft", engine)
  ````

the table declaration for `lis_charging_poi`

  ```python
  class LisChargingPoi(Base):
      __tablename__ =  'lis_charging_poi'
      __table_args__ = {'schema': 'model_draft', 'autoload': True}
  ```

is auto-generated and loaded by accessing

  `saio.model_draft.LisChargingPoi`

or importing

  `from saio.model_draft import LisChargingPoi`
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
        self.tables = {self.translate_tablename_to_klassname(tbl): tbl
                       for tbl in engine.table_names(schema=schema)}
        self.klasses = {}

    def __dir__(self):
        return list(self.tables.keys())

    def __getattr__(self, name):
        if name in self.klasses:
            return self.klasses[name]
        elif name in self.tables:
            tbl_name = self.tables[name]
            __package__ = self.__package__
            klass = type(name, (self.Base,), {'__module__': self.__name__,
                                              '__tablename__': tbl_name,
                                              '__table_args__': {'schema': self.schema, 'autoload': True}})
            self.klasses[name] = klass
            return klass
        else:
            raise AttributeError(name)

    def translate_tablename_to_klassname(self, tbl_name):
        return ''.join(w.capitalize() for w in tbl_name.split('_'))

del ModuleType

def register_schema(schema, engine):
    import sys

    module = SchemaInspectorModule(f"{__name__}.{schema}", "", schema, engine)
    # Make `from saio.{schema} import {table}` work
    sys.modules[module.__name__] = module
    setattr(sys.modules[__name__], schema, module)

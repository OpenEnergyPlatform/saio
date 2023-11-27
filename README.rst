
.. figure:: https://user-images.githubusercontent.com/14353512/185425447-85dbcde9-f3a2-4f06-a2db-0dee43af2f5f.png
    :align: left
    :target: https://github.com/rl-institut/super-repo/
    :alt: Repo logo

===================
SQLAlchemyIO (saio)
===================

Module hack for autoloading table definitions. Also provides a helper function ``as_pandas`` to read an ``sqlalchemy.orm.query.Query`` into a (Geo)Pandas dataframe.

.. list-table::
   :widths: auto

   * - License
     - |badge_license|
   * - Documentation
     - |badge_documentation|
   * - Publication
     -
   * - Development
     - |badge_issue_open| |badge_issue_closes| |badge_pr_open| |badge_pr_closes|
   * - Community
     - |badge_contributing| |badge_contributors| |badge_repo_counts|

.. contents::
    :depth: 2
    :local:
    :backlinks: top


Usage
=====

After:

.. code-block:: python

   import saio
   saio.register_schema("model_draft", engine)

one can import table declarations easily using:

.. code-block:: python

   from saio.model_draft import lis_charging_poi as LisChargingPoi

Note that ``ipython`` and Jupyter Notebook allow using ``<TAB>`` to auto-complete table names.

The helper function ``as_pandas`` reads a query into a GeoDataFrame:

.. code-block:: python

   saio.register_schema("boundaries", engine)

   from saio.boundaries import bkg_vg250_2_lan as BkgLan
   df = saio.as_pandas(session.query(BkgLan))
   df.plot()

Installation
=======================

The package is registered on pypi, so install with:

.. code-block:: shell

   pip install saio

Or get it directly from GitHub:

.. code-block:: shell

   pip install git+https://github.com/coroa/saio.git#egg=saio

Implementation Details
=======================

``saio.register_schema`` instantiates a declarative base using:

.. code-block:: python

   from sqlalchemy.ext.declarative import declarative_base
   Base = declarative_base(bind=engine)
   # The Base can be imported using from saio.model_draft import Base

and then whenever one imports any table from ``saio.model_draft``, i.e., by calling
``from saio.model_draft import lis_charging_poi as LisChargingPoi``, saio does approximately:

.. code-block:: python

   class LisChargingPoi(Base):
       __tablename__ =  'lis_charging_poi'
       __table_args__ = {'schema': 'model_draft', 'autoload': True}







.. |badge_license| image:: https://img.shields.io/github/license/OpenEnergyPlatform/saio
    :target: LICENSE.txt
    :alt: License

.. |badge_documentation| image::
    :target:
    :alt: Documentation

.. |badge_contributing| image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat
    :alt: contributions

.. |badge_repo_counts| image:: http://hits.dwyl.com/OpenEnergyPlatform/saio.svg
    :alt: counter

.. |badge_contributors| image:: https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square
    :alt: contributors

.. |badge_issue_open| image:: https://img.shields.io/github/issues-raw/OpenEnergyPlatform/saio
    :alt: open issues

.. |badge_issue_closes| image:: https://img.shields.io/github/issues-closed-raw/OpenEnergyPlatform/saio
    :alt: closes issues

.. |badge_pr_open| image:: https://img.shields.io/github/issues-pr-raw/OpenEnergyPlatform/saio
    :alt: closes issues

.. |badge_pr_closes| image:: https://img.shields.io/github/issues-pr-closed-raw/OpenEnergyPlatform/saio
    :alt: closes issues

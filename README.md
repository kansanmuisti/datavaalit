General installation
====================

Ubuntu/Debian
-------------

Packages:

    virtualenvwrapper python-imaging

openSUSE
--------

Packages:

    python-virtualenvwrapper python-imaging


Postgres installation
=====================

Ubuntu/Debian
-------------

Packages:

    libpq-dev postgresql-9.1-postgis postgresql postgresql-9.1-contrib  


openSUSE
--------

openSUSE requires an additional package repository:

    sudo zypper ar http://download.opensuse.org/repositories/Application:/Geo/openSUSE_12.2/  

Packages:

    postgresql-server postgresql-devel postgresql-contrib postgis postgis-utils proj libproj-devel

PIP packages:

    psycopg2  

Shell commands:

    sudo su postgres
    createuser -R -S -D -P datavaalit
    createdb -T template0 -O datavaalit -l fi_FI.UTF8 -E UTF8 datavaalit
    # The location of the SQL scripts might vary on distribution.
    cd /usr/share/postgresql/9.1/contrib/postgis-1.5/
    psql -d datavaalit -f postgis.sql
    psql -d datavaalit -f spatial_ref_sys.sql
    psql -d datavaalit -c "GRANT ALL ON geography_columns TO PUBLIC;"
    psql -d datavaalit -c "GRANT ALL ON geometry_columns TO PUBLIC;"
    psql -d datavaalit -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"


Database creation
=================

Shell commands:

    ./manage.py syncdb --all  
    ./manage.py migrate --fake  


Populating the database
=======================

The Finnish geospatial files require a bleeding edge version of python-gdal.

Ubuntu:

    sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
    apt-get update
    apt-get install python-gdal libgdal1 libproj-dev

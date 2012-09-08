Postgres installation
=====================

Ubuntu/Debian packages:
    libpq-dev postgresql-9.1-postgis postgresql postgresql-9.1-contrib

PIP packages:
    psycopg2 

Shell commands:
    sudo su postgres
    createuser -R -S -D -P datavaalit
    createdb -T template_postgis -O datavaalit -E UTF8 datavaalit

Database creation
=================

Shell commands:
    ./manage.py syncdb --all
    ./manage.py migrate --fake

Populating the database
=======================

The Finnish geospatial files require a bleeding edge version of python-gdal.

    sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
    apt-get update
    apt-get install python-gdal libgdal1


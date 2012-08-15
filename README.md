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

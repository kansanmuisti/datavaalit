#!/usr/bin/env python

import sys
import logging
from optparse import OptionParser
import requests_cache

from importers import importer_list, Backend
from importers.utils.http import HttpFetcher
import importers.list

importer_objs = []
logger = None

def init_logging(debug=False):
    logger = logging.getLogger("importer")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    fh = logging.FileHandler('datavaalit.log')
    fh.setLevel(logging.DEBUG)
    if debug:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.propagate = 0
    return logger

def run_import(data_type, run_only=None, **kwargs):
    for imp in importer_objs:
        import_func = getattr(imp, "import_%s" % data_type, None)
        if run_only and imp.name != run_only:
            continue
        if import_func:
            logger.info("Running importer '%s' for %s" % (imp.name, data_type))
            import_func(**kwargs)

parser = OptionParser()
parser.add_option("--list", help="list all importers", dest="list",
                  action="store_true")
parser.add_option("--inspect", help="inspect importer", dest="inspects",
                  action="append")
parser.add_option("--import", help="import data", dest="imports",
                  action="append")
parser.add_option("--select", help="run only selected importer", dest="select_importer",
                  action="store")
parser.add_option("--django", help="use Django backend", dest="django",
                  action="store_true")
parser.add_option("--replace", help="replace existing data in DB", dest="replace",
                  action="store_true")
parser.add_option("-v", "--verbose", help="verbose output", dest="verbose",
                  action="store_true")
parser.add_option("--disable-cache", help="Disable file cache", dest="disable_cache",
                  action="store_true")

# TODO: Parses option dependencies could be handled better. Backlog option is
# relevant only for importers that import updating data. Backlog can be used
# if there is a set of files (time series) that needs to be imported in order
# to retain the temporal order of data items
parser.add_option("-b", "--backlog", help="Import from backlog", dest="backlog",
                  action="store_true", default=False)

(options, args) = parser.parse_args()

if options.list:
    print "%-15s %-40s" % ("name", "description")
    print "-" * 51
    for imp in importer_list:
        print "%-15s %-40s" % (imp.name, imp.description)

if options.inspects:
    for ins_imp in options.inspects:
        print "%-15s" % ins_imp
        print "-" * 15

if options.imports:
    backend = None
    DATA_TYPES = ("elections", "parties", "candidates", "prebudgets", 
                  "prebudgets_csv")

    for imp in options.imports:
        if imp not in DATA_TYPES:
            sys.stderr.write("Unsupported data type '%s'.\nSupported data types:\n" % imp)
            for dt in DATA_TYPES:
                sys.stderr.write("  %s\n" % dt)
            exit(1)

    http = HttpFetcher()

    if not options.disable_cache:
        cache_dir = ".cache"
        http.set_cache_dir(cache_dir)
        requests_cache.configure("importers")

    if options.django:
        from importers.backends.django import DjangoBackend

        # We need to start logging after Django initializes
        # because Django can be configured to reset logging.
        logger = init_logging(debug=options.verbose)

        if not options.disable_cache:
            logger.debug("Setting up HTTP cache in %s" % cache_dir)
        else:
            logger.debug("HTTP caching disabled")
        
        backend = DjangoBackend(logger, replace=options.replace)
    else:
        logger = init_logging(debug=options.verbose)
        
        if options.cache:
            logger.debug("Setting up cache in %s" % cache_dir)
        else:
            logger.debug("Cache disabled")
        
        backend = Backend(logger, replace=options.replace)

    for imp_class in importer_list:
        if options.select_importer:
            if imp_class.name != options.select_importer:
                continue
        imp_obj = imp_class("data", http, logger, backend)
        importer_objs.append(imp_obj)
    else:
        if options.select_importer and len(importer_objs) == 0:
            sys.stderr.write("Importer '%s' not found.\n" % options.select_importer)
            exit(1)

    for dt in DATA_TYPES:
        if dt in options.imports:
            if options.backlog:
                run_import(dt, run_only=options.select_importer, backlog=True)
            else:
                run_import(dt, run_only=options.select_importer)

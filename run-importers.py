#!/usr/bin/env python

import logging
from optparse import OptionParser
import requests_cache

from importers import importer_list, Backend
from importers.utils.http import HttpFetcher
import importers.list

importer_objs = []

def init_logging(debug=False):
    logger = logging.getLogger("importer")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    if debug:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def run_import(data_type):
    for imp in importer_objs:
        import_func = getattr(imp, "import_%s" % data_type)
        if import_func:
            import_func()


parser = OptionParser()
parser.add_option("--list", help="list all importers", dest="list",
                  action="store_true")
parser.add_option("--inspect", help="inspect importer", dest="inspects",
                  action="append")
parser.add_option("--import", help="import data", dest="imports",
                  action="append")
parser.add_option("--django", help="use Django backend", dest="django",
                  action="store_true")
parser.add_option("--replace", help="replace existing data in DB", dest="replace",
                  action="store_true")
parser.add_option("-v", "--verbose", help="verbose output", dest="verbose",
                  action="store_true")

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
    DATA_TYPES = ("parties", "candidates")
    logger = init_logging(debug=options.verbose)
    http = HttpFetcher()
    http.set_cache_dir(".cache")
    requests_cache.configure("importers")

    if options.django:
        from importers.backends.django import DjangoBackend

        backend = DjangoBackend(logger, replace=options.replace)
    else:
        backend = Backend(logger, replace=options.replace)

    for imp_class in importer_list:
        imp_obj = imp_class("data", http, logger, backend)
        importer_objs.append(imp_obj)

    for dt in DATA_TYPES:
        if dt in options.imports:
            run_import(dt)

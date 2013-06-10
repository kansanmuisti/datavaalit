#!/usr/bin/env python

import sys
import logging
from optparse import OptionParser

from exporters import exporter_list, Backend
import exporters.list

exporter_objs = []
logger = None


def init_logging(debug=False):

    logger = logging.getLogger("exporter")
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


def run_export(data_type, run_only=None, **kwargs):

    for exp in exporter_objs:
        export_func = getattr(exp, "export_%s" % data_type, None)
        if run_only and exp.name != run_only:
            continue
        if export_func:
            logger.info("Running exporter '%s' for %s" % (exp.name, data_type))
            export_func(**kwargs)

usage = "usage: %prog [options] datatype"
parser = OptionParser(usage=usage)
parser.add_option("-l", "--list", help="list all importers", dest="list",
                  action="store_true")
parser.add_option("-o", "--outputfile", help="name of the output file", dest="output",
                  action="store_true")
parser.add_option("-f", "--format", help="export format", dest="format",
                  action="store")
parser.add_option("--overwrite", help="overwrite existing file", dest="overwrite",
                  action="store_true")
parser.add_option("-v", "--verbose", help="verbose output", dest="verbose",
                  action="store_true")
parser.add_option("-i", "--info", help="get information on particular exporter", dest="info",
                  action="store")

(options, args) = parser.parse_args()

if options.list:
    print "%-15s %-40s" % ("name", "description")
    print "-" * 51
    for exp in exporter_list:
        print "%-15s %-40s" % (exp.name, exp.description)
    exit(0)

logger = init_logging(debug=options.verbose)
backend = Backend(logger, overwrite=options.overwrite)

if len(args) < 1:
    logger.error("No exporter defined")
elif len(args) > 1:
    logger.error("Only one datatype at a time is supported for an exporter")
else:
    DATA_TYPES = ("prebudgets", "")

    datatype = args[0]

    if datatype not in DATA_TYPES:
        logger.error("Unsupported data type '%s'.\nSupported data types:\n" % datatype)
        for dt in DATA_TYPES:
            sys.stderr.write("  %s\n" % dt)
        exit(1)

    for exp_class in exporter_list:
        if options.select_exporter:
            if exp_class.name != options.select_exporter:
                continue
        exp_obj = exp_class(logger, backend)
        exporter_objs.append(exp_obj)
    else:
        if options.select_exporter and len(exporter_objs) == 0:
            sys.stderr.write("Exporter '%s' not found.\n" % options.select_exporter)
            exit(1)

    for dt in DATA_TYPES:
        if dt in options.imports:
            run_import(dt, run_only=options.select_importer)

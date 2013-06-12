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


def run_export(data_type, *args, **kwargs):

    for exp in exporter_objs:
        export_func = getattr(exp, "export_%s" % data_type, None)
        if export_func:
            logger.info("Running exporter '%s' for %s" % (exp.name, data_type))
            export_func(*args, **kwargs)

usage = "usage: %prog [options] datatype"
parser = OptionParser(usage=usage)
parser.add_option("-l", "--list", help="list all importers", dest="list",
                  action="store_true")
parser.add_option("-o", "--outputfile", help="name of the output file", dest="output",
                  action="store")
parser.add_option("-f", "--format", help="export format", dest="format",
                  action="store")
parser.add_option("--overwrite", help="overwrite existing file", dest="overwrite",
                  action="store_true", default=False)
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

    if not options.output:
        logger.error("No output filename defined for exported data")
        sys.exit(1)

    DATA_TYPES = ("prebudgets", "")

    exp_type = args[0]

    if exp_type not in DATA_TYPES:
        logger.error("Unsupported data type '%s'.\nSupported data types:\n" % exp_type)
        for dt in DATA_TYPES:
            sys.stderr.write("  %s\n" % dt)
        exit(1)

    for exp_class in exporter_list:
        if exp_class.name != exp_type:
                continue
        exp_obj = exp_class(logger, backend)
        exporter_objs.append(exp_obj)
    else:
        if exp_type and len(exporter_objs) == 0:
            sys.stderr.write("Exporter '%s' not found.\n" % exp_type)
            exit(1)

    run_export(exp_type, 'muni', 2012, options.output)

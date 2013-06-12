#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pprint
import logging


class DataExportError(Exception):
    pass


class Backend(object):

    def __init__(self, logger=None, overwrite=False):
        if not logger:
            logger = logging.getLogger(__name__)
        self.logger = logger
        self.overwrite = overwrite

    def submit_prebudgets(self, election, expense_types, candidates):
        '''Expenses argument is an OrderedDict with dicts with candidate name
        as keys and detailed expenses as nested dict pairs.

        Example:
            OrderedDict([('candidate_name1', {expense1 : sum1, expense2 : sum2}),
                         ('candidate_name2', {expense1 : sum1, expense2 : sum2})])

        '''
        print election
        pprint.pprint(expense_types)
        print "Candidate expenses:"
        for cand in candidates:
            pprint.pprint(cand)

        print("Total number of candidates with expenses reported: %d" % len(candidates))


class Exporter(object):

    def __init__(self, logger, backend, overwrite=False):
        self.data = []
        self.logger = logger
        self.backend = backend
        self.overwrite = overwrite

    def write_csv(self, data, filename):

        import csv

        if not self.overwrite and os.path.exists(filename):
            raise IOError('File {0} exists and overwrite is set to False'.format(filename))
        else:
            self.logger.info('Writing csv file...')
            with open(filename, 'wb') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=';',
                                       quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for row in data:
                    csvwriter.writerow(row)

            self.logger.info('Successfully wrote file {0}'.format(filename))

exporter_list = []


def register_exporter(exporter_class):
    if exporter_class in exporter_list:
        return
    exporter_list.append(exporter_class)
    return exporter_class

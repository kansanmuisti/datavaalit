import os
import sys
import pprint
import logging

class DataImportError(Exception):
    pass

class Backend(object):
    def __init__(self, logger=None, replace=False):
        if not logger:
            logger = logging.getLogger(__name__)
        self.logger = logger
        self.replace = replace

    def submit_candidates(self, election, candidates):
        print "Election:"
        pprint.pprint(election)
        print
        print "Candidates:"
        for c in candidates:
            pprint.pprint(c)

    def submit_elections(self, elections):
        print "Elections:"
        for el in elections:
            print "  %s" % el

    def submit_parties(self, parties):
        print "Parties:"
        for p in parties:
            pprint.pprint(p)

    def submit_prebudgets(self, election, expense_types, candidates, advance):
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

class Importer(object):
    def __init__(self, data_path, http, logger, backend, replace=False):
        self.data_path = data_path
        self.http = http
        self.logger = logger
        self.backend = backend
        self.replace = replace


importer_list = []

def register_importer(importer_class):
    if importer_class in importer_list:
        return
    importer_list.append(importer_class)
    return importer_class


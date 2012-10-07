import os
import sys
import pprint

class DataImportError(Exception):
    pass

class Backend(object):
    def __init__(self, logger, replace=False):
        self.logger = logger
        self.replace = replace

    def submit_elections(self, elections):
        print "Elections:"
        for el in elections:
            print "  %s" % el

    def submit_parties(self, parties):
        print "Parties:"
        for p in parties:
            pprint.pprint(p)

    def submit_candidates(self, election, candidates):
        print "Election:"
        pprint.pprint(election)
        print
        print "Candidates:"
        for c in candidates:
            pprint.pprint(c)


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


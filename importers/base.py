import os
import sys
import pprint

class DataImportError(Exception):
    pass

class Backend(object):
    def __init__(self, logger, replace=False):
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
            
    def submit_prebudgets(self, expenses):
        '''Expenses argument is an OrderedDict with dicts with candidate name 
        as keys and detailed expenses as nested dict pairs.
        
        Example:
            OrderedDict([('candidate_name1', {expense1 : sum1, expense2 : sum2}), 
                         ('candidate_name2', {expense1 : sum1, expense2 : sum2})])
         
        '''
        print "Candidate expenses:"
        for candidate, expense_items in expenses.iteritems():
            any_expenses = False
            print("%s:" % (candidate))
            for item in expense_items:
                
                # Remember, expense_item is a tuple (item, (sum, timstamp))
                if expense_items[item][0] and expense_items[item][0] > 0.0: 
                    if item == 'total':
                        print(' ')
                    print("  %s: %s euros (%s)" % (item, expense_items[item][0], expense_items[item][1]))
                    any_expenses = True
                if not any_expenses:
                    print("  No reported expenses")
                    break
                
            print(' ')

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


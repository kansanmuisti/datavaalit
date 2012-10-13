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
            
    def submit_prebudgets(self, expenses, expense_types):
        '''Expenses argument is an OrderedDict with dicts with candidate name 
        as keys and detailed expenses as nested dict pairs.
        
        Example:
            OrderedDict([('candidate_name1', {expense1 : sum1, expense2 : sum2}), 
                         ('candidate_name2', {expense1 : sum1, expense2 : sum2})])
         
        '''
        print "Candidate expenses:"
        n_expenses = len(expenses)
        for candidate_expenses in expenses:
            any_expenses = False
            print("%s:" % (candidate_expenses.pop('first_names') + ' ' + candidate_expenses.pop('last_name')))
            print("  Municipality: %s" % candidate_expenses.pop('municipality'))
            print("  Submitted: %s" % candidate_expenses.pop('timestamp'))
            for key, value in candidate_expenses.iteritems():

                if key and value > 0.0: 
                    print("  %s: %s euros" % (key, value))
                    if key == 'total':
                        print(' ')
                    any_expenses = True
                if not any_expenses:
                    print("  No reported expenses")
                    break
                
            print(' ')
            
        print("Total number of expenses reported: %s" % n_expenses)
        
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


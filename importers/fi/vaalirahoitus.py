from collections import OrderedDict
import csv
#from web.utils.ucsv import unicode_csv_reader
import datetime
from HTMLParser import HTMLParser

from importers import Importer, register_importer

@register_importer
class VaalirahoitusImporter(Importer):
    # FIXME: what is "name" actually referring to?
    name = 'vrv'
    description = 'import candidate election budget (expenses + funding) from vaalirahoitusvalvonta.fi'
    country = 'fi'
    
    def import_prebudgets(self):
        
        # Create the necessary field mappings for different expense types
        EXPENSE_TYPES = [
             {'type': 'total',         'index': 7},
             {'type': 'printed_media', 'index': 8},
             {'type': 'radio',         'index': 9},
             {'type': 'television',    'index': 10},
             {'type': 'web',           'index': 11},
             {'type': 'other_media',   'index': 12},
             {'type': 'outdoors_ads',  'index': 13},
             {'type': 'print_ads',     'index': 14},
             {'type': 'planning',      'index': 15},
             {'type': 'rallies',       'index': 16},
             {'type': 'paid_income',   'index': 17},
             {'type': 'other',         'index': 18}
        ]
        
        URL = "http://www.vaalirahoitusvalvonta.fi/fi/index/vaalirahailmoituksia/raportit/Tietoaineistot/E_EI_KV2012.csv"
        
        # A list to hold reported expenses
        expenses = []
        
        self.logger.info("Fetching URL %s" % URL)
        
        s = self.http.open_url(URL, self.name)
        
        lines = [l for l in s.split('\n')]
        
        # In case there are HTML specific characters, escape them
        #parser = HTMLParser()
        #lines = [parser.unescape(line) for line in lines]
        
        # TODO: quotechar could be used here. However, quotechars can break
        # the read-in
        reader = csv.reader(lines, delimiter=';')
        
        # Fill in the field mapping descriptors
        header = reader.next()
        for expense_type in EXPENSE_TYPES:
            expense_type['description'] = header[expense_type['index']].decode('utf-8').strip("'")
        
        for row in reader:
            
            #row = [item.decode('utf-8') for item in row]
            
            # If there are no items for some reason, continue
            if len(row) < 1:
                continue
            
            # Strip whitespaces form row
            row = [x.strip() for x in row]
            # Strip quotochars form row, TODO: this could be done more 
            # gracefully as part of the read-in
            row = [x.strip("'") for x in row]
            # Replaces commas with dots in decimal delimiters
            row = [x.replace(",", ".") for x in row]
            
            # Create another ordered dict to hold the expenses of an individual
            # candidate
            candidate_expenses = OrderedDict()
            
            # TODO: implement name parsing (several names and canonical name)
            # first_names = row[0], last_name = row[1]
            candidate_expenses['first_names'] = row[0].decode('utf-8')
            candidate_expenses['last_name'] = row[1].decode('utf-8')
            candidate_name = candidate_expenses['first_names'] + ' ' + candidate_expenses['last_name']
            
            # Timestamp is used to record information on when information is 
            # recorded. Django DateTimeField requires YYYY-MM-DD HH:MM
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            
            def to_float(x, tag=candidate_name):
                '''Tries to coerce euro sums into floats.
                '''
                if tag:
                    msg = " (%s)" % tag
                else:
                    msg = ""
                try:
                    if x != '':
                        fx = float(x)
                        if fx < 0:
                            raise ValueError("Spent euros negative")
                        else:
                            return(fx)
                    else:
                        return(None)
                except ValueError, e:
                    self.logger.warning("Bad value for euros%s: %s" % (msg, e))
                    return(None)
            
            # Voting district/municipality is needed in order to identidy 
            # candidate. TODO: should the field mapping be done in some other
            # way? NOTE: key 'municipality' is ok here, but could be something
            # else in some other types of elections
            candidate_expenses['municipality'] = row[3]
            
            for expense_type in EXPENSE_TYPES:
                # Only record the expense type if there is a value associated 
                # to it
                value = to_float(row[expense_type['index']])
                if value:
                    candidate_expenses[expense_type['type']] = value
            
            candidate_expenses['timestamp'] = now
            
            expenses.append(candidate_expenses)
        
        # EXPENSE_TYPES is also returned; backend may have to populate e.g. a 
        # DB table with the information
        self.backend.submit_prebudgets(expenses, EXPENSE_TYPES)
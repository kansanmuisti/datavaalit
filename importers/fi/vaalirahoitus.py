# -*- coding: utf-8 -*-

from collections import OrderedDict
import csv
#from web.utils.ucsv import unicode_csv_reader
import datetime
from HTMLParser import HTMLParser

from importers import Importer, register_importer

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

BACKLOG_URL = 'http://tmp.ypcs.fi/data/kunnallisvaalit2012/?C=M%3BO%3DD'

@register_importer
class VaalirahoitusImporter(Importer):
    
    name = 'vrv'
    description = 'import candidate election budget (expenses + funding) from vaalirahoitusvalvonta.fi'
    country = 'fi'
    
    def _import_prebudgets_from_csv(self, reader, timestamp):
        
        # A list to hold reported expenses
        expenses = []
        
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
            candidate_expenses['first_names'] = row[0]
            candidate_expenses['last_name'] = row[1]
            candidate_name = candidate_expenses['first_names'] + ' ' + candidate_expenses['last_name']
            
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
            
            # Voting district/municipality and election identifier are  needed 
            # in order to identidy candidate. TODO: should the field mapping be 
            # done in some other way? NOTE: key 'municipality' is ok here, but 
            # could be something else in some other types of elections
            candidate_expenses['election'] = {'type': 'muni', 'year': 2012}
            candidate_expenses['municipality'] = row[3]
            
            for expense_type in EXPENSE_TYPES:
                # Only record the expense type if there is a value associated 
                # to it
                value = to_float(row[expense_type['index']])
                if value:
                    candidate_expenses[expense_type['type']] = value
            
            candidate_expenses['timestamp'] = timestamp
            
            expenses.append(candidate_expenses)
        
        # EXPENSE_TYPES is also returned; backend may have to populate e.g. a 
        # DB table with the information
        self.backend.submit_prebudgets(expenses, EXPENSE_TYPES)
    
    def import_prebudgets(self, backlog=False):
           
        # Construct a list of tuples, wher in each tuple the first item is the
        # actial url and the second one is a timestamp describing when the 
        # information was recorded
           
        if backlog:
            from lxml import html
            import urlparse
            dom = html.parse(BACKLOG_URL).getroot()
            csv_files = [link for link in dom.xpath('//a/@href') if link.endswith('.csv')]
            csv_urls = []
            for csv_file in csv_files:
                # Checking the file name should be part of the xpath query
                if 'ilmoitukset' in csv_file:
                    url = urlparse.urljoin(BACKLOG_URL, csv_file)
                    # Get the timestamp from the file name which is of format
                    # 'ehdokkaat_rahoitusrivit_YYYY-MM-DD_HHMM.csv'
                    # TODO: regex would be more elegant
                    timestamp = csv_file.split('_', 2)[2].replace('.csv', '')
                    timestamp = timestamp.replace('_', ' ')
                    # FIXME: this is just waiting to get broken. Insert ':' in 
                    # between HH and MM (apparently demanded by Django)
                    timestamp = timestamp[:-2] + ':' + timestamp[-2:]
    
                    csv_urls.append((url, timestamp))
        else:
            # TODO: hardcoded urls should be defined consistently as globals etc.
            # TODO: timestamp should be fetched from the URL header
            csv_urls = [
                        ("http://www.vaalirahoitusvalvonta.fi/fi/index/vaalirahailmoituksia/raportit/Tietoaineistot/E_EI_KV2012.csv",
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))]
            
        for URL in csv_urls:
            self.logger.info("Fetching URL %s" % URL[0])
            
            s = self.http.open_url(URL[0], self.name)
            
            lines = [l for l in s.split('\n')]
            
            # In case there are HTML specific characters, get rid of them
            lines = [line.replace('&agrave;', 'á').replace('&uuml;', 'ü').replace('&eacute;', 'é') for line in lines]
            
            # TODO: quotechar could be used here. However, quotechars can break
            # the read-in
            reader = csv.reader(lines, delimiter=';')
            
            self._import_prebudgets_from_csv(reader, URL[1])
        
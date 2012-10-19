# -*- coding: utf-8 -*-

from collections import OrderedDict
import csv
#from web.utils.ucsv import unicode_csv_reader
import datetime
import re
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
        candidates = []

        # Fill in the field mapping descriptors
        header = reader.next()
        expense_types = []
        for expense_type in EXPENSE_TYPES:
            et = {'name': expense_type['type']}
            et['description'] = header[expense_type['index']].decode('utf-8').strip("'")
            expense_types.append(et)

        for row in reader:
            row = [item.decode('utf-8') for item in row]

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
            cand = {}

            # TODO: implement name parsing (several names and canonical name)
            # first_names = row[0], last_name = row[1]
            cand['first_names'] = row[0]
            cand['last_name'] = row[1]
            candidate_name = cand['first_names'] + ' ' + cand['last_name']
            cand['municipality'] = {'name': row[3]}

            expenses = []
            for expense_type in EXPENSE_TYPES:
                # Only record the expense type if there is a value associated
                # to it
                value = row[expense_type['index']]
                if not value:
                    continue
                value = value.replace(',', '.')
                # Just make sure the number converts into a float.
                # We won't pass the converted value because we might
                # store the value in a DecimalField.
                try:
                    x = float(value)
                except:
                    self.logger.error("%s %s: invalid value: %s" % (candidate_name, expense_type['type'], value))
                    continue
                expenses.append({'type': expense_type['type'], 'value': value})

            cand['expenses'] = expenses
            cand['timestamp'] = timestamp

            candidates.append(cand)

        election = {'type': 'muni', 'year': 2012}
        # EXPENSE_TYPES is also returned; backend may have to populate e.g. a
        # DB table with the information
        self.backend.submit_prebudgets(election, expense_types, candidates)

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

            REPLACE_TABLE = {
                '&agrave;': 'à',
                '&egrave;': 'è',
                '&uuml;': 'ü',
                '&eacute;': 'é',
                '&aacute;': 'á',
            }
            changed = []
            html_ent = re.compile(r"&[a-z]+;")
            for line in lines:
                if html_ent.search(line):
                    for r in REPLACE_TABLE.keys():
                        line = line.replace(r, REPLACE_TABLE[r])
            	if html_ent.search(line):
            	    self.logger.error("Invalid character in line: '%s'" % line)
            	    raise Exception("Invalid characters in input")
                changed.append(line)
            lines = changed
            # TODO: quotechar could be used here. However, quotechars can break
            # the read-in
            reader = csv.reader(lines, delimiter=';')

            self._import_prebudgets_from_csv(reader, URL[1])


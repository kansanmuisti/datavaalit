import csv
from collections import OrderedDict
import datetime

from importers import Importer, register_importer

@register_importer
class VaalirahoitusImporter(Importer):
    # FIXME: what is "name" actually referring to?
    name = 'vrv'
    description = 'import candidate election budget (expenses + funding) from vaalirahoitusvalvonta.fi'
    country = 'fi'
    
    def import_prebudgets(self):
        
        URL = "http://www.vaalirahoitusvalvonta.fi/fi/index/vaalirahailmoituksia/raportit/Tietoaineistot/E_EI_KV2012.csv"
        
        candidates_odict = OrderedDict()
        
        self.logger.info("Fetching URL %s" % URL)
        
        # QUESTION: self.name (prefix) related to cache operations?
        s = self.http.open_url(URL, self.name)
        
        lines = [l for l in s.split('\n')]
        
        # TODO: quotechar could be used here. However, quotechars can break
        # the read-in
        reader = csv.reader(lines, delimiter=';')
        
        # Skip the header
        reader.next()
        
        for row in reader:
            
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
            
            # TODO: implement name parsing (several names and canonical name)
            
            # first_names = row[0], last_name = row[1]
            candidate_name = row[0].decode('utf8') + ' ' + row[1].decode('utf8')
            
            # Timestamp is used to record information on when information is 
            # recorded
            now = datetime.datetime.now().strftime('%d-%b-%Y %H:%M')
            
            def to_float(x):
                '''Tries to coerce euro sums into floats.
                '''
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
                    self.logger.warning("Bad value for spent euros: %s" % e)
            
            expenses = OrderedDict()
            
            expenses['printed_media'] = (to_float(row[8]), now)
            expenses['radio'] = (to_float(row[9]), now)
            expenses['television'] = (to_float(row[10]), now)
            expenses['web'] = (to_float(row[11]), now)
            expenses['other_media'] = (to_float(row[12]), now)
            expenses['outdoors_adds'] = (to_float(row[13]), now)
            expenses['print_adds'] = (to_float(row[14]), now)
            expenses['planning'] = (to_float(row[15]), now)
            expenses['rallies'] = (to_float(row[16]), now)
            expenses['paid_income'] = (to_float(row[17]), now)
            expenses['other'] = (to_float(row[18]), now)
            expenses['total'] = (to_float(row[7]), now)
            
            candidates_odict[candidate_name] = expenses
        
        self.backend.submit_prebudgets(candidates_odict)
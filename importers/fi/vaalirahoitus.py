import csv

from importers import Importer, register_importer

@register_importer
class VaalirahoitusImporter(Importer):
    # FIXME: what is "name" actually referring to?
    name = 'vaalit.fi'
    description = 'Import candidate elecction budget (expenses + funding from vaalit.fi'
    country = 'fi'
    
    
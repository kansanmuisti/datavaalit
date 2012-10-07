import os
import json
import types

from importers import Importer, register_importer

@register_importer
class InternalImporter(Importer):
    name = "internal"
    description = "import from repository internal file"

    def _import_stuff(self, data_type):
        data = self.js_data[data_type]
        func = getattr(self.backend, "submit_%s" % data_type)
        func(data)

    def __init__(self, *args, **kwargs):
        super(InternalImporter, self).__init__(*args, **kwargs)
        try:
            f = open(os.path.join(self.data_path, 'internal.json'))
        except IOError:
            return
        s = f.read()
        self.js_data = json.loads(s)
        data_types = self.js_data.keys()

        for dt in data_types:
            #
            # Python rocks
            #
            func = lambda self: self._import_stuff(dt)
            method_func = types.MethodType(func, self)
            setattr(self, "import_%s" % dt, method_func)

    def import_elections(self):
        return


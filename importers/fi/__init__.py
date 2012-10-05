from importers import DataImportError, Importer

PARTIES = (
    'KD',
    'Kesk.',
    'Kok.',
    'PS',
    'RKP',
    'SDP',
    'Vas.',
    'Vihr.',
    'SKP',
)

PARTY_MAP = {
    'VAS': 'Vas.',
    'SDP': 'SDP',
    'KOK': 'Kok.',
    'VIHR': 'Vihr.',
    'KESK': 'Kesk.',
    'PS': 'PS',
    'KD': 'KD',
    'SKP': 'SKP',
    'RKP': 'RKP',
}

def canonize_party(party):
    party_upper = party.upper()
    if party_upper in PARTY_MAP:
        party = PARTY_MAP[party_upper]

    if party not in PARTIES:
        raise DataImportError("party %s not found" % party)
    return party

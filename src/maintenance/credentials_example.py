import datetime


SITE_CREDENTIALS = {
    'site1': {
        'type': 'Rosneft',
        'login': '',
        'password': '',
        'url': ''
    }
}

ORGANIZATION_CREDENTIALS = {
    'organization1': {
        'inn': '123456789012',
        'kpp': '123456789',
        'name': 'Организазация 1',
        'name_full': 'Организазация 1 ООО'
    }
}

CONTRACTS_CREDENTIALS = {
    'contract1': {
        'id_external': '123456789',
        'type': 'processing',
        'number': '123456789',
        'date': datetime.datetime.strptime('01/01/10', '%d/%m/%y')
    }
}

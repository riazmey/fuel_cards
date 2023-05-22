
def filling_data():

    from maintenance.credentials import SITE_CREDENTIALS
    from maintenance.credentials import ORGANIZATION_CREDENTIALS
    from maintenance.credentials import CONTRACTS_CREDENTIALS

    def _site_credentials(name: str, key: str) -> str:
        credentials = SITE_CREDENTIALS.get(name, {})
        return credentials.get(key, '')

    def _organization_credentials(name: str, key: str) -> str:
        credentials = ORGANIZATION_CREDENTIALS.get(name, {})
        return credentials.get(key, '')

    def _contract_credentials(name: str, key: str) -> str:
        credentials = CONTRACTS_CREDENTIALS.get(name, {})
        return credentials.get(key, '')

    result = [
        {
            'inn': _organization_credentials('organization1', 'inn'),
            'kpp': _organization_credentials('organization1', 'kpp'),
            'name': _organization_credentials('organization1', 'name'),
            'name_full': _organization_credentials('organization1', 'name_full'),
            'email': _organization_credentials('organization1', 'email'),
            'sites': [
                {
                    'type': _site_credentials('site1', 'type'),
                    'login': _site_credentials('site1', 'login'),
                    'password': _site_credentials('site1', 'password'),
                    'url': _site_credentials('site1', 'url')
                }
            ],
            'contracts': [
                {
                    'id_external': _contract_credentials('contract1', 'id_external'),
                    'type': _contract_credentials('contract1', 'type'),
                    'number': _contract_credentials('contract1', 'number'),
                    'date': _contract_credentials('contract1', 'date')
                }
            ]
        }
    ]

    return result

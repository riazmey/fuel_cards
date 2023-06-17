import csv
import os
import importlib
import datetime

from cards.models import *
from django.db import transaction

from maintenance.data import *


def do_filling():

    class DataCSVFiles:
        name_apps = []
        files = []

        class CSVFile:
            def __init__(self, **kwargs):
                self.app = kwargs.get('app', '')
                self.model = kwargs.get('model', '')
                self.file = kwargs.get('file', '')

        @classmethod
        @transaction.atomic
        def import_data(cls) -> None:
            cls._read_files()
            for data_file in cls.files:
                print(f'    File: {data_file.file} (app: {data_file.app}, model: {data_file.model})')
                model = getattr(importlib.import_module(f'{data_file.app}.models'), data_file.model)
                with open(data_file.file) as csvfile:
                    reader = csv.DictReader(csvfile)
                    print(reader.fieldnames)
                    for row in reader:
                        print(f'        {row}')
                        row['id'] = int(row.get('id'))
                        p = model(**row)
                        p.save()

        @classmethod
        def _add_item(cls, **kwargs) -> None:
            item = cls.CSVFile(**kwargs)
            if item.app and item.app in cls.name_apps:
                cls.name_apps.append(item.app)
            cls.files.append(item)

        @classmethod
        def _read_files(cls) -> None:
            dir_base = os.getcwd()
            dir_csv = f'{dir_base}/maintenance/csv_files/'
            for filename in os.listdir(dir_csv):
                sub_str = filename.split('.')
                if len(sub_str) != 3:
                    continue
                if sub_str[2] != 'csv':
                    continue
                file_name_full = f'{dir_csv}{filename}'
                cls._add_item(app=sub_str[0], model=sub_str[1], file=file_name_full)

    def input_initial_data():

        for data_organization in filling_data():
            inn = data_organization.get('inn', '')
            kpp = data_organization.get('kpp', '')
            name = data_organization.get('name', '')
            name_full = data_organization.get('name_full', '')
            email = data_organization.get('email', '')
            sites = data_organization.get('sites')
            contracts = data_organization.get('contracts')

            defaults = {'name': name, 'name_full': name_full, 'email': email}
            organization_obj, created = Organization.objects.update_or_create(inn=inn, kpp=kpp, defaults=defaults)

            for data_contract in contracts:
                id_external = data_contract.get('id_external', '')
                type_contract = data_contract.get('type')
                number = data_contract.get('number', '')
                date = data_contract.get('date', '')
                type_obj = EnumContractType.objects.get(name=type_contract)
                defaults = {'id_external': id_external, 'number': number, 'date': date}
                contract_obj, created = Contract.objects.update_or_create(organization=organization_obj, type=type_obj,
                                                                          id_external='ISS089296', defaults=defaults)
            for data_site in sites:
                type_site = data_site.get('type')
                login = data_site.get('login')
                password = data_site.get('password')
                url = data_site.get('url')
                type_obj = EnumSiteType.objects.get(name=type_site)

                defaults = {'login': login, 'password': password}
                site_obj, created = Site.objects.update_or_create(type=type_obj, organization=organization_obj,
                                                                  url=url, defaults=defaults)

    def import_from_sites(name_function: str):
        sites = Site.objects.all()
        params = {'verbose': True}
        for site in sites:
            function = getattr(site.api, name_function)
            function(**params)

    def import_transactions(begin: datetime, end: datetime):
        sites = Site.objects.all()
        params = {'begin': begin, 'end': end, 'verbose': True}
        for site in sites:
            site.api.import_transactions(**params)

    print(f'Начало процесса первоначального заполнения')
    print(f'')

    print(f'1. Заполнение предопределенных данных (перечисления)...')
    DataCSVFiles.import_data()
    print(f'')

    print(f'2. Ввод начальных данных...')
    input_initial_data()
    print(f'')

    print(f'3. Импорт остатков на лицевых счетах сайтов...')
    import_from_sites('import_balance')
    print(f'')

    print(f'4. Импорт товаров сайтов...')
    import_from_sites('import_goods')
    print(f'')

    print(f'5. Импорт топливных карт сайтов...')
    import_from_sites('import_cards')
    print(f'')

    print(f'6. Импорт транзакций...')
    begin = datetime.datetime.strptime('01/01/10 00:00:00', '%d/%m/%y %H:%M:%S')
    end = datetime.datetime.strptime('31/12/25 00:00:00', '%d/%m/%y %H:%M:%S')
    import_transactions(begin, end)
    print(f'')

    print(f'7. Импорт лимитов топливных карт...')
    import_from_sites('import_limits')
    print(f'')
    print(f'Процесс начального заполнения завершен успешно')

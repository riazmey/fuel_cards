"""
    Script to import data from .csv file to Model Database DJango
    To execute this script run:
                                1) manage.py shell
                                2) exec(open('initial_filling.py').read())
"""

import csv
import os
import importlib

from cards.models import *
from django.db import transaction
from credentials import CREDENTIALS

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
        dir_csv = f'{dir_base}/csv_files/'
        for filename in os.listdir(dir_csv):
            sub_str = filename.split('.')
            if len(sub_str) != 3:
                continue
            if sub_str[2] != 'csv':
                continue
            file_name_full = f'{dir_csv}{filename}'
            cls._add_item(app=sub_str[0], model=sub_str[1], file=file_name_full)

def input_initial_data():
    defaults = {'name': 'Кубис Транс', 'name_full': 'Кубис Транс ООО', 'email': ''}
    organization, created = Organization.objects.update_or_create(inn='7725755403', kpp='772801001',
                                                                  defaults=defaults)

    type_obj = EnumContractType.objects.get(name='processing')
    defaults = {'number': 'ISS089296', 'date': datetime.datetime.strptime('01/01/19 00:00:00', '%d/%m/%y %H:%M:%S')}
    contract, created = Contract.objects.update_or_create(organization=organization, type=type_obj,
                                                          id_external='ISS089296', defaults=defaults)
    for credential in CREDENTIALS:
        type_obj = EnumSiteType.objects.get(name=credential.type)
        defaults = {'login': credential.login, 'password': credential.password}
        site, created = Site.objects.update_or_create(type=type_obj, organization=organization,
                                                      url=credential.url, defaults=defaults)


def import_from_sites(name_function: str):
    sites = Site.objects.all()
    for site in sites:
        function = getattr(site.api, name_function)
        function()


def import_transactions(begin: datetime, end: datetime):
    sites = Site.objects.all()
    for site in sites:
        site.api.import_transactions(begin, end)


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
print(f'6. Импорт лимитов топливных карт...')
import_from_sites('import_limits')
print(f'')
print(f'7. Импорт транзакций...')
begin = datetime.datetime.strptime('01/01/10 00:00:00', '%d/%m/%y %H:%M:%S')
end = datetime.datetime.strptime('31/12/25 00:00:00', '%d/%m/%y %H:%M:%S')
import_transactions(begin, end)
print(f'')
print(f'Процесс начального заполнения завершен успешно')

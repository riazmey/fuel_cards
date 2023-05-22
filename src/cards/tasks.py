from celery import shared_task

from cards.models import *
from django.utils import timezone
from django.template.context_processors import debug


def import_from_sites(name_function: str) -> (list, bool):
    result = []
    success = True
    sites = Site.objects.all()
    params = {'verbose': debug}
    for site in sites:
        function = getattr(site.api, name_function)
        data, success = function(**params)
        if not success:
            break
        if isinstance(data, list):
            total_data = len(data)
            result += data
            if debug:
                print(f'    Сайт {site}. Загружено/обновлено записей: {total_data}')
        else:
            result.append(data)
    return result, success


@shared_task(name='Загрузка остатков на лицевых счетах (по всем сайтам)')
def import_balance():
    name_function = 'import_balance'
    if debug:
        print('Импорт остатков на лицевых счетах сайтов...')
    data, success = import_from_sites(name_function)
    return success


@shared_task(name='Загрузка товаров (по всем сайтам)')
def import_goods():
    name_function = 'import_goods'
    if debug:
        print('Импорт товаров сайтов...')
    data, success = import_from_sites(name_function)
    return success


@shared_task(name='Загрузка топливных карт (по всем сайтам)')
def import_cards():
    name_function = 'import_cards'
    if debug:
        print('Импорт топливных карт сайтов...')
    data, success = import_from_sites(name_function)
    return success


@shared_task(name='Загрузка лимитов топливных карт (по всем сайтам)')
def import_limits():
    name_function = 'import_limits'
    if debug:
        print('Импорт лимитов топливных карт...')
    data, success = import_from_sites(name_function)
    return success


@shared_task(name='Загрузка транзакций (за прошедший период: параметры timedelta) (по всем сайтам)')
def import_transactions(**kwargs):
    success = True
    sites = Site.objects.all()
    end = timezone.now()
    begin = end - timedelta(**kwargs)
    params = {'begin': begin, 'end': end, 'verbose': debug}
    if debug:
        print(f'Импорт транзакций (с {begin} по {end})...')
    for site in sites:
        data, success = site.api.import_transactions(**params)
        if not success:
            break
        total_data = len(data)
        print(f'    Сайт {site}. Загружено/обновлено записей: {total_data}')
    return success

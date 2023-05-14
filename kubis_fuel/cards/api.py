import math
import multiprocessing
from threading import Thread
from datetime import timedelta

import pytz
import requests
import json

from django.utils import timezone
from django.db.models.functions import datetime


class Petrolplus:
    pass


class Rosneft:
    class URNs:
        get_balance = '/api/emv/v1/ContractBalance'
        get_list_goods = '/api/emv/v1/GetGoodsList'
        get_limits_by_card = '/api/emv/v1/GetCardLimits'
        get_list_cards = '/api/emv/v1/GetCardsByContract'
        get_list_transactions_by_card = '/api/emv/v2/GetOperByCard'
        get_list_transactions = '/api/emv/v2/GetOperByContract'
        set_limit_by_card = '/api/emv/v1/CreateCardLimit'
        del_limit_by_card = '/api/emv/v1/EditCardLimit'
        update_limit_by_card = '/api/emv/v1/DeleteCardLimit'

    def get_balance(self) -> (dict, bool):
        result = {'date': '', 'balance': 0.0, 'credit': 0.0}
        data, received = self._request_get(self.URNs.get_balance)
        if received:
            result.update(date=timezone.now())
            result.update(balance=data.get('Balance', 0.00))
            result.update(credit=data.get('CreditLimit', 0.00))
            return result, True
        return result, False

    def get_list_goods(self) -> (list[dict], bool):
        result = []
        data, received = self._request_get(self.URNs.get_list_goods)
        if received:
            for data_item in data:
                result.append({
                    'id_external': data_item.get('Code', ''),
                    'category': self._name_category(data_item.get('Cat', '')),
                    'name': data_item.get('Name', '')
                })
            return result, True
        return result, False

    def get_list_cards(self) -> (list[dict], bool):
        result = []
        data, received = self._request_get(self.URNs.get_list_cards)
        if received:
            for data_card in data:
                result.append({
                    'number': data_card.get('Num', ''),
                    'status': self._name_status(data_card.get('SCode', ''))
                })
            return result, True
        return result, False

    def get_list_limits_by_card(self, card_number: str) -> (list[dict], bool):
        result = []
        data, received = self._request_get(self.URNs.get_limits_by_card, added_params={'card': card_number})
        if received:
            for data_limit in data:
                limit_type = self._name_limit_type(data_limit.get('GFlag', ''))
                item = ''
                category = ''
                match limit_type:
                    case 'category':
                        category = self._name_category(data_limit.get('GCat', ''))
                    case 'item':
                        item = data_limit.get('GCat', '')
                result.append({
                    'id_external': data_limit.get('Code', ''),
                    'type': limit_type,
                    'item': item,
                    'category': category,
                    'unit': self._name_unit(data_limit.get('Currency', '')),
                    'period': self._name_limit_period(data_limit.get('Prd', '')),
                    'value': data_limit.get('Val', 0.00),
                    'balance': data_limit.get('CurValue', 0.00)
                })
            return result, True
        return result, False

    def get_list_limits(self, list_cards: list) -> (list[dict], bool):
        result = []
        threads = self._threads(list_cards)

        for index in range(len(threads)):
            threads[index]['thread'] = Thread(target=self._get_list_limits_by_thread, args=(threads, index))
            threads[index]['thread'].start()

        for index in range(len(threads)):
            threads[index]['thread'].join()

        index = 0
        for data_thread in threads:
            index += 1
            received = data_thread.get('received', False)
            data_response = data_thread.get('data_response', None)
            if received and isinstance(data_response, list):
                result += data_thread.get('data_response', [])
            else:
                return result, False

        return result, True

    def get_list_transactions(self, **kwargs) -> (list[dict], bool):
        result = []
        card_number = kwargs.get('card_number', '')
        date_begin = kwargs.get('begin')
        date_end = kwargs.get('end')
        periods = self._periods_transaction_requests(date_begin, date_end)
        if card_number:
            for period in periods:
                period['card_number'] = card_number
        threads = self._threads(periods)

        for index in range(len(threads)):
            threads[index]['thread'] = Thread(target=self._get_list_transactions_by_thread,
                                              args=(threads, index))
            threads[index]['thread'].start()

        for index in range(len(threads)):
            threads[index]['thread'].join()

        for data_thread in threads:
            received = data_thread.get('received', False)
            data_response = data_thread.get('data_response', None)
            if received and isinstance(data_response, list):
                result += data_thread.get('data_response', [])
            else:
                return result, False

        return result, True

    def _request_get(self, urn: str, added_params: dict = None) -> (any, bool):
        url_request = f'{self.url}/{urn}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}
        params = {'u': self.login, 'p': self.password, 'contract': self.contract_id, 'type': 'JSON'}
        if added_params:
            params = {**params, **added_params}
        response = requests.get(url_request, headers=headers, json=json.dumps(params), params=params)

        if not response.status_code == 200:
            return response.text, False

        try:
            data = json.loads(response.text)
            return data, True
        except ValueError as error:
            return str(error), False

    def _get_list_limits_by_thread(self, threads: list, index: int) -> None:
        data_request = threads[index].get('data_request')
        if not isinstance(data_request, list):
            return
        result = []
        for card_number in data_request:
            data, received = self.get_list_limits_by_card(card_number)
            if received:
                result.append({'card': card_number, 'limits': data})
            else:
                return
        threads[index]['data_response'] = result
        threads[index]['received'] = True

    def _get_list_transactions_by_thread(self, threads: list, index: int) -> None:
        data_request = threads[index].get('data_request')
        if not isinstance(data_request, list):
            return
        result = []
        for period in data_request:
            data, received = self._get_list_transactions(**period)
            if received:
                result += data
            else:
                return
        threads[index]['data_response'] = result
        threads[index]['received'] = True

    def _get_list_transactions(self, **kwargs) -> (list[dict], bool):
        result = []
        date_begin = kwargs.get('begin')
        date_end = kwargs.get('end')
        card_number = kwargs.get('card_number', '')
        if card_number:
            added_params = {'begin': date_begin.isoformat(), 'end': date_end.isoformat(), 'card': card_number}
            data, received = self._request_get(self.URNs.get_list_transactions_by_card, added_params=added_params)
        else:
            added_params = {'begin': date_begin.isoformat(), 'end': date_end.isoformat()}
            data, received = self._request_get(self.URNs.get_list_transactions, added_params=added_params)
        if received:
            list_data = data.get('OperationList', [])

            if not list_data:
                return result, True

            for data_transaction in list_data:
                type_transaction = self._name_transaction_type(data_transaction.get('Type', ''))
                card = data_transaction.get('Card', ''),
                date = data_transaction.get('Date', '')
                price = data_transaction.get('Price', 0.00)
                price_discount = data_transaction.get('DPrice', 0.00)
                price_with_discount = price + price_discount
                amount = data_transaction.get('Sum', 0.00)
                amount_discount = data_transaction.get('DSum', 0.00)
                amount_with_discount = amount + amount_discount
                date_format = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                date_format = datetime.datetime(year=date_format.year, month=date_format.month, day=date_format.day,
                                                hour=date_format.hour, minute=date_format.minute,
                                                second=date_format.second, tzinfo=pytz.timezone('Europe/Moscow'))

                if not type_transaction or not card:
                    continue

                items = [{
                    'item': data_transaction.get('GCode', ''),
                    'item_description': data_transaction.get('DTL', ''),
                    'quantity': data_transaction.get('Value', 0.00),
                    'price': price,
                    'price_with_discount': price_with_discount,
                    'amount': amount,
                    'amount_with_discount': amount_with_discount
                }]
                result.append({
                    'id_external': data_transaction.get('Code', ''),
                    'type': type_transaction,
                    'card': data_transaction.get('Card', ''),
                    'date': date_format,
                    'details': data_transaction.get('Address', ''),
                    'amount': data_transaction.get('Sum', 0.00),
                    'discount': data_transaction.get('DSum', 0.00),
                    'items': items
                })
            return result, True
        return result, False

    @staticmethod
    def _periods_transaction_requests(begin: datetime, end: datetime) -> list[dict]:
        result = []
        max_period = timedelta(days=30)
        now_date = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
        begin_date = datetime.datetime(year=begin.year, month=begin.month, day=begin.day,
                                       tzinfo=pytz.timezone('Europe/Moscow'))
        end_date = datetime.datetime(year=end.year, month=end.month, day=end.day,
                                     tzinfo=pytz.timezone('Europe/Moscow'))
        if end_date > now_date:
            end_date = datetime.datetime(year=now_date.year, month=now_date.month, day=now_date.day,
                                         tzinfo=pytz.timezone('Europe/Moscow'))
        while begin_date < end_date:
            current_period = {'begin': begin_date, 'end': None}
            begin_date += (max_period - timedelta(seconds=1))
            if begin_date > end_date:
                begin_date = end_date + timedelta(hours=23, minutes=59, seconds=59)
            current_period.update(end=begin_date)
            result.append(current_period)
            begin_date += timedelta(seconds=1)
        return result

    @staticmethod
    def _threads(items: list) -> list:
        result = []
        total_threads = int(round(multiprocessing.cpu_count() * 0.8, 0))
        match multiprocessing.cpu_count():
            case 0:
                total_threads = 1
            case 2:
                total_threads = 2
            case 3:
                total_threads = 2
            case 4:
                total_threads = 3

        for i in range(total_threads):
            result.append({'thread': None, 'data_request': None, 'data_response': None, 'received': False})

        if total_threads > 1:
            if len(items) >= total_threads:
                if (len(items) // total_threads) == (len(items) / total_threads):
                    items_in_list = len(items) / total_threads
                else:
                    items_in_list = math.ceil(len(items) / total_threads)
            else:
                items_in_list = 1
        else:
            items_in_list = len(items)

        items_thread = []
        index_threads = 0
        for i in range(1, len(items) + 1):
            items_thread.append(items[i - 1])
            if (i // items_in_list) == (i / items_in_list):
                data_thread = result[index_threads]
                data_thread.update(data_request=items_thread)
                result[index_threads] = data_thread
                items_thread = []
                index_threads += 1

        if len(items_thread) > 0:
            thread = result[index_threads]
            thread.update(data_request=items_thread)
            result[index_threads] = thread

        index_threads = 0
        while (index_threads + 1) <= total_threads:
            data_request = result[index_threads].get('data_request')
            if not data_request:
                result.pop(index_threads)
                total_threads -= 1
                index_threads -= 1
            index_threads += 1

        return result

    @staticmethod
    def _name_status(name: str) -> str:
        result = 'block'
        if name.strip().lower() == '00':
            result = 'active'
        return result

    @staticmethod
    def _name_category(name: str) -> str:
        result = ''
        match name.strip().lower():
            case 'fuel':
                result = 'fuel'
            case 'service':
                result = 'service'
            case 'goods':
                result = 'goods'
        return result

    @staticmethod
    def _name_unit(name: str) -> str:
        result = ''
        match name.strip().lower():
            case 'c':
                result = 'rub'
            case 'v':
                result = 'litre'
        return result

    @staticmethod
    def _name_limit_period(name: str) -> str:
        result = ''
        match name.strip().lower():
            case 'n':
                result = 'nonrenewable'
            case 'f':
                result = 'day'
            case 'f7':
                result = 'week'
            case 'm':
                result = 'month'
        return result

    @staticmethod
    def _name_limit_type(name: str) -> str:
        result = ''
        match name.strip().lower():
            case 'g':
                result = 'item'
            case 'c':
                result = 'category'
            case 'a':
                result = 'all'
        return result

    @staticmethod
    def _name_transaction_type(type_transaction: int) -> str:
        result = ''
        match type_transaction:
            case 11:
                result = 'sale'
            case 24:
                result = 'return'
        return result


class Tatneft:
    pass

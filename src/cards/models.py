from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models.signals import post_init

from .api import *
from .common import progress_bar


class EnumSiteType(models.Model):
    name = models.CharField(max_length=20, default='', blank=False, verbose_name='Имя')
    repr = models.CharField(max_length=256, default='', blank=False, verbose_name='API сайта')

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'API сайта'
        verbose_name_plural = 'API сайтов'


class EnumCardStatus(models.Model):
    name = models.CharField(max_length=20, default='', blank=False, verbose_name='Имя')
    repr = models.CharField(max_length=256, default='', blank=False, verbose_name='Статус топливной карты')

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'Статус топливной карты'
        verbose_name_plural = 'Статусы топливных карт'


class EnumItemCategory(models.Model):
    name = models.CharField(max_length=20, default='', blank=False, verbose_name='Имя')
    repr = models.CharField(max_length=256, default='', blank=False, verbose_name='Категория товара')

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров'


class EnumUnit(models.Model):
    name = models.CharField(max_length=20, default='', blank=False, verbose_name='Имя')
    is_currency = models.BooleanField(default=False, verbose_name='Является валютой')
    repr = models.CharField(max_length=256, default='', blank=False, verbose_name='Единица измерения')

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерений'


class EnumLimitPeriod(models.Model):
    name = models.CharField(max_length=20, default='', blank=False, verbose_name='Имя')
    repr = models.CharField(max_length=256, default='', blank=False, verbose_name='Тип периода лимита')

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'Тип периода лимита топливной карты'
        verbose_name_plural = 'Типы периодов лимитов топливных карт'


class EnumLimitType(models.Model):
    name = models.CharField(max_length=20, default='', blank=False, verbose_name='Имя')
    repr = models.CharField(max_length=256, default='', blank=False, verbose_name='Тип лимита')

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'Тип лимита топливной карты'
        verbose_name_plural = 'Типы лимитов топливных карт'


class EnumTransactionType(models.Model):
    name = models.CharField(max_length=20, default='', blank=False, verbose_name='Имя')
    repr = models.CharField(max_length=256, default='', blank=False, verbose_name='Тип транзакции')

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'Тип транзакции'
        verbose_name_plural = 'Типы транзакций'


class EnumContractType(models.Model):
    name = models.CharField(max_length=20, default='', blank=False, verbose_name='Имя')
    repr = models.CharField(max_length=256, default='', blank=False, verbose_name='Тип договора')

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'Тип договора'
        verbose_name_plural = 'Типы договоров'


class Organization(models.Model):
    name = models.CharField(max_length=128, default='', blank=False, verbose_name='Наименование (сокращенное)')
    name_full = models.CharField(max_length=255, default='', blank=False, verbose_name='Наименование (полное)')
    inn = models.CharField(max_length=12, default='', blank=False, verbose_name='ИНН')
    kpp = models.CharField(max_length=9, default='', blank=True, verbose_name='КПП')
    email = models.EmailField(max_length=254, default='', blank=True, verbose_name='Электронный адрес (e-mail)')
    repr = models.CharField(max_length=256, default='', blank=True, verbose_name='Организация')

    def save(self, *args, **kwargs):
        self.repr = self.name
        super(Organization, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'


class Customer(models.Model):
    name = models.CharField(max_length=128, default='', blank=False, verbose_name='Наименование (сокращенное)')
    name_full = models.CharField(max_length=255, default='', blank=False, verbose_name='Наименование (полное)')
    inn = models.CharField(max_length=12, default='', blank=False, verbose_name='ИНН')
    kpp = models.CharField(max_length=9, default='', blank=True, verbose_name='КПП')
    email = models.EmailField(max_length=254, default='', blank=True, verbose_name='Электронный адрес (e-mail)')
    repr = models.CharField(max_length=256, default='', blank=True, verbose_name='Клиент')

    def save(self, *args, **kwargs):
        self.repr = self.name
        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Contract(models.Model):
    type = models.ForeignKey(EnumContractType, on_delete=models.PROTECT, db_index=True, blank=False,
                             verbose_name='Тип договора')
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, blank=True, null=True,
                                     verbose_name='Организация')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, blank=True, null=True,
                                 verbose_name='Клиент')
    id_external = models.CharField(max_length=128, default='', blank=True, verbose_name='ID (внешний)')
    number = models.CharField(max_length=40, default='', blank=False, verbose_name='Номер')
    date = models.DateField(default=timezone.now, blank=False, verbose_name='Дата')
    repr = models.CharField(max_length=256, default='', blank=True, verbose_name='Договор')

    def save(self, *args, **kwargs):
        date_repr = self.date.strftime('%d.%m.%Y')
        if self.customer:
            self.repr = f'{self.type} c {self.customer} №{self.number} от {date_repr}'
        elif self.organization:
            self.repr = f'{self.type} c {self.organization} №{self.number} от {date_repr}'
        super(Contract, self).save(*args, **kwargs)

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'


class Site(models.Model):
    type = models.ForeignKey(EnumSiteType, on_delete=models.PROTECT, db_index=True, blank=False,
                             verbose_name='Тип сайта')
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, db_index=True, blank=False,
                                     verbose_name='Организация')
    url = models.URLField(max_length=254, default='', blank=False, verbose_name='Адрес (URL)')
    login = models.CharField(max_length=100, default='', blank=False, verbose_name='Логин')
    password = models.CharField(max_length=50, default='', blank=False, verbose_name='Пароль')
    repr = models.CharField(max_length=256, default='', blank=True, verbose_name='Сайт')

    def save(self, *args, **kwargs):
        self.repr = f'{self.type}, {self.organization}'
        super(Site, self).save(*args, **kwargs)

    @staticmethod
    def post_init(**kwargs):
        site = kwargs.get('instance')
        api = None
        if site.id:
            ClassMixIn = globals().get(site.type.name)
            MetaClass = type(f'API{site.type.name}', (ClassMixIn, BaseAPI), {})
            api = MetaClass(site)
        site.api = api

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = 'Сайты'


class SiteBalance(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, db_index=True, blank=False, verbose_name='Сайт')
    date = models.DateTimeField(default=timezone.now, blank=False, verbose_name='Дата')
    balance = models.FloatField(default=0.00, blank=True, verbose_name='Сумма остаток')
    credit = models.FloatField(default=0.00, blank=True, verbose_name='Сумма кредита')
    available = models.FloatField(default=0.00, blank=True, verbose_name='Сумма доступно (остаток + кредит)')
    repr = models.CharField(max_length=256, blank=True, verbose_name='Остаток ден. средств на сайте')

    def save(self, *args, **kwargs):
        self.available = float(self.balance) + float(self.credit)

        import locale
        date_repr = self.date.strftime('%d.%m.%Y %H:%M:%S')
        available_repr = locale.format_string('%.2f', self.available, grouping=True)

        self.repr = f'{date_repr}, доступно: {available_repr} ({self.site})'
        super(SiteBalance, self).save(*args, **kwargs)

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'Остаток ден. средств на сайте'
        verbose_name_plural = 'Остатки ден. средств на сайтах'


class Card(models.Model):
    site = models.ForeignKey(Site, on_delete=models.PROTECT, db_index=True, blank=False, verbose_name='Сайт')
    relevant = models.BooleanField(db_index=True, default=True, blank=False, verbose_name='Актуальна')
    number = models.CharField(max_length=40, db_index=True, default='', blank=False, verbose_name='Номер карты')
    status = models.ForeignKey(EnumCardStatus, on_delete=models.PROTECT, blank=False, verbose_name='Статус')
    repr = models.CharField(max_length=50, default='', blank=True, verbose_name='Топливная карта')

    def save(self, *args, **kwargs):
        self.number = self.number.strip().replace(' ', '')
        self.repr = self.number

        len_section = 0
        if len(self.number) == 16:
            len_section = 4
        elif len(self.number) == 12:
            len_section = 2
        elif len(self.number) == 10:
            len_section = 4

        if len_section:
            arr_str = [self.number[i:i + len_section] for i in range(0, len(self.number), len_section)]
            self.repr = ' '.join(arr_str)

        super(Card, self).save(*args, **kwargs)

    def __str__(self):
        return self.repr

    class Meta:
        unique_together = ('site', 'number')
        verbose_name = 'Топливная карта'
        verbose_name_plural = 'Топливные карты'


class Item(models.Model):
    site = models.ForeignKey(Site, on_delete=models.PROTECT, db_index=True, blank=False, verbose_name='Сайт')
    id_external = models.CharField(max_length=100, default='', blank=False, verbose_name='ID (внешний)')
    category = models.ForeignKey(EnumItemCategory, on_delete=models.PROTECT, blank=False, verbose_name='Категория')
    name = models.CharField(max_length=100, default='', blank=False, verbose_name='Имя')
    repr = models.CharField(max_length=256, default='', blank=True, verbose_name='Товар сайта')

    def save(self, *args, **kwargs):
        self.repr = f'{self.name} ({self.site})'
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.repr

    class Meta:
        verbose_name = 'Товар сайта'
        verbose_name_plural = 'Товары сайтов'


class Limit(models.Model):
    id_external = models.CharField(max_length=128, default='', blank=False, verbose_name='ID (внешний)')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, db_index=True, blank=False, verbose_name='Сайт')
    card = models.ForeignKey(Card, on_delete=models.PROTECT, blank=False, db_index=True,
                             verbose_name='Топливная карта')
    type = models.ForeignKey(EnumLimitType, on_delete=models.PROTECT, blank=False, db_index=True,
                             verbose_name='Тип лимита')
    category = models.ForeignKey(EnumItemCategory, on_delete=models.PROTECT, blank=True, null=True,
                                 verbose_name='Категория товара')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Товар')
    period = models.ForeignKey(EnumLimitPeriod, on_delete=models.PROTECT, blank=False, verbose_name='Тип периода')
    unit = models.ForeignKey(EnumUnit, on_delete=models.PROTECT, blank=False, verbose_name='Единица измерения')
    value = models.FloatField(default=0.00, blank=True, verbose_name='Значение')
    balance = models.FloatField(default=0.00, blank=True, verbose_name='Остаток')
    repr = models.CharField(max_length=256, default='', blank=True, verbose_name='Лимит топливной карты')

    def save(self, *args, **kwargs):
        match self.type.name:
            case 'all':
                self.category = None
                self.item = None
            case 'category':
                self.item = None
            case 'item':
                self.category = None
        self.repr = f'{self.card}, ID {self.id_external.strip()}, {self.type}, {self.period}'
        super(Limit, self).save(*args, **kwargs)

    def __str__(self):
        return self.repr

    class Meta:
        unique_together = ('card', 'id_external')
        verbose_name = 'Лимит топливной карты'
        verbose_name_plural = 'Лимиты топливных карт'


class Transaction(models.Model):
    site = models.ForeignKey(Site, on_delete=models.PROTECT, db_index=True, blank=False, verbose_name='Сайт')
    id_external = models.CharField(max_length=128, blank=False, verbose_name='ID (внешний)')
    type = models.ForeignKey(EnumTransactionType, on_delete=models.PROTECT, blank=False, verbose_name='Тип транзакции')
    date = models.DateTimeField(default=timezone.now, blank=False, verbose_name='Дата')
    card = models.ForeignKey(Card, on_delete=models.PROTECT, db_index=True, blank=False, verbose_name='Топливная карта')
    details = models.CharField(max_length=1024, default='', blank=True, verbose_name='Описание')
    amount = models.FloatField(default=0.00, blank=False, verbose_name='Сумма')
    discount = models.FloatField(default=0.00, blank=True, verbose_name='Сумма скидки')
    repr = models.CharField(max_length=256, default='', blank=True, verbose_name='Транзакция')

    def save(self, *args, **kwargs):
        self.id_external = self.id_external.strip()
        date_repr = self.date.strftime('%d.%m.%Y %H:%M:%S')
        self.repr = f'{self.type} по карте {self.card}, от {date_repr}, ID {self.id_external}'
        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        return self.repr

    class Meta:
        unique_together = ('card', 'type', 'id_external')
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['date']


class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, db_index=True, blank=False,
                                    verbose_name='Транзакция')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, blank=False, null=True, verbose_name='Товар')
    item_description = models.CharField(max_length=256, blank=True, verbose_name='Описание товара')
    quantity = models.FloatField(default=0.00, blank=False, verbose_name='Количество')
    price = models.FloatField(default=0.00, blank=False, verbose_name='Цена')
    price_with_discount = models.FloatField(default=0.00, blank=True, verbose_name='Цена (с учетом скидки)')
    amount = models.FloatField(default=0.00, blank=False, verbose_name='Сумма')
    amount_with_discount = models.FloatField(default=0.00, blank=True, verbose_name='Сумма (с учетом скидки)')
    repr = models.CharField(max_length=256, default='', blank=True, verbose_name='Товар транзакции')

    def save(self, *args, **kwargs):
        if self.item:
            self.repr = f'{self.item.name} ({self.transaction})'
        else:
            self.repr = f'<Товар отсутствует> ({self.transaction})'
        super(TransactionItem, self).save(*args, **kwargs)

    def __str__(self):
        return self.repr

    class Meta:
        unique_together = ('transaction', 'item')
        verbose_name = 'Товар транзакции'
        verbose_name_plural = 'Товары транзакций'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True,
                                 verbose_name='Клиент')
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, null=True, blank=True,
                                     verbose_name='Организация')

    def __str__(self):
        return self.user.__str__()

    class Meta:
        verbose_name = 'Профиль пользователя (расширение)'
        verbose_name_plural = 'Профили пользователей (расширение)'


class BaseAPI:
    def __init__(self, site: Site):
        self.site = site
        self.url = site.url
        self.login = site.login
        self.password = site.password

        try:
            type_contract = EnumContractType.objects.get(name='processing')
            contract = Contract.objects.get(organization=site.organization, type=type_contract)
            self.contract_id = contract.id_external
        except EnumContractType.DoesNotExist or Contract.DoesNotExist:
            self.contract_id = ''

    @transaction.atomic
    def import_balance(self, **kwargs) -> (dict, bool):
        result = {'obj': None, 'created': False}
        data, success = self.get_balance()
        if success:
            date = data.get('date', '')
            balance = data.get('balance', 0.00)
            credit = data.get('credit', 0.00)
            if date:
                defaults = {'balance': balance, 'credit': credit}
                obj, created = SiteBalance.objects.update_or_create(site=self.site, date=date, defaults=defaults)
                result = {'obj': obj, 'created': created}
        return result, success

    @transaction.atomic
    def import_goods(self, **kwargs) -> (list[dict], bool):
        result = []
        verbose = kwargs.get('verbose', False)
        data, success = self.get_list_goods()
        if success:
            total_items = len(data)
            for i in range(total_items):
                data_item = data[i]
                id_external = data_item.get('id_external', '')
                category = data_item.get('category', '')
                name = data_item.get('name', '')
                category_obj = EnumItemCategory.objects.get(name=category)
                defaults = {'category': category_obj, 'name': name}
                obj, created = Item.objects.update_or_create(site=self.site, id_external=id_external, defaults=defaults)
                result.append({'obj': obj, 'created': created})
                if verbose:
                    counter = i + 1
                    text_prefix = f'Товары ({self.site}) {counter}/{total_items}:'
                    progress_bar(counter, total_items, prefix=text_prefix, length=50)
        return result, success

    @transaction.atomic
    def import_cards(self, **kwargs) -> (list[dict], bool):
        result = []
        list_cards = []
        list_cards_obj = Card.objects.filter(site=self.site, relevant=True)
        for card_obj in list_cards_obj:
            list_cards.append(card_obj.number)
        verbose = kwargs.get('verbose', False)
        data, success = self.get_list_cards()
        if success:
            total_items = len(data)
            for i in range(total_items):
                data_card = data[i]
                number = data_card.get('number', '')
                status = data_card.get('status', '')
                status_obj = EnumCardStatus.objects.get(name=status)
                obj, created = Card.objects.update_or_create(site=self.site, number=number,
                                                             defaults={'status': status_obj, 'relevant': True})
                result.append({'obj': obj, 'created': created})
                if number in list_cards:
                    list_cards.remove(number)
                if verbose:
                    counter = i + 1
                    text_prefix = f'Карты ({self.site}) {counter}/{total_items}:'
                    progress_bar(counter, total_items, prefix=text_prefix, length=50)
            counter = 0
            for number in list_cards:
                Card.objects.update_or_create(site=self.site, number=number,
                                              defaults={'relevant': False})
                if verbose:
                    counter += 1
                    text_prefix = f'Дективация карт ({self.site}) {counter}/{total_items}:'
                    progress_bar(counter, len(list_cards), prefix=text_prefix, length=50)
        return result, success

    @transaction.atomic
    def import_limits_by_card(self, card_number: str) -> (list[dict], bool):
        result = []
        card_obj = self._get_card_obj(card_number)
        if not card_obj:
            return False, result
        data, success = self.get_list_limits_by_card(card_number=card_number)
        if success:
            result = self._import_limits_by_card(card_obj, data)
        return result, success

    @transaction.atomic
    def import_limits(self, **kwargs) -> (list[dict], bool):
        result = []
        list_cards = []
        verbose = kwargs.get('verbose', False)
        list_cards_obj = Card.objects.filter(site=self.site, relevant=True)
        for card_obj in list_cards_obj:
            list_cards.append(card_obj.number)
        data, success = self.get_list_limits(list_cards)
        if success:
            total_items = 0
            if verbose:
                for data_card_limits in data:
                    data_limits = data_card_limits.get('limits', [])
                    total_items += len(data_limits)
            for i in range(len(data)):
                data_card_limits = data[i]
                card_number = data_card_limits.get('card', '')
                data_limits = data_card_limits.get('limits', [])
                card_obj = self._get_card_obj(card_number)
                if not card_obj:
                    continue
                result += self._import_limits_by_card(card_obj, data_limits)
                if verbose:
                    counter = i + 1
                    text_prefix = f'Лимиты ({self.site}) {counter}/{total_items}:'
                    progress_bar(counter, total_items, prefix=text_prefix, length=50)
        else:
            if verbose:
                print('    !!!Не получилось получить данные об остатках лимитов. received = False')
        return result, success

    @transaction.atomic
    def import_transactions_by_card(self, **kwargs) -> (list[dict], bool):
        result = []
        verbose = kwargs.get('verbose', False)
        data, success = self.get_list_transactions(**kwargs)
        if success:
            total_items = len(data)
            for i in range(total_items):
                data_transaction = data[i]
                result += self._import_transaction(**data_transaction)
                if verbose:
                    text_prefix = f'Транзакции ({self.site}) {i}/{total_items}:'
                    progress_bar(i + 1, total_items, prefix=text_prefix, length=50)
        return result, success

    @transaction.atomic
    def import_transactions(self, **kwargs) -> (list[dict], bool):
        result = []
        verbose = kwargs.get('verbose', False)
        data, success = self.get_list_transactions(**kwargs)
        if success:
            total_items = len(data)
            for i in range(total_items):
                data_transaction = data[i]
                result += self._import_transaction(**data_transaction)
                if verbose:
                    text_prefix = f'Транзакции ({self.site}) {i}/{total_items}:'
                    progress_bar(i + 1, total_items, prefix=text_prefix, length=50)
        return result, success

    @transaction.atomic
    def card_status_put(self, **kwargs) -> (Card or None, bool):
        result = None
        data, success = self.card_status_update(**kwargs)
        if success:
            card_number = data.get('card_number', '')
            status_name = data.get('status_name', '')
            status_obj = EnumCardStatus.objects.get(name=status_name)
            defaults = {'status': status_obj}
            result, created = Card.objects.update_or_create(site=self.site, number=card_number, defaults=defaults)
        return result, success

    def _import_transaction(self, **kwargs) -> list[dict]:
        result = []
        id_external = kwargs.get('id_external', '')
        type_name = kwargs.get('type', '')
        card_number = kwargs.get('card', '')
        date = kwargs.get('date', '')
        details = kwargs.get('details', '')
        amount = kwargs.get('amount', 0.00)
        discount = kwargs.get('discount', 0.00)
        items = kwargs.get('items', [])

        type_obj = EnumTransactionType.objects.get(name=type_name)
        card_obj = self._get_card_obj(card_number, False)
        defaults = {'type': type_obj, 'date': date, 'details': details, 'amount': amount, 'discount': discount}

        transaction_obj, created = Transaction.objects.update_or_create(site=self.site, card=card_obj,
                                                                        id_external=id_external, defaults=defaults)
        imported_items = self._import_transaction_items(transaction_obj, items)
        result.append({'obj': transaction_obj, 'items': imported_items, 'created': created})
        return result

    def _import_transaction_items(self, transaction_obj: Transaction, data_transaction_items: list) -> list[dict]:
        result = []
        TransactionItem.objects.filter(transaction=transaction_obj).delete()

        for data_item in data_transaction_items:
            item_id_external = data_item.get('item', '')
            item_description = data_item.get('item_description', '')
            quantity = data_item.get('quantity', 0.00)
            price = data_item.get('price', 0.00)
            price_with_discount = data_item.get('price_with_discount', 0.00)
            amount = data_item.get('amount', 0.00)
            amount_with_discount = data_item.get('amount_with_discount', 0.00)

            item_obj = self._get_item_obj(item_id_external)

            defaults = {'item_description': item_description, 'quantity': quantity, 'price': price,
                        'price_with_discount': price_with_discount, 'amount': amount,
                        'amount_with_discount': amount_with_discount}

            obj, created = TransactionItem.objects.update_or_create(transaction=transaction_obj,
                                                                    item=item_obj, defaults=defaults)
            result.append({'obj': obj, 'created': created})
        return result

    def _import_limits_by_card(self, card_obj: Card, data_limits: list[dict]) -> list[dict]:

        result = []
        Limit.objects.filter(card=card_obj).delete()

        for data_limit in data_limits:
            id_external = data_limit.get('id_external', '')
            type_name = data_limit.get('type', '')
            category_name = data_limit.get('category', '')
            item_id_external = data_limit.get('item', '')
            unit = data_limit.get('unit', '')
            period = data_limit.get('period', '')
            value = data_limit.get('value', 0.00)
            balance = data_limit.get('balance', 0.00)

            type_obj = EnumLimitType.objects.get(name=type_name)
            unit_obj = EnumUnit.objects.get(name=unit)
            period_obj = EnumLimitPeriod.objects.get(name=period)
            category_obj = None
            item_obj = None

            match type_name:
                case 'category':
                    category_obj = EnumItemCategory.objects.get(name=category_name)
                case 'item':
                    item_obj = Item.objects.get(site=self.site, id_external=item_id_external)

            defaults = {'type': type_obj, 'category': category_obj, 'item': item_obj,
                        'unit': unit_obj, 'period': period_obj, 'value': value, 'balance': balance}

            obj, created = Limit.objects.update_or_create(site=self.site, card=card_obj, id_external=id_external,
                                                          defaults=defaults)
            result.append({'obj': obj, 'created': created})

        return result

    def _get_card_obj(self, card_number: str, relevant: bool = True) -> Card or None:
        if not card_number:
            return
        try:
            result = Card.objects.get(site=self.site, number=card_number)
        except Card.DoesNotExist:
            status_obj = EnumCardStatus.objects.get(name='block')
            result = Card.objects.create(site=self.site, number=card_number, status=status_obj, relevant=relevant)
        return result

    def _get_item_obj(self, id_external: str) -> Item or None:
        if not id_external:
            return
        try:
            result = Item.objects.get(site=self.site, id_external=id_external)
        except Item.DoesNotExist:
            result = None
        return result

    def get_balance(self) -> (dict, bool):
        return {}, False

    def get_list_goods(self) -> (list[dict], bool):
        return [], False

    def get_list_cards(self) -> (list[dict], bool):
        return [], False

    def get_list_limits_by_card(self, **kwargs) -> (list[dict], bool):
        return [], False

    def get_list_limits(self, list_cards: list) -> (list[dict], bool):
        return [], False

    def get_list_transactions(self, **kwargs) -> (list[dict], bool):
        return [], False

    def card_status_update(self, **kwargs) -> (dict, bool):
        return {}, False

    def limit_add(self, **kwargs) -> (dict, bool):
        return {}, False

    def limit_update(self, **kwargs) -> (dict, bool):
        return {}, False

    def limit_delete(self, **kwargs) -> (dict, bool):
        return {}, False


post_init.connect(Site.post_init, Site)

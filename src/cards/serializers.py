from rest_framework import serializers
from .models import *


def validate_site(site_id: int):
    try:
        return Site.objects.get(id=site_id)
    except Site.DoesNotExist:
        message = f'Сайт с идентификатором \'{site_id}\' не зарегистрирован в системе'
        raise serializers.ValidationError(message)


def validate_card_status(status_name: str):
    try:
        return EnumCardStatus.objects.get(name=status_name)
    except EnumCardStatus.DoesNotExist:
        message = f'Статус топливной карты с именем \'{status_name}\' не зарегистрирован в системе'
        raise serializers.ValidationError(message)


def validate_enum_limit_type(type_name: str):
    try:
        return EnumLimitType.objects.get(name=type_name)
    except EnumLimitType.DoesNotExist:
        message = f'Тип лимита с именем \'{type_name}\' не зарегистрирован в системе'
        raise serializers.ValidationError(message)


def validate_enum_item_category(category_name: str):
    try:
        return EnumItemCategory.objects.get(name=category_name)
    except EnumItemCategory.DoesNotExist:
        message = f'Категория товара с именем \'{category_name}\' не зарегистрирована в системе'
        raise serializers.ValidationError(message)


def validate_enum_limit_period(period_name: str):
    try:
        return EnumLimitPeriod.objects.get(name=period_name)
    except EnumLimitPeriod.DoesNotExist:
        message = f'Тип периода лимита с именем \'{period_name}\' не зарегистрирован в системе'
        raise serializers.ValidationError(message)


def validate_enum_unit(unit_name: str):
    try:
        return EnumUnit.objects.get(name=unit_name)
    except EnumUnit.DoesNotExist:
        message = f'Единица измерения с именем \'{unit_name}\' не зарегистрирована в системе'
        raise serializers.ValidationError(message)


def validate_period(data: dict):
    begin = data.get('begin')
    end = data.get('end')
    if begin > end:
        message_begin = f'Начальная дата периода ({begin}) не должна быть больше конечной ({end})'
        message_end = f'Конечная дата периода ({end}) не должна быть меньше начальной ({begin})'
        raise serializers.ValidationError({'begin': message_begin, 'end': message_end})


def validate_card(data: dict):
    site_id = data.get('site')
    card_number = data.get('card')
    site_obj = Site.objects.get(id=site_id)
    try:
        card_obj = Card.objects.get(site=site_obj, number=card_number)
        if not card_obj.relevant:
            message = f'Топливная карта \'{card_obj}\' не актуальна (установлена техническая блокировка).'
            raise serializers.ValidationError({'card': message})
    except Card.DoesNotExist:
        message = f'У сайта \'{site_obj}\' отсутствует топливная карта с номером \'{card_number}\''
        raise serializers.ValidationError({'card': message})


def validate_set_card_status_collision(data: dict):
    site_id = data.get('site')
    card_number = data.get('card')
    status_name = data.get('status')
    site_obj = Site.objects.get(id=site_id)
    card_obj = Card.objects.get(site=site_obj, number=card_number)
    status_obj = EnumCardStatus.objects.get(name=status_name)
    if status_obj.name == card_obj.status.name:
        message = f'Текущий статус топливной карты \'{card_obj}\' равен статусу к установке ({status_obj})'
        raise serializers.ValidationError({'status': message})


def validate_item(data: dict):
    site_id = data.get('site')
    item_id_external = data.get('item')
    site_obj = Site.objects.get(id=site_id)
    try:
        return Item.objects.get(site=site_obj, id_external=item_id_external)
    except Item.DoesNotExist:
        message = f'У сайта \'{site_obj}\' товар с внешним ID \'{item_id_external}\' отсутствует'
        raise serializers.ValidationError(message)


def validate_limit_id_external(data: dict):
    site_id = data.get('site')
    card_number = data.get('card')
    limit_id_external = data.get('id_external')
    site_obj = Site.objects.get(id=site_id)
    card_obj = Card.objects.get(site=site_obj, number=card_number)
    try:
        return Limit.objects.get(site=site_obj, card=card_obj, id_external=limit_id_external)
    except Limit.DoesNotExist:
        message = f'У топливной карты \'{card_obj}\' отсутствует лимит с внешним ID \'{limit_id_external}\''
        raise serializers.ValidationError(message)


class SiteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    repr = serializers.CharField()


class EnumCardStatusSerializer(serializers.Serializer):
    name = serializers.CharField()
    repr = serializers.CharField()


class EnumItemCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    repr = serializers.CharField()


class EnumTransactionTypeSerializer(serializers.Serializer):
    name = serializers.CharField()
    repr = serializers.CharField()


class EnumLimitTypeSerializer(serializers.Serializer):
    name = serializers.CharField()
    repr = serializers.CharField()


class EnumLimitPeriodSerializer(serializers.Serializer):
    name = serializers.CharField()
    repr = serializers.CharField()


class EnumUnitSerializer(serializers.Serializer):
    name = serializers.CharField()
    is_currency = serializers.BooleanField()
    repr = serializers.CharField()


class CardSerializer(serializers.ModelSerializer):
    status = EnumCardStatusSerializer()

    class Meta:
        model = Card
        fields = ('number', 'status')


class ItemSerializer(serializers.Serializer):
    id_external = serializers.CharField()
    category = EnumItemCategorySerializer()
    name = serializers.CharField()
    repr = serializers.CharField()


class ItemsTransactionSerializer(serializers.Serializer):
    item = ItemSerializer()
    item_description = serializers.CharField()
    quantity = serializers.FloatField()
    price = serializers.FloatField()
    price_with_discount = serializers.FloatField()
    amount = serializers.FloatField()
    amount_with_discount = serializers.FloatField()


class BalanceGetSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])
    date = serializers.DateField()


class BalanceSerializerData(serializers.ModelSerializer):
    site = SiteSerializer()
    date = serializers.DateTimeField()

    class Meta:
        model = SiteBalance
        fields = ('id', 'site', 'date', 'balance', 'credit', 'available')


class ItemGetSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])


class ItemSerializerData(serializers.ModelSerializer):
    site = SiteSerializer()
    category = EnumItemCategorySerializer()

    class Meta:
        model = Item
        fields = ('id', 'site', 'id_external', 'category', 'name')


class CardGetSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])


class CardGetByStatusSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])
    status = serializers.CharField(validators=[validate_card_status])


class CardSerializerData(serializers.ModelSerializer):
    site = SiteSerializer()
    status = EnumCardStatusSerializer()

    class Meta:
        model = Card
        fields = ('id', 'site', 'number', 'status')


class CardStatusPutSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])
    card = serializers.CharField()
    status = serializers.CharField(validators=[validate_card_status])

    def validate(self, data):
        validate_card(data)
        validate_set_card_status_collision(data)
        return data


class TransactionGetBySiteSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])
    begin = serializers.DateTimeField()
    end = serializers.DateTimeField()

    def validate(self, data):
        validate_period(data)
        return data


class TransactionGetByCardSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])
    card = serializers.CharField()
    begin = serializers.DateTimeField()
    end = serializers.DateTimeField()

    def validate(self, data):
        validate_period(data)
        validate_card(data)
        return data


class TransactionSerializerData(serializers.ModelSerializer):
    site = SiteSerializer()
    type = EnumTransactionTypeSerializer()
    card = CardSerializer()
    items = ItemsTransactionSerializer(many=True, source='transactionitem_set')

    class Meta:
        model = Transaction
        fields = ('id_external', 'site', 'type', 'date', 'card', 'details', 'amount', 'discount', 'items')


class LimitGetBySiteSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])


class LimitGetByCardSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])
    card = serializers.CharField()

    def validate(self, data):
        validate_card(data)
        return data


class LimitPostTypeCategorySerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])
    card = serializers.CharField()
    type = serializers.CharField(validators=[validate_enum_limit_type])
    category = serializers.CharField(validators=[validate_enum_item_category])
    period = serializers.CharField(validators=[validate_enum_limit_period])
    unit = serializers.CharField(validators=[validate_enum_unit])
    value = serializers.FloatField()

    def validate(self, data):
        validate_card(data)
        return data


class LimitPostTypeItemSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])
    card = serializers.CharField()
    type = serializers.CharField(validators=[validate_enum_limit_type])
    item = serializers.CharField()
    period = serializers.CharField(validators=[validate_enum_limit_period])
    unit = serializers.CharField(validators=[validate_enum_unit])
    value = serializers.FloatField()

    def validate(self, data):
        validate_card(data)
        validate_item(data)
        return data


class LimitPostTypeAllSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])
    card = serializers.CharField()
    type = serializers.CharField(validators=[validate_enum_limit_type])
    period = serializers.CharField(validators=[validate_enum_limit_period])
    unit = serializers.CharField(validators=[validate_enum_unit])
    value = serializers.FloatField()

    def validate(self, data):
        validate_card(data)
        return data


class LimitPutSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])
    card = serializers.CharField()
    id_external = serializers.CharField()
    value = serializers.FloatField()

    def validate(self, data):
        validate_card(data)
        validate_limit_id_external(data)
        return data


class LimitDeleteSerializerParams(serializers.Serializer):
    site = serializers.IntegerField(validators=[validate_site])
    card = serializers.CharField()
    id_external = serializers.CharField()

    def validate(self, data):
        validate_card(data)
        validate_limit_id_external(data)
        return data


class LimitSerializerData(serializers.ModelSerializer):
    site = SiteSerializer()
    card = CardSerializer()
    type = EnumLimitTypeSerializer()
    category = EnumItemCategory()
    item = ItemSerializer()
    period = EnumLimitPeriodSerializer()
    unit = EnumUnitSerializer()

    class Meta:
        model = Limit
        fields = ('id_external', 'site', 'card', 'type', 'category', 'item', 'period', 'unit', 'value', 'balance')



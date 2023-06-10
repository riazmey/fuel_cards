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
        message = f'Статус топливной карты \'{status_name}\' не зарегистрирован в системе'
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


'''
class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('site_id', 'number', 'status', 'repr')
        depth = 1
'''

'''
class CardSerializer(serializers.Serializer):
    site = SiteSerializer()
    number = serializers.CharField()
    status = EnumCardStatusSerializer()
    repr = serializers.CharField()

    def create(self, validated_data):
        return Card.objects.create(**validated_data)
'''
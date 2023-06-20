from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import *


class BalanceAPIView(APIView):

    def get(self, request):
        params = BalanceGetSerializerParams(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_id = params.data.get('site')
        date = params.data.get('date')

        queryset = SiteBalance.objects.filter(site=site_id, date__lte=date).order_by('-date')
        if queryset:
            data = queryset[0]
        else:
            data = SiteBalance(site=Site.objects.get(id=site_id), date=date)
        return Response(BalanceSerializerData(data).data)


class ItemAPIView(APIView):

    def get(self, request):
        params = ItemGetSerializerParams(data=request.query_params)
        params.is_valid(raise_exception=True)

        queryset = Item.objects.filter(site__id=params.data.get('site'))
        if queryset:
            return Response(ItemSerializerData(queryset, many=True).data)
        else:
            return Response([])


class CardAPIView(APIView):

    def get(self, request):
        status_name = request.query_params.get('status', None)
        card_number = request.query_params.get('card', None)
        if status_name and card_number:
            params = CardGetByStatusAndNumberSerializerParams(data=request.query_params)
        elif status_name and not card_number:
            params = CardGetByStatusSerializerParams(data=request.query_params)
        elif not status_name and card_number:
            params = CardGetByNumberSerializerParams(data=request.query_params)
        else:
            params = CardGetSerializerParams(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_id = params.data.get('site')
        site_obj = Site.objects.get(id=site_id)

        if status_name and card_number:
            status_obj = EnumCardStatus.objects.get(name=status_name)
            queryset = Card.objects.filter(site=site_obj, status=status_obj, number=card_number, relevant=True)
        elif status_name and not card_number:
            status_obj = EnumCardStatus.objects.get(name=status_name)
            queryset = Card.objects.filter(site=site_obj, status=status_obj, relevant=True)
        elif not status_name and card_number:
            queryset = Card.objects.filter(site=site_obj, number=card_number, relevant=True)
        else:
            queryset = Card.objects.filter(site=site_obj, relevant=True)

        if queryset:
            return Response(CardSerializerData(queryset, many=True).data)
        else:
            return Response([])


class CardStatusAPIView(APIView):

    def put(self, request):
        params = CardStatusPutSerializerParams(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_id = params.data.get('site')
        card_number = params.data.get('card')
        status_name = params.data.get('status')

        site_obj = Site.objects.get(id=site_id)
        card_obj = Card.objects.get(site=site_obj, number=card_number)

        status_current_obj = EnumCardStatus.objects.get(id=card_obj.status.id)

        data, success = site_obj.api.card_status_put(card_number=card_number, status_name=status_name,
                                                     status_name_current=status_current_obj.name)

        if success:
            return Response(CardSerializerData(data).data)
        else:
            return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionAPIView(APIView):

    def get(self, request):
        card_number = request.query_params.get('card', None)
        if card_number:
            params = TransactionGetByCardSerializerParams(data=request.query_params)
        else:
            params = TransactionGetBySiteSerializerParams(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_id = params.data.get('site')
        begin = params.data.get('begin')
        end = params.data.get('end')

        site_obj = Site.objects.get(id=site_id)
        if card_number:
            card_obj = Card.objects.get(site=site_obj, number=card_number)
            queryset = Transaction.objects.filter(card=card_obj, date__gte=begin, date__lte=end)
        else:
            queryset = Transaction.objects.filter(site=site_obj, date__gte=begin, date__lte=end)
        if queryset:
            return Response(TransactionSerializerData(queryset, many=True).data)
        else:
            return Response([])


class LimitAPIView(APIView):

    def get(self, request):
        card_number = request.query_params.get('card', None)
        if card_number:
            params = LimitGetByCardSerializerParams(data=request.query_params)
        else:
            params = LimitGetBySiteSerializerParams(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_id = params.data.get('site')
        site_obj = Site.objects.get(id=site_id)

        if card_number:
            card_obj = Card.objects.get(site=site_obj, number=card_number)
            queryset = Limit.objects.filter(card=card_obj)
        else:
            queryset = Limit.objects.filter(site=site_obj)
        if queryset:
            return Response(LimitSerializerData(queryset, many=True).data)
        else:
            return Response([])

    def post(self, request):
        type_name = request.query_params.get('type', '')
        match type_name:
            case 'category':
                params = LimitPostTypeCategorySerializerParams(data=request.query_params)
            case 'item':
                params = LimitPostTypeItemSerializerParams(data=request.query_params)
            case _:
                params = LimitPostTypeAllSerializerParams(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_id = params.data.get('site')
        card_number = params.data.get('card')
        category_name = params.data.get('category', '')
        item_id_external = params.data.get('item', '')
        period_name = params.data.get('period')
        unit_name = params.data.get('unit')
        value = float(params.data.get('value'))

        site_obj = Site.objects.get(id=site_id)

        data, success = site_obj.api.limit_post(card_number=card_number, type_name=type_name,
                                                category_name=category_name, item_id_external=item_id_external,
                                                period_name=period_name, unit_name=unit_name, value=value)

        if success:
            return Response(LimitSerializerData(data).data)
        else:
            return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        params = LimitPutSerializerParams(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_id = params.data.get('site')
        card_number = params.data.get('card')
        id_external = params.data.get('id_external')
        value = float(params.data.get('value'))

        site_obj = Site.objects.get(id=site_id)
        data, success = site_obj.api.limit_put(card_number=card_number, id_external=id_external, value=value)

        if success:
            return Response(LimitSerializerData(data).data)
        else:
            return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        params = LimitDeleteSerializerParams(data=request.query_params)
        params.is_valid(raise_exception=True)

        site_id = params.data.get('site')
        card_number = params.data.get('card')
        id_external = params.data.get('id_external')

        site_obj = Site.objects.get(id=site_id)
        data, success = site_obj.api.limit_delete(card_number=card_number, id_external=id_external)

        if success:
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(data, status_code)

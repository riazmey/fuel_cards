from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django import forms
from django.utils import timezone
from .models import SiteBalance
from .serializers import SiteBalanceSerializer


# Create your views here.

class SiteBalanceAPIView(APIView):
    def get(self, request):

        params = SiteBalanceSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)

        queryset = SiteBalance.objects.filter(site__id=params.data['site_id'], date__lte=params.data['date']).order_by('-date')
        if queryset:
            data = queryset[0]
        else:
            data = params.data
        return Response(SiteBalanceSerializer(data).data)

    def post(self, request):
        serializer = SiteBalanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    #queryset = SiteBalance.objects.filter(date__lte=timezone.now())
    #serializer_class = SiteBalanceSerializer

#class SiteBalanceAPIView(APIView):
#    queryset = SiteBalance.objects.filter(date__lte=timezone.now())
#    serializer_class = SiteBalanceSerializer

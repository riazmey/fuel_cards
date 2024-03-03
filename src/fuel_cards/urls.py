"""
URL configuration for fuel_cards project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from service.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/balance/', BalanceAPIView.as_view()),
    path('api/v1/item/', ItemAPIView.as_view()),
    path('api/v1/card/', CardAPIView.as_view()),
    path('api/v1/card/status/', CardStatusAPIView.as_view()),
    path('api/v1/transaction/', TransactionAPIView.as_view()),
    path('api/v1/limit/', LimitAPIView.as_view())
]

from django import forms
from .models import *


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = [
            'type',
            'organization',
            'url',
            'login',
            'password'
        ]

        widgets = {
            'url': forms.URLInput(),
            'password': forms.PasswordInput()
        }


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'type',
            'organization',
            'customer',
            'id_external',
            'number',
            'date'
        ]

    def clean(self):
        customer = self.cleaned_data.get('customer')
        organization = self.cleaned_data.get('organization')
        if not customer and not organization:
            self.add_error('customer', 'Необходимо выбрать организацию или клиента!')
            self.add_error('organization', 'Необходимо выбрать организацию или клиента!')
        if customer and organization:
            self.add_error('customer', 'Выберите что-то одно: организация/клиент!')
            self.add_error('organization', 'Выберите что-то одно: организация/клиент!')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'user',
            'organization',
            'customer'
        ]

    def clean(self):
        customer = self.cleaned_data.get('customer')
        organization = self.cleaned_data.get('organization')
        if not customer and not organization:
            self.add_error('customer', 'Необходимо выбрать организацию или клиента!')
            self.add_error('organization', 'Необходимо выбрать организацию или клиента!')
        if customer and organization:
            self.add_error('customer', 'Выберите что-то одно: организация/клиент!')
            self.add_error('organization', 'Выберите что-то одно: организация/клиент!')

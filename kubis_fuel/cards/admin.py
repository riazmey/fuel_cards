from django.contrib import admin
from .models import *
from .forms import *


class OrganizationAdmin(admin.ModelAdmin):
    fields = ['name', 'name_full', ('inn', 'kpp'), 'email']
    list_display = ['name', 'inn', 'email']
    search_fields = ['name']
    ordering = ['name']


class CustomerAdmin(admin.ModelAdmin):
    fields = ['name', 'name_full', ('inn', 'kpp'), 'email']
    list_display = ['name', 'inn', 'email']
    search_fields = ['name']
    ordering = ['name']


class ContractAdmin(admin.ModelAdmin):
    fields = ['type', 'organization', 'customer', 'id_external', ('number', 'date')]
    list_display = ['repr']
    search_fields = ['repr', 'type_repr']
    form = ContractForm


class SiteAdmin(admin.ModelAdmin):
    list_display = ['type', 'organization', 'url']
    list_filter = ['type', 'organization__repr']
    ordering = ['type', 'organization']
    form = SiteForm


class SiteBalanceAdmin(admin.ModelAdmin):
    fields = ['site', 'date', 'balance', 'credit', 'available']
    list_display = ['site', 'date', 'available']
    list_filter = ['site__type']
    date_hierarchy = 'date'
    ordering = ['site', 'date']


class CardAdmin(admin.ModelAdmin):
    fields = ['site', 'number', 'status']
    list_display = ['site', 'number', 'status']
    list_filter = ['site__repr']
    search_fields = ['number']
    ordering = ['site', 'number']


class LimitAdmin(admin.ModelAdmin):
    fields = ['id_external', 'card', 'type', 'category', 'item', 'period', 'unit', 'value', 'balance']
    list_display = ['card', 'id_external', 'type', 'period', 'category', 'value', 'balance']
    list_filter = ['card__repr']
    search_fields = ['card__number', 'id_external']
    ordering = ['card', 'id_external']


class ItemAdmin(admin.ModelAdmin):
    fields = ['site', 'id_external', 'category', 'name']
    list_display = ['name', 'site', 'category']
    list_filter = ['site__repr']
    search_fields = ['name']
    ordering = ['site', 'name']


class TransactionAdmin(admin.ModelAdmin):
    fields = [('type', 'id_external'), 'date', 'card', 'details', 'amount', 'discount']
    list_display = ['type', 'date', 'card', 'id_external', 'amount', 'discount']
    list_filter = ['card', 'type']
    date_hierarchy = 'date'
    search_fields = ['card__repr', 'id_external']
    ordering = ['date', 'card']
    save_as = True


class TransactionItemAdmin(admin.ModelAdmin):
    fields = ['transaction', 'item', 'item_description', 'quantity', 'price',
              'price_with_discount', 'amount', 'amount_with_discount']
    list_display = ['transaction', 'item', 'amount']
    list_filter = ['item']
    search_fields = ['transaction__id_external', 'item__repr']
    ordering = ['transaction', 'amount']
    save_as = True


class ProfileAdmin(admin.ModelAdmin):
    fields = ['user', 'customer', 'organization']
    list_display = ['user', 'customer', 'organization']
    search_fields = ['user__name', 'customer__name', 'organization__name']
    form = ProfileForm


admin.site.register(EnumSiteType)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(SiteBalance, SiteBalanceAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Limit, LimitAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionItem, TransactionItemAdmin)
admin.site.register(Profile, ProfileAdmin)

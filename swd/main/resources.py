from .models import *
from import_export import resources, fields
from import_export.fields import Field


class ItemBuyResource(resources.ModelResource):
    class Meta:
        model = ItemBuy
        fields = ('student__name','student__bitsId','item__title',)

    hostel = Field(column_name='Hostel')
    room = Field(column_name='Room no.')

    def dehydrate_hostel(self, ItemBuy):
        return HostelPS.objects.get(student=ItemBuy.student).hostel

    def dehydrate_room(self, ItemBuy):
        return HostelPS.objects.get(student=ItemBuy.student).room

class TeeBuyResource(resources.ModelResource):
    class Meta:
        model = TeeBuy
        fields = ('student__bitsId', 'student__name', 'nick', 'qty', 'size','tee__title')

    hostel = Field(column_name='Hostel')
    room = Field(column_name='Room no.')

    def dehydrate_hostel(self, TeeBuy):
        return HostelPS.objects.get(student=TeeBuy.student).hostel

    def dehydrate_room(self, TeeBuy):
        return HostelPS.objects.get(student=TeeBuy.student).room

class MessOptionResource(resources.ModelResource):
    class Meta:
        model = MessOption
        fields = ('monthYear','student__name','student__bitsId','mess',)
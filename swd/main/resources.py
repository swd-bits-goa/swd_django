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
        fields = ('monthYear', 'student__name', 'student__bitsId', 'mess',)


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('bitsId', 'name')


class HostelPSResource(resources.ModelResource):
    class Meta:
        model = HostelPS
        fields = ('student__bitsId', 'student__name', 'acadstudent', 'status', 'psStation', 'hostel', 'room')


class DayPassResource(resources.ModelResource):
    class Meta:
        model = DayPass
        fields = ('student__bitsId', 'student__name', 'reason', 'dateTime', 'corrAddress', 'approvedBy__name', 'approved', 'disapproved', 'comment')


class BonafideResource(resources.ModelResource):
    class Meta:
        model = Bonafide
        fields = ('student__bitsId', 'student__name', 'reason', 'otherReason', 'reqDate', 'status')


class LeaveResource(resources.ModelResource):
    class Meta:
        model = Leave
        fields = ('student__bitsId', 'student__name', 'reason', 'dateTimeStart', 'dateTimeEnd', 'consent', 'corrAddress', 'corrPhone', 'approvedBy__name', 'approved', 'disapproved', 'comment')


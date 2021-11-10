import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User
from datetime import date, datetime
from main.models import *

class UserType(DjangoObjectType):
    class Meta:
        model = User

# class FacultyType(DjangoObjectType):
#     class Meta:
#         model = Faculty

class WardenType(DjangoObjectType):
    class Meta:
        model = Warden

# class NucleusType(DjangoObjectType):
#     class Meta:
#         model = Nucleus

# class SuperintendentType(DjangoObjectType):
#     class Meta:
#         model = Superintendent

# class FacultyInchargeType(DjangoObjectType):
#     class Meta:
#         model = FacultyIncharge

class StaffType(DjangoObjectType):
    class Meta:
        model = Staff
   
class StudentType(DjangoObjectType):
    class Meta:
        model = Student

class DayScholarType(DjangoObjectType):
    class Meta:
        model = DayScholar

class HostelPSType(DjangoObjectType):
    class Meta:
        model = HostelPS

class CSAType(DjangoObjectType):
    class Meta:
        model = CSA

class MessOptionType(DjangoObjectType):
    class Meta:
        model = MessOption
    
    
class BonafideType(DjangoObjectType):
    class Meta:
        model = Bonafide
    
class LeaveType(DjangoObjectType):
    class Meta:
        model = Leave

class DayPassType(DjangoObjectType):
    class Meta:
        model = DayPass

class LateComerType(DjangoObjectType):
    class Meta:
        model = LateComer

class DiscoType(DjangoObjectType):
    class Meta:
        model = Disco

class MessOptionOpenType(DjangoObjectType):
    class Meta:
        model = MessOptionOpen
    
    open_now = graphene.Boolean(default_value=False)
    month = graphene.String()

    def resolve_open_now(self, args, **kwargs):
        if datetime.today().date() < self.dateClose:
            return True
        return False
    
    def resolve_month(self, args, **kwargs):
        return self.monthYear.strftime("%B")

class TransactionType(DjangoObjectType):
    class Meta:
        model = Transaction

class MessBillType(DjangoObjectType):   
    class Meta:
        model = MessBill

class DueCategoryType(DjangoObjectType):
    class Meta:
        model = DueCategory

class DueType(DjangoObjectType):
    class Meta:
        model = Due

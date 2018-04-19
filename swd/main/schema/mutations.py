import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User
from datetime import date, datetime
from main.models import *
from .types import *

class UpdateMessOption(graphene.Mutation):
    class Arguments:
        mess = graphene.String(required=True)
        month = graphene.types.datetime.DateTime(required=True)
    
    messoption = graphene.Field(MessOptionType)

    @staticmethod
    def mutate(root, info, mess=None, month=None):
        context = info.context

        if context.user.is_authenticated:
            student = Student.objects.get(user=context.user)
            messoption = MessOption(student=student, monthYear=month, mess=mess)
            messoption.save()
            return UpdateMessOption(messoption=messoption)
        else:
            return None

class ApplyLeave(graphene.Mutation):
    class Arguments:
        dateTimeStart = graphene.types.datetime.DateTime(required=True)
        dateTimeEnd = graphene.types.datetime.DateTime(required=True)
        reason = graphene.String(required=True)
        corrAddress = graphene.String(required=True)
        corrPhone = graphene.String(required=True)
        consent = graphene.String(required=True)

# CONSENT_CHOICES
# Letter
# Fax
# Email

    leave = graphene.Field(LeaveType)

    @staticmethod
    def mutate(root, info,  dateTimeStart=None, dateTimeEnd=None, reason=None, corrAddress=None, corrPhone=None, consent=None):
        context = info.context

        if context.user.is_authenticated:
            student = Student.objects.get(user=context.user)
            leave = Leave(student=student, dateTimeStart=dateTimeStart, dateTimeEnd=dateTimeEnd, reason=reason, corrAddress=corrAddress, corrPhone=corrPhone)
            leave.save()
            return ApplyLeave(leave=leave)
        else:
            return None            

class Mutation(graphene.ObjectType):
    update_mess_option = UpdateMessOption.Field()
    apply_leave = ApplyLeave.Field()
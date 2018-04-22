import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User
from datetime import date, datetime
from main.models import *
from .types import *
import datetime
from datetime import date

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

class SubmitBonafideApplication(graphene.Mutation):
    class Arguments:
        reason = graphene.String()
        otherReason = graphene.String()
    bonafide = graphene.Field(BonafideType)
    @staticmethod
    def mutate(root, info, reason=None, otherReason=None):
        context = info.context
        if context.user.is_authenticated:
            print(context.user)
            student = Student.objects.get(user=context.user)
            rev_date= date.today()
            str_date = rev_date.strftime("%Y/%m/%d %H:%M:%S")
            arr_date = str_date.split('/')
            bonafides = Bonafide.objects.filter(student=student)
            sem_count=[0,0]
            for bon in bonafides:
                if int(arr_date[0])==bon.reqDate.year:
                    sem_count[(int(bon.reqDate.month)-1)//6]+=1
            if sem_count[(int(arr_date[1])-1)//6] > 2:
                return None
            bonafide = Bonafide.objects.create(student=student, reason=reason,otherReason=otherReason, reqDate=rev_date, printed=False)
            bonafide.save()
            return SubmitBonafideApplication(bonafide=bonafide)
        else:
            return None
          
class Mutation(graphene.ObjectType):
    update_mess_option = UpdateMessOption.Field()
    submit_bonafide_application = SubmitBonafideApplication.Field()
    apply_leave = ApplyLeave.Field()

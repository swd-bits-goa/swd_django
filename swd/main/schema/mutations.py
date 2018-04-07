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

class Mutation(graphene.ObjectType):
    update_mess_option = UpdateMessOption.Field()
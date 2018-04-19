import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User
from datetime import date, datetime
from main.models import *
from .types import *

class UpdateMessOption(graphene.Mutation):
    class Arguments:
        mess = graphene.String(required=True)

    messoption = graphene.Field(MessOptionType)

    @staticmethod
    def mutate(root, info, mess=None, month=None):
        context = info.context

        if context.user.is_authenticated:
            openmess = MessOptionOpen.objects.filter(dateClose__gte = date.today()).latest("monthYear")
            student = Student.objects.get(user=context.user)
            messoption = MessOption(student=student, messoptionopen=openmess, mess=mess)
            messoption.save()
            return UpdateMessOption(messoption=messoption)
        else:
            return None

class Mutation(graphene.ObjectType):
    update_mess_option = UpdateMessOption.Field()

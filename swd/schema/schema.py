import graphene
from main.schema.queries import Query 
from main.schema.mutations import Mutation
from django.contrib.auth.models import User

class Query(Query, graphene.ObjectType):
    pass

class Mutation(Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query,mutation=Mutation)
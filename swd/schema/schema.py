import graphene
import main.schema
from django.contrib.auth.models import User

class Query(main.schema.Query, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
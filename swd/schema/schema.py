import graphene
import main.schema

class Query(main.schema.Query, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
import graphene


class SimilarWebRank(graphene.ObjectType):
    global_rank = graphene.String(description='Similar web global rank')
    country_rank_us = graphene.String(description='Similar web us country rank')
    country_rank_in = graphene.String(description='Similar web india country rank')

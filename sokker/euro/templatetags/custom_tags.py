from django import template
from ..models import Game, Winners  # Adjust the import according to your model
from arcades.models import Game as GameArcades
from django.db.models import Max, IntegerField
from django.db.models.functions import Cast

register = template.Library()


@register.simple_tag
def get_group_games(cup_id, group_id):
    # Fetch the list of semi-final matches based on the passed cup_id
    return Game.objects.filter(c_id=cup_id, group_id=group_id).order_by("cup_round")

@register.simple_tag
def get_last_round_arcades(cup_id, group_id):
    # Fetch the list of games and return the maximum `cup_round`
    max_round = GameArcades.objects.filter(c_id=cup_id, group_id=group_id, g_status="yes")\
                .annotate(cup_round_as_int=Cast("cup_round", IntegerField()))\
                .aggregate(Max("cup_round_as_int"))["cup_round_as_int__max"]
    if max_round is None:
        return "1"
    return str(max_round)


@register.simple_tag
def get_group_games_arcades(cup_id, group_id, rounds=None):
    # Fetch the list of semi-final matches based on the passed cup_id
    if rounds:
        return  GameArcades.objects.filter(c_id=cup_id, group_id=group_id, cup_round=str(rounds)).order_by("cup_round")
    return GameArcades.objects.filter(c_id=cup_id, group_id=group_id).order_by("cup_round")

@register.simple_tag
def get_winners(cup_id, position, first=True):
    # Fetch the list of semi-final matches based on the passed cup_id
    if first:
        return Winners.objects.filter(cup_id=cup_id, position=position).first()
    winners = Winners.objects.filter(cup_id=cup_id, position=position)
    if len(winners) > 1:
        second_winner = winners[1]  # Get the second element
    else:
        second_winner = None  # Handle the case where there is no second element
    return second_winner

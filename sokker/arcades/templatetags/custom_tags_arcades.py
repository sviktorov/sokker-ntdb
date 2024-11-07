from django import template
from ..models import Game, Winners  # Adjust the import according to your model

register = template.Library()


@register.simple_tag
def get_group_games(cup_id, group_id):
    # Fetch the list of semi-final matches based on the passed cup_id
    return Game.objects.filter(c_id=cup_id, group_id=group_id).order_by("cup_round")


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

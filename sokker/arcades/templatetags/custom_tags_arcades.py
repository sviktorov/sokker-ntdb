from django import template
from ..models import Game, Winners, CupTeams, Cup, RankGroups # Added CupTeams import
from ..utils import get_next_monday_or_saturday
from django.db.models import Q
from django.core.paginator import Paginator
register = template.Library()

@register.simple_tag
def define(val=None):
  return val


@register.simple_tag
def get_active_cups():
    return Cup.objects.filter(c_active=True)

@register.simple_tag
def get_team_standing_by_cup(cup, team):
    queryset = RankGroups.objects.filter(c_id=cup, t_id=team).order_by("-points", "-gdif", "-gscored").first()
    return queryset

@register.simple_tag
def get_team_by_position_in_standings(cup_id, group_id, position):
    queryset = RankGroups.objects.filter(c_id=cup_id, g_id=group_id).order_by("-points", "-gdif", "-gscored")
    
    return queryset[int(position) - 1]

@register.simple_tag
def get_next_cl_date(date):
    # Fetch the list of semi-final matches based on the passed cup_id
    return get_next_monday_or_saturday(date)

@register.simple_tag
def get_group_games(cup_id, group_id):
    # Fetch the list of semi-final matches based on the passed cup_id
    return Game.objects.filter(c_id=cup_id, group_id=group_id).order_by("cup_round")

@register.simple_tag
def get_cup_team_games(cup_id, team_id):
    # Fetch the list of semi-final matches based on the passed cup_id
    return Game.objects.filter(c_id=cup_id).filter(Q(t_id_h=team_id) | Q(t_id_v=team_id)).order_by("cup_round")

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

@register.simple_tag
def score_display_for_team(game, team_id):
    if not game:
        return "N/A"
    return game.score_display_by_team(team_id)

@register.simple_tag
def score_display_for_team_as_class(game, team_id):
    if not game:
        return "N/A"
    return game.score_display_by_team_as_class(team_id)


@register.simple_tag
def score_points_for_team(game, team_id):
    if not game:
        return 0
    return game.score_points_by_team(team_id)

@register.simple_tag
def get_team_pot_game(c_id, team_id, pot_id, game_number):
    games = Game.objects.filter(
        (Q(t_id_h__in=CupTeams.objects.filter(pot_id=pot_id).exclude(t_id=team_id).values_list('t_id', flat=True)) |
         Q(t_id_v__in=CupTeams.objects.filter(pot_id=pot_id).exclude(t_id=team_id).values_list('t_id', flat=True))),
    ).filter(Q(t_id_h__id=team_id) | Q(t_id_v__id=team_id), c_id=c_id).order_by("cup_round").all()
    try:
        return games[game_number - 1]  # Subtract 1 since list indices start at 0
    except IndexError:
        return None

@register.filter(name='get_item')
def get_item(queryset, position):
    index = int(position) - 1
    try:
        return queryset[index].t_id.name  # Subtract 1 since list indices start at 0
    except (IndexError, TypeError):
        return None

@register.filter(name='show_goals')
def show_goals(goals):
    if goals is None:
        return "-"
    if goals == 0:
        return "0"
    else:
        return goals



@register.filter(name='show_goals_total')
def show_goals_total(game_list, place="home"):
    if game_list is None:
        return "-"
    flag = False    
    total = 0 

    if place == "home":
        if game_list[0].goals_home is not None:  
            flag = True
            total += game_list[0].goals_home
        if game_list[1].goals_away is not None:
            flag = True
            total += game_list[1].goals_away
        
    elif place == "away":
        if game_list[0].goals_away is not None:
            flag = True
            total += game_list[0].goals_away
        if game_list[1].goals_home is not None:
            flag = True
            total += game_list[1].goals_home
    if flag:
        return total 
    else:
        return "-"

@register.filter
def split(value, arg):
    return str(value).split(arg)
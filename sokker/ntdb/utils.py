from django.db.models import F, ExpressionWrapper, FloatField, CharField, Value, IntegerField, Max, Window, Sum

from django.db.models.functions import Concat, FirstValue
from ntdb.models import ArchivePlayer

import re


def set_pharse_player_data(player):
    player_data = "formidable [{}] stamina	tragic [{}] keeper\ndivine [{}] pace	divine [{}] defender\nincredible [{}] technique	very good [{}] playmaker\nexcellent [{}] passing	adequate [{}] striker"
    if not player:
        return player_data.format("", "", "", "", "", "", "", "")
    player_data = player_data.format(
        player.skillstamina,player.skillkeeper,
        player.skillpace, player.skilldefending,
        player.skilltechnique, player.skillplaymaking,
        player.skillpassing, player.skillscoring)
    return player_data

def extract_skill_value(text, skill_name):
    pattern = r'\[(\d+)\]\s*' + re.escape(skill_name)
    match = re.search(pattern, text)
    return match.group(1) if match else ""


def get_fullname_wrapper():
    return ExpressionWrapper(
        Concat(F("name"), Value(" "), F("surname")),
        output_field=CharField(),
    )


def get_gk_wrapper():
    return ExpressionWrapper(
        2 * F("skillkeeper") + 1.5 * F("skillpace") + F("skillpassing"),
        output_field=FloatField(),
    )


def get_def_wrapper():
    return ExpressionWrapper(
        1.5 * F("skillpace")
        + 1.5 * F("skilldefending")
        + F("skillplaymaking")
        + F("skilltechnique")
        + 0.5 * F("skillpassing"),
        output_field=FloatField(),
    )


def get_mid_wrapper():
    return ExpressionWrapper(
        1.5 * F("skillpassing")
        + 1.5 * F("skillplaymaking")
        + F("skillpace")
        + F("skilltechnique")
        + F("skilldefending")
        + 0.5 * F("skillscoring")
        + 0.25 * F("skillstamina"),
        output_field=FloatField(),
    )


def get_wing_wrapper():
    return ExpressionWrapper(
        1.5 * F("skillpassing")
        + 1 * F("skillplaymaking")
        + 1.5 * F("skillpace")
        + 1.5 * F("skilltechnique")
        + 0.5 * F("skilldefending")
        + 0.5 * F("skillscoring")
        + 0.25 * F("skillstamina"),
        output_field=FloatField(),
    )

def get_att_wrapper():
    return ExpressionWrapper(
        F("skilltechnique") + F("skillpace") + F("skillscoring"),
        output_field=FloatField(),
    )

def get_ntgames_wrapper():
    return Window(
        expression=Max('ntmatches'),
        partition_by='sokker_id'
    )

def get_ntgoals_wrapper():
    return Window(
        expression=Max('ntgoals'),
        partition_by='sokker_id'
    )
    
def get_ntassists_wrapper():
    return Window(
        expression=Max('ntassists'),
        partition_by='sokker_id'
    )

def get_games_wrapper():
    return Window(
        expression=Max('matches'),
        partition_by='sokker_id'
    )

def get_goals_wrapper():
    return Window(
        expression=Max('goals'),
        partition_by='sokker_id'
    )
    
def get_assists_wrapper():
    return Window(
        expression=Max('assists'),
        partition_by=F('sokker_id')
    )

def get_player_stat_for_age_season_type(sokker_id, age, stat_field, max_value=None):
    age_season = ArchivePlayer.objects.filter(sokker_id=sokker_id, age=age).order_by("-age").first()
    age_season_before = ArchivePlayer.objects.filter(sokker_id=sokker_id, age=age-1).order_by("-age").first()

    if not age_season:
        return 0
    
    end_field_value = getattr(age_season, stat_field)

    if not end_field_value:
        return 0
    
    if not age_season_before:
        start_field_value = None
    else:
        start_field_value = getattr(age_season_before, stat_field)
    
    if not start_field_value:
        if max_value:
            if end_field_value > max_value:
                return max_value
        return end_field_value
    else:
        result = int(end_field_value) - int(start_field_value)
        if max_value:
            if result > max_value:
                return max_value
        return result
   
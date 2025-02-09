from django import template
from ..models import ArchivePlayer, Player
from django.db.models import Max
from sokker_base.models import Country
from ntdb.utils import get_player_stat_for_age_season_type

from django.core.cache import cache
from functools import wraps
from hashlib import sha256
import string

from django.db.models.functions import Cast
from ntdb.tables import return_distinct_all_time_records_by_position
from ntdb.utils import get_gk_wrapper, get_def_wrapper, get_mid_wrapper, get_att_wrapper

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import base64 
from io import BytesIO 


register = template.Library()

CACHE_TIMEOUT_STATS = 1*60*60*24*7

def percentage(value, total):
    """Calculate percentage of value compared to total"""
    if not total or not value:
        return 0
    return round((value / total) * 100, 1)



def cache_result(timeout=900, key_format=None):
    """
    Caches function result based on parameters.
    
    :param timeout: Cache timeout in seconds (default 900s = 15 minutes)
    :param key_format: Custom key format (e.g., "player_stats:{team_id}:{sokker_id}")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract function argument names
            func_args = func.__code__.co_varnames[:func.__code__.co_argcount]
            params = dict(zip(func_args, args))  # Map positional args
            params.update(kwargs)  # Add keyword args
            # Handle None values in params
            safe_params = {k: str(v) if v is not None else 'x' for k, v in params.items()}

            # Build cache key using provided key_format
            try:
                if key_format:
                    # Extract all required keys from the format string
                    required_keys = [k[1] for k in string.Formatter().parse(key_format) if k[1] is not None]
                    # Add empty values for missing parameters
                    for key in required_keys:
                        if key not in safe_params:
                            safe_params[key] = ''
                    # Replace spaces and special characters with underscores
                    safe_params = {k: str(v).replace(' ', '_').replace(':', '_') for k, v in safe_params.items()}
                    cache_key = key_format.format(**safe_params)
                else:
                    # Default cache key with function name + params
                    cache_key = f"{func.__name__}:{safe_params}"
            except KeyError as e:
                # Fallback to a simpler cache key if format fails
                cache_key = f"{func.__name__}:{str(safe_params)}"
            
            # print(f"Cache key: {cache_key}")  # Debug log
            
            # Check cache
            cached_result = cache.get(cache_key)
            # print(f"Cache hit: {cached_result is not None}")  # Debug log

            if cached_result is not None:
                # print("Returning cached result")  # Debug log
                return cached_result

            # Compute result if not cached
            # print("Computing new result")  # Debug log
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            return result
        return wrapper
    return decorator



@register.simple_tag
@cache_result(timeout=CACHE_TIMEOUT_STATS, key_format="player_active_stats:{player}:{find_position}:{no_age}")
def get_player_active_stats(player, find_position=False, no_age=False):
    end_age = 50

    if player.age < 21:
        end_age = player.age
    if end_age == 50 and player.age < 28:
        end_age = player.age
    if no_age:
        end_age = 50
    if player.position == "GK":
        best = Player.objects.annotate(gk_points=get_gk_wrapper()).filter(countryid=player.countryid, position="GK", age__lte=end_age).order_by("-gk_points")
    if player.position == "DEF":
        best = Player.objects.annotate(def_points=get_def_wrapper()).filter(countryid=player.countryid, position="DEF", age__lte=end_age).order_by("-def_points")
    if player.position == "MID":
        best = Player.objects.annotate(mid_points=get_mid_wrapper()).filter(countryid=player.countryid, position="MID", age__lte=end_age).order_by("-mid_points")
    if player.position == "ATT":
        best = Player.objects.annotate(att_points=get_att_wrapper()).filter(countryid=player.countryid, position="ATT", age__lte=end_age).order_by("-att_points")
    top = best[0]

    if find_position:
        # Find position of the player in the list
        for index, record in enumerate(best, 1):
            if record.sokker_id == player.sokker_id:
                return index
        return None
    
    # Find the player's record in the list
    rating = 0
    
    for record in best:
        if record.sokker_id == player.sokker_id:
            rating = record
            break
    if not rating:
        return None
    if player.position == "GK":
        top_rating = top.gk_points
        return rating.gk_points, str(int(percentage(rating.gk_points, top_rating))), rating.age
    if player.position == "DEF":
        top_rating = top.def_points
        return rating.def_points, str(int(percentage(rating.def_points, top_rating))), rating.age
    if player.position == "MID":
        top_rating = top.mid_points
        return rating.mid_points, str(int(percentage(rating.mid_points, top_rating))), rating.age
    if player.position == "ATT":
        top_rating = top.att_points
        return rating.att_points, str(int(percentage(rating.att_points, top_rating))), rating.age
    return None

@register.simple_tag
@cache_result(timeout=CACHE_TIMEOUT_STATS, key_format="player_all_time_stats:{player}:{find_position}:{is_u21}")
def get_player_all_time_stats(player, find_position=False, is_u21=False):
    end_age = 50
    if is_u21:
        end_age = 21
    if player.age < 21:
        end_age = player.age
    if end_age == 50 and player.age < 28:
        end_age = player.age
    country = Country.objects.filter(code=player.countryid).first()
    best = return_distinct_all_time_records_by_position(player.position, country, 16, end_age)
    top = best[0]

    if find_position:
        # Find position of the player in the list
        for index, record in enumerate(best, 1):
            if record.sokker_id == player.sokker_id:
                return index
        return None
    
    # Find the player's record in the list
    rating = 0
    for record in best:
        if record.sokker_id == player.sokker_id:
            rating = record
            break
    if not rating:
        return 0, 0, player.age
    if player.position == "GK":
        top_rating = top.gk_points
        return rating.gk_points, str(int(percentage(rating.gk_points, top_rating))), rating.age
    if player.position == "DEF":
        top_rating = top.def_points
        return rating.def_points, str(int(percentage(rating.def_points, top_rating))), rating.age
    if player.position == "MID":
        top_rating = top.mid_points
        return rating.mid_points, str(int(percentage(rating.mid_points, top_rating))), rating.age
    if player.position == "ATT":
        top_rating = top.att_points
        return rating.att_points, str(int(percentage(rating.att_points, top_rating))), rating.age
    return None


@register.simple_tag
@cache_result(timeout=CACHE_TIMEOUT_STATS, key_format="player_stats:{sokker_id}:{stat_type}:{age_limit}")
def get_player_stats(sokker_id, stat_type, age_limit=None):
    # Get the maximum value of the specified stat for the player
    if stat_type == 'name':
        r= ArchivePlayer.objects.filter(sokker_id=sokker_id).order_by("-age").first()
        return r.name + " " + r.surname
    if age_limit:
        stat = ArchivePlayer.objects.filter(sokker_id=sokker_id, age__lte=age_limit).values(stat_type).aggregate(max_value=Max(stat_type))['max_value']
    else:
        stat = ArchivePlayer.objects.filter(sokker_id=sokker_id).values(stat_type).aggregate(max_value=Max(stat_type))['max_value']
    if not stat:
        stat = 0
    return stat


@register.simple_tag
@cache_result(timeout=18000, key_format="player_stats_team:{team_id}:{sokker_id}:{stat_type}:{stat_name}:{age_limit}:{season_limit}")
def get_player_stats_in_team(team_id, sokker_id, stat_type, stat_name, age_limit=None, season_limit=None):
    # Get the maximum value of the specified stat for the player
    if age_limit:
        age_seasons = ArchivePlayer.objects.filter(sokker_id=sokker_id, age__lte=age_limit).order_by("-age")
    else:
        age_seasons = ArchivePlayer.objects.filter(sokker_id=sokker_id).order_by("-age")
    stat_value = 0
    # print(team_id, sokker_id, stat_type, stat_name, age_limit, season_limit)

    for age_season in age_seasons:
        if stat_type == "team": 
            if age_season.teamid and age_season.teamid.id == team_id:
                stat = get_player_stat_for_age_season_type(sokker_id, age_season.age, stat_name, season_limit)
                if stat:
                    stat_value += stat
        elif stat_type == "youth":
            if age_season.youthteamid and age_season.youthteamid.id == team_id:
                stat = get_player_stat_for_age_season_type(sokker_id, age_season.age, stat_name, season_limit)
                if stat:
                    stat_value += stat
    return stat_value


@register.simple_tag
#@cache_result(timeout=CACHE_TIMEOUT_STATS, key_format="player_progression:{player}:{position}")
def get_player_skill_progression(player, position):
    plt.switch_backend('Agg')
    
    # Query based on position
    if position == "GK":
        best = ArchivePlayer.objects.annotate(skill_points=get_gk_wrapper())
    elif position == "DEF":
        best = ArchivePlayer.objects.annotate(skill_points=get_def_wrapper())
    elif position == "MID":
        best = ArchivePlayer.objects.annotate(skill_points=get_mid_wrapper())
    elif position == "ATT":
        best = ArchivePlayer.objects.annotate(skill_points=get_att_wrapper())
    
    best = best.filter(
        countryid=player.countryid, 
        position=position, 
        sokker_id=player.sokker_id
    ).exclude(age=player.age).order_by("-skill_points")
    

    # Create history data
    history = [(record.age, record.skill_points) for record in best]
    data = np.array(history)

    # Convert to DataFrame and sort by age
    df = pd.DataFrame(data, columns=["Age", position])
    df = df.sort_values("Age")  # Sort to ensure chronological order

    # Get min and max ages from data
    min_age = int(min(df["Age"]))
    max_age = int(max(df["Age"]))
    max_age_prediction = min(max_age + 15, 34)
    
    # Create smooth prediction points
    prediction_ages = np.linspace(min_age, max_age_prediction)
    only_prediction_ages = np.linspace(max_age, max_age_prediction)

    # Fit polynomial to actual data points
    poly = PolynomialFeatures(degree=3, interaction_only=True)
    model = LinearRegression(copy_X=True, positive=True)
    X = df["Age"].values.reshape(-1, 1)
    y = df[position].values
    X_poly = poly.fit_transform(X)
    model.fit(X_poly, y)
    
   
    # Initialize last_pred with the last actual value from the data
    last_pred = df[position].iloc[0]
    predicted_curve = []
    for age in prediction_ages:
        age_poly = poly.transform([[age]])
        pred = model.predict(age_poly)[0]
        
        
      # Enhanced growth between 16-29
        if age <= 29:
        # Quadratic growth before 29
            growth_factor = 1.2  # Slight boost for realistic training effect
        else:
            # Exponential decline after 30
            decline_rate = 0.08  # Controls the decline speed (higher = sharper decline)
            decline_factor = np.exp(-decline_rate * (age - 29))  
            pred = pred * decline_factor  # Apply exponential decay
            print(age, pred)
        
        predicted_curve.append(pred)
        last_pred = pred



    # Create plot
    plt.figure(figsize=(12, 6))
    # Add scatter plot for actual data points
    plt.scatter(df["Age"], df[position], color="blue", s=50, zorder=5, label="Actual Points")
    # Add line for actual data
    plt.plot(df["Age"], df[position], color="blue", alpha=0.5)
    # Add prediction line
    #predicted_curve = predicted_curve[-len(only_prediction_ages):]  # Get last elements matching only_prediction_ages length
    print(predicted_curve)
    plt.plot(prediction_ages, predicted_curve, color="red", linestyle='--', label="Prediction")
    
    plt.xlabel("Age")
    plt.ylabel("Skill Points")
    plt.legend()
    plt.title("Player Skill Progression")
    plt.grid(True, linestyle='--', alpha=0.7)

    # Save plot to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()

    graph = base64.b64encode(image_png).decode('utf-8')

    return {
        'plot': graph
    }

   
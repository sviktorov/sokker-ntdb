from django.urls import path

from . import views


urlpatterns = [
    path(
        "tactics-transfer",
        views.fetch_tactics_data,
        name="tactics_transfer",
    ),
    path(
        "player-prediction",
        views.PlayerPrediction.as_view(),
        name="player_prediction",
    ),
]

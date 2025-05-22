from .models import (
    Cup,
    CupTeams,
    CupDraw,
    Game,
    RankGroups,
    Winners,
    Medals,
    RankAllTime,
    CupCategory,
    CupGameStats,
    GameDetails,
    Player,
    PlayoffPots,
    PlayoffDraw,
)

from import_export import resources
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django.contrib import admin
from .utils import WEEKDAY_CHOICES

@admin.register(PlayoffPots)
class PlayoffPotsAdmin(ImportExportModelAdmin):
    autocomplete_fields = ('c_id', 't_id')
    list_display = ("c_id", "pot_id", "t_id")
    list_filter = ("c_id", "pot_id", "t_id")
    search_fields = ('c_id', 'pot_id', 't_id')

@admin.register(PlayoffDraw)
class PlayoffDrawAdmin(ImportExportModelAdmin):
    autocomplete_fields = ('c_id', 't_id')
    list_display = ("c_id", "pot_id", "t_id", "draw_id")
    list_filter = ("c_id", "pot_id", "t_id", "draw_id")
    search_fields = ('c_id', 'pot_id', 't_id', 'draw_id')


@admin.register(CupCategory)
class CupCategoryAdmin(ImportExportModelAdmin):
    list_display = ("name",)


@admin.action(description='Mark selected items as active')
def mark_as_active(modeladmin, request, queryset):
    queryset.update(c_active=True)

@admin.action(description='Mark selected items as inactive')
def mark_as_inactive(modeladmin, request, queryset):
    queryset.update(c_active=False)

@admin.register(Cup)
class CupAdmin(ImportExportModelAdmin):

    list_display = (
        "id",
        "c_name",
        "c_edition",
        "c_active",
        "c_status",
        "c_draw_status",
        "category",
    )
    list_filter = (
        "c_active",
        "c_status",
        "c_draw_status",
        "category",
    )
    ordering = ("c_name",)
    search_fields = ('c_name',)
    actions = [mark_as_active, mark_as_inactive]


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Replace the default JSONField with a MultipleChoiceField
        form.base_fields["match_days"] = forms.MultipleChoiceField(
            choices=WEEKDAY_CHOICES,
            required=False,
            widget=FilteredSelectMultiple("Match Days", is_stacked=False),
            initial=[int(v) for v in obj.match_days] if obj and obj.match_days else [],
        )
        return form

  
    
class CupTeamsAdminResource(resources.ModelResource):
    pot_id = resources.Field(attribute='pot_id', column_name='pot_id')
    rating = resources.Field(attribute='rating', column_name='rating')
    cl_draw = resources.Field(attribute='cl_draw', column_name='cl_draw')

    class Meta:
        model = CupTeams 
        fields = ('id', 'c_id', 't_id', 'g_id', 'pot_id', 'rating', 'cl_draw', 't_id__name')
        export_order = ('id', 'c_id', 't_id', 'g_id', 'pot_id', 'rating', 'cl_draw', 't_id__name')
        import_id_fields = ('id', 'c_id', 't_id', 'g_id', 'pot_id', 'rating', 'cl_draw')


@admin.register(CupTeams)
class CupTeamsAdmin(ImportExportModelAdmin):
    autocomplete_fields = ('t_id', 'c_id')   
    list_display = ("t_id", "pot_id", "c_id", "g_id", "rating", "cl_draw")
    ordering = ("c_id",)
    search_fields = ('t_id',)
    list_filter = ("c_id", "g_id", "pot_id")
    resource_class = CupTeamsAdminResource


@admin.register(CupDraw)
class CupDrawAdmin(ImportExportModelAdmin):
    autocomplete_fields = ('t_id',)   
    list_display = ("t_id", "c_id", "g_id", "rating")
    ordering = ("c_id",)
    search_fields = ('t_id',)
    list_filter = ("c_id", "g_id", "c_id")


@admin.action(description='Mark selected items as played')
def mark_as_played(modeladmin, request, queryset):
    queryset.update(g_status='yes')

@admin.action(description='Mark selected items as adjusted')
def mark_as_adjusted(modeladmin, request, queryset):
    queryset.update(g_status='ADJ')

@admin.action(description='Mark selected items as reseted')
def mark_as_reseted(modeladmin, request, queryset):
    queryset.update(g_status='')

@admin.action(description='Mark selected items as arranged')
def mark_as_arranged(modeladmin, request, queryset):
    queryset.update(g_status='arranged')

@admin.action(description='Mark Has Stats flag as 0')
def mark_stats_flag_0(modeladmin, request, queryset):
    queryset.update(has_stats=False)

@admin.action(description='Mark Has stats flag as 1')
def mark_stats_flag_1(modeladmin, request, queryset):
    queryset.update(has_stats=True)

@admin.register(GameDetails)
class GameDetailsAdmin(ImportExportModelAdmin):
    list_display = ("game_id", "team_id", "is_home")
    list_filter = ("game_id__c_id", "team_id", "is_home")
    search_fields = ('game_id', 'team_id')

@admin.register(Game)
class GameAdmin(ImportExportModelAdmin):
    autocomplete_fields = ('t_id_h', 't_id_v', 'c_id')  
    list_display = (
        "t_id_h",
        "t_id_v",
        "cup_round",
        "goals_home",
        "goals_away",
        "playoff_position",
        "group_id",
        "has_stats",
        "g_status",
    )
    list_filter = (
        "c_id",
        "group_id",
        "cup_round",
        "playoff_position",
        "g_status",
        "has_stats",
    )
    ordering = (
        "t_id_h",
        "t_id_v",
    )
    search_fields = ('t_id_h', 't_id_v', 'c_id',)

    actions = [mark_as_played, mark_as_adjusted, mark_as_reseted, mark_as_arranged, mark_stats_flag_0, mark_stats_flag_1]
@admin.register(RankGroups)
class RankGroupsAdmin(ImportExportModelAdmin):
    autocomplete_fields = ('t_id', 'c_id')  
    list_display = ("t_id", "c_id", "g_id", "points", "grecieved", "gscored", "gdif")
    list_filter = (
        "c_id",
        "g_id",
    )
    ordering = ("-points", "-gdif")


@admin.register(Medals)
class MedalsAdmin(ImportExportModelAdmin):
    autocomplete_fields = ('t_id',)  
    list_display = ("t_id", "position_1", "position_2", "position_3", "position_4")
    list_filter = ("t_id",)
    ordering = ("position_1",)


@admin.register(Winners)
class WinnersAdmin(ImportExportModelAdmin):
    autocomplete_fields = ('team_id', 'cup_id')  
    list_display = (
        "team_id",
        "cup_id",
        "position",
    )
    list_filter = (
        "team_id",
        "position",
    )
    ordering = ("cup_id",)


@admin.register(RankAllTime)
class RankAllTimeAdmin(ImportExportModelAdmin):
    list_display = ("t_id", "c_flow", "points", "grecieved", "gscored", "gdif")
    list_filter = (
        "t_id",
        "c_flow",
    )
    ordering = ("-points", "-gdif")


@admin.register(Player)
class PlayerAdmin(ImportExportModelAdmin):
    list_display = ("name", "team_id", "country_id")
    list_filter = ("team_id", "country_id")
    ordering = ("name",)
    search_fields = ('name',)


@admin.register(CupGameStats)
class CupGameStatsAdmin(ImportExportModelAdmin):
    list_display = ("player_id", "team_id", "goals", "game_id", "assists", "red_cards", "yellow_cards")
    list_filter = ("team_id", "game_id__c_id", "player_id")
    search_fields = ('team_id', 'game_id__c_id', 'player_id')

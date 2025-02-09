from .models import Player, ArchivePlayer, NTTeamsStats
from sokker_base.models import Country
from django_filters import FilterSet
import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from .utils import (
    get_gk_wrapper,
    get_def_wrapper,
    get_mid_wrapper,
    get_att_wrapper,
    get_fullname_wrapper,
    get_wing_wrapper,
    get_ntgames_wrapper,
    get_ntgoals_wrapper,
    get_ntassists_wrapper,
    get_games_wrapper,
    get_goals_wrapper,
    get_assists_wrapper,
)
from django.urls import reverse
from django.utils.safestring import mark_safe
import logging

logger = logging.getLogger(__name__)


class TeamColumn(tables.Column):
    _country_cache = {}  # Class-level cache for country names

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orderable = False
        self.verbose_name = _("Team")

    def render(self, value, record):
        logger.debug("render() called with value: %s, record: %s", value, record)
        team = getattr(
            record, "teamid", None
        )  # Get the teamid attribute from the record
        if team is None:
            return "x"  # Return a default value if teamid is not found

        flag_image = ""
        if team and team.country:
            flag_image = f"https://sokker.org/static/pic/flags/{team.country.code}.svg"

        # Use cached country name if available
        if record.countryid not in self._country_cache:
            country = Country.objects.filter(code=record.countryid).first()
            self._country_cache[record.countryid] = country.name if country else None
        
        country_name = self._country_cache[record.countryid]
        
        url = f"https://sokker.org/en/app/team/{team.id}/"
        url2 = reverse('best_players_team_stats', kwargs={'team_id': team.id, 'country_name': country_name})
        html_string = f'{team.name} <img width="20" height="13" src="{flag_image}" alt="Team Flag"> \
                        <a href="{url2}" target="_blank"><i class="fas fa-chart-line"></i></a> \
                        <a href="{url}" target="_blank"><i class="fas fa-futbol"></i></a>'
        return mark_safe(html_string)  # Mark HTML as safe for renderingMark HTML as safe for rendering


class YouthTeamColumn(tables.Column):
    _country_cache = {}  # Class-level cache for country names
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orderable = False
        self.verbose_name = _("Youth Team")

    def render(self, value, record):
        logger.debug("render() called with value: %s, record: %s", value, record)
        team = getattr(
            record, "youthteamid", None
        )  # Get the teamid attribute from the record
        if team is None:
            return "x"  # Return a default value if teamid is not found

        flag_image = ""
        if team and team.country:
            flag_image = f"https://sokker.org/static/pic/flags/{team.country.code}.svg"

        # Use cached country name if available
        if record.countryid not in self._country_cache:
            country = Country.objects.filter(code=record.countryid).first()
            self._country_cache[record.countryid] = country.name if country else None
        
        country_name = self._country_cache[record.countryid]
        

        url = f"https://sokker.org/en/app/team/{team.id}/"
        url2 = reverse('best_players_team_stats', kwargs={'team_id': team.id, 'country_name': country_name})
        html_string = f'{team.name} <img width="20" height="13" src="{flag_image}" alt="Team Flag"> \
                        <a href="{url2}" target="_blank"><i class="fas fa-chart-line"></i></a> \
                        <a href="{url}" target="_blank"><i class="fas fa-futbol"></i></a>'
        return mark_safe(html_string)  # Mark HTML as safe for rendering



class SokkerID(tables.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orderable = False
        self.verbose_name = _("Link")

    def render(self, value, record):
        sokker_id = getattr(
            record, "sokker_id", None
        )  # Get the sokker_id attribute from the record
        if sokker_id is None:
            return "-"  # Return a default value if sokker_id is not found
        url = "https://sokker.org/player/PID/{}".format(sokker_id)
        html_string = f'<a href="{url}" target="_blank"><i class="fas fa-futbol"></i></a>'
        return mark_safe(html_string)


class RankInTable(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orderable = False  # Set the column as not orderable
        self.verbose_name = _("N.")


class FullNameColumn(tables.Column):
    _country_cache = {}  # Class-level cache for country names
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orderable = False  # Set the column as not orderable
        self.verbose_name = _("Name")

    def order(self, queryset, is_descending):
        if is_descending:
            order_by_string = "-fullname"
        else:
            order_by_string = "fullname"
        queryset = queryset.annotate(
            fullname=get_fullname_wrapper(),
        ).order_by(order_by_string)
        return (queryset, True)

    def render(self, value, record):

        sokker_id = record.sokker_id
        country_id = record.countryid
        if not country_id:
            country_id = 54
        if country_id not in self._country_cache:
            country = Country.objects.filter(code=country_id).first()
            self._country_cache[country_id] = country.name if country else None
        country_name = self._country_cache[country_id]

        url = reverse(
            "player_history",
            kwargs={"sokker_id": sokker_id, "country_name": country_name},
        )
 # Return a default value if sokker_id is not found
        url2 = "https://sokker.org/player/PID/{}".format(sokker_id)
        html_string = f'{value} <a href="{url}" target="_blank"><i class="fas fa-chart-line"></i></a> \
                       <a href="{url2}" target="_blank"><i class="fas fa-futbol"></i></a>'
        return mark_safe(html_string)


class GkPointsColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verbose_name = _("GK")

    def order(self, queryset, is_descending):
        if is_descending:
            order_by_string = "-gk_points"
        else:
            order_by_string = "gk_points"
        queryset = queryset.annotate(
            gk_points=get_gk_wrapper(),
        ).order_by(order_by_string)
        return (queryset, True)


class DefPointsColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verbose_name = _("DEF")

    def order(self, queryset, is_descending):
        if is_descending:
            order_by_string = "-def_points"
        else:
            order_by_string = "def_points"
        queryset = queryset.annotate(
            def_points=get_def_wrapper(),
        ).order_by(order_by_string)
        return (queryset, True)


class MidPointsColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verbose_name = _("MID")

    def order(self, queryset, is_descending):
        if is_descending:
            order_by_string = "-mid_points"
        else:
            order_by_string = "mid_points"
        queryset = queryset.annotate(
            mid_points=get_mid_wrapper(),
        ).order_by(order_by_string)
        return (queryset, True)


class WingPointsColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verbose_name = _("WING")

    def order(self, queryset, is_descending):
        if is_descending:
            order_by_string = "-wing_points"
        else:
            order_by_string = "wing_points"
        queryset = queryset.annotate(
            wing_points=get_wing_wrapper(),
        ).order_by(order_by_string)
        return (queryset, True)

class AttPointsColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verbose_name = _("ATT")

    def order(self, queryset, is_descending):
        if is_descending:
            order_by_string = "-att_points"
        else:
            order_by_string = "att_points"
        queryset = queryset.annotate(
            att_points=get_att_wrapper(),
        ).order_by(order_by_string)
        return (queryset, True)


class PlayerTable(tables.Table):
    teamid = TeamColumn()
    youthteamid = YouthTeamColumn()
    rank = RankInTable("{{ row_counter|add:'1' }}")
    fullname = FullNameColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(fullname=get_fullname_wrapper())
        queryset.exclude(fullname=" ")
        return queryset

    class Meta:
        model = Player
        per_page = 100
        fields = ("rank", "fullname", "age", "teamid", "youthteamid")
        sequence = ("rank", "fullname", "age", "teamid", "youthteamid")


class ArchivePlayerTable(tables.Table):
    teamid = TeamColumn()
    youthteamid = YouthTeamColumn()
    rank = RankInTable("{{ row_counter|add:'1' }}")
    fullname = FullNameColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(fullname=get_fullname_wrapper())

        queryset.exclude(fullname=" ")
        return queryset

    class Meta:
        model = ArchivePlayer
        per_page = 100
        fields = ("rank", "fullname", "age", "teamid", "youthteamid")
        sequence = ("rank", "fullname", "age", "teamid", "youthteamid")


class GKPlayerTable(PlayerTable):
    gk_points = GkPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            gk_points=get_gk_wrapper(),
        )

        queryset.filter(position="GK")
        return queryset.order_by("-gk_points")

    class Meta:
        model = Player
        template_name = "django_tables2/bootstrap.html"
        fields = ("rank", "fullname", "age", "gk_points")
        sequence = ("rank", "fullname", "age", "gk_points")


class GKArchivePlayerTable(ArchivePlayerTable):
    gk_points = GkPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            gk_points=get_gk_wrapper(),
        )

        queryset.filter(position="GK")
        return queryset.order_by("-gk_points")

    class Meta:
        fields = ("rank", "fullname", "age", "gk_points")
        sequence = ("rank", "fullname", "age", "gk_points")


class DefPlayerTable(PlayerTable):
    def_points = DefPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            def_points=get_def_wrapper(),
        )

        queryset.filter(position="DEF")
        return queryset.order_by("-def_points")

    class Meta:
        fields = ("rank", "fullname", "age", "def_points")
        sequence = ("rank", "fullname", "age", "def_points")


class DefArchivePlayerTable(ArchivePlayerTable):
    def_points = DefPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            def_points=get_def_wrapper(),
        )

        queryset.filter(position="DEF")
        return queryset.order_by("-def_points")

    class Meta:
        template_name = "django_tables2/bootstrap.html"
        fields = ("rank", "fullname", "age", "def_points")
        sequence = ("rank", "fullname", "age", "def_points")


class MidPlayerTable(PlayerTable):
    mid_points = MidPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            mid_points=get_mid_wrapper(),
        )

        queryset.filter(position="MID")
        return queryset.order_by("-mid_points")

    class Meta:
        fields = ("rank", "fullname", "age", "mid_points")
        sequence = ("rank", "fullname", "age", "mid_points")

class WingPlayerTable(PlayerTable):
    wing_points = WingPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            wing_points=get_wing_wrapper(),
        )

        queryset.filter(position="MID")
        return queryset.order_by("-wing_points")

    class Meta:
        fields = ("rank", "fullname", "age", "wing_points")
        sequence = ("rank", "fullname", "age", "wing_points")


class MidArchivePlayerTable(ArchivePlayerTable):
    mid_points = MidPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            mid_points=get_mid_wrapper(),
        )

        queryset.filter(position="MID")
        return queryset.order_by("-mid_points")

    class Meta:
        fields = ("rank", "fullname", "age", "mid_points")
        sequence = ("rank", "fullname", "age", "mid_points")

class WingArchivePlayerTable(ArchivePlayerTable):
    wing_points = WingPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            def_points=get_wing_wrapper(),
        )

        queryset.filter(position="MID")
        return queryset.order_by("-wing_points")

    class Meta:
        fields = ("rank", "fullname", "age", "wing_points")
        sequence = ("rank", "fullname", "age", "wing_points")


class AttPlayerTable(PlayerTable):
    att_points = AttPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            def_points=get_att_wrapper(),
        )

        queryset.filter(position="ATT")
        return queryset.order_by("-att_points")

    class Meta:
        fields = ("rank", "fullname", "age", "att_points")
        sequence = ("rank", "fullname", "age", "att_points")


class AttArchivePlayerTable(ArchivePlayerTable):
    att_points = AttPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            att_points=get_att_wrapper(),
        )

        queryset.filter(position="ATT")
        return queryset.order_by("-att_points")

    class Meta:
        fields = ("rank", "fullname", "age", "att_points")
        sequence = ("rank", "fullname", "age", "att_points")

class NTGamesArchivePlayerTable(ArchivePlayerTable):
    ntmatches_max = tables.Column(
        verbose_name='NT Matches',  # Or whatever header you want to display
        order_by=('-ntmatches_max',)
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(ntmatches_max=get_ntgames_wrapper()).order_by("-ntmatches_max")

    class Meta:
        exclude = ('age',)
        fields = ("rank", "fullname", "ntmatches_max")
        sequence = ("rank", "fullname", "ntmatches_max")

class NTGoalsArchivePlayerTable(ArchivePlayerTable):
    ntgoals_max = tables.Column(
        verbose_name='NT Goals',  # Or whatever header you want to display
        order_by=('-ntgoals_max',)
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(ntgoals_max=get_ntgoals_wrapper()).order_by("-ntgoals_max")

    class Meta:
        exclude = ('age',)
        fields = ("rank", "fullname", "ntgoals_max")
        sequence = ("rank", "fullname", "ntgoals_max")


class NTAssistsArchivePlayerTable(ArchivePlayerTable):
    ntassists_max = tables.Column(
        verbose_name='NT Assists',  # Or whatever header you want to display
        order_by=('-ntassists_max',)
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(ntassists_max=get_ntassists_wrapper()).order_by("-ntassists_max")

    class Meta:
        exclude = ('age',)
        fields = ("rank", "fullname", "ntassists_max")
        sequence = ("rank", "fullname", "ntassists_max")

class GamesArchivePlayerTable(ArchivePlayerTable):
    games_max = tables.Column(
        verbose_name='Games',  # Or whatever header you want to display
        order_by=('-games_max',)
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(games_max=get_games_wrapper()).order_by("-games_max")

    class Meta:
        exclude = ('age',)
        fields = ("rank", "fullname", "games_max")
        sequence = ("rank", "fullname", "games_max")

class GoalsArchivePlayerTable(ArchivePlayerTable):
    goals_max = tables.Column(
        verbose_name='NT Goals',  # Or whatever header you want to display
        order_by=('-goals_max',)
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(goals_max=get_goals_wrapper()).order_by("-goals_max")

    class Meta:
        fields = ("rank", "fullname", "goals_max")
        sequence = ("rank", "fullname", "goals_max")



class AssistsArchivePlayerTable(ArchivePlayerTable):
    assists_max = tables.Column(
        verbose_name='Assists',  # Or whatever header you want to display
        order_by=('-assists_max',)
    )
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.annotate(assists_max=get_assists_wrapper()).order_by("assists_max")

    class Meta:
        exclude = ('age',)
        fields = ("rank", "fullname", "assists_max")
        sequence = ("rank", "fullname", "assists_max")


class NTGamesYouthTeamsArchivePlayerTable(ArchivePlayerTable):
    class Meta:
        exclude = ('age',)
        fields = ("rank", "fullname")
        sequence = ("rank", "fullname")   


def return_distinct_all_time_records_by_position(
    sPosition, country, start_age, end_age
):
    distinctIDs = []
    aPlayers = []
    if not country:
        return []
    if sPosition == "GK":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(gk_points=get_gk_wrapper())
            .filter(gk_points__gt=0)
            .filter(countryid=country.code)
            .filter(position=sPosition)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("-gk_points")
        )
    if sPosition == "DEF":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(def_points=get_def_wrapper())
            .filter(def_points__gt=0)
            .filter(position=sPosition)
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("-def_points")
        )
    if sPosition == "MID":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(mid_points=get_mid_wrapper())
            .filter(mid_points__gt=0)
            .filter(position=sPosition)
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("-mid_points")
        )
    if sPosition == "WING":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(wing_points=get_wing_wrapper())
            .filter(wing_points__gt=0)
            #.filter(position="MID")
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("-wing_points")
        )
    if sPosition == "ATT":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(att_points=get_att_wrapper())
            .filter(att_points__gt=0)
            .filter(position=sPosition)
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("-att_points")
        )
    if sPosition == "NT_GAMES":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(ntmatches_max=get_ntgames_wrapper())
            #.filter(position=sPosition)
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("ntmatches_max")
        )
    if sPosition == "NT_GAMES_YOUTH_TEAMS":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(ntmatches_max=get_ntgames_wrapper())
            .filter(ntmatches_max__gt=0)
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("ntmatches_max")
        )
    if sPosition == "NT_GOALS":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(ntgoals_max=get_ntgoals_wrapper())
            #.filter(position=sPosition)
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("ntgoals_max")
        )
    if sPosition == "NT_ASSISTS":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(ntassists_max=get_ntassists_wrapper())
            #.filter(position=sPosition)
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("ntassists_max")
        )
    if sPosition == "ASSISTS":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(assists_max=get_assists_wrapper())
            #.filter(position=sPosition)
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("assists_max")
        )
    if sPosition == "GOALS":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(goals_max=get_goals_wrapper())
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("goals_max")
        )       
    if sPosition == "GAMES":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(games_max=get_games_wrapper())
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("games_max")
        )
    aPlayersDistinct = []
    for p in aPlayers:
        if p.sokker_id not in distinctIDs:
            aPlayersDistinct.append(p)
            distinctIDs.append(p.sokker_id)
    return aPlayersDistinct


class PlayerFilter(FilterSet):
    class Meta:
        model = Player
        fields = {"age": ["exact"], "position": ["exact"]}


class ArchivePlayerDetailsTable(ArchivePlayerTable):
    att_points = AttPointsColumn()
    def_points = DefPointsColumn()
    gk_points = GkPointsColumn()
    mid_points = MidPointsColumn()
    wing_points = WingPointsColumn()
    teamid = TeamColumn()
    ntmatches = tables.Column(verbose_name=_("NT Matches"))
    ntgoals = tables.Column(verbose_name=_("NT Goals"))
    ntassists = tables.Column(verbose_name=_("NT Assists"))
    matches = tables.Column(verbose_name=_("Matches"))
    goals = tables.Column(verbose_name=_("Goals"))
    assists = tables.Column(verbose_name=_("Assists"))

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            att_points=get_att_wrapper(),
            gk_points=get_gk_wrapper(),
            def_points=get_def_wrapper(),
            mid_points=get_mid_wrapper(),
            wing_points=get_wing_wrapper(),
            matches=get_games_wrapper(),
            goals=get_goals_wrapper(),
            assists=get_assists_wrapper(),
            ntmatches=get_ntgames_wrapper(),
            ntgoals=get_ntgoals_wrapper(),
            ntassists=get_ntassists_wrapper(),
        )

        return queryset.order_by("-age")

    class Meta:
        exclude = ("rank", "last_name")
        fields = (
            "fullname",
            "age",
            "gk_points",
            "att_points",
            "mid_points",
            "wing_points",
            "def_points",
            "ntmatches",
            "ntgoals",
            "ntassists",
            "teamid",
            "youthteamid",
        )
        sequence = (
            "fullname",
            "age",
            "gk_points",
            "att_points",
            "mid_points",
            "wing_points",
            "def_points",
            "ntmatches",
            "ntgoals",
            "ntassists",
            "teamid",
            "youthteamid",
        )
        per_page = 100

class NTTeamsStatsTable(tables.Table):
    teamid = TeamColumn()
    ntmatches = tables.Column(verbose_name=_("NT Matches"))
    ntgoals = tables.Column(verbose_name=_("NT Goals"))
    ntassists = tables.Column(verbose_name=_("NT Assists"))

    class Meta:
        model = NTTeamsStats
        exclude = ("id","countryid", "stat_type", "json_data_youth", "json_data")

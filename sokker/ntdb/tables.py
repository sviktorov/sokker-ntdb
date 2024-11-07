from .models import Player, ArchivePlayer
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
)
from django.urls import reverse
from django.utils.safestring import mark_safe
import logging

logger = logging.getLogger(__name__)


class TeamColumn(tables.Column):
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

        url = f"https://sokker.org/en/app/team/{team.id}/"
        html_string = f'<a href="{url}" target="_blank"><img width="20" height="13" src="https://sokker.org/static/pic/flags/{team.country.code}.svg" alt="Team Flag">{team.name}</a>'
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
        html_string = f'<a href="{url}" target="_blank">link</a>'
        return mark_safe(html_string)


class RankInTable(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orderable = False  # Set the column as not orderable
        self.verbose_name = _("N.")


class FullNameColumn(tables.Column):
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
        country = Country.objects.filter(code=country_id).first()

        url = reverse(
            "player_history",
            kwargs={"sokker_id": sokker_id, "country_name": country.name},
        )
        html_string = f'<a href="{url}">{value}</a>'
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
    rank = RankInTable("{{ row_counter|add:'1' }}")
    sokker_id = SokkerID()
    fullname = FullNameColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(fullname=get_fullname_wrapper())
        queryset.exclude(fullname=" ")
        return queryset

    class Meta:
        model = Player
        per_page = 100
        fields = ("rank", "sokker_id", "fullname", "age")
        sequence = ("rank", "sokker_id", "fullname", "age")


class ArchivePlayerTable(tables.Table):
    team_link = TeamColumn()
    rank = RankInTable("{{ row_counter|add:'1' }}")
    sokker_id = SokkerID()
    fullname = FullNameColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(fullname=get_fullname_wrapper())

        queryset.exclude(fullname=" ")
        return queryset

    class Meta:
        model = ArchivePlayer
        per_page = 100
        fields = ("rank", "sokker_id", "fullname", "age", "teamid")
        sequence = ("rank", "sokker_id", "fullname", "age", "teamid")


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
        fields = ("rank", "sokker_id", "fullname", "age", "gk_points")
        sequence = ("rank", "sokker_id", "fullname", "age", "gk_points")


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
        fields = ("rank", "sokker_id", "fullname", "age", "gk_points")
        sequence = ("rank", "sokker_id", "fullname", "age", "gk_points")


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
        fields = ("rank", "sokker_id", "fullname", "age", "def_points")
        sequence = ("rank", "sokker_id", "fullname", "age", "def_points")


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
        fields = ("rank", "sokker_id", "fullname", "age", "def_points")
        sequence = ("rank", "sokker_id", "fullname", "age", "def_points")


class MidPlayerTable(PlayerTable):
    mid_points = MidPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            def_points=get_mid_wrapper(),
        )

        queryset.filter(position="MID")
        return queryset.order_by("-mid_points")

    class Meta:
        fields = ("rank", "sokker_id", "fullname", "age", "mid_points")
        sequence = ("rank", "sokker_id", "fullname", "age", "mid_points")


class MidArchivePlayerTable(ArchivePlayerTable):
    mid_points = MidPointsColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            def_points=get_mid_wrapper(),
        )

        queryset.filter(position="MID")
        return queryset.order_by("-mid_points")

    class Meta:
        fields = ("rank", "sokker_id", "fullname", "age", "mid_points")
        sequence = ("rank", "sokker_id", "fullname", "age", "mid_points")


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
        fields = ("rank", "sokker_id", "fullname", "age", "att_points")
        sequence = ("rank", "sokker_id", "fullname", "age", "att_points")


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
        fields = ("rank", "sokker_id", "fullname", "age", "att_points")
        sequence = ("rank", "sokker_id", "fullname", "age", "att_points")


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
            .filter(position=sPosition)
            .filter(countryid=country.code)
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
            .filter(position=sPosition)
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("-mid_points")
        )

    if sPosition == "ATT":
        aPlayers = (
            ArchivePlayer.objects.annotate(fullname=get_fullname_wrapper())
            .annotate(att_points=get_att_wrapper())
            .filter(position=sPosition)
            .filter(countryid=country.code)
            .filter(age__lte=end_age)
            .filter(age__gte=start_age)
            .exclude(name="")
            .exclude(surname="")
            .order_by("-att_points")
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
    teamid = TeamColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            att_points=get_att_wrapper(),
            gk_points=get_gk_wrapper(),
            def_points=get_def_wrapper(),
            mid_points=get_mid_wrapper(),
        )

        return queryset.order_by("-age")

    class Meta:
        exclude = ("rank", "last_name")
        fields = (
            "sokker_id",
            "fullname",
            "age",
            "gk_points",
            "att_points",
            "mid_points",
            "def_points",
            "teamid",
        )
        sequence = (
            "sokker_id",
            "fullname",
            "age",
            "team_link",
            "gk_points",
            "att_points",
            "mid_points",
            "def_points",
            "teamid",
        )
        per_page = 100

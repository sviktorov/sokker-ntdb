from .models import RankGroups
import django_tables2 as tables
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class NTTeamColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orderable = False
        self.verbose_name = _("Team")

    def render(self, value, record):

        team = getattr(record, "t_id", None)  # Get the teamid attribute from the record
        if team is None:
            return "x"  # Return a default value if teamid is not found

        url = f"https://sokker.org/en/app/team/{team.t_sokker_id}/"
        html_string = f'<a href="{url}" target="_blank"><img width="20" height="16"  src="https://sokker.org/static/pic/flags/{team.t_sokker_id}.svg" alt="Team Flag">{team.t_name}</a>'
        return mark_safe(html_string)  # Mark HTML as safe for rendering


class RankGroupsTable(tables.Table):
    t_id = NTTeamColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    class Meta:
        model = RankGroups
        fields = (
            "t_id",
            "games",
            "wins",
            "draw",
            "loose",
            "gscored",
            "grecieved",
            "gdif",
            "points",
        )

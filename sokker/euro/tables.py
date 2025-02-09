from .models import RankGroups
import django_tables2 as tables
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import re

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


def extract_number_from_string(s):
    match = re.search(r'\((\d+)\)', s)
    if match:
        return int(match.group(1))
    return None  # Return None if no number is found

class OrderRowColumn(tables.Column):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orderable = False
        self.verbose_name = _("N")
    
    def render(self, value, record, table, bound_row):    
        # Calculate the actual row number based on the page number
        page = 1
        per_page = table.per_page if hasattr(table, 'per_page') else 10
        row_number = (page - 1) * per_page + bound_row.row_counter + 1

        if row_number > len(table.rows):
            return row_number % len(table.rows) or len(table.rows)  # Use modulo to wrap around
        return row_number


class RankGroupsTable(tables.Table):
    pk = OrderRowColumn()
    t_id = NTTeamColumn()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    class Meta:
        model = RankGroups
        
        fields = (
            "pk",
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
        
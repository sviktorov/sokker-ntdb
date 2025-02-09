from .models import RankGroups
import django_tables2 as tables
from euro.tables import OrderRowColumn


class RankGroupsTable(tables.Table):
    pk = OrderRowColumn()
    t_id = tables.Column(verbose_name="Team")
    games = tables.Column(verbose_name="Games")
    wins = tables.Column(verbose_name="Won")
    draw = tables.Column(verbose_name="Draw")
    loose = tables.Column(verbose_name="Lost")
    gscored = tables.Column(verbose_name="G. S.")
    grecieved = tables.Column(verbose_name="G. R.")
    gdif = tables.Column(verbose_name="G. Diff.")
    points = tables.Column(verbose_name="Points")

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
       

from .models import RankGroups
import django_tables2 as tables
from euro.tables import OrderRowColumn


class RankGroupsTable(tables.Table):
    pk = OrderRowColumn()

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

from .models import RankGroups
import django_tables2 as tables


class RankGroupsTable(tables.Table):

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

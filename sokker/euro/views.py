from django_tables2.views import MultiTableMixin
from django.views.generic import TemplateView
from .models import Cup, CupTeams, RankGroups
from .tables import RankGroupsTable


class CupDetails(MultiTableMixin, TemplateView):
    template_name = "euro/cup-details.html"  # Create this template
    context_object_name = "objects"
    tables = []

    def dispatch(self, request, *args, **kwargs):
        cup_id = kwargs.get("cup_id")
        cup_object = Cup.objects.filter(id=cup_id).first()
        if cup_object:
            distinct_groups = (
                RankGroups.objects.filter(c_id=cup_object)
                .values("g_id")
                .distinct()
                .order_by("g_id")
            )
            for g_id in distinct_groups:
                group = (
                    RankGroups.objects.filter(c_id=cup_object, g_id=g_id["g_id"])
                    .order_by("-points")
                    .order_by("-gdif")
                )
                self.tables.append(
                    RankGroupsTable(group),
                )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cup_id = kwargs.get("cup_id")
        cup_object = Cup.objects.filter(id=cup_id).first()
        if cup_object:
            title = cup_object.c_name
            context["page_title"] = title
        context["page_siblings"] = []
        return context

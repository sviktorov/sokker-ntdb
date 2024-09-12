from django_tables2.views import MultiTableMixin
from django.views.generic import TemplateView
from .models import Cup, RankGroups, Game
from .tables import RankGroupsTable
from django.utils.translation import gettext_lazy as _


class CupIndex(TemplateView):
    template_name = "euro/index.html"  # Create this template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cup_list = Cup.objects.all().order_by("c_edition")
        context["page_title"] = _("Euro Cups")
        context["page_siblings"] = []
        context["cups"] = cup_list
        return context


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
        final = Game.objects.filter(c_id=cup_id, playoff_position="final").first()
        final_bronze = Game.objects.filter(
            c_id=cup_id, playoff_position="3/4 final"
        ).first()
        semi_finals = Game.objects.filter(
            c_id=cup_id, playoff_position__in=["s1", "s2"]
        ).order_by("playoff_position")

        quarter_finals = Game.objects.filter(
            c_id=cup_id, playoff_position__in=["q1", "q2", "q3", "q4"]
        ).order_by("playoff_position")

        eight_finals = Game.objects.filter(
            c_id=cup_id,
            playoff_position__in=[
                "e1",
                "e2",
                "e3",
                "e4",
                "e5",
                "e6",
                "e7",
                "e8",
            ],
        ).order_by("playoff_position")
        if cup_object:
            title = cup_object.c_name
            context["page_title"] = title
        context["page_siblings"] = []
        context["final"] = final
        context["final_bronze"] = final_bronze
        context["semi_finals"] = semi_finals
        context["quarter_finals"] = quarter_finals
        context["eight_finals"] = eight_finals

        context["cup"] = cup_object

        return context

from .models import Country, UserCountry
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from django.contrib import admin
from .models import Country, UserCountry, PointsRequirementsCountry, Team


@admin.register(Country)
class CountryAdmin(ImportExportModelAdmin):
    list_display = ("name", "currency_name", "currency_rate", "active")
    list_filter = ("active",)
    search_fields = ("name", "currency_name")
    ordering = ("name",)


@admin.register(UserCountry)
class UserCountryAdmin(admin.ModelAdmin):
    list_display = ("user", "country")
    list_filter = ("country",)
    search_fields = ("user__username", "country__name")
    ordering = ("user",)

    def countries_display(self, obj):
        return ", ".join([country.name for country in obj.country.all()])

    countries_display.short_description = _("Countries")


@admin.register(PointsRequirementsCountry)
class PointsRequirementsCountryAdmin(ImportExportModelAdmin):
    list_display = ("age", "gk_points", "def_points", "mid_points", "att_points")
    search_fields = ("age", "country__name")
    list_filter = ("country",)
    ordering = ("age",)


@admin.register(Team)
class TeamAdmin(ImportExportModelAdmin):
    autocomplete_fields = ('country',)
    list_display = ("id", "name", "country", "daily_update")
    list_filter = ("country",)
    ordering = ("name",)
    search_fields = ('name','id')   

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["extra_title"] = _("Teams")
        extra_context["extra_actions"] = True
        return super().changelist_view(request, extra_context=extra_context)


admin.site.site_header = "Sokker NTDB"
admin.site.site_title = "Sokker NTDB"

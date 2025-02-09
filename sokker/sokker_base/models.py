from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Country(models.Model):
    id = models.IntegerField(primary_key=True, default=1)
    code = models.IntegerField(default=1, unique=True)
    name = models.CharField(max_length=100)
    currency_name = models.CharField(max_length=100, blank=True, null=True)
    currency_rate = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _("Countries")


class UserCountry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.ForeignKey(
        Country, null=True, blank=True, on_delete=models.CASCADE
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "country")
        verbose_name_plural = _("User Countries")

    def __str__(self):
        return f"{self.user.username} - {self.country.name}"


class PointsRequirementsCountry(models.Model):
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, null=True
    )
    age = models.IntegerField(null=True, blank=True)
    gk_points = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    def_points = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    mid_points = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    att_points = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    class Meta:
        verbose_name_plural = _("Point Requirements per Country")
        verbose_name_plural = _("Point Requirements per Countries")

    def __str__(self):
        return f"{self.age} - {self.country.name}"


class Team(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=250, blank=True, null=True)
    country = models.ForeignKey(
        Country, to_field="code", on_delete=models.CASCADE, blank=True, null=True
    )  # Foreign key to 'code'
    daily_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if self and self.name:
            return self.name
        else:
            return f"sokker id team - {self.id}"

from django.db import models
from django.utils.translation import gettext_lazy as _
from sokker_base.models import PointsRequirementsCountry, Team


class Player(models.Model):
    sokker_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    surname = models.CharField(max_length=255, null=True, blank=True)
    countryid = models.IntegerField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    teamid = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="player_team",
    )
    youthteamid = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="youth_player_team",
    )
    value = models.IntegerField(null=True, blank=True)
    wage = models.IntegerField(null=True, blank=True)
    cards = models.IntegerField(null=True, blank=True)
    goals = models.IntegerField(null=True, blank=True)
    assists = models.IntegerField(null=True, blank=True)
    matches = models.IntegerField(null=True, blank=True)
    ntcards = models.IntegerField(null=True, blank=True)
    ntgoals = models.IntegerField(null=True, blank=True)
    ntassists = models.IntegerField(null=True, blank=True)
    ntmatches = models.IntegerField(null=True, blank=True)
    injurydays = models.IntegerField(null=True, blank=True, verbose_name=_("Inj."))
    national = models.IntegerField(null=True, blank=True)
    skillform = models.IntegerField(null=True, blank=True, verbose_name=_("Form"))
    skillexperience = models.IntegerField(null=True, blank=True, verbose_name=_("Exp"))
    skillteamwork = models.IntegerField(null=True, blank=True, verbose_name=_("TW"))
    skilldiscipline = models.IntegerField(null=True, blank=True, verbose_name=_("TD"))
    transferlist = models.IntegerField(null=True, blank=True)
    skillstamina = models.IntegerField(null=True, blank=True, verbose_name=_("St."))
    skillpace = models.IntegerField(null=True, blank=True, verbose_name=_("Pace"))
    skilltechnique = models.IntegerField(null=True, blank=True, verbose_name=_("Tech"))
    skillpassing = models.IntegerField(null=True, blank=True, verbose_name=_("Pass"))
    skillkeeper = models.IntegerField(null=True, blank=True, verbose_name=_("Gk"))
    skilldefending = models.IntegerField(null=True, blank=True, verbose_name=_("Def"))
    skillplaymaking = models.IntegerField(null=True, blank=True, verbose_name=_("Pm"))
    skillscoring = models.IntegerField(null=True, blank=True, verbose_name=_("Att"))
    position = models.CharField(
        max_length=3, null=True, blank=True, verbose_name=_("Pos.")
    )
    date = models.CharField(max_length=20, null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    daily_update = models.DateTimeField(null=True, blank=True)

    def calculate_gk_points(self):
        skill_keeper = self.skillkeeper or 0
        skill_pace = self.skillpace or 0
        skill_passing = self.skillpassing or 0

        skill_pace = float(skill_pace)
        skill_passing = float(skill_passing)
        skill_keeper = float(skill_keeper)
        return 2 * skill_keeper + 1.5 * skill_pace + skill_passing

    def calculate_def_points(self):
        skill_pace = self.skillpace or 0
        skill_defending = self.skilldefending or 0
        skill_playmaking = self.skillplaymaking or 0
        skill_technique = self.skilltechnique or 0
        skill_passing = self.skillpassing or 0

        skill_pace = float(skill_pace)
        skill_defending = float(skill_defending)
        skill_playmaking = float(skill_playmaking)
        skill_technique = float(skill_technique)
        skill_passing = float(skill_passing)
        return (
            1.5 * skill_pace
            + 1.5 * skill_defending
            + skill_playmaking
            + skill_technique
            + 0.5 * skill_passing
        )

    def calculate_mid_points(self):
        skill_pace = self.skillpace or 0
        skill_defending = self.skilldefending or 0
        skill_playmaking = self.skillplaymaking or 0
        skill_technique = self.skilltechnique or 0
        skill_passing = self.skillpassing or 0
        skill_stamina = self.skillstamina or 0

        skill_pace = float(skill_pace)
        skill_defending = float(skill_defending)
        skill_playmaking = float(skill_playmaking)
        skill_technique = float(skill_technique)
        skill_passing = float(skill_passing)
        skill_stamina = float(skill_stamina)
        return (
            1.5 * skill_passing
            + 1.5 * skill_playmaking
            + skill_pace
            + skill_technique
            + 0.5 * skill_defending
            + 0.25 * skill_stamina
        )

    def calculate_att_points(self):
        skill_technique = self.skilltechnique or 0
        skill_pace = self.skillpace or 0
        skill_scoring = self.skillscoring or 0

        skill_pace = float(skill_pace)
        skill_technique = float(skill_technique)
        skill_scoring = float(skill_scoring)
        return skill_technique + skill_pace + skill_scoring

    def db_requirements(self):
        req = PointsRequirementsCountry.objects.filter(
            age=self.age, country__code=self.countryid
        ).first()
        print(req)
        if not req:
            req = (
                PointsRequirementsCountry.objects.filter(
                    country__code=self.countryid,
                )
                .order_by("-age")
                .first()
            )

        return req

    def att_points_dif(self, req):
        return self.calculate_att_points() - float(req.att_points)

    def mid_points_dif(self, req):
        return self.calculate_mid_points() - float(req.mid_points)

    def def_points_dif(self, req):
        return self.calculate_def_points() - float(req.def_points)

    def gk_points_dif(self, req):
        return self.calculate_gk_points() - float(req.gk_points)

    def position_score(self):
        req = self.db_requirements()
        if req:
            if self.position == "ATT":
                return self.att_points_dif(req)
            if self.position == "MID":
                return self.mid_points_dif(req)
            if self.position == "DEF":
                return self.mid_points_dif(req)
            if self.position == "GK":
                return self.gk_points_dif(req)
        return 0

    def best_position(self):
        req = self.db_requirements()
        if req:
            att_p = self.att_points_dif(req)
            def_p = self.def_points_dif(req)
            mid_p = self.mid_points_dif(req)
            gk_p = self.gk_points_dif(req)
            m = max(att_p, def_p, mid_p, gk_p)
            if m == att_p:
                return "ATT"
            if m == mid_p:
                return "MID"
            if m == def_p:
                return "DEF"
            if m == gk_p:
                return "GK"
        return "NA"

    def __str__(self):
        if self.name and self.surname:
            return self.name + " " + self.surname
        else:
            return str(self.sokker_id)

    class Meta:
        verbose_name = "Player"


class ArchivePlayer(models.Model):
    sokker_id = models.IntegerField(null=True, blank=True, default=None)
    name = models.CharField(max_length=255, null=True, blank=True)
    surname = models.CharField(max_length=255, null=True, blank=True)
    countryid = models.IntegerField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    teamid = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="archive_player_team",
    )
    youthteamid = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="archive_youth_player_team",
    )
    value = models.IntegerField(null=True, blank=True)
    wage = models.IntegerField(null=True, blank=True)
    cards = models.IntegerField(null=True, blank=True)
    goals = models.IntegerField(null=True, blank=True)
    assists = models.IntegerField(null=True, blank=True)
    matches = models.IntegerField(null=True, blank=True)
    ntcards = models.IntegerField(null=True, blank=True)
    ntgoals = models.IntegerField(null=True, blank=True)
    ntassists = models.IntegerField(null=True, blank=True)
    ntmatches = models.IntegerField(null=True, blank=True)
    injurydays = models.IntegerField(null=True, blank=True, verbose_name=_("Inj."))
    national = models.IntegerField(null=True, blank=True)
    skillform = models.IntegerField(null=True, blank=True, verbose_name=_("Form"))
    skillexperience = models.IntegerField(null=True, blank=True, verbose_name=_("Exp"))
    skillteamwork = models.IntegerField(null=True, blank=True, verbose_name=_("TW"))
    skilldiscipline = models.IntegerField(null=True, blank=True, verbose_name=_("TD"))
    transferlist = models.IntegerField(null=True, blank=True)
    skillstamina = models.IntegerField(null=True, blank=True, verbose_name=_("St."))
    skillpace = models.IntegerField(null=True, blank=True, verbose_name=_("Pace"))
    skilltechnique = models.IntegerField(null=True, blank=True, verbose_name=_("Tech"))
    skillpassing = models.IntegerField(null=True, blank=True, verbose_name=_("Pass"))
    skillkeeper = models.IntegerField(null=True, blank=True, verbose_name=_("Gk"))
    skilldefending = models.IntegerField(null=True, blank=True, verbose_name=_("Def"))
    skillplaymaking = models.IntegerField(null=True, blank=True, verbose_name=_("Pm"))
    skillscoring = models.IntegerField(null=True, blank=True, verbose_name=_("Att"))
    position = models.CharField(
        max_length=3, null=True, blank=True, verbose_name=_("Pos.")
    )
    date = models.CharField(max_length=20, null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    daily_update = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Archive Player"

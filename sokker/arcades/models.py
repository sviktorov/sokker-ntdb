from django.db import models
from django.utils.translation import gettext_lazy as _
from sokker_base.models import Team
from django.core.exceptions import ObjectDoesNotExist


class Cup(models.Model):
    id = models.AutoField(primary_key=True)  # Assuming c_id is an auto-incrementing ID
    # New header_image field
    header_image = models.ImageField(upload_to="header_images/", null=True, blank=True)
    forum_link = models.CharField(max_length=255, null=True, blank=True)
    c_name = models.CharField(max_length=255)
    c_edition = models.IntegerField(null=True, blank=True)
    c_flow = models.IntegerField(null=True, blank=True, default=1)
    c_teams = models.IntegerField(null=True, blank=True)
    c_groups = models.IntegerField(null=True, blank=True)
    c_g_winners = models.IntegerField(
        null=True, blank=True
    )  # Assuming this is the number of group winners
    c_games_groups = models.IntegerField(null=True, blank=True)
    c_games = models.IntegerField(null=True, blank=True)
    c_status = models.CharField(max_length=50)
    c_draw_status = models.CharField(max_length=50)
    c_draw_date = models.DateTimeField(null=True, blank=True, default=None)
    c_notes = models.TextField(null=True, blank=True)  # Assuming this can be nullable
    c_active = models.BooleanField(default=False)  # Assuming this is a boolean field

    def __str__(self):
        return self.c_name


class CupTeams(models.Model):
    id = models.AutoField(primary_key=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    t_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    g_id = models.IntegerField()

    def __str__(self):
        return f"Game {self.id}: {self.c_id} vs {self.t_id}"

    class Meta:
        verbose_name_plural = _("Cup Teams")


class CupDraw(models.Model):
    id = models.AutoField(primary_key=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    t_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    g_id = models.IntegerField()

    def __str__(self):
        return f"Game {self.id}: {self.c_id} vs {self.t_id}"


def get_default_team():
    try:
        return Team.objects.get(pk=100000000)
    except ObjectDoesNotExist:
        # Handle the case where the team doesn't exist yet.
        # You can raise an error or return a sensible default.
        return None  # Or raise an error, or create a default team


class Game(models.Model):
    id = models.AutoField(primary_key=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    t_id_h = models.ForeignKey(
        Team,
        related_name="home_team_base",
        on_delete=models.CASCADE,
        default=get_default_team(),
    )
    t_id_v = models.ForeignKey(
        Team,
        related_name="away_team_base",
        on_delete=models.CASCADE,
        default=get_default_team(),
    )
    g_status = models.CharField(max_length=50)
    group_id = models.CharField()
    goals_home = models.IntegerField(null=True, blank=True)
    goals_away = models.IntegerField(null=True, blank=True)
    cup_round = models.CharField(max_length=50)
    matchID = models.CharField(max_length=255)
    playoff_position = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return (
            f"Game {self.id}: {self.t_id_h} vs {self.t_id_v} - Status: {self.g_status}"
        )

    def away_points(self):
        if self.goals_home is None or self.goals_away is None:
            return 0
        if self.goals_away > self.goals_home:
            return 3
        if self.goals_home == self.goals_away:
            return 1
        return 0

    def home_points(self):
        if self.goals_home is None or self.goals_away is None:
            return 0
        if self.goals_home > self.goals_away:
            return 3
        if self.goals_home == self.goals_away:
            return 1
        return 0

    def home_status(self):
        if self.goals_home is None or self.goals_away is None:
            return _("N/A")
        if self.goals_home > self.goals_away:
            return _("win")
        if self.goals_home == self.goals_away:
            return _("draw")
        return _("loss")

    def away_status(self):
        if self.goals_home is None or self.goals_away is None:
            return _("N/A")
        if self.goals_away > self.goals_home:
            return _("win")
        if self.goals_away == self.goals_home:
            return _("draw")
        return _("loss")


class RankGroups(models.Model):
    id = models.AutoField(primary_key=True)
    t_id = models.ForeignKey(
        Team, related_name="team_rank_arcades", on_delete=models.CASCADE
    )
    games = models.IntegerField(null=True, blank=True)
    g_id = models.IntegerField(null=True, blank=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    wins = models.IntegerField(null=True, blank=True)
    loose = models.IntegerField(null=True, blank=True)
    gdif = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    gscored = models.IntegerField(null=True, blank=True)
    grecieved = models.IntegerField(null=True, blank=True)
    draw = models.IntegerField(null=True, blank=True)
    qualified = models.CharField(max_length=50)

    def __str__(self):
        return f"Team {self.id}: {self.t_id}  - Cup: {self.c_id} points {self.points}"

    class Meta:
        verbose_name_plural = _("Rank Groups")


class Medals(models.Model):
    id = models.AutoField(primary_key=True)
    t_id = models.ForeignKey(
        Team, related_name="team_medal_arcades", on_delete=models.CASCADE
    )
    position_1 = models.IntegerField(null=True, blank=True)
    position_2 = models.IntegerField(null=True, blank=True)
    position_3 = models.IntegerField(null=True, blank=True)
    position_4 = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Medals")


class Winners(models.Model):
    id = models.AutoField(primary_key=True)
    position = models.IntegerField(null=True, blank=True)
    cup_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    team_id = models.ForeignKey(
        Team, related_name="team_winners", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = _("Winners")


class RankAllTime(models.Model):
    id = models.AutoField(primary_key=True)
    t_id = models.ForeignKey(
        Team, related_name="team_rank_all_time", on_delete=models.CASCADE
    )
    games = models.IntegerField(null=True, blank=True)
    wins = models.IntegerField(null=True, blank=True)
    loose = models.IntegerField(null=True, blank=True)
    gdif = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    gscored = models.IntegerField(null=True, blank=True)
    grecieved = models.IntegerField(null=True, blank=True)
    draw = models.IntegerField(null=True, blank=True)
    c_flow = models.IntegerField(null=True, blank=True, default=1)

    def __str__(self):
        return f"Team {self.id}: {self.t_id}  - Cup: {self.c_id} points {self.points}"

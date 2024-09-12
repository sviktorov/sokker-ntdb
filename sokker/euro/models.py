from django.db import models
from django.utils.translation import gettext_lazy as _


class Cup(models.Model):
    id = models.AutoField(primary_key=True)  # Assuming c_id is an auto-incrementing ID
    c_name = models.CharField(max_length=255)
    c_edition = models.IntegerField(null=True, blank=True)
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


class NTTeam(models.Model):
    id = models.AutoField(primary_key=True)
    t_nation = models.CharField(max_length=255)
    t_name = models.CharField(max_length=255)
    t_manager = models.CharField(max_length=255, null=True, blank=True)
    t_s_ranking = models.IntegerField(null=True, blank=True)
    t_sokker_id = models.CharField(max_length=255)
    t_email = models.EmailField(null=True, blank=True)
    t_arena = models.CharField(max_length=255)

    def __str__(self):
        return self.t_name


class CupTeams(models.Model):
    id = models.AutoField(primary_key=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    t_id = models.ForeignKey(NTTeam, on_delete=models.CASCADE)
    g_id = models.IntegerField()

    def __str__(self):
        return f"Game {self.id}: {self.c_id} vs {self.t_id}"


class CupDraw(models.Model):
    id = models.AutoField(primary_key=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    t_id = models.ForeignKey(NTTeam, on_delete=models.CASCADE)
    g_id = models.IntegerField()

    def __str__(self):
        return f"Game {self.id}: {self.c_id} vs {self.t_id}"


class Game(models.Model):
    id = models.AutoField(primary_key=True)
    c_id = models.ForeignKey(Cup, on_delete=models.CASCADE)
    t_id_h = models.ForeignKey(
        NTTeam, related_name="home_team", on_delete=models.CASCADE
    )
    t_id_v = models.ForeignKey(
        NTTeam, related_name="away_team", on_delete=models.CASCADE
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

    def home_status(self):
        if self.goals_home > self.goals_away:
            return _("win")
        if self.goals_home == self.goals_away:
            return _("draw")
        return _("loss")

    def away_status(self):
        if self.goals_away > self.goals_home:
            return _("win")
        if self.goals_away == self.goals_home:
            return _("draw")
        return _("loss")


class RankGroups(models.Model):
    id = models.AutoField(primary_key=True)
    t_id = models.ForeignKey(NTTeam, related_name="team_rank", on_delete=models.CASCADE)
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

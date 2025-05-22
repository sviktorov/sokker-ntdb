from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse




class Country(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name

class Team(models.Model):   
    id = models.AutoField(primary_key=True)
    team_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    idcountry = models.ForeignKey(Country, on_delete=models.CASCADE)
    def __str__(self):
        return self.name


class Player(models.Model):
    MAX_VALUE_SKILL = 25
    POSITION_CHOICES = [
        ('Goalkeeper', 'Goalkeeper'),
        ('Defender', 'Defender'),
        ('Winger', 'Winger'),
        ('Midfielder', 'Midfielder'),
        ('Forward', 'Forward'),
    ]

    player_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    idcountry = models.ForeignKey(Country, on_delete=models.CASCADE)
    age = models.IntegerField()
    position = models.CharField(max_length=10, choices=POSITION_CHOICES)
    height = models.IntegerField(help_text="Height in cm")
    potential = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Potential percentage"
    )
    value = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Value in euros"
    )
    wage = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Wage in euros"
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='players'
    )
    in_club_since = models.DateField()
    
    # Player attributes
    condition = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Condition percentage"
    )
    form = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Form percentage"
    )
    experience = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Experience rating"
    )
    
    # Skills
    overall = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_VALUE_SKILL)],
        help_text="Overall rating"
    )
    stamina = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_VALUE_SKILL)],
        help_text="Stamina rating"
    )
    goalkeeper = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_VALUE_SKILL)],
        help_text="Goalkeeper skill"
    )
    tackling = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_VALUE_SKILL)],
        help_text="Tackling skill"
    )
    heading = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_VALUE_SKILL)],
        help_text="Heading skill"
    )
    winger = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_VALUE_SKILL)],
        help_text="Winger skill"
    )
    playmaking = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_VALUE_SKILL)],
        help_text="Playmaking skill"
    )
    passing = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_VALUE_SKILL)],
        help_text="Passing skill"
    )
    attacking = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(MAX_VALUE_SKILL)],
        help_text="Attacking skill"
    )

    class Meta:
        ordering = ['-overall']
        indexes = [
            models.Index(fields=['player_id']),
            models.Index(fields=['name']),
            models.Index(fields=['team']),
        ]

    def __str__(self):
        return f"{self.name} ({self.team})"

    
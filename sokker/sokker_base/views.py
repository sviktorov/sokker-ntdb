from django.views.generic import TemplateView
from sokker_base.models import Country, TROPHY_TYPES, TeamTrophies, LeagueTable
from django.http import Http404, HttpResponse

from PIL import Image, ImageDraw, ImageFont
import io
import os
from django.conf import settings
from django.db.models import F, IntegerField, ExpressionWrapper, Sum
from arcades.utils import COLORS, draw_cell


class StandingsView(TemplateView):
    template_name = "sokker_base/standings.html"

    def get_context_data(self, **kwargs):
        country = Country.objects.filter(name=self.kwargs["country_name"].capitalize()).first()
        context = super().get_context_data(**kwargs)
        standings = LeagueTable.objects.annotate(
            goal_difference=ExpressionWrapper(
                F('scored') - F('conceded'),
                output_field=IntegerField()
            )
        ).filter(country=country, season=self.kwargs["season_id"], league=self.kwargs["league_id"]).order_by('-points', '-goal_difference', '-scored')
        
        seasons = LeagueTable.objects.filter(league=self.kwargs["league_id"]).values_list('season', flat=True).distinct().order_by('-season')

        context["country"] = country
        context["season_id"] = str(self.kwargs["season_id"])
        context["league_id"] = self.kwargs["league_id"]
        context["standings"] = standings
        context["seasons"] = seasons
        return context

class StandingsAllView(TemplateView):
    template_name = "sokker_base/standings_all.html"

    def generate_image(self, standings, country, league_id):
        # Set up image dimensions
        padding = 20
        row_height = 40  # Increased for better medal visibility
        header_height = 120  # Increased for better header visibility
        col_width = 60 
        col_width_team = 200
        width = col_width * 10 + padding * 2 + col_width_team
        height = header_height + (len(standings) * row_height) + padding * 2 + 10
        
        # Create image with white background
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)          

        try:
            # Try to load a nice font, fall back to default if not available
            font = ImageFont.truetype("Arial", 16)
            title_font = ImageFont.truetype("Arial", 20)
            header_font = ImageFont.truetype("Arial", 18)   
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
    
        # Draw title
        title = f"Standing all time {country.name} Top division"
        draw.text((padding + 15, padding), title, fill='black', font=title_font)

        # Draw headers with colored circles for medals
        headers = ['#', 'Team', 'Played', 'Won', 'Drawn', 'Lost', 'Scored', 'Conce.', 'G. Diff', 'Points']
        x = 0
        for i, header in enumerate(headers):
     
            y = header_height - row_height
            if i == 1:
                width = col_width_team
            else:
                width = col_width
            if i == 2:
                x = x + col_width_team 
            else:
                x = x + col_width
            if i == 0:
                x= padding
            draw_cell(draw, font, x, y, width, row_height, header, bg_color=COLORS['header'], text_color='white')
        for i, standing in enumerate(standings):
            x = padding
            y = header_height + (i * row_height)
            if i % 2 == 0:
                bg_color = COLORS['row_even']
                color = 'black'
            else:
                bg_color = COLORS['row_odd']
                color = 'white'
            draw_cell(draw, font, x, y, col_width, row_height, str(i+1), bg_color=bg_color, text_color=color)
            x = x + col_width
            draw_cell(draw, font, x, y, col_width_team, row_height, standing['team__name'][:20], bg_color=bg_color, text_color=color)
            x = x + col_width_team
            draw_cell(draw, font, x, y, col_width, row_height, str(standing['total_played']), bg_color=bg_color, text_color=color)
            x = x + col_width
            draw_cell(draw, font, x, y, col_width, row_height, str(standing['total_won']), bg_color=bg_color, text_color=color)
            x = x + col_width
            draw_cell(draw, font, x, y, col_width, row_height, str(standing['total_drawn']), bg_color=bg_color, text_color=color)
            x = x + col_width
            draw_cell(draw, font, x, y, col_width, row_height, str(standing['total_lost']), bg_color=bg_color, text_color=color)
            x = x + col_width
            draw_cell(draw, font, x, y, col_width, row_height, str(standing['total_scored']), bg_color=bg_color, text_color=color)
            x = x + col_width
            draw_cell(draw, font, x, y, col_width, row_height, str(standing['total_conceded']), bg_color=bg_color, text_color=color)
            x = x + col_width
            draw_cell(draw, font, x, y, col_width, row_height, str(standing['total_goal_difference']), bg_color=bg_color, text_color=color)
            x = x + col_width
            draw_cell(draw, font, x, y, col_width, row_height, str(standing['total_points']), bg_color=bg_color, text_color=color)
            


        # Save image to bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Return image response
        response = HttpResponse(buffer, content_type='image/png')
        response['Content-Disposition'] = 'inline; filename="trophies.png"'
        return response    
            
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        
        # Check if format=image is requested
        if request.GET.get('format') == 'image':
            return self.generate_image(context['standings'], context['country'], context['league_id'])
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        country = Country.objects.filter(name=self.kwargs["country_name"].capitalize()).first()
        context = super().get_context_data(**kwargs)
        standings = LeagueTable.objects.values('team', 'team__name', 'team__id').annotate(
            total_points=Sum('points'),
            total_played=Sum('played'),
            total_won=Sum('won'),
            total_drawn=Sum('drawn'),
            total_lost=Sum('lost'),
            total_scored=Sum('scored'),
            total_conceded=Sum('conceded'),
            total_goal_difference=Sum(
                ExpressionWrapper(F('scored') - F('conceded'), output_field=IntegerField())
            ),
        ).filter(country=country, league=self.kwargs["league_id"]).order_by('-total_points', '-total_goal_difference', '-total_scored')
        

        context["country"] = country
        context["league_id"] = self.kwargs["league_id"]
        context["standings"] = standings

        return context
    
class TeamTrophiesView(TemplateView):
    template_name = "sokker_base/team-trophies.html"

    def draw_medal(self, draw, x, y, color, size=20):
        """Draw a circular medal with the given color"""
        draw.ellipse([(x, y), (x + size, y + size)], fill=color, outline='#666666')
        
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        
        # Check if format=image is requested
        if request.GET.get('format') == 'image':
            return self.generate_image(context['team_trophies'], context['country_name'], context['trophy_type'])
        
        return super().get(request, *args, **kwargs)

    def generate_image(self, team_trophies, country_name, trophy_type):
        # Set up image dimensions
        padding = 20
        row_height = 40  # Increased for better medal visibility
        header_height = 120  # Increased for better header visibility
        col_width = 150
        width = col_width * 4 + padding * 2 
        height = header_height + (len(team_trophies) * row_height) + padding * 2 + 10

        # Create image with white background
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)

        try:
            # Try to load a nice font, fall back to default if not available
            font = ImageFont.truetype("Arial", 16)
            title_font = ImageFont.truetype("Arial", 20)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()

        # Draw title
        title = f"Trophies {country_name} {trophy_type}"
        draw.text((padding + 15, padding), title, fill='black', font=title_font)

        # Medal colors
        gold = '#FFD700'
        silver = '#C0C0C0'
        bronze = '#CD7F32'

        # Draw headers with colored circles for medals
        headers = ['Team']
        for i, header in enumerate(headers):
            x = padding + (col_width * i)
            y = header_height - row_height
            draw.text((x + 15, y + 10), header, fill='black', font=font)

        # Draw medals in headers
        medal_y = header_height - row_height + 5
        # Gold medal
        self.draw_medal(draw, padding + col_width + 65, medal_y + 5, gold)
        # Silver medal
        self.draw_medal(draw, padding + col_width * 2 + 65, medal_y + 5, silver)
        # Bronze medal
        self.draw_medal(draw, padding + col_width * 3 + 65, medal_y + 5, bronze)

        # Draw alternating row backgrounds
        draw.line([(padding, header_height - row_height), (width - padding, header_height - row_height)], fill='#dee2e6', width=1)
        for i, trophy in enumerate(team_trophies):
            y = header_height + (i * row_height)
            if i % 2 == 0:
                draw.rectangle([(padding + 15, y + 10), (width - padding, y + row_height)], fill='#f8f9fa')

        # Draw data
        for i, trophy in enumerate(team_trophies):
            y = header_height + (i * row_height) + 10  # Added 10px vertical padding
            # Team name
            draw.text((padding + 15, y), trophy['team_name'][:20], fill='black', font=font)
            # Medal counts
            draw.text((padding + col_width + 65, y), str(trophy['first_place']), fill='black', font=font)
            draw.text((padding + col_width * 2 + 65, y), str(trophy['second_place']), fill='black', font=font)
            draw.text((padding + col_width * 3 + 65, y), str(trophy['third_place']), fill='black', font=font)

        # Draw grid lines
        for i in range(len(team_trophies) + 1):
            y = header_height + (i * row_height)
            draw.line([(padding, y), (width - padding, y)], fill='#dee2e6', width=1)

        for i in range(5):  # vertical lines
            x = padding + (col_width * i)
            draw.line([(x, header_height - row_height), (x, height - padding)], fill='#dee2e6', width=1)

        # Save image to bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Return image response
        response = HttpResponse(buffer, content_type='image/png')
        response['Content-Disposition'] = 'inline; filename="trophies.png"'
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        country = Country.objects.filter(name=self.kwargs["country_name"].capitalize()).first()
        if not country and self.kwargs["trophy_type"] != 'champions_cup':
            raise Http404("Country not found")
        
        # Base filter without country for champions cup
        base_filter = {
            'trophy_type': self.kwargs["trophy_type"],
            'level': 1,
            'position__in': [1, 2, 3]
        }
        
        # Add country filter only if not champions cup
        if self.kwargs["trophy_type"] != 'champions_cup':
            base_filter['country'] = country
        
        # Get all trophies and group by team
        team_trophies = TeamTrophies.objects.filter(
            **base_filter
        ).values('team', 'team__name').distinct()  # Get distinct teams
        
        # Create a list to store aggregated results
        aggregated_trophies = []
        
        for team in team_trophies:
            # Base filter for individual position queries
            position_filter = {
                'trophy_type': self.kwargs["trophy_type"],
                'level': 1,
                'team_id': team['team']
            }
            
            # Add country filter only if not champions cup
            if self.kwargs["trophy_type"] != 'champions_cup':
                position_filter['country'] = country
            
            team_stats = {
                'team_id': team['team'],
                'team_name': team['team__name'],
                'first_place': TeamTrophies.objects.filter(
                    **position_filter,
                    position=1
                ).values('occurrences').first(),
                'second_place': TeamTrophies.objects.filter(
                    **position_filter,
                    position=2
                ).values('occurrences').first(),
                'third_place': TeamTrophies.objects.filter(
                    **position_filter,
                    position=3
                ).values('occurrences').first()
            }
            
            # Set occurrences to 0 if no trophies found
            team_stats['first_place'] = team_stats['first_place']['occurrences'] if team_stats['first_place'] else 0
            team_stats['second_place'] = team_stats['second_place']['occurrences'] if team_stats['second_place'] else 0
            team_stats['third_place'] = team_stats['third_place']['occurrences'] if team_stats['third_place'] else 0
            
            aggregated_trophies.append(team_stats)
        
        # Sort by first place occurrences first, then second place, then third place
        team_trophies = sorted(
            aggregated_trophies,
            key=lambda x: (x['first_place'], x['second_place'], x['third_place']),
            reverse=True
        )

        context["country_name"] = self.kwargs["country_name"]
        context["trophy_type"] = self.kwargs["trophy_type"]
        context["team_trophies"] = team_trophies
        return context
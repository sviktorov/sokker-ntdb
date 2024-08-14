from django.core.management.base import BaseCommand
from sokker_base.models import PointsRequirementsCountry, Country


class Command(BaseCommand):
    help = "Update players public skills"

    def handle(self, *args, **options):

        # Open the file in read mode
        country_id = 54
        country = Country.objects.filter(code=country_id).first()
        with open("req.txt", "r") as file:
            # Iterate over each line in the file
            for line in file:
                # Process each line here
                line_str = line.strip()
                print(
                    line.strip()
                )  # Print the line after stripping any leading/trailing whitespace
                split_data = line_str.split("|")
                age = split_data[0]
                pos = split_data[1]
                points = split_data[2]
                r = PointsRequirementsCountry.objects.filter(
                    country__code=country_id, age=age
                ).first()
                if not r:
                    r = PointsRequirementsCountry()
                r.country = country
                r.age = age
                if pos == "GK" or pos == "GK ":
                    r.gk_points = points
                if pos == "DEF":
                    r.def_points = points
                if pos == "MID":
                    r.mid_points = points
                if pos == "ATT":
                    r.att_points = points
                r.save()

            

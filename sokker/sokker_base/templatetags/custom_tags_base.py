from django import template
from ..models import Country  # Adjust the import according to your model

register = template.Library()


@register.simple_tag
def get_active_countries():
    # Fetch the list of semi-final matches based on the passed cup_id
    return Country.objects.filter(active=True).order_by("name")

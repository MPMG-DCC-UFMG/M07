from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='to_date')
def to_date(value):
    return datetime.fromtimestamp(value/1000) 

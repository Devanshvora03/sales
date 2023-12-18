from django import template
from django.contrib.auth.models import Group
import math


register = template.Library()

@register.filter(name='add_class')
def add_class(field,css):
    try:
        return field.as_widget(attrs={"class":css})
    except:
        pass 
   

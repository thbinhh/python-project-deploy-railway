from django import template
from ecommerce.models import *
import random
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def getChilds(parentId):
    return Category.objects.filter(cate_parent_id=parentId)

@register.filter
def shuffle(value):
    temp = list(value)
    random.shuffle(temp)
    return temp

@register.filter
def format_price(value):
    return intcomma(int(value))


@register.filter
def round_rating(value):
    return round(value,2)
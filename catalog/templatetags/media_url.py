from django import template

register = template.Library()

@register.filter
def media_url(image):
    if image:
        return f'/media/{image}'
    return '#'
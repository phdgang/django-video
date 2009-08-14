from random import randint
from django import template
from django.template.loader import render_to_string

register = template.Library()

def random_thumbnail(video):
    count = video.thumbnails.count()

    return video.thumbnails.all()[randint(0, count - 1)]

@register.inclusion_tag('video/preview.html', takes_context=False)
def preview(video, width="100%"):
    thumbnail = None
    if video.has_thumbnails():
        thumbnail = random_thumbnail(video)

    return {'thumbnail' : thumbnail,
            'video' : video,
            'width' : width}

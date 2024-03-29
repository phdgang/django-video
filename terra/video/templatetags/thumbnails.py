"""
Copyright (C) 2008 Y-NODE Software
Author: Aleksey Artamonov <aleksey.artamonov@y-node.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from django import template
from django.template.loader import render_to_string
from video import defaults
from video.config import get_thumbnail_setting
from video.templatetags.type_transforms import transform

register = template.Library()

thumbnails_parameters = ['width', 'player_id']

def add_defaults(dict):
    result = dict

    for parameter in thumbnails_parameters:
        if not parameter in dict:
            try:
                result[parameter] = str(get_thumbnail_setting(parameter))
            except:
                pass

    return result

@register.tag(name="thumbnails")
def do_thumbnails(parser, token):
    try:
        tag_info = token.split_contents()
        tag_name = tag_info[0]
        video = tag_info[1]
        info_dict = {}

        for element in tag_info[2:]:
            parameter, value = element.split('=')
            info_dict[parameter] = value

        add_defaults(info_dict)
        info_dict['video'] = video
    except IndexError:
        raise template.TemplateSyntaxError, "%r tag requires at least one argument" % tag_name
    except ValueError:
        raise template.TemplateSyntaxError, "Extra arguments of %r tag must be in the form \"parameter=value\"" % tag_name

    return ThumbnailsNode(info_dict)

class ThumbnailsNode(template.Node):
    def __init__(self, options):
        self.options = options

    def render(self, context):
        for parameter, value in self.options.items():
            try:
                tmp = template.Variable(value)
                actual_value = tmp.resolve(context)
            except template.VariableDoesNotExist:
                t = type(get_thumbnail_setting(parameter))
                actual_value = transform(value, t)

            self.options[parameter] = actual_value

        return render_to_string("video/thumbnails.html", self.options)

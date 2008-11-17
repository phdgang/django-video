"""
Copyright (C) 2008 Y-NODE Software
Author: Aleksey Artamonov <aleksey.artamonov@y-node.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from django.conf import settings
from video import defaults
import re

def get_setting(setting):
    setting = setting.upper()

    if hasattr(settings, "TERRA_%s" % setting):
        return getattr(settings, "TERRA_%s" % setting)
    else:
        return getattr(defaults, setting)

def get_player_setting(setting):
    return get_setting("PLAYER_%s" % setting)

def get_encoding_setting(setting):
    return get_setting("ENCODING_%s" % setting)

def get_thumbnail_setting(setting):
    return get_setting("THUMBNAIL_%s" % setting)


VIDEO_DIR = None
def get_video_dir():
    global VIDEO_DIR

    if not VIDEO_DIR:
        regexp = re.compile("^()$|^(.*[^/])/?")
        groups = re.match(regexp, get_setting('video_dir')).groups()
        VIDEO_DIR = groups[0] or groups[1]

    return VIDEO_DIR

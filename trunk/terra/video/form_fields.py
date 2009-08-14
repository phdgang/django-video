"""
Copyright (C) 2008 Y-NODE Software
Author: Aleksey Artamonov <aleksey.artamonov@y-node.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

import magic
import re
from django.forms.fields import FileField, ValidationError
from django.utils.translation import ugettext_lazy as _

HEADER = 4096

mime = magic.open(magic.MAGIC_MIME)
mime.load()

video_re = re.compile("^video\/.+")
def is_video(path):
    type = mime.file(path)
    return video_re.match(type) != None

def is_video_buffer(buffer):
    type = mime.buffer(buffer)
    return video_re.match(type) != None

class VideoField(FileField):
    default_error_messages = {
        'invalid_video': _(u"Upload a valid video. The file you uploaded was either not a video or a corrupted video."),
    }

    def clean(self, data, initial=None):
        f = super(VideoField, self).clean(data, initial)
        
        if f is None:
            return None
        elif not data and initial:
            return initial

        file = None
        buffer = None

        try:
            if hasattr(data, 'temporary_file_path'):
                file = data.temporary_file_path()
            else:
                if hasattr(data, 'read'):
                    buffer = data.read(HEADER)
                else:
                    buffer = data['content']

            if file:
                if not is_video(file):
                    raise ValidationError("1")
            elif buffer:
                if not is_video_buffer(buffer):
                    raise ValidationError("2")
            else:
                raise Exception("Can't get uploaded file's contents in usual way. Weird :(")
        except ValidationError:
            raise ValidationError(self.error_messages['invalid_video'])

        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        return f

"""
Copyright (C) 2008 Y-NODE Software
Author: Aleksey Artamonov <aleksey.artamonov@y-node.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from django.contrib import admin
from video.models import Video, Thumbnail
from video.forms import UploadForm

class VideoAdmin(admin.ModelAdmin):
    date_hierarchy = 'upload_date'
    form = UploadForm
    fields = ('video',)

    def save_model(self, request, object, form, change):
        if not change:
            super(VideoAdmin, self).save_model(request, object, form, change)
        else:
            pass

class ThumbnailAdmin(admin.ModelAdmin):
    pass



admin.site.register(Video, VideoAdmin)
admin.site.register(Thumbnail, ThumbnailAdmin)

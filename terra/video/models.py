"""
Copyright (C) 2008 Y-NODE Software
Author: Aleksey Artamonov <aleksey.artamonov@y-node.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

import os
import time
import django.conf
import re

from django.db import models
from datetime import timedelta
from video.timedeltafield import TimedeltaField
from video.config import get_setting, get_video_dir, get_thumbnail_setting
from video.fields import DynamicUploadFileField
from video.video_dispatcher import install_dispatcher
from video.signals import pre_upload, post_upload
from PIL import Image
from distutils.dir_util import remove_tree


TEMP_VIDEO_DIR = get_setting('temp_video_dir')

class ThumbnailManager(models.Manager):
    def ordered_by_time(self):
        return self.get_query_set().order_by('position')

class Thumbnail(models.Model):
    image = models.ImageField(null=False, upload_to=TEMP_VIDEO_DIR)
    video = models.ForeignKey('Video', related_name='thumbnails')
    position = TimedeltaField(null=False)
    _width = models.IntegerField(default=-1)
    _height = models.IntegerField(default=-1)

    objects = ThumbnailManager()

    def get_upload_to(self, attname):
        tmp = self.video.get_upload_to()
        thumb_dir = get_thumbnail_setting('dir')
        return "%s/%s" % (tmp, thumb_dir)

    def url(self):
        return self.image.url

    def time(self):
        return self.position.seconds

    def _get_size(self):
        if self._width == -1:
            img = Image.open(self.image.path)
            self._width = img.size[0]
            self._height = img.size[1]
            self.save()

        return (self._width, self._height)

    def _get_width(self):
        return self._get_size()[0]

    def _get_height(self):
        return self._get_size()[1]

    width = property(_get_width)
    height = property(_get_height)
            

class VideoManager(models.Manager):
    def encoded(self):
        return self.get_query_set().filter(_finished_encoding=True)

class Video(models.Model):
    video = DynamicUploadFileField(null=False, upload_to=TEMP_VIDEO_DIR,
                                   signal=lambda x: post_upload.send(sender=Video, instance=x))
    encoded_video = models.FileField(default=None, upload_to=TEMP_VIDEO_DIR)
    _finished_encoding = models.BooleanField(default=False, null=None)
    upload_dir = models.FilePathField(null=True, default=None)
    upload_date = models.DateTimeField(auto_now_add=True)

    objects = VideoManager()
     

    def __unicode__(self):
        return self.video.url

    def url(self):
        if self.finished_encoding():
            return self.encoded_video.url
        else:
            return None

    def get_upload_to(self, attname):
        if not self.upload_dir:
            video_dir = get_video_dir()
            self.upload_dir = time.strftime(video_dir) + '/%d/' % self.id
            self.save()

        return self.upload_dir

    def delete(self):
        self.clean_auxiliarry_files()
        dir = os.path.abspath(os.path.dirname(self.video.path))

        super(Video, self).delete()
        remove_tree(dir)

    def save(self, **kwargs):
        created = not self.id

        super(Video, self).save(**kwargs)

        if created:
            pre_upload.send(sender=Video, instance=self)

    def clean_auxiliarry_files(self):
        if self.finished_encoding():
            video_dir = os.path.abspath(os.path.dirname(self.encoded_video.path))
            enc_logfile = get_setting('encoding_log_file')
            if enc_logfile:
                try:
                    os.remove(os.path.join(video_dir, enc_logfile))
                except:
                    pass
        if self.has_thumbnails():
            thumbnail_dir = os.path.join(video_dir, get_setting('thumbnail_dir'))
            thumbnail_logfile = get_setting('thumbnail_log_file')
            if thumbnail_logfile:
                try:
                    os.remove(os.path.join(thumbnail_dir, thumbnail_logfile))
                except:
                    pass

    def finished_encoding(self):
        return self._finished_encoding

    def has_thumbnails(self):
        return self.thumbnails.count() > 0

    def reencode(self):
        post_upload.send(sender=Video, instance=self)

    def _remove_media_root_prefix(self, path):
        if hasattr(django.conf.settings, 'MEDIA_ROOT'):
            media_root = django.conf.settings.MEDIA_ROOT
            regexp = re.compile('%s(.*)' % re.escape(media_root))
            try:
                new_path = re.match(regexp, path).groups()[0]
            except AttributeError:
                raise ValueError("Path '%s' does not contain MEDIA_ROOT '%s' as prefix" % (path, media_root))

            return new_path
            

    def _set_encoded_video(self, encoded_video_path):
        self.encoded_video = self._remove_media_root_prefix(encoded_video_path)
        self._finished_encoding = True
        self.save()

    def _set_thumbnails(self, thumbnails):
        for thumbnail, position in thumbnails:
            Thumbnail.objects.create(image=self._remove_media_root_prefix(thumbnail), video=self, position=position)

install_dispatcher(Video)

"""
Copyright (C) 2008 Y-NODE Software
Author: Aleksey Artamonov <aleksey.artamonov@y-node.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

from django.db.models import ImageField, FileField, signals
from django.conf import settings
from distutils.dir_util import mkpath
from video.signals import pre_upload
import shutil, os, glob, re

class DynamicUploadFileField(FileField):
    def __init__(self, *args, **kwargs):
        if not 'upload_to' in kwargs:
            kwargs['upload_to'] = 'tmp'
        self.signal = kwargs.get('signal', None)
        if 'signal' in kwargs:
            del(kwargs['signal'])

        super(DynamicUploadFileField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(DynamicUploadFileField, self).contribute_to_class(cls, name)
        pre_upload.connect(self._move, sender=cls)

    def _move(self, instance=None, **kwargs):
        if hasattr(instance, 'get_upload_to'):
            src = getattr(instance, self.attname)
            if src:
                src = str(src)
                m = re.match(r"%s/(.*)" % self.upload_to, src)
                if m:
                    upload_path = instance.get_upload_to(self.attname)
                    dst = "%s%s" % (
                        upload_path, 
                        m.groups()[0]
                        )
                    basedir = os.path.join(
                      settings.MEDIA_ROOT, 
                      os.path.dirname(dst)
                    )
                    fromdir = os.path.join(
                      settings.MEDIA_ROOT, 
                      src
                    )
                    mkpath(basedir)
                    shutil.move(fromdir, 
                      os.path.join(basedir, 
                                   m.groups()[0])
                    )
                    setattr(instance, self.attname, dst)
                    instance.save()

                    if self.signal:
                        self.signal(instance)

    def db_type(self):
        return 'varchar(200)'

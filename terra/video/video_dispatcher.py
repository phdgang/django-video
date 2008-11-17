"""
Copyright (C) 2008 Y-NODE Software
Author: Aleksey Artamonov <aleksey.artamonov@y-node.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

import os

import video.encoder
import video.thumbnailer
from django.dispatch import dispatcher
from video.signals import post_upload

def process_jobs(sender, **kwargs):
    instance = kwargs['instance']

    path = instance.video.path
    dir = os.path.dirname(path)
    output = "%s/%d.flv" % (dir, instance.id)
    video.encoder.ENCODER_JOB.schedule((path, output), callback=post_encode,
                                       callbackargs=(instance,))

def post_encode(instance, encoded_video_path):
    if encoded_video_path:
        instance._set_encoded_video(encoded_video_path)
        make_thumbnails(instance, encoded_video_path)

def make_thumbnails(instance, encoded_video_path):
    
    video.thumbnailer.THUMBNAILER_JOB.schedule((encoded_video_path,),
                                               callback=post_make_thumbnails,
                                               callbackargs=(instance, encoded_video_path))

def post_make_thumbnails(instance, encoded_video_path, thumbnails):
    if thumbnails:
        instance._set_thumbnails(thumbnails)

def install_dispatcher(cls):
    post_upload.connect(process_jobs, sender=cls)

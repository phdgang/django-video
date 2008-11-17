"""
Copyright (C) 2008 Y-NODE Software
Author: Aleksey Artamonov <aleksey.artamonov@y-node.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

import re
import os
import shutil
import datetime
import video.config
import distutils.dir_util
import PIL.Image
from video.job_server import JOB_SERVER
from job import Job


def settings_dict():
    ordinary_parameters = ["minimum_number", "timestep", "log_file", "width"]
    inherited_parameters = ["width"]
    special_parameters = {"log_file" : lambda value: value if value else "/dev/null"}

    result = {}

    for setting in ordinary_parameters:
        value = video.config.get_thumbnail_setting(setting)
        if setting in special_parameters:
            handler = special_parameters[setting]
            value = handler(value)
        result[setting] = value

    for setting in inherited_parameters:
        value = video.config.get_thumbnail_setting(setting)
        if value == None:
            value = video.config.get_encoding_setting(setting)

        if setting in special_parameters:
            handler = special_parameters[setting]
            value = handler(value)

        result[setting] = value

    return result

def generate_thumbnails(video_file):
    MTN_CMD = "mtn -o .jpg -n -c %(minimum_number)d -Z -b 2 -D 0 -s %(timestep)d -i -t -I -O %(dir)s %(video)s \
>> %(dir)s/%(log_file)s 2>> %(dir)s/%(log_file)s"
    thumbnail_extension = ".jpg"

    settings = settings_dict()
    log = video.config.get_setting('log_function')
    stop_on_errors = video.config.get_setting('stop_on_errors')

    if os.path.exists(video_file):
        settings["video"] = video_file
        out_path = os.path.join(os.path.dirname(video_file),
                                video.config.get_thumbnail_setting('dir'))
        settings["dir"] = out_path
        distutils.dir_util.mkpath(out_path)        

        cmd = MTN_CMD % settings
        log(cmd)
        exitcode = os.system(cmd)
        if exitcode != 0:
            if stop_on_errors:
                raise OSError, exitcode
            else:
                log("[thumbnails] Command returned exitcode %d" % exitcode)
                return None
        else:
            filename_re = re.compile("^([^.]*(\.[^.]*)*?)\.?[^.]*$")

            filename = filename_re.match(os.path.basename(video_file)).groups()[0]
            united_thumbnail = "%s/%s%s" % (out_path, filename, thumbnail_extension)
            os.remove(united_thumbnail)

            dir_contents = os.listdir(out_path)
            thumbnails_re = re.compile("^%s_(\d\d_\d\d_\d\d_\d+%s)$" % (re.escape(filename), re.escape(thumbnail_extension)))
            thumbnails = filter(lambda t: thumbnails_re.match(t) != None, dir_contents)
            thumbnails_new = map(lambda t: thumbnails_re.match(t).groups()[0], thumbnails)

            result = []
            for (old, new) in zip(map(lambda x: "%s/%s" % (out_path, x), thumbnails),
                                  map(lambda x: "%s/%s" % (out_path, x), thumbnails_new)):
                shutil.move(old, new)
                result.append(new)

            return resize_thumbnails(result, settings['width'])
    else:
        if stop_on_errors:
            raise IOError, "%s doesn't exists" % video_file
        else:
            log("[thumbnails] %s doesn't exists" % video_file)
            return None


import PIL
from PIL import Image

def resize_keeping_aspect(image_path, width):
    img = PIL.Image.open(image_path)
    wratio = (width / float(img.size[0]))
    height = int((float(img.size[1]) * float(wratio)))
    img = img.resize((width, height), PIL.Image.ANTIALIAS)
    img.save(image_path)

def resize_thumbnails(thumbnails, width):
    thumbnail_extension = ".jpg"

    log = video.config.get_setting('log_function')
    stop_on_errors = video.config.get_setting('stop_on_errors')
    regexp = re.compile("^(\d\d)_(\d\d)_(\d\d)_\d+%s$" % re.escape(thumbnail_extension))

    result = []

    for t in thumbnails:
        log("Resizing image: %s" % t)
        try:
            resize_keeping_aspect(t, width)
        except Exception, e:
            if stop_on_errors:
                raise
            else:
                log("[resize_thumbnails] Can't resize an image: %s" % str(e))
                return None
        else:
            match = re.match(regexp, os.path.basename(t))
            groups = match.groups()
            hours = int(groups[0])
            minutes = int(groups[1])
            seconds = int(groups[2])
            shift = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
            result.append((t, shift))

    return result

THUMBNAILER_JOB = Job(JOB_SERVER, generate_thumbnails, depfuncs=(settings_dict, resize_thumbnails, resize_keeping_aspect),
                      modules=("re", "os", "shutil", "datetime", "video.config", "PIL"), globals=globals())

"""
Copyright (C) 2008 Y-NODE Software
Author: Aleksey Artamonov <aleksey.artamonov@y-node.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

import pp
import os
import shutil
import video.config
from video.job import Job
from video.job_server import JOB_SERVER


def settings_dict():
    parameters = ["afreq", "abitrate", "framerate", "vbitrate", "width", "height", "log_file"]
    special_parameters = {"log_file" : lambda value: value if value else "/dev/null"}

    result = {}

    for setting in parameters:
        value = video.config.get_encoding_setting(setting)
        if setting in special_parameters:
            handler = special_parameters[setting]
            value = handler(value)
            
        result[setting] = value

    return result

def encode(path, output_path):
    MENCODER_CMD = "\
mencoder -forceidx -of lavf -oac mp3lame -srate %(afreq)d \
-ofps %(framerate)d -ovc lavc -lameopts abr:br=%(abitrate)d \
-lavcopts autoaspect:vcodec=flv:vbitrate=%(vbitrate)d:mbd=2:mv0:\
trell:v4mv:cbp:last_pred=3 \
-vf harddup,expand=:::::4/3,scale=%(width)d:%(height)d \
-o \"%(output)s\" \"%(input)s\" >> %(dir)s/%(log_file)s 2>> %(dir)s/%(log_file)s"

    settings = settings_dict()
    log = video.config.get_setting('log_function')
    stop_on_errors = video.config.get_setting('stop_on_errors')

    if os.path.exists(path):
        settings['input'] = path
        settings['output'] = output_path
        settings['dir'] = os.path.dirname(output_path)

        cmd = MENCODER_CMD % settings
        log(cmd)
        exitcode = os.system(cmd)

        if exitcode != 0:
            if stop_on_errors:
                raise OSError, exitcode
            else:
                log("[encoding] Command returned exitcode %d" % exitcode)
                return None

        return inject_metadata(output_path)
    else:
        if stop_on_errors:
            raise IOError, "%s doesn't exists" % path
        else:
            log("[encoding] %s doesn't exists" % path)
            return None

def inject_metadata(path):
    YAMDI_CMD = "yamdi -i %(input)s -o %(output)s"

    stop_on_errors = video.config.get_setting('stop_on_errors')
    log = video.config.get_setting('log_function')

    if os.path.exists(path):
        tmp_file = path + "_tmp"
        shutil.copyfile(path, tmp_file)

        cmd = YAMDI_CMD % { 'input' : tmp_file, 'output' : path }
        log(cmd)
        exitcode = os.system(cmd)
        os.remove(tmp_file)
        if exitcode != 0:
            if stop_on_errors:
                raise OSError, exitcode
            else:
                log("[metadata] Command returned exitcode %d" % exitcode)
                return None

        return path
    else:
        if stop_on_errors:
            raise IOError, "[metadata] %s doesn't exists" % path
        else:
            log("[metadata] %s doesn't exists" % path)
            return None
        if exitcode != 0:
            if stop_on_errors:
                raise OSError, exitcode
            else:
                log("[metadata] Command returned exitcode %d" % exitcode)
                return None

        return path

ENCODER_JOB = Job(JOB_SERVER, encode, depfuncs=(settings_dict, inject_metadata),
                  modules=("os", "shutil", "video.config"), globals=globals())

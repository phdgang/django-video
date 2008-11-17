"""
Copyright (C) 2008 Y-NODE Software
Author: Aleksey Artamonov <aleksey.artamonov@y-node.com>

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

def string_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError, "Can't transform %s to bool" % s

coercion_exceptions = { bool : string_to_bool }

def transform(s, t):
    if t in coercion_exceptions:
        return coercion_exceptions[t](s)
    else:
        return t(s)

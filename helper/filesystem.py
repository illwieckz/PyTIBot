# PyTIBot - IRC Bot using python and the twisted library
# Copyright (C) <2016>  <Sebastian Schmidt>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import pytibot
from helper.decorators import memoize


@memoize
def get_base_dir():
    """Return the base directory for this project"""
    return os.path.dirname(os.path.realpath(pytibot.__file__))

def isfile(path):
    """Checks if a file exists in the virtual filesystem

    path needs to use the UNIX style path separator('/')"""
    return os.path.isfile(get_abs_path(path))

def isdir(path):
    """Checks if a path exists in the virtual filesystem

    path needs to use the UNIX style path separator('/')"""
    return os.path.isdir(get_abs_path(path))

@memoize
def get_abs_path(path):
    """Return the absolute path of a file in the virtual filesystem"""
    path = path.split("/")
    if "." in path or ".." in path:
        raise SystemError("Relative paths are not supported")
    while "" in path:
        path.remove("")
    return os.path.join(get_base_dir(), *path)

def listdir(directory):
    """List all files in the given directory of the virtual filesystem"""
    if not isdir(directory):
        raise SystemError("No such directory: {}".format(directory))
    return os.listdir(get_abs_path(directory))

def get_contents(path):
    """Return the contents of a file in the virtual filesystem

    filename needs to use the UNIX style path separator('/')"""
    if not isfile(path):
        raise IOError("No such file: {}".format(path))
    with open(get_abs_path(path), "r") as f:
        return f.read()

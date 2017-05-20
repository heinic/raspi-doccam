#!/usr/bin/env python
# coding=UTF-8

# Raspberry Pi document camera
# Copyright (C) 2017  Nico Heitmann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging, logging.handlers
import sys

def log(message, tag="doccam-core"):
    """Log a message. Add a tag to distinguish sources (default: doccam-core)."""
    logging.info("{tag}: {message}".format(tag=tag, message=message))

def shutdown():
    """Stop the logger gracefully."""
    logging.shutdown()


logging.basicConfig(stream=sys.stdout, format="%(message)s", level=15)

logHandlerFile = logging.handlers.RotatingFileHandler("/var/log/doccam-core",
        maxBytes=6400, backupCount=3)
logHandlerFile.setLevel(15)

logFormatter = logging.Formatter("%(asctime)s %(message)s")
logHandlerFile.setFormatter(logFormatter)

logging.getLogger().addHandler(logHandlerFile)

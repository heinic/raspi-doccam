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

import threading
from PIL import Image
import tempfile

import picamera

import logger

def setBounds(res, crop):
    """Update the resolution and crop of the camera."""
    global cam

    if(cam.crop != crop):
        logger.log("Updating crop from {oldcrop} to {newcrop}."
                .format(oldcrop=cam.crop, newcrop=crop))
        cam.crop = crop

    # Chooses the correct resolution for the cropped area
    newres = (int(res[0] * crop[2]),
            int(res[1] * crop[3]))
    if(cam.rotation in (90, 270)):
        newres = (newres[1], newres[0])

    if(cam.resolution != newres):
        logger.log("Updating resolution from {oldres} to {newres}; full size: {fullres}"
                .format(oldres=cam.resolution,newres=newres, fullres=res))
        cam.resolution = newres

global lock
lock = threading.Lock()

lock.acquire()
global cam
cam = picamera.PiCamera()

global MAX_RESOLUTION
global DEFAULT_RESOLUTION
global THUMB_RESOLUTION
MAX_RESOLUTION = cam.MAX_RESOLUTION
DEFAULT_RESOLUTION = (1296, 972)
THUMB_RESOLUTION = (160, 90)


setBounds(DEFAULT_RESOLUTION, (0, 0, 1, 1))
cam.framerate = 30
lock.release()

global globalCrop
globalCrop = [0, 0, 1, 1]


def capture(file, format="png", res=DEFAULT_RESOLUTION):
    """Capture an image to file.

    Uses the global crop."""
    global globalCrop, lock
    lock.acquire()
    setBounds(res, globalCrop)
    cam.capture(file, format=format)
    lock.release()

def captureArea(file, format="png", res=DEFAULT_RESOLUTION, crop=(0, 0, 1, 1)):
    """Capture an image to file.

    Uses the global crop and crops the resulting image.
    This allows exact cropping even if the area is oddly shaped."""

    # Build an array containing the coordinates of the
    # corners of the crop rectangle
    crop = [crop[0], crop[1],
            crop[2] + crop[0],
            crop[3] + crop[1]]

    # Capture to a file
    picFile = tempfile.SpooledTemporaryFile(max_size=3000000)
    capture(picFile)
    picFile.seek(0)

    # Load captured image into a new PIL image object
    img = Image.open(picFile)
    w, h = img.size

    # Crop the image and convert the relative
    # coordinates to pixel space
    img.crop((int(crop[0] * (w - 1)), int(crop[1] * (h - 1)),
              int(crop[2] * (w - 1)), int(crop[3] * (h - 1))
              )).save(file, format=format)

    picFile.close()


def zoom(sizediff):
    """Zoom by sizediff (relative to the entire image).

    Positive numbers increase the visibe area. The center is stationary.
    Changes the global crop."""
    def clamp(minV, maxV, value):
        return max(minV, min(maxV, value))

    global globalCrop

    newCrop = [globalCrop[i] for i in range(4)]
    newCrop[2] += sizediff; newCrop[3] += sizediff

    newCrop[2] = clamp(0.1, 1, newCrop[2])
    newCrop[3] = clamp(0.1, 1, newCrop[3])

    newCrop[0] += (globalCrop[2] - newCrop[2]) / 2.0
    newCrop[1] += (globalCrop[3] - newCrop[3]) / 2.0

    newCrop[0] = clamp(0, 1 - newCrop[2], newCrop[0])
    newCrop[1] = clamp(0, 1 - newCrop[3], newCrop[1])

    globalCrop = newCrop
    cam.crop = globalCrop

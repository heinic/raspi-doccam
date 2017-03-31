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

import os, sys, io, time
import threading, subprocess
import socket, json
import picamera
import string

from PIL import Image

def setCamBounds(res, zoom):
    """Updates the resolution and crop of the camera"""
    global cam, rotateVal

    if(cam.zoom != zoom):
        print("Updating zoom from " + str(cam.zoom) + " to " + str(zoom) + ".")
        cam.zoom = zoom

    # Chooses the correct resolution for the cropped area
    newres = (int(res[0] * zoom[2]),
            int(res[1] * zoom[3]))
    if(rotateVal % 180 == 90):
        newres = (newres[1], newres[0])

    if(cam.resolution != newres):
        print("Updating resolution from " + str(cam.resolution) + " to " +
                str(newres) + ". Full size: " + str(res))
        cam.resolution = newres

def ipcListen():
    """Waits for requests via IPC and handles them in seperate threads"""
    global enableIPC

    sockServer = socket.socket()
    sockServer.bind(("127.3.1.4", 3141));

    while enableIPC:
        sockServer.listen(1)
        # Accept the next connection
        conn = sockServer.accept()

        print("IPC: {!s}".format(conn[1]))

        threadHandle = threading.Thread(target = ipcHandle, args = {conn[0]})
        threadHandle.daemon = True
        threadHandle.start()

def ipcHandle(conn):
    """Handle IPC requests"""
    global cam, cameraL
    global rotateVal, flipVal, cropVal, resVal
    global wifiSsid, wifiPass, wifiChanged

    listen = True
    try:
        while listen:
            strdat = conn.recv(4094)
            if not strdat: break
            data = json.loads(strdat) # load json to an array
            print(threading.currentThread().getName() + " => " + str(data))

            if data[0] == "conf":
                if data[1] == "load": # Load config
                    loadConfig()
                    conn.send("success")
                if data[1] == "save": # Save config
                    saveConfig()
                    conn.send("success")

            if data[0] == "cam": # Camera related actions
                # if data[1] == "cappic": # Save an image at the file path data[2]
                #     cam.capture(data[2])
                #     conn.send("success")
                if data[1] == "cappic_stream": # Capture image and send it via the IPC socket
                    data[2] = data[2].split(';')
                    res = resVal

                    # Change the resolution if requested
                    if(data[2][0] and data[2][0] == 'thumb'):
                        res = (160, 120)
                    if(data[2][0] and data[2][0] == 'hires'):
                        res = cam.MAX_RESOLUTION

                    try:
                        # Use the camera semaphore to ensure the camera is only
                        # used by one thread at a time
                        cameraL.acquire()

                        if(len(data[2]) != 5): # No crop requested
                            # Send image without cropping
                            setCamBounds(res, cropVal)
                            cam.capture(conn.makefile("wb"), format="png")

                        else: # Crop requested
                            setCamBounds(res, cropVal)

                            # Build an array containing the coordinates of the
                            # corners of the zoom rectangle
                            zoom = [float(data[2][1]), float(data[2][2]),
                                    float(data[2][3]) + float(data[2][1]),
                                    float(data[2][4]) + float(data[2][2])]

                            # Capture to a file
                            cam.capture("lastpic.png")

                            # Load captured image into a new PIL image object
                            img = Image.open("lastpic.png")
                            w, h = img.size

                            # Crop the image and convert the relative
                            # coordinates to pixel space
                            img.crop((int(zoom[0] * (w - 1)), int(zoom[1] * (h - 1)),
                                      int(zoom[2] * (w - 1)), int(zoom[3] * (h - 1))
                                      )).save(conn.makefile("wb"), "png")
                    except Exception as e:
                        cameraL.release()
                        raise
                    listen = False

                    # Reset camera and release lock
                    setCamBounds(resVal, cropVal)
                    cameraL.release()
                if data[1] == "flip":
                    if data[2] == "": # Respond with the current flip
                        conn.send(flipVal)
                    else: # Change flip
                        if(data[2] == "n" or data[2] == "h" or data[2] == "v"):
                            flipVal = data[2]
                            cam.hflip = flipVal == "h"
                            cam.vflip = flipVal == "v"

                            conn.send("success")
                if data[1] == "rot":
                    if data[2] == "": # Respond with current rotation
                        conn.send(str(rotateVal))
                    else: # Change rotation
                        try:
                            if(int(data[2]) % 90 == 0 and int(data[2]) >= 0 and int(data[2]) < 360):
                                rotateVal = int(data[2])
                                cam.rotation = rotateVal

                                setCamBounds(resVal, cropVal)

                                conn.send("success")
                        except ValueError as e: # EAFP
                            pass
                if data[1] == "preview":
                    global previewVal
                    if data[2] == "": # Send bach the preview status
                        conn.send(str(int(previewVal)))
                    else: # Change preview status
                        if(data[2] == "0" or data[2] == "1"):
                            previewVal = data[2] == "1"
                            if previewVal:
                                cam.start_preview()
                            else:
                                cam.stop_preview()
                            conn.send("success")
                if data[1] == "crop":
                    if data[2] == "": # Respond with current crop
                        conn.send(json.dumps(cropVal))
                    else: # Set global crop
                        newCrop = json.loads(data[2])
                        if(len(newCrop) == 4):
                            cropVal = newCrop
                            cam.crop = cropVal
                            conn.send("success")
                # if data[1] == "awb":
                #     global awbVal, awbGains
                #     if data[2] == "":
                #         conn.send(json.dumps(awbVal))
                #     else:
                #         awbVal = data[2]
                #         awbGains = cam.awb_gains
                #         cam.awb_mode = awbVal
                #         cam.awb_gains = awbGains
                #         conn.send("success")

            if data[0] == "wifi": # WiFi settings
                if data[1] == "newpass":
                    # Generate a new password using /dev/urandom
                    chars = string.ascii_letters + string.digits
                    chars += "+-/*_<>=?!&()[]}{/\\"
                    passwd = ""
                    for i in range(10):
                        charid = os.urandom(1)
                        char = chars[ord(charid) % len(chars)]
                        passwd += char

                    wifiPass = passwd
                    wifiChanged = True
                    print('New Password: "{!s}"'.format(passwd))
                    conn.send(wifiPass)
                if data[1] == "pass": # Respond with the current password
                    conn.send(wifiPass)
                if data[1] == "ssid":
                    if data[2] == "": # Respond with the current SSID
                        conn.send(wifiSsid)
                    else: # Change the SSID
                        wifiSsid = data[2]
                        wifiChanged = True
                        conn.send("success")
    except Exception as e:
        raise

    print("Done Handling IPC request")

def videoListen():
    """Waits for connections to port 8101 and sends a stream encoded in h264"""
    global cam
    sockServer = socket.socket()
    sockServer.bind(("0.0.0.0", 8101));
    sockServer.listen(0)

    while enableIPC:
        conn = None
        try:
            time.sleep(1)
            conn = sockServer.accept()
            print("Sending Video Stream to " + str(conn[1]))

            cam.start_recording(conn[0].makefile("wb"), format="h264");
            cam.wait_recording(300)
        except Exception as e:
            print(e)
            if e == "KeyboardInterrupt":
                raise
            pass
        finally:
            print("Video Stream Ended!")
            if cam.recording:
                try:
                    cam.stop_recording()
                except Exception as e: pass
            try:
                conn[0].shutdown(socket.SHUT_RDWR)
            except Exception as e:
                pass
            conn = None

def loadConfig():
    """Loads configuration"""
    # Hostapd:
    global wifiSsid, wifiPass, wifiChanged
    wifiSsid = "---"
    wifiPass = "---"

    wifilines = None
    with io.open("/etc/hostapd/hostapd.conf") as file:
        wifilines = file.readlines()

    for line in wifilines:
        if(line.startswith("ssid=")):
            wifiSsid = line.split("=", 1)[1].strip()
            print('SSID: "{!s}"'.format(wifiSsid))
        if(line.startswith("wpa_passphrase=")):
            wifiPass = line.split("=", 1)[1].strip()
            print('PASS: "{!s}"'.format(wifiPass))
    wifiChanged = False

def saveConfig():
    """Saves all of the changed configuration variables"""
    print("Saving Config")
    # Hostapd:

    if wifiChanged:
        global wifiSsid, wifiPass, wifiChanged
        print("Saving hostapd config")

        wifilines = None
        with io.open("/etc/hostapd/hostapd.conf") as file:
            wifilines = file.readlines()

        for i in range(0, len(wifilines)):
            line = wifilines[i]
            if(line.startswith("ssid=")):
                line = u'ssid={!s}\n'.format(wifiSsid)
            if(line.startswith("wpa_passphrase=")):
                line = u'wpa_passphrase={!s}\n'.format(wifiPass)
            wifilines[i] = line

        with io.open("/etc/hostapd/hostapd.conf", "wt") as file:
            for line in wifilines:
                file.write(line)

        print("Restarting hostapd...")
        subprocess.call(["sudo", "service", "hostapd", "restart"])
    else:
        print("Not saving hostapd config")
    print("Done Saving Config")

print("***********************************")
print("*                                 *")
print("*  Raspberry Pi Dokumentenkamera  *")
print("*                                 *")
print("***********************************")
print


global resVal, flipVal, rotateVal, cropVal
resVal = (1296, 972)
flipVal = "n"
rotateVal = 0
cropVal = (0, 0, 1, 1)

global previewVal
previewVal = False

global cameraL
cameraL = threading.BoundedSemaphore(value = 1)

# global awbVal, awbGains
# awbVal = "auto"
# awbGains = (1, 1)

global enableIPC
enableIPC = True

# PiCamera init
cameraL.acquire()
global cam
print("Initializing camera... ")
cam = picamera.PiCamera()
setCamBounds(resVal, cropVal)
cam.framerate = 30
cameraL.release()

# Config
print("Loading config... ")
loadConfig()
print("done")

print("Starting background threads...")
# IPC
threadServerIPC = threading.Thread(target = ipcListen)
threadServerIPC.daemon = True
threadServerIPC.start()
print("- IPC")

# h264 Vido Server
threadServerVideo = threading.Thread(target = videoListen)
threadServerVideo.daemon = True
threadServerVideo.start()
print("- h264 Video")

print
print("------------- Ready -------------")

raw_input()
enableIPC = False

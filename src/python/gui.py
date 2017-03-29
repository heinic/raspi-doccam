#!/usr/bin/env python
# coding=UTF-8

from Tkinter import *
from RPi import GPIO

import sys, time
import socket, subprocess, json

def comm(data):
    """Communicate with camera.py using a socket"""
    sock = socket.socket()
    sock.connect(("127.3.1.4", 3141))

    strdat = json.dumps(data)

    sock.send(strdat)
    retdat = sock.recv(4096)

    sock.close()
    print("IPC: " + strdat + "; answer: " + retdat)
    return retdat

global screens
screens = []

class MenuScreen(object):
    """Represents a generic screen with 4 button inputs"""

    def __init__(self): pass

    def onPress(self, num): pass

    def prepUI(self, root): pass

    def cleanUI(self): pass

class SimpleScreen(MenuScreen):
    """A simple screen with a title and 4 possible action buttons"""

    def __init__(self, title, subNames, subActions):
        super(SimpleScreen, self).__init__()
        self.title = title
        self.info = ""
        self.subNames = subNames
        self.subActions = subActions

    def onPress(self, num):
        print("Button " + str(num) + " pressed!");
        action = self.subActions[num]
        if not action == 0: action()
        else: print("No Action found!")

    def prepUI(self):
        global buttons, backgroundfr, root, labelTitle, labelInfo

        labelTitle.config(text = self.title)
        labelInfo.config(text = self.info)
        for i in range(4):
            buttons[i].config(text = self.subNames[i])
            if self.subNames[i] == "":
                # Add text to empty buttons to ensure a consistent layout
                buttons[i].config(text = "fill it up!")
                buttons[i].lower(backgroundfr)

    def cleanUI(self):
        global buttons, backgroundfr, labelTitle, labelInfo

        labelTitle.config(text = "Raspberry Pi Dokumentenkamera")
        labelInfo.config(text = "")
        for i in range(4):
            if self.subNames[i] == "":
                buttons[i].lift(backgroundfr)

class DialogScreen(MenuScreen):
    """A screen with multiple options; only one can be chosen and a callback is
    executed"""

    def __init__(self, title, options, action):
        super(DialogScreen, self).__init__()
        self.title = title
        self.info = ""
        self.options = options
        self.action = action

    def onPress(self, num):
        print("Button " + str(num) + " pressed!");
        if(self.options[num] != ""):
            self.action(num)
            popScreen()

    def prepUI(self):
        global buttons, backgroundfr, root, labelTitle, labelInfo
        labelTitle.config(text = self.title)
        labelInfo.config(text = self.info)
        for i in range(4):
            buttons[i].config(text = self.options[i])
            if self.options[i] == "":
                # Add text to empty buttons to ensure a consistent layout
                buttons[i].config(text = "fill it up!")
                buttons[i].lower(backgroundfr)

    def cleanUI(self):
        global buttons, backgroundfr, labelTitle, labelInfo
        labelTitle.config(text = "Raspberry Pi document camera")
        labelInfo.config(text = "")
        for i in range(4):
            if self.options[i] == "":
                buttons[i].lift(backgroundfr)


class MainMenu(SimpleScreen):
    def __init__(self):
        super(MainMenu, self).__init__("Raspi document camera",
        ("", "", "Settings", "Quit"), (0, 0, self.openOptions, exit))

    def openOptions(self):
        showScreen(SettingsMenu())

class SettingsMenu(SimpleScreen):
    def __init__(self):
        super(SettingsMenu, self).__init__("Settings",
        ("Network", "Image", "More...", "Back"),
        (self.openNetwork, self.openImage, self.openOther, popScreen))

    def openOther(self):
        menuOther = SimpleScreen("More Settings",
        ("Help / About", "", "Dev options", "Back"),
        (self.openHelp, 0, self.openDev, popScreen))
        showScreen(menuOther)

    def openNetwork(self):
        showScreen(NetworkSettingsMenu())

    def openImage(self):
        showScreen(ImageSettingsMenu())

    def openDev(self):
        showScreen(DevSettingsMenu())

    def openHelp(self):
        helpMenu = SimpleScreen("Help / About", ("", "", "", "Back"),
                (0, 0, 0, popScreen))
        helpMenu.info = ("Raspberry Pi document camera\n" +
                "Source code: licensed under GNU GPL-3.0\n" +
                "https://github.com/heinic/\n  raspi-doccam-software\n")
        showScreen(helpMenu)

class NetworkSettingsMenu(SimpleScreen):
    def __init__(self):
        super(NetworkSettingsMenu, self).__init__("Network settings",
                ("New WiFI\npassword", "", "", "Back"),
                (self.changeWIFIPass, 0, 0, popScreen))
        self.update()

    def update(self):
        self.info = ("WiFi - SSID: " + comm(("wifi", "ssid", "")) +
                "\nPassword: " + comm(("wifi", "pass", "")) + "\n")

    def changeWIFIPass(self):
        dialog = DialogScreen("Change WiFi password",
                ("Change", "", "", "Cancel"), self.onChangeWifiPass)
        dialog.info = ("Are you sure you want to change\n" +
                "the WiFi password? This cannot be undone.\n")
        showScreen(dialog)

    def onChangeWifiPass(self, num):
        if(num == 0):
            print("Changing WiFi Password")
            comm(("wifi", "newpass", ""))
            self.update()

class ImageSettingsMenu(SimpleScreen):
    def __init__(self):
        super(ImageSettingsMenu, self).__init__("Image Settings",
                ("Rotate", "Mirror", "Preview", "Back"),
                (self.changeRot, self.changeFlip, self.changePrev, popScreen))

    def changeFlip(self):
        dialog = DialogScreen("Mirror image",
                ("No Flip", "Horizontal", "Vertical", "Cancel"),
                self.onChangeFlip)
        showScreen(dialog)

    def onChangeFlip(self, num):
        if(num < 3):
            flips = "n", "h", "v"
            comm(("cam", "flip", flips[num]))

    def changeRot(self):
        dialog = DialogScreen("Rotate image", ("No rotation", "90°\nclockwise",
                "180°", "90° counter-\nclockwise"), self.onChangeRot)
        showScreen(dialog)

    def onChangeRot(self, num):
        comm(("cam", "rot", str(num * 90)))

    def changePrev(self):
        dialog = DialogScreen("Preview", ("Disable", "Enable", "", "Back"),
                self.onChangePrev)
        dialog.info = ("Choose whether a preview should\n" +
                "be available on the HDMI port.\n")
        showScreen(dialog)

    def onChangePrev(self, num):
        if (num < 2):
            comm(("cam", "preview", str(num)))

class DevSettingsMenu(SimpleScreen):
    def __init__(self):
        super(DevSettingsMenu, self).__init__("Developer options",
                ("", "", "", "Back"), (0, 0, 0, popScreen))

def showScreen(scr):
    global screens
    if(len(screens) != 0):
        screens[len(screens) - 1].cleanUI()
    scr.prepUI()
    screens.append(scr)

def popScreen():
    global screens
    screens.pop().cleanUI()
    screens[len(screens) - 1].prepUI()


GPIO.setmode(GPIO.BCM)
global buttonChannels
buttonChannels = (17, 22, 23, 27)

GPIO.setup(buttonChannels, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def onPress(num):
    """Called when a button is pressed"""
    global screens
    screens[len(screens) - 1].onPress(num)

def onGPIOEvent(channel):
    """Called when a Button connected to GPIO is pressed"""
    global buttonChannels, screens, buttons

    # Debounce button
    time.sleep(.1)
    if(GPIO.input(channel)): return

    buttonNum = [i for i, v in enumerate(buttonChannels) if v == channel][0]

    # Visual button press feedback
    buttons[buttonNum].config(relief=SUNKEN)

    # Debounced wait for release
    while not GPIO.input(channel):
        while not GPIO.input(channel):
            time.sleep(0.05)
        time.sleep(0.1)

    buttons[buttonNum].config(relief=RAISED)

    # Forward event to central handler
    screens[len(screens) - 1].onPress(buttonNum)

for ch in buttonChannels:
    GPIO.add_event_detect(ch, GPIO.FALLING, callback=onGPIOEvent)

global root
root = Tk()
root.title("Raspberry Pi document camera")
root.geometry("320x240")
root.attributes("-fullscreen", True)

global backgroundfr

backgroundfr = Frame(root)
backgroundfr.grid(rowspan = 4, columnspan = 4, sticky = N + E + S + W)

# Add buttons
global buttons
buttons = []

buttons.append(Button(root, text="Option 0", command=lambda: onPress(0)))
buttons.append(Button(root, text="Option 1", command=lambda: onPress(1)))
buttons.append(Button(root, text="Option 2", command=lambda: onPress(2)))
buttons.append(Button(root, text="Option 3", command=lambda: onPress(3)))

buttons[0].grid(row=3, column=0, sticky = N + E + S + W)
buttons[1].grid(row=3, column=1, sticky = N + E + S + W)
buttons[2].grid(row=3, column=2, sticky = N + E + S + W)
buttons[3].grid(row=3, column=3, sticky = N + E + S + W)

# Add default labels
global labelTitle
labelTitle = Label(root, text="Raspberry Pi Dokumentenkamera", font=("sans-serif", 12))
labelTitle.grid(row=0, columnspan=4)

global labelInfo
labelInfo = Label(root, text="inittext", font=("sans-serif", 11), anchor = SW, justify = LEFT)
labelInfo.grid(row=2, columnspan=4, sticky = S + W)

for i in range(4):
    root.grid_columnconfigure(i, weight=1)

# Expand row 2 and push buttons down
root.grid_rowconfigure(2, weight=1)

# Open default screen
menuMain = MainMenu()
showScreen(menuMain)

root.mainloop()

GPIO.cleanup()
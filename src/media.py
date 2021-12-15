import os
from pad4pi import rpi_gpio
import subprocess

def playSound(file):
    os.system("mpg123 sounds/" + file + ".mp3 > /dev/null 2>&1 &")

def getPpd():
    prn = subprocess.check_output("lpstat -d | awk '{print $NF}'", shell=True).decode("utf-8").strip()
    print("prn: " + prn)
    ppd = "/etc/cups/ppd/" + prn +".ppd"
    print("ppd: " + ppd)
    with open(ppd) as ppdfile:
        ppdstd = [x for x in ppdfile if x.startswith("*PCFileName:")]
        ppdstd = ppdstd[0].lower().split('"')[1].split(".ppd")[0]
    return ppdstd

class KeyStore():
    def  __init__(self):
        KEYPAD = [
            ["1", "2", "3", "A"],
            ["4", "5", "6", "B"],
            ["7", "8", "9", "C"],
            ["*", "0", "#", "D"]
        ]
        ROW_PINS = [21, 20,16, 12]# BCM numbering
        COL_PINS = [26, 19, 13, 6] # BCM numberin
        factory = rpi_gpio.KeypadFactory()
        self.keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)
        self.keypad.registerKeyPressHandler(self.storeKey)
        self.keypressed = ""

    def storeKey(self,key):
        self.keypressed = key

    def restartKey(self):
        self.keypressed = ""

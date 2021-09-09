#!/usr/bin/env python3

import re
import time
import requests
import os
import subprocess
import glob
import configparser
import random

from datetime import date, datetime
from time import sleep
from threading import Thread
from queue import Queue

from RPLCD.i2c import CharLCD
#from RPi_GPIO_i2c_LCD import lcd
#import serial

from pad4pi import rpi_gpio

CODE_DIGITS = 3
temp_digits = 0

DEFAULT_COPIES = 1
DEFAULT_SIDES = "two-sided-long-edge" #two-sided-long-edge, two-sided-short-edge, one-sided
DEFAULT_MEDIA = "A4"

PRINT_CMD = "lp -n %(copies)s -o sides=%(sides)s -o media=%(media)s %(in)s"
PRINTRAW_CMD = "lp -o raw %(in)s"


#mylcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=0, cols=16, rows=2, charmap='A02')
mylcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, charmap='A02')

# mylcd = lcd.HD44780(0x27)
#ser = serial.Serial('/dev/ttyS0', 19200)  # open serial port

KEYPAD = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

#ROW_PINS = [23, 24, 10, 9] # BCM numbering
#COL_PINS = [11, 25, 8, 7] # BCM numbering
ROW_PINS = [5, 6, 13, 19] # BCM numbering
COL_PINS = [26, 16, 20, 21] # BCM numbering


key_lookup = ""




def main():
    play("start")
    print ("start")

    display("Stampa la fanza","by itec")
    resetdisplay = True
    displaytime = time.time() + 10

    # for ppd in sorted(glob.glob(os.path.dirname(os.path.realpath(__file__)) + "/ppd/*.ppd")):
    prn = subprocess.check_output("lpstat -d | awk '{print $NF}'", shell=True).decode("utf-8").strip()
    print("prn: " + prn)
    ppd = "/etc/cups/ppd/" + prn +".ppd"
    print("ppd: " + ppd)
    #cerca il nome standard
    with open(ppd) as ppdfile:
        ppdstd = [x for x in ppdfile if x.startswith("*PCFileName:")]
        ppdstd = ppdstd[0].lower().split('"')[1].split(".ppd")[0]
    print("ppdstd: " + ppdstd)

    code = ""
    global key_lookup
    key_lookup = ""
    global temp_digits
    temp_digits = CODE_DIGITS

    factory = rpi_gpio.KeypadFactory()
    keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

    keypad.registerKeyPressHandler(printKey)


    #loop
    #try:
    while True:
        time.sleep(0.05)

        if resetdisplay == True and time.time() > displaytime:
            displaycode(code)
            temp_digits = CODE_DIGITS
            resetdisplay = False

        if code != '':
            if time.time() > keytime + 3:
                code = ''
                #keytime = time.time()
                print ("Resettato")
                play("reset")
                displaycode(code)


        if key_lookup != "":
            # print(key_lookup)


            keytime = time.time()
            if(key_lookup == "D"):
                code = ''
                temp_digits = CODE_DIGITS
                print ("Resettato")
                play("reset")
                displaycode(code)
            elif(key_lookup == "xxx"):
                code = code[:-1]
                play("button")
                displaycode(code)
            elif key_lookup != "None":
                code += key_lookup
                play("button")
                if code == "ACA": # ACAB easter egg
                    temp_digits = 4
                displaycode(code)

            if len(code) == temp_digits:
                print(code)

                # fname = [x for x in sorted(glob.glob(os.path.dirname(os.path.realpath(__file__)) + '/spool/**/%s-*' % code, recursive=True))
                #     if not x.endswith('.info') and not x.endswith('.keep') and not x.endswith('.raw')]
                
                #questo cerca direttamente il raw
                fname = [x.replace('.' + ppdstd + '.raw','') for x in sorted(glob.glob(os.path.dirname(os.path.realpath(__file__)) + '/spool/**/%s-*.' % code + ppdstd + '.raw', recursive=True))]


                if not fname:
                    print ("Non trovato " + code)
                    play("fail")
                    display("No fanza", formatcode(code))
                else:
                    #fname = fname[0]
                    fname = random.choice(fname)

                    #leggo la configurazione
                    config = configparser.ConfigParser()
                    name = "-".join(os.path.basename(fname).split("-")[1:])
                    copies = DEFAULT_COPIES
                    sides = DEFAULT_SIDES
                    media = DEFAULT_MEDIA

                    
                    try:
                        # print(os.path.dirname(fname) + "/" + code + '.info')
                        config.read(os.path.dirname(fname) + "/" + code + '.info')
                        printconf = config['print']
                        name = printconf.get('name', name)
                        copies = printconf.getint('copies', copies)
                        sides = printconf.get('sides', sides)
                        media = printconf.get('media', media)
                    except Exception:
                        pass

                    try:
                        config.read(fname + '.info')
                        printconf = config['print']
                        name = printconf.get('name', name)
                        copies = printconf.getint('copies', copies)
                        sides = printconf.get('sides', sides)
                        media = printconf.get('media', media)
                    except Exception:
                        pass

                    print("Conf:",name, copies, sides, media)

                    print ("Stampo " + code)
                    play("print")
                    display("Stampo", name) 

                    #cerca il raw:
                    rawname = fname + "." + ppdstd + ".raw"
                    if os.path.isfile(rawname):
                        #stampo
                        cmd = PRINTRAW_CMD.split(' ')
                        cmd = [x % {'in': rawname} for x in cmd]
                        cmd = " ".join(cmd)
                        print (cmd)
                        os.system(cmd)
                    else:
                        #stampo
                        cmd = PRINT_CMD.split(' ')
                        cmd = [x % {'in': fname, 'copies': copies, 'sides': sides, 'media': media} for x in cmd]
                        cmd = " ".join(cmd)
                        print (cmd)
                        os.system(cmd)
                
                code = ''
                resetdisplay = True
                temp_digits = CODE_DIGITS
                displaytime = time.time() + 5

            key_lookup = ""
    #except:
    #    keypad.cleanup()


def displaycode(code):
    display("Stampa la fanza", formatcode(code))

def display(ro1, ro2):
    r1 = ro1[:16].center(16,' ')
    r2 = ro2[:16].center(16,' ')

    mylcd.write_string(r1 + '\r\n' + r2)


    #mylcd.set(r1, 1)
    #mylcd.set(r2, 2)

    #r1 = ro1[:20].center(20,' ')
    #r2 = ro2[:20].center(20,' ')
    #ser.write(b'\xfe\x42') #power on display
    #ser.write(("\n" + r1 + r2).encode())

    #print("-" + r1 + "-" + r2 + "-")

def formatcode(code):
    #return (code + "-")[0:CODE_DIGITS]
    return (code + "-"*(temp_digits - len(code)))

def play(file):
    os.system("mpg123 sounds/" + file + ".mp3 > /dev/null 2>&1 &")
                     
def printKey(key):
    #print(key)
    global key_lookup
    key_lookup = key

if __name__ == "__main__":
    main()

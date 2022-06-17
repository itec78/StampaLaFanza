#!/usr/bin/env python3

import re
import time
import requests
import os
import glob
import configparser
import random

from datetime import date, datetime
from time import sleep
from threading import Thread
from queue import Queue

from RPLCD.i2c import CharLCD

# Internal project imports
from src.parser import readParameters
from src.media import playSound, KeyStore, getPpd
from src.screen import ScreenManager

def main():
    # First read user parameters and asign them to configuration vars
    userParameters = readParameters()

    CODE_DIGITS = userParameters.digits

    DEFAULT_COPIES = userParameters.copies
    DEFAULT_SIDES = userParameters.sides #two-sided-long-edge, two-sided-short-edge, one-sided
    DEFAULT_MEDIA = userParameters.media

    PRINT_CMD = "lp -n %(copies)s -o sides=%(sides)s -o media=%(media)s %(in)s"
    PRINTRAW_CMD = "lp -o raw %(in)s"

    code = ""
    resetdisplay = True
    displaytime = time.time()
    # Object inizialization
    ks = KeyStore()
    sm = ScreenManager(userParameters.st,CODE_DIGITS,address=userParameters.i2c)
    ppdstd = getPpd()

    # START
    playSound("start")
    print ("start")
    sm.display("Stampa la fanza", "Initializing")

    # Program main loop
    while True:
        time.sleep(0.05)
        if resetdisplay == True and time.time() > displaytime:
            sm.displayCode(code)
            sm.temp_digits = CODE_DIGITS
            resetdisplay = False

        #  Resets the introduced code after not pressing buttons for a while
        if code != '':
            if time.time() > keytime + 3:
                code = ''
                playSound("reset")
                sm.displayCode(code)

        
        if ks.keypressed != "":
            keytime = time.time()
            # Action bindings
            if(ks.keypressed == "D"):
                code = ''
                sm.temp_digits = CODE_DIGITS
                print ("Resettato")
                playSound("reset")
                sm.displayCode(code)
            elif(ks.keypressed == "xxx"):
                code = code[:-1]
                playSound("button")
                sm.displayCode(code)
            elif ks.keypressed != "None":
                code += ks.keypressed
                playSound("button")
                if code == "ACA": # ACAB easter egg
                    sm.temp_digits = 4
                sm.displayCode(code)

            # This is when user introduces al the code characters
            if len(code) == sm.temp_digits:
                fname = [x.replace('.' + ppdstd + '.raw','') for x in sorted(glob.glob(os.path.dirname(os.path.realpath(__file__)) + '/spool/**/%s-*.' % code + ppdstd + '.raw', recursive=True))]
                if not fname:
                    print ("Non trovato " + code)
                    playSound("fail")
                    sm.display404(code)
                else:
                    # TO-DO: I think this can be moved to other file
                    # Printer or something like that
                    fname = random.choice(fname)

                    # leggo la configurazione 
                    # Printer configuration
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

                    print("Conf:",name, copies, sides, media)
                    print ("Stampo " + code)
                    playSound("print")
                    sm.display("Stampo", name) 

                    #cerca il raw:
                    rawname = fname + "." + ppdstd + ".raw"
                    if os.path.isfile(rawname):
                        #stampo
                        cmd = PRINTRAW_CMD.split(' ')
                        cmd = [x % {'in': rawname} for x in cmd]
                        cmd = " ".join(cmd)
                        os.system(cmd)
                
                code = ''
                resetdisplay = True
                sm.temp_digits = CODE_DIGITS
                displaytime = time.time() + 5
        ks.restartKey()

if __name__ == "__main__":
    main()

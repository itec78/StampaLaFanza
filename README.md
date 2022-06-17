# Stampa la fanza
Allows to print a set of fanzines using a laser printer, raspberry pi and keypad

True spaghetti code, please help me to improve it!

# Instructions

Connect the keypad to gpio, the display to i2c and adjust settings

Install the printer and set it as default (pcl driver is better than postscript)

Add files to spool folder, renaming it to [num]-[filename].pdf

Grant user access to folder /etc/cups/ppd/

Run spoolraw.py to spool files

Run stampalafanza.py


![Printer](/printer.png)

![Console](/console.png)



# Pantalla oled 
- Install adafruit library 
# https://github.com/adafruit/Adafruit_CircuitPython_Bundle
# https://github.com/adafruit/Adafruit_CircuitPython_SSD1306
- I would recomend to install it in a Python venv not in the native python
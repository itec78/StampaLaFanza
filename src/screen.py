import time
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

class ScreenManager:
    def __init__(self,screentype,temp_digits = 3,font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",address=0):
        self.screentype = screentype
        self.temp_digits = temp_digits

        if screentype.lower() == "oled":
            self.i2c = busio.I2C(SCL, SDA)

            self.disp = adafruit_ssd1306.SSD1306_I2C(128, 32, self.i2c)
            self.disp.fill(0)
            self.disp.show()

            self.width = self.disp.width
            self.height = self.disp.height
            self.image = Image.new("1", (self.width,self.height))

            self.draw = ImageDraw.Draw(self.image)
            self.x = 0

            self.padding = -2
            self.top = self.padding
            self.bottom = self.height - self.padding
            
            self.font = ImageFont.truetype(font_path,size=14)
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        elif screentype.lower() == "lcd":
            self.mylcd = CharLCD(i2c_expander='PCF8574', address=adress, port=1, cols=16, rows=2, charmap='A02')
        else:
            print("Error, invalid screen type")
            exit(1)

    def __displayLcd(self):
        r1 = ro1[:16].center(16,' ')
        r2 = ro2[:16].center(16,' ')
        self.mylcd.write_string(r1 + '\r\n' + r2)

    def __displayOled(self,ro1,ro2):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.draw.text((self.x, self.top + 0), ro1, font=self.font,fill=255)
        self.draw.text((self.x, self.top + 16), ro2, font=self.font,fill=255)
        self.disp.image(self.image)
        self.disp.show()
        time.sleep(0.1)

    def display(self,ro1,ro2):
        if self.screentype == "oled":
            self.__displayOled(ro1,ro2)
        elif self.screentype == "lcd":
            self.__displayLcd(ro1,ro2)

    def __formatCode(self,code):
        return ("      " + code + "-"*(self.temp_digits - len(code)))

    def displayCode(self,code):
        fc = self.__formatCode(code)
        self.display("Stampa La Fanza", fc)

    def display404(self,code):
        fc = self.__formatCode(code)
        self.display("No fanza",fc)

import sys
import argparse

def readParameters():
    usage_examples = sys.argv[0] + " -digits 4 -i2c 0x3c \n"
    parser = argparse.ArgumentParser(epilog=usage_examples,formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-digits",help="Number of digits to identify fanzines", default=3,type=int)
    parser.add_argument("-copies", help="Number of copies by default", default=1, type=int)
    parser.add_argument("-sides", help="Sides for printing by default two-sided-long-edge, accepted values [two-sided-long-edge, two-sided-short-edge, one-sided]",default="two-sided-long-edge")
    parser.add_argument("-media", help="Page size, by default it's A4", default="A4")
    parser.add_argument("-i2c", help="I2c address for your device, default value 0x27", default="0x27")
    parser.add_argument("-st", help="Screen type, accepted values ['oled', 'lcd'] default oled ", default="oled")
    args = parser.parse_args()
    args.i2c = int(args.i2c,16)
    return args
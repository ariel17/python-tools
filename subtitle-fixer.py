#!/usr/bin/python

import argparse
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(\
        description=("Subtitles fixer. Useful when subtitles have a " + \
        "significant offset respecting the video."))

parser.add_argument("-x", "--separator", type=str, \
        default="--> ", help=("String. Symbol separator for subtitles " + \
        "duration. Default: '--> '."))

parser.add_argument("-s", "--src", type=str, \
        required=True, help="String. Source file name.")

parser.add_argument("-d", "--dst", type=str, \
        required=True, help="String. Destination file name.")

parser.add_argument("-o", "--offset", type=int, \
        default=0, help=("Integer. Time offset: positive offset makes " + \
        "subtitles shows later; negative shows earlier. Default: 0 seconds."))


def offsetter(src, dst, offset, separator):
    fdsrc = open(src, "r")
    fddst = open(dst, "w")
    t = datetime.today()
    for line in fdsrc:
        if separator in line:
            parts = line.split(separator)
            new_parts = []
            for part in parts:
                hh, mm, ss = part.split(":")
                ss, ms = ss.split(",")
                base = datetime(year=t.year, month=t.month, day=t.day, \
                        hour=int(hh), minute=int(mm), second=int(ss), \
                        microsecond=int(ms))
                deltaoffset = timedelta(seconds=offset) 
                result = (base + deltaoffset).strftime("%H:%M:%S,%%s") % ms
                new_parts.append( result )
            line = separator.join(new_parts)
        fddst.write(line)
    fdsrc.close()
    fddst.close()

if __name__ == '__main__':
    args = parser.parse_args()
    offsetter(args.src, args.dst, args.offset, args.separator)

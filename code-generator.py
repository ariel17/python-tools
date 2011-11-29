#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Description: String code generator.
"""
__author__ = "Ariel Gerardo Ríos (ariel.gerardo.rios@gmail.com)"


import random
import argparse


LANG = 'ABCDEFGHJKMNPQRSTUVWXYZ'
random.seed()


parser = argparse.ArgumentParser(description="Basic string code generator "\
        "in Python :)")

parser.add_argument("-c", "--cant", type=int, required=True,
        help="How many codes to generate.")

parser.add_argument("-e", "--length", type=int, required=True,
        help="Code length.")

parser.add_argument("-l", "--lang", type=str, required=False, default=LANG,
        help="Language to use. Default: %s" % LANG)

parser.add_argument("-a", "--add-consecutives", action="store_true",
        default=False, help="Add consecutive chars? Default: False.")


if __name__ == '__main__':

    args = parser.parse_args()
    
    codes = set()
    lang_len = len(args.lang)
    
    for c in xrange(args.cant):
        code = ""
        while len(code) < args.length:
            rand_pos = random.randint(0, lang_len - 1)
            char = LANG[rand_pos]
            if code and not args.add_consecutives and code[-1] == char:
                continue
            code += char
            codes.add(code)
        print code

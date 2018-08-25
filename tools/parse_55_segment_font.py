#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Parses font.def and generates table with letters
# ----------------------------------------------------------------------------
"""
Tool to convert a font-file to .asm code
"""
import argparse
import json
import sys


__docformat__ = 'restructuredtext'

# fonts that shouldn't be translated (manually generated)
DONT_TRANSLATE = ('tateti', 'dollar')

FONT = {
    # ordered by ascii
    'space': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x20
    'exclam': [0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1], # 0x21
    'quote': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x22 - N/A
              #                    1                   2                   3                   4                   5
              #0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4
    'tateti': [0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x23 - bat 1
    'dollar': [0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x24 - bat 2

    'percent':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x24 - ... 1
    'and':    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x25 - ... 2

    'single_quote': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x27 - N/A
    'open_p': [1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0], # 0x28
    'closed_p': [0,0,1,1,1,1,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0], # 0x29
    'star': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x2a - N/A
    'plus': [0,0,0,0,0,0,0,0,0,1,1,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1],  # 0x2b
    'comma': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,1], # 0x2c
    'minus': [0,0,0,0,0,0,0,0,0,1,1,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,0,0,1], # 0x2d
    'dot': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], # 0x2e
    'slash': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x2f - N/A

    '0': [1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0,1,1,1,0,0,1,0,1,0,0,0,1,1,1,1,1,1,1], # 0x30
    '1': [1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1], # 0x31
    '2': [1,0,1,1,1,1,0,1,1,1,1,0,0,1,0,0,1,1,0,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,1,1,1], # 0x32
    '3': [1,0,1,1,1,1,0,1,0,1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,1,1,0,0,1,1,1,0,0,0,0,0,1,0,0,0,0,1,0,0,1,1], # 0x33
    '4': [1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,0,1,1], # 0x34
    '5': [1,1,1,1,1,1,1,0,0,1,1,1,0,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,1,1,1], # 0x35
    '6': [1,0,1,1,1,1,0,0,0,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,1,1,1], # 0x36
    '7': [1,1,1,1,1,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,0,0,0,1,1,1,0,0,1,0,1,1,1,1,1,1,1,0,0,0,1], # 0x37
    '8': [1,0,1,1,1,1,0,1,0,1,0,0,0,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,1,1,1], # 0x38
    '9': [1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,0,1,1], # 0x39

    'colon': [0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,1], # 0x3a
    'semin_colon': [0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,1], # 0x3b
    'less': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x3c - N/A
    'eq': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x3d - N/A
    'greater': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x3e - N/A
    'interr': [1,0,1,1,1,1,0,1,1,1,1,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,1], # 0x3f

    'at': [1,0,1,1,1,1,0,1,1,1,1,0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,1], # 0x40
         #                    1                   2                   3                   4                   5
         #0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4
    'a': [1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1], # 0x41
    'b': [1,1,1,1,1,1,0,1,0,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,1,1,1], # 0x42
    'c': [1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0], # 0x43
    'd': [1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0], # 0x44
    'e': [1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,1,1,1], # 0x45
    'f': [1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,1,0,1], # 0x46
    'g': [1,0,1,1,1,1,0,0,0,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0,0,1,1,0,0,0,0,0,1,0,0,0,0,0,1,1,1,1], # 0x47
    'h': [1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,1,1,1], # 0x48
    'i': [1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1], # 0x49
    'j': [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0], # 0x4a
    'k': [1,1,0,0,0,1,1,1,0,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,0,1,1,1,0,0,1,0,1,1,1,0,0,0,1,1,1,1,1], # 0x4b
    'l': [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0], # 0x4c
    'm': [1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1], # 0x4d
    'n': [1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,0,1,1,1,1,1], # 0x4e
    'o': [1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0], # 0x4f
    'p': [1,1,1,1,1,1,0,1,1,1,1,0,0,1,0,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,1,0,1], # 0x50
    'q': [1,0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,1,1,0], # 0x51
    'r': [1,1,1,1,1,1,0,1,0,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,1,1,0,0,1,1,1,1,1,1], # 0x52
    's': [1,0,1,1,1,1,0,0,0,1,1,1,0,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,0,1,1], # 0x53
    't': [1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1], # 0x54
    'u': [1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0], # 0x55
    'v': [1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,1,1,0], # 0x56
    'w': [1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0,1,1,1,0,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1], # 0x57
    'x': [1,1,0,0,0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,0,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1,1,1,1,0,1,0,1,1,1,0,1,1,1,1,1,1,1], # 0x58
    'y': [1,1,0,0,0,1,1,1,1,1,1,0,0,1,0,1,1,1,1,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,1,0,0,1], # 0x59
    'z': [1,1,1,1,1,1,1,1,1,1,1,0,0,1,0,0,1,1,0,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,1,1,1], # 0x5a

    'llave_izq': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x5b - N/A
    'inv_slash': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x5c - N/A
    'llave_der': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x5d - N/A
    'caret': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # 0x5e - N/A

    '_': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0], # 0x5f

    'pipe': [0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1], # 0x7c
}

BIT_TRANS = {
   0:1,   # top-left
   1:0,   # top-left
   2:5,   # top-center
   3:2,   # top-center
   4:6,   # top-center
   5:3,   # top-right
   6:4,   # top-right
   7:10,  # center-right
   8:16,  # center-right
   9:22, # center-right
  10:24,  # center-right
  11:31, # center-right
  12:14, # center-right
  13:30, # center-right
  14:35, # center-right
  15:7,  # center-right
  16:18, # or [27] center-left
  17:25, # center-left
  18:15, # center-left
  19:26, # center-left
  20:13, # center-left
  21:36, # center-left
  22:37, # center-left
  23:38, # center-left
  24:46,  # bottom-center
  25:45,  # bottom-center
  26:44,  # (bottom-center)
  27:43,  # (bottom-left block)
  28:42,  # (bottom-left block)
  29:49,  # (bottom-left block)
  30:51,  # (bottom-center)
  31:53,  # or [54] (bottom-center)
  32:54,  # or [53] (bottom-center)
  33:52,  # (bottom-center
  34:48,  # (bottom-right block)
  35:50,  # (bottom-right block)
  36:19,  # center-center
  37:23,  # center-center
  38:20,  # center-center
  39:21,  # center-center
  40:11,  # center-center
  41:8,   # center-center
  42:17,  # center-center
  43:9,   # center-center
  44:12,  # center-center
  45:33,  # arriba palito q
  46:41,  # palito de Q
  47:40,  # (al lado palito q)
  48:39,  # (al lado palito q)
  49:32,  # arriba palito q
  50:28,  # arriba palito q
  51:27,  # or [18] center-left
  52:34,  # center-left
  53:47,  # (bottom-right block)
  54:29,  # arriba palito q
}


class Parser:
    def __init__(self, output_fd):
        self._output_fd = output_fd

    def run(self):
        """Execute the conversor."""
        self._output_fd.write("""
;=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-;
; Autogenerated - DO NOT MODIFY

bits    16
cpu     8086

;=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-;

""")
        ascii_val = 0x20
        for key, val in FONT.items():
            self.parse(key, val, ascii_val)
            ascii_val += 1

    def parse(self, key, val, ascii_val):
        mask = 0
        for idx, n in enumerate(val):
            if n == 1:
                # certain keys shouldn't be translated since they
                # were generated manually
                if key in DONT_TRANSLATE:
                    new_masks = idx
                else:
                    new_masks = BIT_TRANS[idx]
                mask |= pow(2, new_masks)
        # write it in 4 different words
        self._output_fd.write(';ASCII: {:#02x}\n'.format(ascii_val))
        self._output_fd.write('global table_{0}\ntable_{0}:\n        dw '.format(key))
        word = mask & 0xffff
        self._output_fd.write('{:#018b},'.format(word))
        word = (mask  >> 16) & 0xffff
        self._output_fd.write('{:#018b},'.format(word))
        word = (mask  >> 32) & 0xffff
        self._output_fd.write('{:#018b},'.format(word))
        word = (mask  >> 48) & 0xffff
        self._output_fd.write('{:#018b}\n'.format(word))

def parse_args():
    """Parse the arguments."""
    parser = argparse.ArgumentParser(
        description='Converts font.json to asm', epilog="""Example:

$ %(prog)s fonts.json -o table.asm
""")
    parser.add_argument('-o', '--output-file', metavar='<filename>',
            help='output file. Default: stdout')

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    if args.output_file is not None:
        with open(args.output_file, 'w+') as fd:
            Parser(fd).run()
    else:
        Parser(sys.stdout).run()

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-

import string
from itertools import groupby

# constants
LOWER = string.ascii_lowercase
DEBUG = False


# assumes s has no white spaces
def compress(string):
    ''' a simple prefix compression algorithm -- EXPAND'''

    compressed = ""

    if DEBUG:
        print('string recieved is', string)

    # group chars by their occurance
    count = groupby(string)
    result = [(key, sum(1 for _ in count)) for key, count in count]

    # concatonate key with its count
    for tup in result:
        key = tup[0]        # char
        value = tup[1]      # char count

        # check input validity
        if key not in LOWER:
            return 'Invalid: contains non-lowercase characters'

        # do not compress just 2 occurances of char
        if value > 2:
            compressed += str(value) + key
        else:
            compressed += key * value

    return compressed


def decompress(string):
    decompressed = ""

    i = 0
    while i < len(s):

        if string[i] in '3456789':
            decompressed += int(string[i]) * string[i + 1]
            # skip the next element bc we don't want to over count
            i += 2

        else:
            decompressed += string[i]
            i += 1

    return decompressed

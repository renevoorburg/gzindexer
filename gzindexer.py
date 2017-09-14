#!/usr/bin/env python

"""
gzindexer
Parses a gzip compressed file to output the byte locations ( {start_byte} {length} ) of the consecutive members.

Supply the file to be indexed as parameter:
$ python3 gzindexer.py infile.gz

This output can be used for quick random files access to specific members:
$ dd bs=1 skip={start_byte} count={length} if=infile.gz | gzip -dc

RV, 2017-09-14
"""

import sys
import gzip
import io
import os

gzip_magic = [b'\x1f', b'\x8b', b'\x08']

magic_window = []
matches = []

try:
    filename = sys.argv[1]
except IndexError:
    print("Please supply a filename.\n")
    exit(1)

if not os.path.isfile(filename):
    print("File {} not found.\n". format(filename))
    exit(1)

if not os.access(filename, os.R_OK):
    print("Cannot read file {} .\n". format(filename))
    exit(1)

bytes_read = 0
with open(filename, "rb") as f:
    ''' try to find gzip_mapic matches: '''
    byte = f.read(1)
    while byte:
        magic_window.append(byte)
        if len(magic_window) == 3:
            if magic_window == gzip_magic:
                matches.append(bytes_read-2)
            magic_window.pop(0)
        byte = f.read(1)
        bytes_read += 1
    matches.append(bytes_read)

    '''validate & print correct matches:'''
    print('# {}: [start] [bytes]'.format(filename))
    start_m_index = 0
    while start_m_index < len(matches) - 1:
        gzip_found = False
        end_m_index = start_m_index + 1
        while not (gzip_found or end_m_index >= len(matches)):
            start_byte = matches[start_m_index]
            num_bytes = matches[end_m_index] - start_byte
            f.seek(start_byte)
            data = f.read(num_bytes)
            try:
                gzip.open(io.BytesIO(data), 'rb').read()
                gzip_found = True
                start_m_index = end_m_index
                print("{} {}".format(start_byte, num_bytes))
            except:
                end_m_index += 1
        if not gzip_found:
            start_m_index += 1

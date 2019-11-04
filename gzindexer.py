#!/usr/bin/env python

"""
gzindexer
Parses a gzip compressed file to output the byte locations ( {start_byte} {length} ) of the consecutive members.

Supply the file to be indexed as parameter:
usage: python3 gzindexer.py [-h] [-x XPATH] filename

optional arguments:
  -h, --help  show help message and exit
  -x XPATH    add result of given XPATH expression to the index

The output can be used for quick random files access to specific members:
$ dd bs=1 skip={start_byte} count={length} if=infile.gz | gzip -dce

RV, 2019-11-03
"""

from __future__ import print_function
import gzip
import io
import os
import argparse
from lxml import etree

gzip_magic = [b'\x1f', b'\x8b', b'\x08']

magic_window = []
matches = []

xmlparser = etree.XMLParser(recover=True)

parser = argparse.ArgumentParser(description='Creates an index for quick access to concatenated gzip files.')
parser.add_argument('-x', action="store", dest="xpath", help="add result of given XPATH expression to index")
parser.add_argument('filename', action="store")
options = parser.parse_args()

if not os.path.isfile(options.filename):
    print("File {} not found.\n". format(options.filename))
    exit(1)

if not os.access(options.filename, os.R_OK):
    print("Cannot read file {} .\n". format(options.filename))
    exit(1)

bytes_read = 0
with open(options.filename, "rb") as f:
    """ try to find gzip_magic matches: """
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

print('# {}: [start] [bytes]'.format(options.filename), end='')
if options.xpath is not None:
    print(" [{}]".format(options.xpath), end='')
print()

""" validate & print correct matches: """
start_m_index = 0
f = open(options.filename, "rb")
while start_m_index < len(matches) - 1:
    gzip_found = False
    end_m_index = start_m_index + 1
    while not (gzip_found or end_m_index >= len(matches)):

        """ try to find a gzip segment at start_byte, length num_bytes """
        start_byte = matches[start_m_index]
        num_bytes = matches[end_m_index] - start_byte
        f.seek(start_byte)
        data = f.read(num_bytes)
        try:
            content = gzip.open(io.BytesIO(data), 'rb').read()
        except:
            end_m_index += 1
            continue
        gzip_found = True
        start_m_index = end_m_index
        print("{} {}".format(start_byte, num_bytes), end='')

        """ try to apply the xpath, if set """
        if options.xpath is not None:
            try:
                root = etree.fromstring(content, xmlparser)
                r = root.xpath(options.xpath)
                print(" {}".format(r), end='')
            except:
                pass

        print()
    if not gzip_found:
        start_m_index += 1

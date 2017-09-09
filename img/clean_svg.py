#!/usr/bin/python

from optparse import OptionParser

# parse command line arguments
usage = "usage: %prog [options] arg"
parser = OptionParser(usage)
parser.add_option("--n", type="int", dest="nn", default=1)
(options, args) = parser.parse_args()

if len(args) != 1:
    print "Please pass only one file!"

import xml.etree.ElementTree as ET

tree = ET.parse(args[0])
root = tree.getroot()
width=root.attrib['width']
height=root.attrib['height']
#del root.attrib['width']
#del root.attrib['height']

root.attrib['viewBox'] = '0 0 '+str(width)+' '+str(height)
root.attrib['preserveAspectRatio']="xMidYMid meet"
tree.write(args[0])

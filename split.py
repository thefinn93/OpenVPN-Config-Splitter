#!/usr/bin/env python3
# OpenVPN Inline Config Splitter
# Copyright (C) 2015  Finn Herzfeld

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

##################################################
# Janky Solutions' Standard Jankification Notice #
# You are hereby informed that this script janky #
# as all shit, and is deisgned explicitly to     #
# parse the files created by the pfSense OpenVPN #
# client export utility available in pfSense 2.2 #
# If you experience issues, fix them your own    #
# damn self and send a pull request.             #
##################################################
import sys
import os

## ghetto config. Should proly replace this with a proper config file eventually
config = {}
config['storage'] = "~/.config/vpn"
config['mkdir'] = True


def mkfilename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' ']).rstrip()


def parse(path, foldername=None):
    lines = open(path).read().split("\n")
    outconfig = []
    current_inline = None
    inlines = {}
    key_direction = None
    for line in lines:
        line = line.strip()
        if len(line) > 0:
            if line[0] == "<":  # Beginning or end of an inline thing
                if current_inline is None:  # We're not in an inline block yet, so let's begin one
                    current_inline = line.strip()[1:-1]
                    inlines[current_inline] = []
                else:   # This is the end of an inline block, so nothing to do
                    current_inline = None
            else:
                if current_inline is None:
                    words = line.split(" ")
                    if foldername is None and len(words) > 1:
                        if words[0] in ["verify-x509-name"]:
                            foldername = mkfilename(words[1])
                    if words[0] == "key-direction":
                        key_direction = words[1]
                    else:
                        outconfig.append(line)
                else:
                    inlines[current_inline].append(line)

    storage = os.path.expanduser(config['storage'])
    if config['mkdir']:
        storage = os.path.join(storage, foldername)
        try:
            os.makedirs(storage)
        except FileExistsError:
            pass
    mainfile = os.path.join(storage, "%s.conf" % foldername)
    with open(mainfile, 'w') as f:
        for filename in inlines:
            if filename == "tls-auth" and key_direction is not None:
                outconfig.append("%s %s %s" % (filename, os.path.join(storage, filename),
                                               key_direction))
            else:
                outconfig.append("%s %s.pem" % (filename, os.path.join(storage, filename)))
        f.write("\n".join(outconfig))
        f.write("\n")
    for filename in inlines:
        with open("%s.pem" % os.path.join(storage, filename), 'w') as f:
            f.write("\n".join(inlines[filename]))
            f.write("\n")
    print("Go ahead and import %s into your network manager" % mainfile)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = None
        if len(sys.argv) > 2:
            name = sys.argv[2]
        parse(sys.argv[1], name)

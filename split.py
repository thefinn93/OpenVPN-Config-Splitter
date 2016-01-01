#!/usr/bin/env python3
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
            outconfig.append("%s %s" % (filename, os.path.join(storage, filename)))
        f.write("\n".join(outconfig))
    for filename in inlines:
        with open(os.path.join(storage, filename), 'w') as f:
            f.write("\n".join(inlines[filename]))
    print("Go ahead and import %s into your network manager" % mainfile)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = None
        if len(sys.argv) > 2:
            name = sys.argv[2]
        parse(sys.argv[1], name)
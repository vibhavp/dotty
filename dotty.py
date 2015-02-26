#!/bin/python3

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import json
import sys
import os

def main():
    try:
        js = json.load(open(sys.argv[1]))
    except Exception as e:
        print("Usage: dotty.py FILE", file=sys.stderr)
        exit(1)
        
    os.chdir(os.expanduser(os.path.dirname(sys.argv[1])))
    directories  = js.get("directories")
    links = js.get("links")
    commands = js.get("commands")
    # Check if directories exist.
    for path in directories:
        exp = os.path.expanduser(path)
        if (not os.path.isdir(exp)):
            print(exp+" doesnt exist, creating.")
            os.makedirs(exp)

    for src in links:
        dest = os.path.expanduser(links[src])
        src = os.path.abspath(src)
        print("Linking %s -> %s" % (dest, src))
        os.symlink(src, dest)

    for command in commands:
        os.system(command)

    print("Done!")

if __name__ == "__main__":
    main()

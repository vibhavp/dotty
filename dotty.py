#!/usr/bin/env python3
from __future__ import print_function

# Copyright (C) 2015 Vibhav Pant <vibhavp@gmail.com>
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
import os
import shutil
from sys import stderr
import argparse

# Fix Python 2.x.
try: input = raw_input
except NameError: pass

def ask_user(prompt):
    valid = {"yes":True, 'y':True, '':True, "no":False, 'n':False}
    while True:
        print("{0} ".format(prompt),end="")
        choice = input().lower()
        if choice in valid:
            return valid[choice]
        else:
            print("Enter a correct choice.", file=stderr)


def create_directory(path):
    exp = os.path.expanduser(path)
    if (not os.path.isdir(exp)):
        print("{0} doesnt exist, creating.".format(exp))
        os.makedirs(exp)


def create_symlink(src, dest, replace):
    dest = os.path.expanduser(dest)
    src = os.path.abspath(src)
    broken_symlink = os.path.lexists(dest) and not os.path.exists(dest)
    if os.path.lexists(dest):
        if os.path.islink(dest) and os.readlink(dest) == src:
            print("Skipping existing {0} -> {1}".format(dest, src))
            return
        elif replace or ask_user("{0} exists, delete it? [Y/n]".format(dest)):
            if os.path.isfile(dest) or broken_symlink or os.path.islink(dest):
                os.remove(dest)
            else:
                shutil.rmtree(dest)
        else:
            return
    print("Linking {0} -> {1}".format(dest, src))
    try:
        os.symlink(src, dest)
    except AttributeError:
        import ctypes
        symlink = ctypes.windll.kernel32.CreateSymbolicLinkW
        symlink.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        symlink.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(src) else 0
        symlink(dest, src, flags)


def copy_path(src, dest):
    dest = os.path.expanduser(dest)
    src = os.path.abspath(src)
    if os.path.exists(dest):
        if ask_user("{0} exists, delete it? [Y/n]".format(dest)):
            if os.path.isfile(dest) or os.path.islink(dest):
                os.remove(dest)
            else:
                shutil.rmtree(dest)
        else:
            return
    print("Copying {0} -> {1}".format(src, dest))
    if os.path.isfile(src):
        shutil.copy(src, dest)
    else:
        shutil.copytree(src, dest)


def run_command(command):
    os.system(command)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="the JSON file you want to use")
    parser.add_argument("-r", "--replace", action="store_true",
                        help="replace files/folders if they already exist")
    args = parser.parse_args()
    js = json.load(open(args.config))
    os.chdir(os.path.expanduser(os.path.abspath(os.path.dirname(args.config))))

    if 'directories' in js: [create_directory(path) for path in js['directories']]
    if 'link' in js: [create_symlink(src, dst, args.replace) for src, dst in js['link'].items()]
    if 'copy' in js: [copy_path(src, dst) for src, dst in js['copy'].items()]
    if 'install' in js and 'install_cmd' in js:
        packages = ' '.join(js['install'])
        run_command("{0} {1}".format(js['install_cmd'], packages))
    if 'commands' in js: [run_command(command) for command in js['commands']]
    print("Done!")

if __name__ == "__main__":
    main()

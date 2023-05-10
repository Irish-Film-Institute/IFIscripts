#!/usr/bin/env python3

import argparse
import os
import sys
import shutil


def set_options():
    parser = argparse.ArgumentParser(
        description='IFI Irish Film Institute accession shell creator.'
                    ' Written by Yazhou He.'
    )
    parser.add_argument(
        'input'
    )
    parser.add_argument(
        '-as11',
        action='store_true',
        help='AS-11 UK DPP requires requires files except .mxf (A&V) files in the objects folder kept.'
    )
    parser.add_argument(
        '-dcp',
        action='store_true',
        help='Digital Cinema Package (DCP) requires files except .mxf (A&V) files in the objects folder kept.'
    )
    parser.add_argument(
        '-o',
        help='Set output directory.', required=True
    )
    return parser.parse_args()


def main():
    args = set_options()
    input = args.input
    output = args.o
    if not os.path.exists(input):
        print("Input directory doesn't exist! Exit...")
        sys.exit()
    if not os.path.exists(output):
        print("Output directory doesn't exist! Exit...")
        sys.exit()
    for root, dirs, files in os.walk(input):
        aip = os.path.basename(root)
        if 'aaa' in aip:
            aip_full = root
            print("\nAIP has found: %s" % aip_full)
            aip_paste = aip + '_shell'
            aip_paste_full = os.path.join(output, aip_paste)
            try:
                os.mkdir(aip_paste_full)
                print("\nMaking %s in %s" % (aip_paste, aip_paste_full))
            except:
                print("%s already exists in the output directory" % aip_paste)
                sys.exit()
            for aroot, adirs, afiles in os.walk(aip_full):
                dir_path = aroot.replace(aip_full, "")
                dir_path = dir_path[1:]
                print("\nroot: %s\nsubfiles: %s\nsubfolders: %s" % (dir_path, afiles, adirs))
                if adirs:
                    print("\n---clone folders---")
                    for adir in adirs:
                        adir_full = os.path.join(aroot, adir)
                        adir_paste = os.path.join(aip_paste, dir_path, adir)
                        adir_paste_full = os.path.join(output, adir_paste)
                        print(adir_full + " ->")
                        os.mkdir(adir_paste_full)
                        print("-> " + adir_paste_full)
                if afiles:
                    print("\n---copy files---")
                    for afile in afiles:
                        afile_full = os.path.join(aroot, afile)
                        afile_paste_full = os.path.join(output, aip_paste, dir_path, afile)
                        if "objects" in afile_full:
                            if args.as11 or args.dcp:
                                if not afile_paste_full.endswith(".mxf"):
                                    shutil.copy(afile_full, afile_paste_full)
                                    print(afile_paste_full)
                                else:
                                    print("*Skip " + afile_full)
                            else:
                                print("*Skip objects/" + afile)
                        else:
                            shutil.copy(afile_full, afile_paste_full)
                            print(afile_paste_full)


if __name__ == "__main__":
    main()

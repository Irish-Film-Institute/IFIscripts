#!/usr/bin/env python3

import argparse
import os
import sys
import shutil
import subprocess


def set_options():
    parser = argparse.ArgumentParser(
        description='IFI Irish Film Institute accession ffmpeg metadata ingest running check.'
                    ' Written by Yazhou He.'
    )
    parser.add_argument(
        'input',
        help='Set the folder of one batch as the input directory'
    )
    return parser.parse_args()


def main():
    args = set_options()
    input = args.input
    if not os.path.exists(input):
        print("Input directory doesn't exist! Exit...")
        sys.exit()
    failed_list = []
    i = 1
    for root, dir, file in os.walk(input,topdown=True):
        basename = os.path.basename(root)
        if 'aaa' in basename:
            aip = root
            print("\nAIP found:\t%s" % aip)
            for aroot, adir, afile in os.walk(aip):
                if "objects" in aroot:
                    objects = aroot
                    print("objects/ found:\t%s" % objects)
                    media_list = os.listdir(objects)
                    for file in media_list:
                        obj = os.path.join(objects, file)
                        if obj.endswith(('.MP4', '.mp4', '.MOV', '.mov', '.mkv', '.mxf', '.MXF', '.WAV', '.wav', '.aiff', '.AIFF', 'mp3', 'MP3', 'm2t', 'MTS', '.dv', '.DV', '.iso', '.ISO')):
                            print("media found:\t%s" % obj)
                            ffprobe_cmd = ['ffprobe', obj]
                            try:
                                subprocess.check_output(ffprobe_cmd)
                                print("\n\nmedia passed ffprobe!\n\n")
                            except subprocess.CalledProcessError as e:
                                print(e)
                                print("\n\nmedia failed ffprobe!")
                                failed_list.append(obj)
                                print("failed_list:\n\t %s\n\n" % failed_list)
    if not failed_list:
        print("all objects in this batch passed ffprobe!")
    else:
        list_path = os.path.join(os.path.dirname(input), os.path.basename(input) + '_failed_list.txt')
        print("Export failed list to %s" % list_path)
        export = open(list_path, 'a', encoding='utf-8')
        for failed_item in failed_list:
            export.write(failed_item)
            print(failed_item)
        export.close()



if __name__ == "__main__":
    main()

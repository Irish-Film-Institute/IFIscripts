#!/usr/bin/env python3
'''
Allow sipcreator to batch process multiple folders in a directory
-dcp option is needed to process folders and grab html files
'''
import argparse
import os
import sys
import ififuncs
import sipcreator
from masscopy import analyze_log


def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Launches sipcreator.py on multiple objects.'
        'Wraps objects into an Irish Film Institute SIP'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-i',
        help='full path of input folder - this folder should contain subfolders which in turn contain video files', required=True
    )
    parser.add_argument(
        '-o', '-output',
        help='full path of output directory', required=True
    )
    parser.add_argument(
        '-rename_uuid', action='store_true',
        help='Use with caution! This will rename an object with a randonly generated UUID'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.'
    )
    parser.add_argument(
        '-l', action='store_true',
        help='invokes the -lto argument in copyit.py - uses gcp instead of rsync.'
    )
    parser.add_argument(
        '-sc', action='store_true',
        help='special collections workflow'
    )
    parser.add_argument(
        '-d', '-dcp', action='store_true',
        help='Adds DCP specific processing, like creating objects subfolder with text extracted from <ContentTitleText> in the CPL.'
    )
    parser.add_argument(
        '-zip', action='store_true',
        help='Uses makezip.py to store the objects in an uncompressed ZIP'
    )
    parser.add_argument(
        '-oe',
        help='Enter the Object Entry number for the representation.SIP will be placed in a folder with this name.'
    )
    parser.add_argument(
        '-supplement_extension_pattern', nargs='+',
        help='Enter the filename extensions, seperated by spaces, which determine which files to be added to the supplemental subfolder within the metadata directory. For example -supplement_extension_pattern xml pdf txt docx will take all filenames with these extensions within your input directory and store them in metadata/supplemental.  Use this for information that supplements your preservation objects but is not to be included in the objects folder.'
    )
    parser.add_argument(
        '-object_extension_pattern', nargs='+',
        help='Enter the filename extensions, seperated by spaces, which determine which files to be added to the objects directory. For example -object_extension_pattern mxf stl will take all filenames with these extensions within your input directory and store them in objects.'
    )
    parser.add_argument(
        '-y',
        action='store_true',
        help='Answers YES to the question: Do you want to proceed? useful for unattended batches but not recommended without running -dryrun first'
    )
    parser.add_argument(
        '-dryrun', action='store_true',
        help='The script will reveal which identifiers will be assigned but will not actually perform any actions.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def main(args_):
    ''''
    Launch all the functions for creating an IFI SIP.
    '''
    args = parse_args(args_)
    source_folder = args.i
    print(args)
    oe_dict = {}
    user = ififuncs.determine_user(args)
    if not args.sc:
        if args.oe:
            object_entry = args.oe
        else:
            object_entry = ififuncs.get_object_entry()
        oe_digits = int(object_entry.replace('oe', ''))
    else:
        object_entry = 'not_applicable'
        oe_digits = ''
    for folder in sorted(os.listdir(source_folder)):
        full_path = os.path.join(source_folder, folder)
        if os.path.isdir(full_path):
            try:
                folder_contents = os.listdir(full_path)
            except PermissionError:
                continue
            if not args.sc:
                object_entry_complete = 'oe' + str(oe_digits)
            else:
                object_entry_complete = folder
            inputs = []
            supplements = []
            for files in folder_contents:
                if args.object_extension_pattern:
                    if os.path.splitext(files)[1][1:].lower() in args.object_extension_pattern:
                        inputs.append(os.path.join(full_path, files))
                    if os.path.splitext(files)[1][1:].lower() in args.supplement_extension_pattern:
                        supplements.append(os.path.join(full_path, files))
                else:
                    inputs.append(os.path.join(full_path, files))
            if inputs:
                print(' - Object Entry: %s\n - Inputs: %s\n - Supplements: %s\n' % (object_entry_complete, inputs, supplements))
                oe_dict[object_entry_complete] = [inputs, supplements, full_path]
                if not args.sc:
                    oe_digits += 1
            else:
                print('Skipping %s as there are no files in this folder that match the -object_extension_pattern' % full_path)
    if args.dryrun:
        print('Exiting as you selected -dryrun')
        sys.exit()
    logs = []
    if args.y:
        proceed = 'Y'
    else:
        proceed = ififuncs.ask_yes_no(
            'Do you want to proceed?'
        )
    if proceed == 'Y':
        for sips in sorted(oe_dict):
            sipcreator_cmd = ['-i',]
            for sipcreator_inputs in oe_dict[sips][0]:
                sipcreator_cmd.append(sipcreator_inputs)
            if oe_dict[sips][1] and not args.sc:
                sipcreator_cmd += ['-supplement']
                for sipcreator_supplements in oe_dict[sips][1]:
                    sipcreator_cmd.append(sipcreator_supplements)
            if not args.sc:
                sipcreator_cmd += ['-user', user, '-oe', sips, '-o', args.o]
            else:
                output = os.path.join(args.o, sips)
                sipcreator_cmd += ['-user', user, '-o', output, '-sc']
            if args.rename_uuid:
                sipcreator_cmd.append('-rename_uuid')
            if args.zip:
                sipcreator_cmd.append('-zip')
            if args.l:
                sipcreator_cmd.append('-l')
            print(sipcreator_cmd)
            sipcreator_log, _ = sipcreator.main(sipcreator_cmd)
            logs.append(sipcreator_log)
            for i in logs:
                if os.path.isfile(i):
                    print(("%-*s   : copyit job was a %s" % (50, os.path.basename(i), analyze_log(i))))

if __name__ == '__main__':
    main(sys.argv[1:])
    
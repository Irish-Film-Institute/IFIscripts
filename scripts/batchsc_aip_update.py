#!/usr/bin/env python

import sys
import os
import argparse
import shutil
import package_update
import rename_objects
import ififuncs

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Batch update Special Collections\' AIPs.'
        ' Written by Yazhou He.'
    )
    parser.add_argument(
        'input',
        help='full path of package'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.'
    )
    parser.add_argument(
        '-movetoobjects', action='store_true',
        help='Batch move subfiles to root of objects/ and update manifests.'
    )
    parser.add_argument(
        '-rename', action='store_true',
        help='Batch rename files in objects/ and update manifests.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def main(args_):
    args = parse_args(args_)
    if args.user:
        user = args.user
    else:
        user = ififuncs.get_user()
    source = args.input
    if args.movetoobjects:
        # get path for sips
        sips = os.listdir(source)
        for sip in sips:
            sip_path = os.path.join(source, sip)
            if os.path.isdir(sip_path):
                print('Found SIP\t%s' % sip_path)
                # get uuid/ for sip
                for dir in os.listdir(sip_path):
                    uuid = os.path.join(sip_path,dir)
                    if os.path.isdir(uuid):
                        uuid = os.path.join(sip, uuid)
                        print('Found UUID\t%s' % uuid)
                        # get objects/ for sip
                        objects = os.path.join(uuid, 'objects')
                        print('Found objects\t%s' % objects)
                        files_path=[]
                        dirs_path=[]
                        for root, dirs, files in os.walk(objects):
                            # get files in the subfolders
                            if 'objects' in root and not root.endswith('objects'):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    files_path.append(file_path)
                            # get 1st-level subfolders
                            if root.endswith('objects'):
                                for dir in dirs:
                                    dir_path = os.path.join(root, dir)
                                    dirs_path.append(dir_path)
                        if files_path:
                            print('Found files')
                            cmd=['-i']
                            for file_path in files_path:
                                cmd.append(file_path)
                            cmd += ['-new_folder', objects, '-user', user, '-aip', uuid]
                            print(cmd)
                            package_update.main(cmd)
                        else:
                            print('No subfiles need to be moved.')
                        if dirs_path:
                            print('Delete subfolders')
                            for dir in dirs_path:
                                shutil.rmtree(dir)
                        else:
                            print('No subfolders need to be deleted.')
                print()
    if args.rename:
        error_list = []
        oe_dirs = os.listdir(source)
        for oe_dir in oe_dirs:
            oe_paths = os.path.join(source, oe_dir)
            if os.path.isdir(oe_paths):
                cmd = ['-aip', '-user', user, oe_paths]
                print('rename_objects.py', cmd)
                try:
                    error = rename_objects.main(cmd)
                    if error:
                        error_list += error
                        print("\n\n---\nBelow paths have not completed updating manifest after renaming:")
                        for item in error_list:
                            print(item)
                        print("---\n\n")
                except:
                    error_list.append(oe_paths)
                    print("\n\n---\nBelow paths have not completed updating manifest after renaming:")
                    for item in error_list:
                        print(item)
                    print("---\n\n")
    if error_list:
        print("\n\n---\n(Final) Below paths have not completed updating manifest after renaming:")
        for item in error_list:
            print(item)

if __name__ == '__main__':
    main(sys.argv[1:])
    
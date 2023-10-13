#!/usr/bin/env python

import sys
import os
import argparse
import shutil
import package_update
import renamefiles
import ififuncs

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Batch update Special Collections\' titles.'
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
        # get path for titles
        titles = os.listdir(source)
        error_list = []
        for title in titles:
            aaa_path = os.path.join(source, title)
            if os.path.isdir(aaa_path):
                print('Found aip\t%s' % aaa_path)
                # get uuid/ for aip
                for dir in os.listdir(aaa_path):
                    aip_path = os.path.join(aaa_path,dir)
                    if os.path.isdir(aip_path):
                        # uuid = os.path.join(title, uuid)
                        print('Found UUID\t%s' % aip_path)
                        # get objects/ for aip
                        objects = os.path.join(aip_path, 'objects')
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
                            cmd += ['-new_folder', objects, '-user', user, '-aip', aip_path]
                            print(cmd)
                            error_path = package_update.main(cmd)
                            if error_path:
                                error_list.append(error_path)
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
                    error = renamefiles.main(cmd)
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
        print("\n\n---\n(Final) Below paths have not completed updating manifest:")
        for item in error_list:
            print(item)

if __name__ == '__main__':
    main(sys.argv[1:])
    
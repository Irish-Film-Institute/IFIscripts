#!/usr/bin/env python

import sys
import os
import shutil
import package_update
import ififuncs

def main():
    user = ififuncs.get_user()
    source = sys.argv[1]
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

if __name__ == '__main__':
    main()
    
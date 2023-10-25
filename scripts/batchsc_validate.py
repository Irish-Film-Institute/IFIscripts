#!/usr/bin/env python3

import os
import datetime
import tempfile
import subprocess
import shutil
from ififuncs import make_desktop_logs_dir

def get_raw_list(source):
    print('\n\n***Get RAW Packages***')
    roots = os.listdir(source)
    raw_list=[]
    for root in roots:
        path = os.path.join(source, root)
        if os.path.isdir(path):
            dirs = os.listdir(path)
            if not any(len(dir) == 36 for dir in dirs):
                print('Message:\t%s is a raw package.                                        ' % path, end='\r')
                raw_list.append(path)
            else:
                print('Message:\t%s includes UUID, should be an AIP (processed package).     ' % path, end='\r')
    print('Message:\tfound %s raw packages from the input directory.              ' % len(raw_list))
    return raw_list

def cleanup(pack_list):
    print('\n\n***Clean Up Bad Files***')
    if os.access(pack_list[0], os.W_OK):
        rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
        count = 0
        for pack in pack_list:
            for root, _, files in os.walk(pack):
                for file in files:
                    for item in rm_these:
                        if file == item:
                            path = os.path.join(root,file)
                            print('Action:\t\tremove %s.' % path)
                            os.remove(path)
                            count = count + 1
        print('Message:\tremoved - %s bad files from the input directory.' % count)
    else:
        print('Message:\tCannot remove bad files - no permission to write.')
    print('***END of Clean Up Bad Files***')

def batch_validate(pack_list, output):
    print('\n\n***Clean Up Bad Files in checksum manifests & Batch Validate Packages***')
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    validate_list=['All checksums have validated', 'All checksums have validated\n']
    validate_raw_list=[]
    desktop_logs_dir = make_desktop_logs_dir()
    logs_dir_subdir = datetime.datetime.now().strftime("%Y%m%d%H") + '_sc_validation'
    if not os.path.exists(logs_dir_subdir):
        os.makedirs(logs_dir_subdir)
    for pack in pack_list:
        validated_flag = True
        for root, _, files in os.walk(pack):
            for file in files:
                if file.endswith('_manifest.md5'):
                    manifest_path = os.path.join(root,file)
                    print('\nAction:\t\tclean up %s.' % manifest_path)
                    with open(manifest_path, 'r') as f1:
                        lines = f1.readlines()
                    with open(manifest_path, 'w') as f2:
                        for line in lines:
                            rm_flag = False
                            for item in rm_these:
                                if item in line:
                                    rm_flag = True
                                    break
                            if not rm_flag:
                                f2.write(line)
                        print('Action:\t\trun validate.py on %s.' % manifest_path)
                        temp_file = os.path.join(logs_dir_subdir,file + '_result.txt')
                        with open(temp_file, 'w') as f:
                            f.write(manifest_path + '\n')
                    subprocess.check_output(['validate.py', manifest_path, '-y', '>>', temp_file], shell=True)
                    print('Message:\tvalidation outputs exported to %s.' % temp_file)
                    with open(temp_file, 'r') as f3:
                        lines = f3.readlines()
                    sub_validated_flag = False
                    for item in validate_list:
                        if item in lines:
                            os.remove(temp_file)
                            print('Action:\t\tremove %s as it passed validation.' % temp_file)
                            sub_validated_flag = True
                    if not sub_validated_flag:
                        validated_flag = False
        if validated_flag:
            validate_raw_list.append(pack)
    print('Message:\tall failed validation outputs exported to %s.\n' % logs_dir_subdir)
    print('***END of Clean Up Bad Files in checksum manifests & Batch Validate Packages***')
    print('***Move Validated Packages***')
    validate_raw_list = list(set(validate_raw_list))
    for pack in validate_raw_list:
        shutil.move(pack,output)
        print('Action:\t\tmove %s to %s.' % (pack, output))
    print('***END of Move Validated Packages***')

def cleanup_log_md5(output):
    print('\n\n***Clean Up Logs and Manifests***')
    prelist = os.listdir(output)
    pack_list=[]
    for item in prelist:
        o_path = os.path.join(output,item)
        pack_list.append(o_path)
    if os.access(pack_list[0], os.W_OK):
        count = 0
        for pack in pack_list:
            for root, _, files in os.walk(pack):
                for file in files:
                    if file.endswith('_manifest.md5') or file.endswith('.log'):
                        path = os.path.join(root,file)
                        print('Action:\t\tremove %s.     ' % path, end='\r')
                        os.remove(path)
                        count = count + 1
        print('Message:\tremoved %s logs/manifests from the input directory.     \n' % count)
    else:
        print('Message:\tCannot remove files - no permission to write.     ')
    print('***END of Clean Up Logs and Manifests***')
    
def main():
    print('Procedures:')
    print('1. Get all RAW packages')
    print('2. Clean up bad files - .DS_Store, Thumbs.db, desktop.ini')
    print('3. Clean up bad files in checksum manifests & batch validate packages')
    print('4. Move validated packages to a separate folder')
    print('5. clean up the logs and manifests left in the validated packages')
    source = input('\nDrag/Input the directory including the RAW packages to be validated:\n')
    output = input('\nDrag/Input the directory for moving validated RAW packages to:\n')
    raw_list = get_raw_list(source)
    cleanup(raw_list)
    batch_validate(raw_list, output)
    cleanup_log_md5(output)
    return raw_list
    
if __name__ == '__main__':
    main()

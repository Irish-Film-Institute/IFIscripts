#!/usr/bin/env python3

import os
import datetime
import tempfile
import subprocess
import shutil

def get_raw_list(source):
    print('\n\n***Get RAW Packages***')
    roots = os.listdir(source)
    raw_list=[]
    for root in roots:
        path = os.path.join(source, root)
        if os.path.isdir(path):
            dirs = os.listdir(path)
            if not any(len(dir) == 36 for dir in dirs):
                print('Message:\t%s is a raw package.     ' % path, end='\r')
                raw_list.append(path)
            else:
                print('Message:\t%s includes UUID, should be a sipped directory.     ' % path, end='\r')
    print('Message:\tfound %s raw packages from the input directory.     \n' % len(raw_list))
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
                            print('Action:\t\tremove %s.     ' % path, end='\r')
                            os.remove(path)
                            count = count + 1
        print('Message:\tremoved - %s bad files from the input directory.     \n' % count)
    else:
        print('Message:\tCannot remove bad files - no permission to write.     ')

def batch_validate(pack_list, output):
    print('\n\n***Batch Validate Packages***')
    print('\n\n***Clean Up Bad Files\' checksums***')
    rm_these = ['.DS_Store', 'Thumbs.db', 'desktop.ini']
    validate_list=['All checksums have validated', 'All checksums have validated\n']
    validate_raw_list=[]
    temp_dir = os.path.join(tempfile.gettempdir(), 'sc_validate_' + datetime.datetime.now().strftime("%Y%m%d%H"))
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
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
                        temp_file = os.path.join(temp_dir,file + '_result.txt')
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
    print('Message:\tall failed validation outputs exported to %s.\n' % temp_dir)
    validate_raw_list = list(set(validate_raw_list))
    for pack in validate_raw_list:
        shutil.move(pack,output)
        print('Action:\t\tmove %s to %s.' % (pack, output))

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
    
def main():
    source = input('\nInput the directory including the RAW packages to be checked fixity:\n')
    output = input('\nInput the directory for validated RAW packages:\n')
    raw_list = get_raw_list(source)
    cleanup(raw_list)
    batch_validate(raw_list, output)
    cleanup_log_md5(output)
    return raw_list
    
if __name__ == '__main__':
    main()

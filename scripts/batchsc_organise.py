#!/usr/bin/env python3

import sys
import os
import shutil
import re

def rename_sub(packs):
    print('\n\n***Rename folders/files - replace all spaces and special characters to _***')
    triggers = [' ', '#', '%', '&', '\'', '*', '+', '/', ':', '?', '@', '<', '>', '|', '"', '©', '(', ')']
    answer = input('Rename RAW packages will have no record in the log file.\nInstead, process RAW packages then use \'batchsc_aip_update.py -rename\' to keep actions in the log.\nAre you sure you want to proceed?\nAnswer y/n\t->')
    if answer.lower() == 'y':
        for pack in packs:
            print('Renaming for %s' % pack)
            dir_list=[]
            for root, dirs, files in os.walk(pack):  
                for dir in dirs:
                    dir_list.append(os.path.join(root, dir))
            for n in range(len(dir_list)):
                flag = False
                dir_item = dir_list[n]
                dirname = os.path.basename(dir_item)
                dir_dir = os.path.dirname(dir_item)
                for trigger in triggers:
                    if trigger in dirname:
                        new_dirname = dirname.replace(trigger, '_')
                        os.rename(os.path.join(dir_dir,dirname),os.path.join(dir_dir,new_dirname))
                        flag = True
                        # print('Renamed %s to %s' % (os.path.join(dir_dir,dirname),os.path.join(dir_dir,new_dirname)))
                        # below is different from the loop for files
                        dir_list=[i.replace(dirname,new_dirname) if dirname in i else i for i in dir_list]
                        dirname = new_dirname
                if re.findall('__+', dirname):
                    new_dirname = re.sub('__+', '_', dirname)
                    os.rename(os.path.join(dir_dir,dirname),os.path.join(dir_dir,new_dirname))
                    flag = True
                    # print('Renamed %s to %s' % (os.path.join(dir_dir,dirname),os.path.join(dir_dir,new_dirname)))
                    dir_list=[i.replace(dirname,new_dirname) if dirname in i else i for i in dir_list]
                if flag:
                    now = os.path.join(dir_dir,new_dirname)
                    print('Renamed %s to %s' % (dir_item,now))
            print()
            for root, dirs, files in os.walk(pack):    
                for file in files:
                    flag = False
                    was = os.path.join(root, file)
                    title = os.path.splitext(file)[0]
                    extension = os.path.splitext(file)[1]
                    for trigger in triggers:
                        if trigger in title:
                            new_title = title.replace(trigger, '_')
                            new_file = new_title + extension
                            os.rename(os.path.join(root,file),os.path.join(root,new_file))
                            flag = True
                            # below is different from the loop for dirs
                            file = new_file
                            title = new_title
                    if re.findall('__+', file):
                        new_file = re.sub('__+', '_', file)
                        os.rename(os.path.join(root,file),os.path.join(root,new_file))
                        flag = True
                    if flag:
                        now = os.path.join(root,new_file)
                        print('Renamed %s to %s' % (was,now))
            print('---')

def rename_pack(packs):
    print('\n\n***Rename packages - replace spaces to _ and remove all special characters***')
    triggers = [',', '#', '%', '&', '\'', '*', '+', '/', ':', '?', '@', '<', '>', '|', '"', '©', '(', ')', '']
    for pack in packs:
        flag = False
        packname = os.path.basename(pack)
        pack_dir = os.path.dirname(pack)
        for trigger in triggers:
            if trigger in packname:
                new_packname = packname.replace(trigger, '')
                os.rename(os.path.join(pack_dir,packname),os.path.join(pack_dir,new_packname))
                flag = True
                # print('Renamed %s to %s' % (os.path.join(pack_dir,packname),os.path.join(pack_dir,new_packname)))
                packname = new_packname
        if re.findall(' ', packname):
            new_packname = re.sub(' ', '_', packname)
            os.rename(os.path.join(pack_dir,packname),os.path.join(pack_dir,new_packname))
            flag = True
            # print('Renamed %s to %s' % (os.path.join(pack_dir,packname),os.path.join(pack_dir,new_packname)))
        if re.findall('__+', packname):
            new_packname = re.sub('__+', '_', packname)
            os.rename(os.path.join(pack_dir,packname),os.path.join(pack_dir,new_packname))
            flag = True
            # print('Renamed %s to %s' % (os.path.join(pack_dir,packname),os.path.join(pack_dir,new_packname)))
        if not packname.islower():
            new_packname = packname.lower()
            os.rename(os.path.join(pack_dir,packname),os.path.join(pack_dir,new_packname))
            flag = True
        if flag:
            now = os.path.join(pack_dir,new_packname)
            print('Renamed %s to %s' % (pack,now))

def move_to_root(packs):
    print('\n\n***Move subfiles - move all files to the root of the packages***')
    for pack in packs:
        print('Moving for %s' % pack)
        m = 0
        last_dir=''
        for root, _, files in os.walk(pack):
            for file in files:
                file_path = os.path.join(root,file)
                str_dir = root.replace(pack, '')
                str_dir = str_dir.replace('\\', '', 1)
                str_dir = str_dir.replace('/', '', 1)
                str_dir = str_dir.replace('\\', '_')
                str_dir = str_dir.replace('/', '_')
                if str_dir != '':
                    if str_dir == last_dir:
                        new_file_path = os.path.join(pack, str(m) + '_' + file)
                    else:
                        m = m + 1
                        new_file_path = os.path.join(pack, str(m) + '_' + file)
                        last_dir = str_dir
                    shutil.move(file_path, new_file_path)
                    print('Moved %s to %s' % (file_path, new_file_path))
        print('---')

def delete_subfolders(packs):
    print('\n\n***Delete subfolders - Delete all subfolders in each packages***')
    answer = input('Make sure all subfolders are all empty and all subfiles are moved to the root by the function 3!\nAre you sure you want to proceed?\nAnswer y/n\t->')
    if answer.lower() == 'y':
        failed_list=[]
        for pack in packs:
            for root, dirs, _ in os.walk(pack):
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        shutil.rmtree(dir_path)
                        print('Deleted subfolder %s' % dir_path)
                    except:
                        failed_list.append(pack)
                        print('CANNOT delete subfolder %s' % dir_path)
        if failed_list:
            failed_list = set(failed_list)
            print('---\nFollowing packages have problems deleting subfolders and need to operate manually:')
            for item in failed_list:
                print('\n%s' % item)
    else:
        sys.exit()
      
def main():
    root = sys.argv[1]
    dirs = os.listdir(root)
    print('Packages found in the input directory:')
    packs=[]
    for dir in dirs:
        pack_path = os.path.join(root,dir)
        print('\t' + pack_path)
        packs.append(pack_path)
    if not packs:
        print('No package was found in the directory.\nCheck the input directory and run the script again.\nScript ends.')
        sys.exit()
    answer = input('Are you sure you want to proceed?\nAnswer y/n\t->')
    if answer.lower() == 'y':
        print()
        menu=[
            '1. (Use with caution) Rename folders/files - replace all spaces and special characters to _',
            '2. Rename packages - replace spaces to _ and remove all special characters',
            '3. Move subfiles - move all files to the root of the packages',
            '4. (Use only after 3.) Delete subfolders - Delete all subfolders in each packages'
        ]
        print(*menu, sep = '\n')
        func = '0'
        while int(func) < 1 or int(func) > 4:
            func = input('Which feature do you need?\t-> ')  
            if func == '1':
                rename_sub(packs)
            elif func == '2':
                rename_pack(packs)
            elif func == '3':
                move_to_root(packs)
            elif func == '4':
                delete_subfolders(packs)
    else:
        print('Check the input directory and run the script again.\nScript ends.')
        sys.exit()
    
if __name__ == '__main__':
    main()

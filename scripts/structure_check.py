#! /usr/bin/env python3

'''
This script is to check the structure of a batch of SIPs/AIPs(and AIP shells)
It will show the directory tree of each information package
Users are able to manually record if the structure is right or not 
The script will list a summary at the end
'''

import sys
import os
import argparse
import shutil

def parse_args(args_):
    parser = argparse.ArgumentParser(
        description='Directory tree of each information package in a batch.'
                    ' Written by Yazhou He.'
    )
    parser.add_argument(
        '-i',
        help='full path of a batch of SIPs/AIPs/AIP shells', required=True
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def tree1(object):
    os.system('tree ' + object)

def tree2(object):
    'quote from https://stackoverflow.com/a/9728478'
    for root, dirs, files in os.walk(object):
        level = root.replace(object, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))

def note():
    print('Check that there are a MD5 checksums manifest and a SHA-512 checksums manifest at the root of an AIP/AIP shell.\n'
          'Check that there are a MD5 checksums manifest at the root of a SIP.\n'
          'Check that there are logs, metadata, objects folders in the information package.'
        )
    
def show_dirtree(objects_list):
    fault_list=[]
    for object in objects_list:
        object_flag = False
        if 'oe' in object:
            object_flag = True
            print('\nSIP\t' + object)
        elif 'aaa' in object and object.endswith('_shell'):
            object_flag = True
            print('\nAIP shell\t' + object)
        elif 'aaa' in object:
            object_flag = True
            print('\nAIP\t' + object)
        if object_flag == True:
            if sys.platform == "win32":
                os.system('cls')
            else:
                os.system('clear')
            note()
            if shutil.which('tree'):
                tree1(object)
            else:
                tree2(object)
            mark = input('\n*Type anything and enter if it is a failure.\n*Press enter if it a pass.\n')
            if mark:
                fault_list.append(object)
    return fault_list

def main(args_):
    args = parse_args(args_)
    source = args.i
    dir_list = [os.path.join(source, dir) for dir in sorted(os.listdir(source))]
    fault_list = show_dirtree(dir_list)
    if fault_list:
        print('\n-----\nHere are the failed information packages you just marked out:')
        print(*fault_list, sep='\n')
    else:
        print('\n-----\nAll information packages have passed check!\n')


if __name__ == '__main__':
    main(sys.argv[1:])
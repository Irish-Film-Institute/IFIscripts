#!/usr/bin/env python3
'''
Get shells, proxies, and mezzanines from Rackstation by accession number.
'''
import argparse
import os
import sys
import platform
import shutil
import batchmakeshell
import csv

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Get shells, proxies, and mezzanines from Rackstation by accession number.'
        ' Written by Yazhou He.'
    )
    parser.add_argument(
        '-t', '-type',
        help='type of required DIP: shell, proxy, mezz', required=True
    )
    parser.add_argument(
        '-n', '-number', nargs='+',
        help='required accession numbers, can be more than one'
    )
    parser.add_argument(
        '-csv', help='csv file including the accession numbers with title row \'accession number\''
    )
    parser.add_argument(
        '-i', '-input',
        help='path of the [ROOT] of rackstation drive including shell/proxy/mezz', required=True
    )
    parser.add_argument(
        '-o', '-output',
        help='full path of output directory'
    )
    parser.add_argument(
        '-justcheck', action='store_true',
        help='check existance only instead of copying'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def check_input(type, source):
    # get type and directory name
    if type == 'shell':
        keyword_a = 'Documentation'
        keyword_b = 'accessioned_shells'
    elif type == 'proxy':
        keyword_a = 'Browse_Store'
        keyword_b = 'clean_proxies'
    elif type == 'mezz':
        keyword_a = 'FCP_Edit'
        keyword_b = 'mezzanines_from_accessions'
    else:
        print('*****Wrong type! The value should be \'shell\', \'proxy\', or \'mezz\'.')
        sys.exit()
    # get input of the type
    type_input=''
    for root, dirs, files, in os.walk(source):
        if root.endswith(keyword_a) and keyword_b in dirs and platform.system() == 'Darwin':
            type_input = os.path.join(source, keyword_b)
            print('Found directory for %s: %s' % (type, type_input))
            break
        elif keyword_b in dirs and platform.system() == 'Windows':
            type_input = os.path.join(source, keyword_b)
            print('Found directory for %s: %s' % (type, type_input))
            break
    if not type_input:
        print('CANNOT found directory for %s! Check input!' % type)
        sys.exit()
    return type_input

def get_fpaths(numbers, source):
    print('\n-----\nGetting path for DIP...')
    paths=[]
    fail_list=[]
    for number in sorted(numbers):
        get_flag = False
        for root, dirs, files in os.walk(source):
            for file in files:
                print(file, end='\r')
                if file.startswith(number):
                    path = os.path.join(root,file)
                    paths.append(path)
                    get_flag = True
                    print('\tFound DIP for %s: %s' % (number, path))
                    break
        if not get_flag:
            print('*CANNOT found DIP for %s!' % number)
            fail_list.append(number)
    return paths, fail_list

def get_dpaths(numbers, source):
    print('\n-----\nGetting path for DIP...')
    paths=[]
    fail_list=[]
    for number in sorted(numbers):
        get_flag = False
        sub_source = os.listdir(source)
        for sub in sub_source:
            sub = os.path.join(source, sub)
            if os.path.isdir(sub):
                dirs = os.listdir(sub)
                for dir in dirs:
                    print(dir, end='\r')
                    if dir.endswith(number + '_shell'):
                        path = os.path.join(sub,dir)
                        paths.append(path)
                        get_flag = True
                        print('\tFound DIP for %s: %s' % (number, path))
                        break
        if not get_flag:
            print('*CANNOT found DIP for %s!' % number)
            fail_list.append(number)
    return paths, fail_list

def main(args_):
    args = parse_args(args_)
    type = args.t
    source = args.i
    if args.n:
        accession_numbers = args.n
    elif args.csv:
        csvfile = args.csv
        accession_numbers = []
        title_dict = {}
        with open(csvfile, 'r', encoding='utf-8') as f1:
            reader = csv.reader(f1)
            titles = next(reader)
            for idx, title in enumerate(titles):
                title_dict[title] = idx
            index = title_dict['accession number']
            for row in reader:
                accession_numbers.append(row[index])
    print(sorted(accession_numbers))
    type_source = check_input(type, source)
    if type == 'shell':
        paths, fail_list = get_dpaths(accession_numbers, type_source)
    else:
        paths, fail_list = get_fpaths(accession_numbers, type_source)
    destination = args.o
    if not args.justcheck:
        # copy from path of each file to destination
        print('\n-----\nCopying DIP to \'%s\'...' % destination)
        if type == 'shell':
            for path in paths:
                cmd = [path, '-o', destination, '-copyshell']
                sys.stdout = open(os.devnull, 'w')
                try:
                    batchmakeshell.main(cmd)
                    sys.stdout = sys.__stdout__
                    print('\n\t%s has copied to the destination\n' % path)
                except:
                    print('*CANNOT copy %s!' % path)
        else:
            for path in paths:
                shutil.copy(path, destination)
                print('\n\t%s has copied to the destination\n' % path)
    # print accesion number failed getting path
    if fail_list:
        print('\n-----\nCANNOT get DIP by below accession number:')
        for fail_aip in fail_list:
            print('\t' + fail_aip)
    else:
        print('\n-----\nAll DIPs have been found (and copied if required).')

if __name__ == '__main__':
    main(sys.argv[1:])

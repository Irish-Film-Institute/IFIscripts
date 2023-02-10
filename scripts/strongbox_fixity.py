#!/usr/bin/env python3
'''
Analyses the CSV file reports from Strongbox.
Accepts an identifier input, at least the package ID but
the UUID would also be useful.
The script then finds the relevant entries, harvests the checksums and
stores them as a regular manifest.
It would make sense to also accept an existing sha512 manifest as an argparse
so that the script can tell if they are identical.

'''
import os
import sys
import collections
import argparse
import unicodedata
import ififuncs

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Analyses the CSV file reports from Strongbox.'
        'Prints the output to the terminal if the -manifest option is not used'
        'if the -manifest option is used, just the differences, if any, will appear on screen'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-csv', help='Path to the strongbox CSV file.'
    )
    parser.add_argument(
        '-i',
        help='Path of the parent folder containing the accessioned packages'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def diff_manifests(manifest, strongbox_list):
    '''
    Compare the list of strongbox hashes to the original AIP manifest.
    '''
    print('\nStrongbox_fixity - IFIscripts')
    print('Analysing %s\n' % manifest)
    # 
    error_type = 0
    white_list = ['manifest-sha512.txt', 'manifest.md5']
    with open(manifest, 'r', encoding='utf-8') as original_manifest:
        aip_manifest = original_manifest.read().splitlines()
    # A list of items in strongbox, that are different in aip sha512 manifest
    strongbox_check = [item for item in strongbox_list if item not in aip_manifest]
    # A list of manifest-sha512.txt and manifest.md5 in strongbox, that are exception for diff
    strongbox_except = list(filter(lambda file: any([item in file for item in white_list]), strongbox_check))
    # A list of remaning items in the strongbox_check, that are the items need to be diff'ed
    strongbox_remain = list(set(strongbox_check).difference(set(strongbox_except)))
    new_manifest = []
    # A list of items in the AIP manifest, that are different in the strongbox manifest
    aip_check =  [item for item in aip_manifest if item not in strongbox_list]
    # check if the files are actually on the strongbox
    if len(strongbox_list) == 0:
        print('ERROR ***************************************')
        print('ERROR ***************************************The files are not on strongbox!!')
        error_type = 1
    # checks if everything in the strongbox list is in the aip manifest.
    elif len(strongbox_check) == 2 and len(strongbox_except) == 2 and len(strongbox_remain) == 0:
        print('All files in the strongbox manifest are present in your AIP manifest and the hashes validate')
    else:
        for i in strongbox_check:

            print('%s is in the strongbox but NOT in the AIP manifest' % i)
        error_type = 1
    if len(aip_check) == 0:
        print('All files in the AIP manifest are present in your strongbox manifest and the hashes validate')
    else:
        for i in strongbox_check:
            print('%s is in the AIP manifest but NOT in the Strongbox manifest' % i)
        error_type = 1
    print('\nAnalysis complete\n')
    return error_type

def get_checksums(csv_file):
    csv_dict = ififuncs.extract_metadata(csv_file)
    return csv_dict

def find_checksums(csv_dict, identifier):
    '''
    Finds the relevant entries in the CSV and prints to terminal
    '''
    manifest_lines = []
    for items in csv_dict:
        for x in items:
            if type(x) in [collections.OrderedDict, dict]:
                if identifier in x['path']:
                    identifier_string = "/%s/" % identifier
                    manifest_line = x['hash_code'] + '  ' + x['path'].replace(identifier_string, '')
                    manifest_lines.append(manifest_line)
    strongbox_list = sorted(manifest_lines, key=lambda x: (x[130:]))
    return strongbox_list

def find_manifest(source):
    '''
    Recursively search through a package for a sha512 package.
    '''
    for root, dirnames, filenames in os.walk(source):
        for files in filenames:
            if files.endswith('_manifest-sha512.txt'):
                return os.path.join(root, files)

def main(args_):
    args = parse_args(args_)
    csv_file = args.csv
    source = args.i
    csv_dict = get_checksums(csv_file)
    error_list = []
    package_list = sorted(os.listdir(source))
    for package in package_list:
        full_path = os.path.join(source, package)
        if os.path.isdir(full_path):
            basename = os.path.basename(package)
            if package[:3] == 'aaa':
                strongbox_list = find_checksums(csv_dict, package)
                manifest = find_manifest(full_path)
                error_type = diff_manifests(manifest, strongbox_list) # manifest needs to be declared here
                if error_type != 0:
                    error_list.append(package)
                '''
                for i in strongbox_list:
                    print i
                '''
    if error_list:
        print("-----\nStrongbox Fixity Summary:\n Above AIP(s) returns exceptions. Check the details above.")
        for item in error_list:
            print(" " + item)
if __name__ == '__main__':
    main(sys.argv[1:])

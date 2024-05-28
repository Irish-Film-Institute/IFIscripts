#!/usr/bin/env python3

'''
Analyses the CSV file reports from StorCycle.
'''

import os
import sys
import time
import collections
import argparse
import unicodedata
import ififuncs

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Analyses the CSV file reports from StorCycle.'
        ' StorCycle CSV report can be found in Reports -> File Listings.'
        ' Click \'Details\' icon in a job and click \'SAVE AS CSV\' at the bottom.'
        ' Written by Yazhou He.'
    )
    parser.add_argument(
        '-csv', help='Path to the storcycle CSV file.'
    )
    parser.add_argument(
        '-i',
        help='Path of the parent folder containing the AIPs.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def diff_manifests(manifest, storcycle_list, txt_name_source):
    '''
    Compare the list of storcycle hashes to the original AIP manifest.
    '''
    print('Analysing %s\n' % manifest)
    # Add error flag
    error_type = 0
    white_list = ['manifest-sha512.txt', 'manifest.md5']
    with open(manifest, 'r', encoding='utf-8') as original_manifest:
        aip_manifest = original_manifest.read().splitlines()
        ### checksum type not consisent, hold off for agreement
        aip_manifest_temp = []
        for line in aip_manifest:
            line = line[34:]
            aip_manifest_temp.append(line)
        # aip_manifest = original_manifest.read().splitlines()
        ### checksum type not consisent, hold off for agreement
    # A list of items through storcycle, that are different in local aip md5 manifest
    storcycle_check = [item for item in storcycle_list if item not in aip_manifest_temp]
    # A list of manifest.md5 and manifest.md5 through storcycle, that are exception for diff
    storcycle_except = list(filter(lambda file: any([item in file for item in white_list]), storcycle_check))
    # A list of remaning items through the storcycle, that are the items need to be diff'ed
    storcycle_remain = list(set(storcycle_check).difference(set(storcycle_except)))
    new_manifest = []
    # A list of items in the local AIP manifest, that are different from the storcycle list
    aip_check =  [item for item in aip_manifest_temp if item not in storcycle_list]
    # Remove md5 value
    for i in aip_check:
        j = aip_check.index(i)
        aip_check[j] = i[32:]
    intsec = list(set(storcycle_remain).intersection(set(aip_check)))
    if intsec != 0:
        print('ERROR for dev: strongbox system remain func return value: intsec\nintsec = list(set(storcycle_remain).intersection(set(aip_check)))')
        sys.exit()
    # Check if the files are stuck in the delayed action
    # Check if the files are actually in the storcycle
    if len(storcycle_list) == 0:
        print('ERROR *************************************** ERROR\nThe files are not in storcycle!!')
        ififuncs.generate_txt(
            '',
            txt_name_source,
            'Target AIP fixity = FAIL - items are NOT in the storcycle')
        error_type = 1
    # Check if everything in the storcycle list is in the local aip manifest.
    elif len(storcycle_check) == 2 and len(storcycle_except) == 2 and len(storcycle_remain) == 0:
        print('All files in the storcycle manifest are present in your local AIP manifest') # and the hashes validate')
        ififuncs.generate_txt(
            '',
            txt_name_source,
            'Target AIP fixity = PASS - All files in the storcycle manifest are present in your local AIP manifest') # and the hashes validate')
    else:
        for i in storcycle_remain:
            print('%s is in the storcycle but NOT in the local AIP manifest' % i)
            ififuncs.generate_txt(
            '',
            txt_name_source,
            'Target AIP fixity = FAIL - %s is in the storcycle but NOT in the local AIP manifest' % i)
        error_type = 1
    # Check if everything in the local aip manifest list is through the storcycle.
    if len(aip_check) == 0:
        print('All files in the local AIP manifest are present in your storcycle csv') # and the hashes validate')
        ififuncs.generate_txt(
            '',
            txt_name_source,
            'Target AIP fixity = PASS - All files in the local AIP manifest are present in your storcycle csv') # and the hashes validate')
    else:
        for i in aip_check:
            print('%s is in the local AIP manifest but NOT in the storcycle csv' % i)
            ififuncs.generate_txt(
                '',
                txt_name_source,
                'Target AIP fixity = FAIL - %s is in the local AIP manifest but NOT in the storcycle csv' % i)
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
                if identifier in x['Path'] and x['Directory'] == 'false':
                    identifier_string = "\\%s\\" % identifier
                    ### checksum type not consisent, hold off for agreement
                    manifest_line = x['Path'].split(identifier_string)[1].replace('\\', '/')
                    # manifest_line = x['Checksum'].split('.')[1] + '  ' + x['Path'].split(identifier_string)[1].replace('\\', '/')
                    ### checksum type not consisent, hold off for agreement
                    manifest_lines.append(manifest_line)
    storcycle_list = sorted(manifest_lines, key=lambda x: (x[34:]))
    return storcycle_list

def find_manifest(source):
    '''
    Recursively search through a package for a md5 package.
    '''
    for root, dirnames, filenames in os.walk(source):
        for files in filenames:
            if files.endswith('_manifest.md5') and root == source:
                return os.path.join(root, files)

def main(args_):
    args = parse_args(args_)
    csv_file = args.csv
    source = args.i
    csv_dict = get_checksums(csv_file)
    error_list = []
    package_list = sorted(os.listdir(source))
    # Create storcycle fixity report in non-PREMIS format
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    txt_name_filename = (os.path.basename(sys.argv[0]).split(".")[0]) + time.strftime("_%Y_%m_%dT%H_%M_%S")
    txt_name_source = "%s/%s.txt" % (desktop_logs_dir, txt_name_filename)
    ififuncs.generate_txt('',txt_name_source, 'Target Directory: %s' % source)
    for package in package_list:
        print('\nStorCycle fixity check for ' + package)
        full_path = os.path.join(source, package)
        if os.path.isdir(full_path):
            if package[:3] == 'aaa':
                ififuncs.generate_txt('',txt_name_source, 'Target AIP = %s' % os.path.basename(full_path))
                storcycle_list = find_checksums(csv_dict, package)
                manifest = find_manifest(full_path)
                error_type = diff_manifests(manifest, storcycle_list, txt_name_source) # manifest needs to be declared here
                if error_type != 0:
                    error_list.append(package)
                '''
                for i in storcycle_list:
                    print i
                '''
    ififuncs.generate_txt(
            '',
            txt_name_source,
            '----\nFinal Results:'
        )
    if error_list:
        print("-----\nstorcycle Fixity Summary:\n Below AIP(s) returns exceptions. Check the details above or in the %s.txt in Desktop/ifiscripts_log folder." % txt_name_filename)
        ififuncs.generate_txt('',txt_name_source, 'FIXITY FAILED AIPS = %s' % error_list)
        for item in error_list:
            print(" " + item)
    else:
        print("-----\nAll objects in the input directory have passed the fixity check!")
        ififuncs.generate_txt('',txt_name_source, 'ALL AIPS PASS FIXITY')

if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/env python3

import sys
import argparse
import csv
import time
import os
import ififuncs
from operator import itemgetter

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Merge helper accessions registers and sorted by object entry numbers.'
        ' Merged register will be stored in the Desktop/ifiscripts_log.'
        ' Written by Yazhou He.'
    )
    parser.add_argument(
        'input', nargs='+'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def nameit():
    proceed = 'n'
    while proceed.lower() == 'n':
        name_list = ['filmo_csv_merged',
                    'pbcore_merged',
                    'sorted_merged',
                    'helper_register_merged',]
        print('\n\nSelect the index of the name you want to use.\nType in the name if not in the list:\n')
        i = 1
        for item in name_list:
            print('\t' + str(i) + '. ' + item)
            i = i + 1
        print()
        user_input = input()
        try:
            index = int(user_input)-1
            name = name_list[index]
            print('\nName selected: ' + name_list[index])
        except ValueError:
            name = user_input
            print('\nName typed: ' + user_input)
        csv_name = time.strftime("%Y-%m-%dT%H_%M_%S_") + name + '.csv'
        proceed = ififuncs.ask_yes_no('Are you really sure? - The name will be:\n ' + csv_name)
    return csv_name

def sortit(title_list):
    title = ''
    if title not in title_list:
        print('\n\nSelect the index of the title in csv you want to sort by.')
        i = 1
        for item in title_list:
            print('\t' + str(i) + '. ' + item)
            i = i + 1
        i = int(input('\n'))
        while i > len(title_list) or i < 1:
            print('\n\nSelect the index of the title in csv you want to sort by.')
            i = 1
            for item in title_list:
                print('\t' + str(i) + '. ' + item)
                i = i + 1
            i = int(input('\n'))
    title = title_list[i-1]
    print('\nTitle selected: ' + title)
    return title

def main(args_):
    '''
    Launches functions that will merge and sort helper accessions registers
    '''
    args = parse_args(args_)
    csvs = args.input
    data = []
    fieldname = ififuncs.extract_metadata(csvs[0])[1]
    print('CSV Title:', end=' ')
    print(*fieldname, sep=' | ')
    for file in csvs:
        data.extend(ififuncs.extract_metadata(file)[0])
    title = sortit(fieldname)
    data.sort(key=itemgetter(title))
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    csv_name = nameit()
    new_csv = os.path.join(desktop_logs_dir, csv_name)
    with open(new_csv, 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldname)
        writer.writeheader()
        writer.writerows(data)
    print('\nYour merged CSV file is located here: %s' % new_csv)
    print('Comma/\',\' should be the only separator for this CSV. (Un-tick Semicolon/\';\' if it is selected.)')
    return new_csv

if __name__ == '__main__':
    main(sys.argv[1:])

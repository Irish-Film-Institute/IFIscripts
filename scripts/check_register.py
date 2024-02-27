#!/usr/bin/env python3

import csv
from collections import defaultdict
import operator
import argparse
import sys
import os
import get_ps_list

def parse_args(args_):
    parser = argparse.ArgumentParser(
        description='Check any mismatch on registers.'
                    ' Written by Yazhou He.'
    )
    parser.add_argument(
        '-preservation_storage_csv',
        help='(Optional) The correct mapping csv generated from get_ps_list.py. Script will get one if not.'
    )
    parser.add_argument(
        '-register_csv',
        help='The to-be-checked register csv, could be the digital accession register or the helper register.', required=True
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def get_mapping(csvfile):
    with open(csvfile, 'r', encoding='utf-8') as f1:
            reader1 = csv.DictReader(f1)
            mapping1 = defaultdict(list)
            mapping2 = defaultdict(list)
            for row in reader1:
                mapping1[row['accession number']] = row['object entry number']
                mapping2[row['object entry number']] = row['accession number']
            mapping1 = dict(sorted(mapping1.items(), key=operator.itemgetter(0)))
            mapping2 = dict(sorted(mapping2.items(), key=operator.itemgetter(0)))
    return mapping1, mapping2

def comparsion(mapping1, mapping3, preservation_storage_csv_title, register_csv_title):
    flag = True
    for key, values in mapping3.items():
        if len(values) > 1:
            print(f'In {register_csv_title}, accession number {key} maps to multiple object entry number: {values}')
            if key in mapping1:
                correct_value = mapping1[key]
                if correct_value in values:
                    print(f'\tThe correct object entry number from {preservation_storage_csv_title} is: {correct_value}\n')
                else:
                    print(f'\tThe correct object entry number from {preservation_storage_csv_title} is not present in {register_csv_title}\n')
            flag = False
        elif key in mapping1 and mapping1[key] != values[0]:
            print(f'Mismatch: accession number {key} maps to {mapping1[key]} in {preservation_storage_csv_title} but maps to {values[0]} in {register_csv_title}\n')
            flag = False
    return flag

def main(args_):
    args = parse_args(args_)
    preservation_storage_csv = args.preservation_storage_csv
    register_csv = args.register_csv

    while not preservation_storage_csv:
        try:
            ps_path = input('\nInput the path of preservation storage:\n\n')
            preservation_storage_csv = get_ps_list.main(['-i', ps_path])
        except:
            preservation_storage_csv = ''
            print('Cannot get list from input path.')

    mapping1, mapping2 = get_mapping(preservation_storage_csv)
    mapping3, mapping4 = get_mapping(register_csv)
    
    preservation_storage_csv_title = os.path.basename(preservation_storage_csv)
    register_csv_title = os.path.basename(register_csv)
    
    flag = True
    # primary key: accession number
    flag = comparsion(mapping1, mapping3, preservation_storage_csv_title, register_csv_title)
    # primary key: object entry number
    flag = comparsion(mapping2, mapping4, preservation_storage_csv_title, register_csv_title)

    if flag:
        print(f'All values are matched between {preservation_storage_csv_title} and {register_csv_title}')

if __name__ == '__main__':
    main(sys.argv[1:])

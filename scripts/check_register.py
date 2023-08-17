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
        help='the correct mapping csv'
    )
    parser.add_argument(
        '-register_csv',
        help='the to-be-checked csv', required=True
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def main(args_):
    args = parse_args(args_)
    file1 = args.preservation_storage_csv
    file2 = args.register_csv

    while not file1:
        try:
            ps_path = input('\nInput the path of preservation storage:\n\n')
            file1 = get_ps_list.main(['-i', ps_path])
        except:
            file1 = ''
            print('Cannot get list from input path.')

    with open(file1, 'r', encoding='utf-8') as f1:
        reader1 = csv.DictReader(f1)
        mapping1 = defaultdict(list)
        mapping2 = defaultdict(list)
        for row in reader1:
            mapping1[row['accession number']] = row['object entry number']
            mapping2[row['object entry number']] = row['accession number']
        mapping1 = dict(sorted(mapping1.items(), key=operator.itemgetter(0)))
        mapping2 = dict(sorted(mapping2.items(), key=operator.itemgetter(0)))
        
    
    with open(file2, 'r', encoding='utf-8') as f2:
        reader2 = csv.DictReader(f2)
        mapping3 = defaultdict(list)
        mapping4 = defaultdict(list)
        for row in reader2:
            mapping3[row['accession number']].append(row['object entry number'])
            mapping4[row['object entry number']].append(row['accession number'])
        mapping3 = dict(sorted(mapping3.items(), key=operator.itemgetter(0)))
        mapping4 = dict(sorted(mapping4.items(), key=operator.itemgetter(0)))
    
    csv1 = os.path.basename(file1)
    csv2 = os.path.basename(file2)
    
    flag = True
    # primary key: accession number
    for key, values in mapping3.items():
        if len(values) > 1:
            print(f'In {csv2}, accession number {key} maps to multiple object entry number: {values}')
            if key in mapping1:
                correct_value = mapping1[key]
                if correct_value in values:
                    print(f'\tThe correct object entry number from {csv1} is: {correct_value}\n')
                else:
                    print(f'\tThe correct object entry number from {csv1} is not present in {csv2}\n')
            flag = False
        elif key in mapping1 and mapping1[key] != values[0]:
            print(f'Mismatch: accession number {key} maps to {mapping1[key]} in {csv1} but maps to {values[0]} in {csv2}\n')
            flag = False

    # primary key: object entry number
    for key, values in mapping4.items():
        if len(values) > 1:
            print(f'In {csv2}, object entry number {key} maps to multiple accession number: {values}')
            if key in mapping2:
                correct_value = mapping2[key]
                if correct_value in values:
                    print(f'\tThe correct accession number from {csv1} is: {correct_value}\n')
                else:
                    print(f'\tThe correct accession number from {csv1} is not present in {csv2}\n')
            flag = False
        elif key in mapping2 and mapping2[key] != values[0]:
            print(f'Mismatch: object entry number {key} maps to {mapping2[key]} in {csv1} but maps to {values[0]} in {csv2}\n')
            flag = False

    if flag:
        print(f'All values are matched between {csv1} and {csv2}')

if __name__ == '__main__':
    main(sys.argv[1:])

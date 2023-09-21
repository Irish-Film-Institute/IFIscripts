#!/usr/bin/env python3

import sys
import argparse
import os
import time
import ififuncs
import csv

def parse_args(args_):
    parser = argparse.ArgumentParser(
        description='Get a CSV of AIPs in preservation storage with accession number and object entry number'
                    ' Written by Yazhou He.'
    )
    parser.add_argument(
        '-i',
        help='root path of preservation_storage', required=True
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def main(args_):
    args = parse_args(args_)
    package_list = os.listdir(args.i)
    data=[]
    for i in package_list:
        package = os.path.join(args.i, i)
        if os.path.isdir(package) and 'aaa' in package:
            results={}
            results['package'] = os.path.basename(package)
            uuid_path = sorted(os.listdir(package))
            for uuid_dir in uuid_path:
                if len(uuid_dir)==36 and not uuid_dir.endswith('.txt') and not uuid_dir.endswith('.md5'):
                    log_dir = os.path.join(package, uuid_dir, 'logs')
            logs = sorted(os.listdir(log_dir))
            for log in logs:
                if log.endswith('_seq2ffv1_log.log') or log.endswith('_sip_log.log'):
                    log_path = os.path.join(log_dir, log)
                    break
                else:
                    log_path=''
            if os.path.isfile(log_path):
                with open(log_path, 'r', encoding='utf-8') as log_object:
                    log_lines = log_object.readlines()
                    for lines in log_lines:
                        if 'eventIdentifierType=accession number,' in lines:
                            aaa = lines.split('=')[-1].replace('\n', '')
                            results['accession number'] = aaa
                        if 'eventIdentifierType=object entry,' in lines or 'eventIdentifierType=object entry number,' in lines:
                            oe = lines.split('=')[-1].replace('\n', '')
                            results['object entry number'] = oe
            data.append(results)
        print('AIP found (filename): %s\tOE number (log): %s\tAccession number (log): %s' % (os.path.basename(package), oe, aaa), end = '\r')

    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    csv_name = time.strftime("%Y-%m-%dT%H_%M_%S_") + 'oe_aaa_map_ps.csv'
    new_csv = os.path.join(desktop_logs_dir, csv_name)
    fieldname = ['package', 'accession number', 'object entry number']
    with open(new_csv, 'a', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldname)
        writer.writeheader()
        writer.writerows(data)
    print('\nYour package list from preservation storage is located here: %s' % new_csv)
    return new_csv

if __name__ == '__main__':
    main(sys.argv[1:])

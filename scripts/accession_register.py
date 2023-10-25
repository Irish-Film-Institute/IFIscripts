#!/usr/bin/env python3
'''
Generates a helper accessions register based on the metadata in other
spreadsheets.
'''
import sys
import argparse
import csv
import time
import os
import ififuncs

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Generates a helper accessions register.'
        ' Written by Kieran O\'Leary.'
    )
    parser.add_argument(
        '-sorted_csv', help='Path to sorted helper CSV'
    )
    parser.add_argument(
        '-pbcore_csv',
        help='Path to technical/PBCore CSV.'
    )
    parser.add_argument(
        '-filmo_csv',
        help='Path to Filmographic CSV. Must contain Filmographic URN.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args


def find_checksums(csv_file, identifier):
    '''
    Finds the relevant entries in the CSV and prints to terminal
    '''
    csv_dict = ififuncs.extract_metadata(csv_file)
    manifest_lines = []
    for items in csv_dict:
        for x in items:
            if type(x) is dict:
                if identifier in x['path']:
                    identifier_string = "/%s/" % identifier
                    manifest_line = x['hash_code'] + '  ' + x['path'].replace(identifier_string, '')
                    manifest_lines.append(manifest_line)
    strongbox_list = sorted(manifest_lines, key=lambda x: (x[130:]))
    return strongbox_list

def get_file_create_date(file):
    timestamp = os.path.getmtime(file)
    timestruct = time.localtime(timestamp)
    date = time.strftime('%Y-%m-%d', timestruct)
    return date

def main(args_):
    '''
    Launches functions that will generate a helper accessions register
    '''
    args = parse_args(args_)
    sorted_csv_dict = ififuncs.extract_metadata(args.sorted_csv)[0]
    pbcore_csv_dict = ififuncs.extract_metadata(args.pbcore_csv)[0]
    filmo_csv_dict = ififuncs.extract_metadata(args.filmo_csv)[0]
    for accession in sorted_csv_dict:
        accession_number = accession['accession number']
        accession['date accessioned'] = get_file_create_date(args.sorted_csv)
        if None in accession.keys():
            del accession[None]
        for technical_record in pbcore_csv_dict:
            if technical_record['Accession Number'] == accession_number:
                accession['acquisition method'] = technical_record['Type Of Deposit']
                accession['acquired from'] = technical_record['Donor']
                try:
                    accession['date acquired'] = time.strftime("%Y-%m-%d", time.strptime(technical_record['Date Of Donation'], "%d/%m/%Y"))
                except ValueError:
                    accession['date acquired'] = technical_record['Date Of Donation']
                for filmographic_record in filmo_csv_dict:
                    if filmographic_record['Filmographic URN'] == technical_record['Reference Number']:
                        if filmographic_record['Title/Name'] == '':
                            title = filmographic_record['Series Title'] + '; ' + filmographic_record['Episode No']
                        else:
                            title = filmographic_record['Title/Name']
                        simple = '%s (%s) | %s' % (title, filmographic_record['Year'], technical_record['dig_object_descrip'])
                        if accession['acquisition method'] == 'Reproduction':
                            simple += ' | Reproduction of %s' % technical_record['TTape Origin']
                        accession['simple name; basic description; identification; historical information'] = simple
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    new_csv_filename = time.strftime("%Y-%m-%dT%H_%M_%S_") + 'helper_register.csv'
    new_csv = os.path.join(desktop_logs_dir, new_csv_filename)
    with open(new_csv, 'w', encoding='utf-8') as csvfile:
            fieldnames = ififuncs.extract_metadata(args.sorted_csv)[1]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')
            writer.writeheader()
            for i in sorted_csv_dict:
                writer.writerow(i)
    print('\nYour helper CSV file is located here: %s' % new_csv)
    print('ATTENTION:')
    print('\tComma/\',\' should be the only separator when you open this CSV. (Un-tick Semicolon/\';\' if it is selected.)')
    print('\tIf the \'date acquired\' is unsure, fill in \'unknown\' in the field and do not leave it blank!')
    print('\tThe \'date accessioned\' should be the date you fill into DIGITAL ACCESION REGISTER. Change it if it\'s a different day!')
    print('\t\'acquired from\' should be \'body #number\', add correct #number into the field when you fill into DIGITAL ACCESION REGISTER!')
    print('\tMinimise the terms - ie, \'Deposit via overarching agreements\' -> \'Deposit\', \'Interop Digital Cinema Package\' -> \'Digital Cinema Package\'')
    return new_csv



if __name__ == '__main__':
    main(sys.argv[1:])

#!/usr/bin/env python3

import os
import argparse
import time
import shutil
import validate
import ififuncs

def parse_args():
    '''
    Parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Recursively launch validate.py for md5 manifests')
    parser.add_argument('input', help='full path to the parent folder including packages')
    parser.add_argument('-sip', help='only looks for manifests at the root of the SIP/AIP for whole package validation - $uuid_manifest.md5', action='store_true')
    parser.add_argument('-y', help ='invokes -y option in validate.py, answers Y to manifest issues', action='store_true')
    parsed_args = parser.parse_args()
    return parsed_args

def main():
    args = parse_args()
    sources = []
    results = []
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    txt_name_filename = "batchvalidate_report" + time.strftime("_%Y_%m_%dT%H_%M_%S")
    txt_name_source = "%s/%s.txt" % (desktop_logs_dir, txt_name_filename)
    ififuncs.generate_txt('', txt_name_source, 'batchvalidate.py report\n')
    if not args.sip:
        sources.append(args.input)
    else:
        dir_list = os.listdir(args.input)
        for dir in dir_list:
            sources.append(os.path.join(args.input, dir))
    for source in sources:
        for root, _, files in os.walk(source):
            error_counter = 0
            for file in files:
                if file.endswith('_manifest.md5'):
                    if  os.path.basename(root) != 'logs' and not args.sip:
                        manifest = os.path.join(root, file)
                        print(manifest)
                    elif root == source and args.sip:
                        manifest = os.path.join(root, file)
                        print(manifest)
                    else:
                        continue
                    if manifest:
                        if args.y:
                            error_counter = validate.main([manifest, '-y'])
                        else:
                            error_counter = validate.main([manifest])
                        if error_counter == 0:
                            print('Validation succeed.\n---\n')
                            results.append([manifest, 'success'])
                            ififuncs.generate_txt('', txt_name_source, 'SUCCESS - ' + manifest)
                        else:
                            print('Validation failed.\n---\n')
                            results.append([manifest, 'failure'])
                            ififuncs.generate_txt('', txt_name_source, 'FAILURE - ' + manifest)
    print('---\nValidation Summary:')
    for result in results:
        print(result)
    print('\n\nBatch validation outcome has been exported to ' + txt_name_source)
    if args.sip:
        shutil.copy(txt_name_source, source)
        print('and copied to ' + source)
    
if __name__ == '__main__':
    main()

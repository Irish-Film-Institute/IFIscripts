#!/usr/bin/env python
'''
Moves files into subfolders, updates logfiles and manifests.
'''
import os
import argparse
import sys
import datetime
import re
import ififuncs
import package_update

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Rename files in a SIP/AIP, updates logfiles and manifests.'
        ' Written by Yazhou He.'
    )
    parser.add_argument(
        'input',
        help='full path of Object Entry package'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.'
    )
    parser.add_argument(
        '-aip', action='store_true',
        help='Update sha512 manifest as well. (Defaultly only update md5 manifest as SIP mode).'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def main(args_):
    '''
    Launch all the functions for updating an IFI SIP/AIP.
    '''
    args = parse_args(args_)
    if args.user:
        user = args.user
    else:
        user = ififuncs.get_user()
    source = args.input
    sip_paths = []
    # modified ififuncs.check_for_sip for >1 sip_path in oe_path, return sip_paths[]
    for sip_dirs in os.listdir(source):
        if 'manifest.md5' in sip_dirs:
            oe_path = source
            uuid = sip_dirs.replace('_manifest.md5', '')
            sip_path = os.path.join(oe_path, uuid)
            if os.path.isdir(sip_path):
                sip_paths.append(sip_path)
    if not sip_paths:
        sip_paths[0] = source
        oe_path = os.path.dirname(source)
    start = datetime.datetime.now()
    print(args)
    error_list =[]
    for sip_path in sip_paths:
        ifchange_list = []
        uuid = os.path.basename(sip_path)
        new_log_textfile = os.path.join(sip_path, 'logs' + '/' + uuid + '_sip_log.log')
        sip_manifest = os.path.join(oe_path, uuid + '_manifest.md5')
        try:
            if args.aip:
                sip_manifest_sha512 = os.path.join(oe_path, uuid) + '_manifest-sha512.txt'
                ififuncs.generate_log(
                    new_log_textfile,
                    'EVENT = rename_objects.py started'
                )
                ififuncs.generate_log(
                    new_log_textfile,
                    'eventDetail=rename_objects.py %s' % ififuncs.get_script_version('rename_objects.py')
                )
                ififuncs.generate_log(
                    new_log_textfile,
                    'Command line arguments: %s' % args
                )
                ififuncs.generate_log(
                    new_log_textfile,
                    'EVENT = agentName=%s' % user
                )
                triggers = [',', '#', '%', '&', '\'', '*', '+', '/', ':', '?', '@', '<', '>', '|', '"', '©', '', '▒']
                for root, _, files in os.walk(sip_path):
                    for filename in files:
                        file = os.path.join(root, filename)
                        file_dir = root
                        flag = False
                        for trigger in triggers:
                            if trigger in os.path.splitext(filename)[0]:
                                new_filename = os.path.splitext(filename)[0].replace(trigger, '_') + os.path.splitext(filename)[1]
                                os.rename(os.path.join(file_dir,filename),os.path.join(file_dir,new_filename))
                                flag = True
                                filename = new_filename
                        if re.findall('__+', filename):
                            new_filename = re.sub('__+', '_', filename)
                            os.rename(os.path.join(file_dir,filename),os.path.join(file_dir,new_filename))
                            flag = True
                            filename = new_filename
                        if flag:
                            final_filename = os.path.join(file_dir,new_filename)
                            relative_filename = file.replace(source + '/', '').replace('\\', '/')
                            relative_filename = file.replace(source + '\\', '').replace('\\', '/')
                            relative_new_filename = final_filename.replace(source + '/', '').replace('\\', '/')
                            relative_new_filename = final_filename.replace(source + '\\', '').replace('\\', '/')
                            print('Renamed %s to %s' % (file,final_filename))
                            ififuncs.generate_log(
                                new_log_textfile,
                                'EVENT = eventType=filename change,'
                                ' eventOutcomeDetailNote=%s has been renamed to %s'
                                ' agentName=os.rename()'
                                % (file, final_filename)
                            )
                            ifchange_manifest = package_update.update_manifest(
                                sip_manifest,
                                relative_filename,
                                relative_new_filename,
                                new_log_textfile
                            )
                            ifchange_list.append(ifchange_manifest)
                            if args.aip:
                                ifchange_manifest_sha512 = package_update.update_manifest(
                                    sip_manifest_sha512,
                                    relative_filename,
                                    relative_new_filename,
                                    new_log_textfile
                                )
                                ifchange_list.append(ifchange_manifest_sha512)
                ififuncs.generate_log(
                    new_log_textfile,
                    'EVENT = rename_objects.py finished'
                )
                ifchange_log_manifest = ififuncs.checksum_replace(sip_manifest, new_log_textfile, 'md5')
                ifchange_list.append(ifchange_log_manifest)
                if args.aip:
                    ifchange_log_manifest_sha512 = ififuncs.checksum_replace(sip_manifest_sha512, new_log_textfile, 'sha512')
                    ifchange_list.append(ifchange_log_manifest_sha512)
                finish = datetime.datetime.now()
                print('\n- %s ran this script at %s and it finished at %s' % (user, start, finish))
        except:
            error_list.append(False)
        if False in ifchange_list:
            print('***%s has not completed updating manifest' % sip_path)
            error_list.append(sip_path)
    return error_list
        
if __name__ == '__main__':
    main(sys.argv[1:])


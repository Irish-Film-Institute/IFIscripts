#! /usr/bin/env python3

'''
This script is to check losslessness for a batch of sipped image sequence objects
It will check the losslessness from *IP/$uuid/logs/$uuid_sip_log.log
It will return the result of 'lossless' or 'lossy' for each information package
'''

import sys
import os
import argparse

def parse_args(args_):
    parser = argparse.ArgumentParser(
        description='Losslessness check for a batch of sipped image sequence objects (SIPs/AIPs/AIP shells).'
                    ' Written by Yazhou He.'
    )
    parser.add_argument(
        '-i',
        help='full path of a batch of SIPs/AIPs/AIP shells', required=True
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def find_packages(source):
	dir_list = sorted(os.listdir(source))
	package_list=[]
	for package in dir_list:
		p_type=''
		if package[:2] == 'oe':
			p_type = 'SIP'
			package_list.append(package)
		elif package[:3] == 'aaa' and package.endswith('_shell'):
			p_type = 'AIP shell'
			package_list.append(package)
		elif package[:3] == 'aaa':
			p_type = 'AIP'
			package_list.append(package)
		print("%s %s\tfound in the source directory" %(p_type,package))
	return package_list

def find_log_result(source, package_list):
	results={}
	for package in package_list:
		package_path = os.path.join(source, package)
		uuid_path = sorted(os.listdir(package_path))
		for uuid_dir in uuid_path:
			if len(uuid_dir)==36 and not uuid_dir.endswith('.txt') and not uuid_dir.endswith('.md5'):
				log_dir = os.path.join(package_path, uuid_dir, 'logs')
		logs = sorted(os.listdir(log_dir))
		for log in logs:
			if log.endswith('_seq2ffv1_log.log'):
				log_path = os.path.join(log_dir, log)
				break
			else:
				log_path=''
		if os.path.isfile(log_path):
			results[package] = 'ERROR - cannot find target in the log'
			with open(log_path, 'r', encoding='utf-8') as log_object:
				log_lines = log_object.readlines()
				for lines in log_lines:
					if 'eventOutcome=lossless' in lines:
						results[package] = 'lossless'
						break
					elif 'eventOutcome=lossy' in lines:
						results[package] = 'lossy'
						break
					else:
						results[package] = 'ERROR - cannot find target in the log'
		else:
			results[package] = 'ERROR - cannot find the log'
	return results

def main(args_):
	args = parse_args(args_)
	source = args.i
	package_list = find_packages(source)
	results = find_log_result(source, package_list)
	print()
	lossless_list=[]
	lossy_list=[]
	error_list=[]
	for key in results:
		print(key + ':\t' + results[key])
		if results[key] == 'lossless':
			lossless_list.append(key)
		elif results[key] == 'lossy':
			lossy_list.append(key)
		else:
			error_list.append(key)
	print()
	print('Lossless information packages:')
	print(*lossless_list, sep='\n')
	if not lossy_list and not error_list:
		print('---\nAll inforamtion packages are lossless!')
	else:
		print('---\nLossy information packages:')
		print(*lossy_list, sep='\n')
		print(*error_list, sep='*\tERROR - log check failed\n', end='*\tERROR - log check failed\n')


if __name__ == '__main__':
    main(sys.argv[1:])

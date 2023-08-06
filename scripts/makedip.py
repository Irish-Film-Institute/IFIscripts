#!/usr/bin/env python3
'''
Accept options from command line and make access copy.
Use makedip.py -h for help
'''

import argparse
import os
import bitc
import prores

def set_options():
    '''
    Parse command line options.
    '''
    parser = argparse.ArgumentParser(
        description='IFI Irish Film Institute batch h264/aac proxy creator. ProRes HQ optional.'
        ' Written by Kieran O\'Leary and Yazhou He.'
    )
    parser.add_argument(
        'input'
    )
    parser.add_argument(
        '-o',
        help='Set output directory.'
        'The default directory is the same directory as input.', required=True
    )
    parser.add_argument(
        '-prores',
        action='store_true',
        help='Use ProRes HQ instead of h264'
        'The default codec is h264'
    )
    parser.add_argument(
        '-wide',
        action='store_true', help='Adds 16:9 metadata flag'
    )
    parser.add_argument(
        '-bitc',
        action='store_true', help='Adds BITC and watermark'
    )
    parser.add_argument(
        '-dcp',
        action='store_true', help='Make h264 proxy for DCP (single reel only), which has 2 mxf inputs'
    )
    return parser.parse_args()

def get_packagename(args, full_path):
    if args.dcp:
        package_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(full_path)))))
    else: 
        package_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path))))
    return package_name

def rename_proxy(output, full_path, type, args):
    filename = os.path.basename(full_path)
    proxy_filename = os.path.join(output, filename + '_' + type + '.mov')
    package_name = get_packagename(args, full_path)
    if package_name.startswith('aaa') or package_name.startswith('oe'):
        os.rename(proxy_filename, os.path.join(output, package_name) + '_' + type + '.mov')
        print('The proxy has been made as ' + os.path.join(output, package_name) + '_' + type + '.mov')
    else:
        print('The proxy has been made as ' + proxy_filename)

def main():
    '''
    Launch the various functions that will make a h264/mp4 access copy.
    '''
    args = set_options()
    source = args.input
    for root, _, filenames in os.walk(source):
        if args.dcp:
            if sum([filename.count('.mxf') for filename in filenames]) == 2:
                dcp_i = [os.path.join(root, mxf) for mxf in filenames if mxf.endswith('mxf')]
                if not get_packagename(args, dcp_i[0]) in str(os.listdir(args.o)):
                    bitc_cmd = [dcp_i, '-o', args.o, '-dcp']
                    if not args.bitc:
                        bitc_cmd.extend(['-clean'])
                    bitc.main(bitc_cmd)
                    rename_proxy(args.o, dcp_i[0], 'h264', args)
                else:
                    print('Skipping %s as the proxy already exists ' % dcp_i[0] + os.path.join(args.o, get_packagename(args, dcp_i[0])) + '_h264.mov')
            elif sum([filename.count('.mxf') for filename in filenames]) > 2:
                print('Cannot make DIP for DCP multiple reels. Please do it manually.\n Command line: ffmpeg -i $v_mxf -i $a_mxf -c:a copy -c:v libx264 -pix_fmt yuv420p $output\n')
        else:
            for filename in filenames:
                full_path = os.path.join(root, filename)
                if full_path.endswith(('.mov', '.mkv', '.mxf', '.dv', '.m2t')):
                    if args.prores:
                        if not args.wide:
                            prores.main([full_path, '-o', args.o, '-hq'])
                        else:
                            prores.main([full_path, '-wide', '-o', args.o, '-hq'])
                        rename_proxy(args.o, full_path, 'prores', args)
                    else:
                        if not get_packagename(args, full_path) in str(os.listdir(args.o)):
                            bitc_cmd = [full_path, '-o', args.o]
                            if not args.bitc:
                                bitc_cmd.extend(['-clean'])
                            if args.wide:
                                bitc_cmd.extend(['-wide'])
                            bitc.main(bitc_cmd)
                            rename_proxy(args.o, full_path, 'h264', args)
                        else:
                            print('Skipping %s as the proxy already exists ' % full_path + os.path.join(args.o, get_packagename(args, full_path)) + '_h264.mov')

if __name__ == "__main__":
    main()

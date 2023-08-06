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
        action='store_true', help='Make h264 proxy for DCP, which has 2 mxf inputs'
    )
    return parser.parse_args()

def rename_proxy(output, full_path, type):
    filename = os.path.basename(full_path)
    proxy_filename = os.path.join(output, filename + '_' + type + '.mov')
    if os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path)))).startswith('aaa'):
        os.rename(proxy_filename, os.path.join(output, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path))))) + '_' + type + '.mov')
    elif os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path)))).startswith('oe'):
        os.rename(proxy_filename, os.path.join(output, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path))))) + '_' + type + '.mov')


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
                if not (os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(dcp_i[0]))))) in str(os.listdir(args.o)):
                    bitc_cmd = [dcp_i, '-o', args.o, '-dcp']
                    if not args.bitc:
                        bitc_cmd.extend(['-clean'])
                    bitc.main(bitc_cmd)
                    rename_proxy(args.o, dcp_i[0], 'h264')
                else:
                    print('Skipping %s as the proxy already exists ' % dcp_i[0] + os.path.join(args.o, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(dcp_i[0]))))) + '_h264.mov')
        else:
            for filename in filenames:
                full_path = os.path.join(root, filename)
                if full_path.endswith(('.mov', '.mkv', '.mxf', '.dv', '.m2t')):
                    if args.prores:
                        if not args.wide:
                            prores.main([full_path, '-o', args.o, '-hq'])
                        else:
                            prores.main([full_path, '-wide', '-o', args.o, '-hq'])
                        rename_proxy(args.o, full_path, 'prores')
                        '''
                        proxy_filename = os.path.join(args.o, filename +'_prores.mov')
                        if os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path)))).startswith('aaa'):
                            os.rename(proxy_filename, os.path.join(args.o, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path))))) + '_prores.mov')
                        elif os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path)))).startswith('oe'):
                            os.rename(proxy_filename, os.path.join(args.o, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path))))) + '_prores.mov')
                        '''
                    else:
                        if not (os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path))))) in str(os.listdir(args.o)):
                            bitc_cmd = [full_path, '-o', args.o]
                            if not args.bitc:
                                bitc_cmd.extend(['-clean'])
                            if args.wide:
                                bitc_cmd.extend(['-wide'])
                            bitc.main(bitc_cmd)
                            rename_proxy(args.o, full_path, 'h264')
                            '''
                            proxy_filename = os.path.join(args.o, filename +'_h264.mov')
                            if os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path)))).startswith('aaa'):
                                os.rename(proxy_filename, os.path.join(args.o, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path))))) + '_h264.mov')
                            if os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path)))).startswith('oe'):
                                os.rename(proxy_filename, os.path.join(args.o, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path))))) + '_h264.mov')
                            '''
                        else:
                            print('Skipping %s as the proxy already exists ' % full_path + os.path.join(args.o, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(full_path))))) + '_h264.mov')

if __name__ == "__main__":
    main()

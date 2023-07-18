#!/usr/bin/env python3
import os
import sys
import time
import argparse
import subprocess
import platform
import ififuncs
import framemd5

def parse_args():
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='create framemd5 for a batch of SIP objects. check if all the hashes match to the md5 manifest in the PSM packages.'
        ' Written by Yazhou He'
    )
    parser.add_argument(
        '-sip',
        help='Path to the parent folder containing a batch of SIPs.'
    )
    parser.add_argument(
        '-psm',
        help='Path to the parent folder containing a batch of PSMs.'
    )
    parsed_args = parser.parse_args()
    return parsed_args

def batchframemd5(sip_path):
    print("\n\nPART 1 - framemd5 creation")
    oe = os.listdir(sip_path)
    framemd5_f = []
    for sip in oe:
        if sip[:2] == 'oe':
            print("\n**** SIP has been found: %s" % sip)
            sip_d = os.path.join(sip_path, sip)
            uuid = os.listdir(sip_d)
            for item in uuid:
                if os.path.isdir(os.path.join(sip_d, item)):
                    uuid_d = os.path.join(sip_d, item)
                    obj = os.path.join(uuid_d, 'objects')
                    obj_d = os.listdir(obj)
                    for item in obj_d:
                        if not item.endswith('.qctools.mkv'):
                            v = os.path.join(obj, item)
                            print("**** Object has been found: %s" % v)
                    try:
                        '''
                        if platform.system() == 'Windows':
                            framemd5_cmd = ['python', 'framemd5.py', '-i', v]
                        else:
                            framemd5_cmd = ['python3', 'framemd5.py', '-i', v]
                        print(framemd5_cmd)
                        subprocess.check_output(framemd5_cmd)
                        '''
                        framemd5_cmd = ['-i', v]
                        framemd5.main(framemd5_cmd)
                    except Exception as e:
                        print(e)
                        print("!!!! framemd5.py failed!")
                    obj_d = os.listdir(obj)
                    for item in obj_d:
                        if item.endswith('.framemd5'):
                            framemd5_sip = os.path.join(obj, item)
                            framemd5_f.append(framemd5_sip)
                            print("**** Framemd5 has been genreated: " + framemd5_sip)
    return framemd5_f

def diff_framemd5(framemd5_f, psm_path, txt_name_source):
    print("\n\nPART 2 - framemd5 vs md5 fixity check")

    print('Framemd5 exists:')
    for f in framemd5_f:
        print('\t' + f)
    framemd5_count = len(framemd5_f)

    print('Md5 exists:')
    psms = os.listdir(psm_path)
    md5_f = []
    for psm in psms:
        psm_d = os.path.join(psm_path, psm)
        for root, dir, file in os.walk(psm_d):
            for f in file:
                if f.endswith('.md5'):
                    md5 = os.path.join(psm_d, f)
                    md5_f.append(md5)
                    print('\t' + md5)
    md5_count = len(md5_f)
    
    if framemd5_count == md5_count:
        print('**** SIPs/framemd5 count matches PSMs/md5 count %s\n' % framemd5_count)
        ififuncs.generate_txt('',txt_name_source, 'SIPs/framemd5 count matches PSMs/md5 count %s' % framemd5_count)
    else:
        print('!!!! SIPs/framemd5 count %s DOES NOT match PSMs/md5 count %s' % (framemd5_count, md5_count))
        ififuncs.generate_txt('',txt_name_source, 'SIPs/framemd5 count %s DOES NOT match PSMs/md5 count %s' % (framemd5_count, md5_count))
        # sys.exit()
    
    i = 0
    while i < framemd5_count:
        with open(framemd5_f[i], 'r') as f1, open(md5_f[i], 'r') as f2:
            flag = True
            for l1, l2 in zip(f1, f2):
                if not l1.startswith('#') and not l2.startswith('#'):
                    if l1 != l2:
                        flag = False
                        print('-----\n!!!! %s DOES NOT match %s\n\tFrom %s:\n\t%s\tFrom %s:\n\t%sMISMATCH FOUND - GOING TO THE NEXT MANIFEST...' % (framemd5_f[i], md5_f[i], framemd5_f[i], l1, md5_f[i], l2))
                        ififuncs.generate_txt('',txt_name_source, '! %s DOES NOT match %s\n\tFrom %s:\n\t%s\tFrom %s:\n\t%s' % (framemd5_f[i], md5_f[i], framemd5_f[i], l1, md5_f[i], l2))
                        # mismatch_list.append()
                        break
        if flag:
            print('-----\n**** All checksums match between %s and %s' % (framemd5_f[i], md5_f[i]))
            ififuncs.generate_txt('',txt_name_source, '* All checksums match between %s and %s' % (framemd5_f[i], md5_f[i]))
        i = i + 1
    else:
        print('-----\nFixity check completed')  

def batchrm_framemd5(sip_path):
    print("\n\nPART 3 - framemd5 deletation")
    framemd5_f = []
    for root, dir, file in os.walk(sip_path):
        if root.endswith('objects'):
            for f in file:
                f_abspath = os.path.join(root, f)
                if f.endswith('.framemd5') and os.path.isfile(f_abspath):
                    os.remove(f_abspath)
                    framemd5_f.append(f_abspath)
    return framemd5_f

def main():
    args = parse_args()
    sip_path = args.sip
    psm_path = args.psm
    framemd5_f = batchframemd5(sip_path)
    time.sleep(1)
    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    txt_name_filename = (os.path.basename(sys.argv[0]).split(".")[0]) + time.strftime("_%Y_%m_%dT%H_%M_%S")
    txt_name_source = "%s/%s.txt" % (desktop_logs_dir, txt_name_filename)
    ififuncs.generate_txt('',txt_name_source, 'SIP Directory: %s' % sip_path)
    ififuncs.generate_txt('',txt_name_source, 'PSM Directory: %s' % psm_path)
    diff_framemd5(framemd5_f, psm_path, txt_name_source)
    time.sleep(1)
    del_framemd5_f = batchrm_framemd5(sip_path)
    if not del_framemd5_f:
        print('!!! Cannot delete framemd5 files!')
    else:
        print("**** Below framemd5 files have been deleted:")
        for f in del_framemd5_f:
            print('\t' + f)

if __name__ == '__main__':
    main()
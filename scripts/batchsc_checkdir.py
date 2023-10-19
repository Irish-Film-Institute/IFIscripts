#!/usr/bin/env python3

import os
import shutil

def move_aip():
    'Check if the packages include UUID folder (meaning AIPs) in the root.'
    print('\n\n***Move AIP***')
    inp = input('Drag/Input the directory including both RAW packages and AIPs to be checked:\t')
    output = input('Drag/Input the directory the AIPs are to be moved:\t')
    roots = os.listdir(inp)
    for root in roots:
        path = os.path.join(inp, root)
        if os.path.isdir(path):
            dirs = os.listdir(path)
            if any(len(dir) == 36 and os.path.isdir(os.path.join(path,dir)) for dir in dirs):
                print('Message:\t%s is an AIP. Move to AIP folder.' % path)
                shutil.move(path, output)

def move_sipped_raw():
    'Check if any RAW packages have pre-existing AIPs and move them to a separate folder. Comparison by name similiarity check.'
    print('\n\n***Move Sipped RAW Packages***')
    d_raw = input('Drag/Input directory of RAW packages:\t')
    d_aip = input('Drag/Input directory of AIP packages:\t')
    output = input('Drag/Input directory for moving RAW packages that have pre-existing AIPs to:\t')
    aips = os.listdir(d_aip)
    roots = os.listdir(d_raw)
    for root in roots:
        raw_parts = root.split(" ")
        for aip in aips:
            aip_parts = aip.split("_")
            i = 0
            goon = True
            while i < len(raw_parts) and goon and len(raw_parts) == len(aip_parts):
                if raw_parts[i].lower() == aip_parts[i] and i != len(raw_parts)-1:
                    goon = True
                    i = i + 1
                elif i == len(raw_parts)-1 and i > 0:
                    print('\ntrigger:\t %s in raw and %s in AIP, index=%s' % (raw_parts[i], aip_parts[i], i))
                    ask = input("Alert:\tdoes RAW \'%s\' and AIP \'%s\' have the same title?\n\tanswer y/n -> " % (root, aip))
                    if ask.lower() == 'y':
                        inp = os.path.join(d_raw, root)
                        print('Message:\tmove %s to %s.' % inp, output)
                        shutil.move(inp, output)
                        goon = False
                    else:
                        goon = False
                else:
                    goon = False
                '''
                elif i > 0 and raw_parts[i].lower() != aip_parts[i]:
                    ask = input("\nAlert:\tdoes RAW \'%s\' and AIP \'%s\' have the same title?\n\tanswer y/n -> " % (root, aip))
                    if ask.lower() == 'y':
                        inp = os.path.join(d_raw, root)
                        print('Message:\tmove %s to sipped_raw folder.' % inp)
                        shutil.move(inp, output)
                        goon = False
                    else:
                        goon = False
                '''

def main():
    menu=[
        '1. Check if each is an AIP (processed package), and move AIPs to a separate folder.',
        '2. Check if each RAW (unprocessed package) has a pre-existing AIP. If so, move the RAW to a separate folder.'
    ]
    print(*menu, sep = '\n')
    func = input('Which feature do you need?  ->  ')  
    if func == '1':
        move_aip()
    elif func == '2':
        move_sipped_raw()
    
if __name__ == '__main__':
    main()

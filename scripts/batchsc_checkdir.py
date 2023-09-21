#!/usr/bin/env python3

import os
import shutil

def move_sip():
    'Check if the packages include UUID folder in the root.'
    print('\n\n***Move SIP***')
    inp = input('Drag/Input the directory including both RAW packages and SIPs to be checked:\t')
    output = input('Drag/Input the directory the SIPs are to be moved:\t')
    roots = os.listdir(inp)
    for root in roots:
        path = os.path.join(inp, root)
        if os.path.isdir(path):
            dirs = os.listdir(path)
            if any(len(dir) == 36 and os.path.isdir(os.path.join(path,dir)) for dir in dirs):
                print('Message:\t%s is a SIP. Move to SIP folder.' % path)
                shutil.move(path, output)

def move_sipped_raw():
    'Check if the RAW packages have been sipped and move them to sipped RAW folder. Comparison by name similiarity check.'
    print('\n\n***Move Sipped RAW Packages***')
    d_raw = input('Input directory of RAW packages:\t')
    d_sip = input('Input directory of SIP packages:\t')
    output = input('Input directory for moving sipped RAW packages:\t')
    sips = os.listdir(d_sip)
    roots = os.listdir(d_raw)
    for root in roots:
        raw_parts = root.split(" ")
        for sip in sips:
            sip_parts = sip.split("_")
            i = 0
            goon = True
            while i < len(raw_parts) and goon and len(raw_parts) == len(sip_parts):
                if raw_parts[i].lower() == sip_parts[i] and i != len(raw_parts)-1:
                    goon = True
                    i = i + 1
                elif i == len(raw_parts)-1 and i > 0:
                    print('\ntrigger:\t %s in raw and %s in sip, index=%s' % (raw_parts[i], sip_parts[i], i))
                    ask = input("Alert:\tdoes RAW \'%s\' and SIP \'%s\' have the same title?\n\tanswer y/n -> " % (root, sip))
                    if ask.lower() == 'y':
                        inp = os.path.join(d_raw, root)
                        print('Message:\tmove %s to sipped_raw folder.' % inp)
                        shutil.move(inp, output)
                        goon = False
                    else:
                        goon = False
                else:
                    goon = False
                '''
                elif i > 0 and raw_parts[i].lower() != sip_parts[i]:
                    ask = input("\nAlert:\tdoes RAW \'%s\' and SIP \'%s\' have the same title?\n\tanswer y/n -> " % (root, sip))
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
        '1. Check if it\'s a SIP',
        '2. Check if each raw has been sipped'
    ]
    print(*menu, sep = '\n')
    func = input('Which feature do you need?  ->  ')  
    if func == '1':
        move_sip()
    elif func == '2':
        move_sipped_raw()
    
if __name__ == '__main__':
    main()

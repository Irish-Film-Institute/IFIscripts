#!/usr/bin/env python3
'''
Generate a helper DCDM PBCore based on the required technical metadata for DCDM PBCore.
Reason for this as a helper PBCore script for DCDM:
    The directory structure of DCDM could be inconsistent;
    Some values could be fixed for DCDM (this is ensured during the QC steps);
    Some values could be ingested from object files
The helper PBCore generated will not merged into the archival information package
but just to the ifiscripts_log folder.
'''
import sys
import os
import argparse
import xml.etree.ElementTree as ET
import datetime
import ififuncs

def make_csv(csv_filename):
    '''
    Writes a CSV with IFI database headings.
    '''
    ififuncs.create_csv(csv_filename, [
        'ImportNo'
        'Reference Number',
        'Donor',
        'Edited By',
        'Date Created',
        'Date Last Modified',
        'Film Or Tape',
        'Date Of Donation',
        'Accession Number',
        'Habitat',
        'backup_habitat',
        'TTape Origin',
        'Type Of Deposit',
        'Depositor Reference',
        'Master Viewing',
        'Language Version',
        'Condition Rating',
        'Companion Elements',
        'EditedNew',
        'FIO',
        'CollectionTitle',
        'Created By',
        'instantiationIdentif',
        'instantDate_other',
        'instantDate_type',
        'instantiationDate_mo',
        'instantiationStandar',
        'InstantMediaty',
        'instantFileSize_byte',
        'instantFileSize_gigs',
        'essenceTrackEncodvid',
        'essenceTrackSampling',
        'essenceBitDepth_vid',
        'essenceFrameSize',
        'essenceAspectRatio',
        'essenceTrackEncod_au',
        'essenceBitDepth_au',
        'FrameCount',
        'ColorSpace',
        'Pix_fmt',
        'dig_object_descrip',
        'Restrictions'
    ])

def getRatio(Width, Height):
    if Width == '1998' and Height == '1080':
        essenceAspectRatio = '1.85:1'
    elif Width == '1920' and Height == '1080':
        essenceAspectRatio = '1.78:1'
    elif Width == '2048' and Height == '1080':
        essenceAspectRatio = '1.90:1'
    elif Width == '2048' and Height == '858':
        essenceAspectRatio = '2.39:1'
    elif Width == '4096' and Height == '1716':
        essenceAspectRatio = '2.39:1'
    else:
        print('***** essenceAspectRatio does not follow the standard and cannot be calculated')
        essenceAspectRatio = 'n/a'
    return essenceAspectRatio

def parse_args(args_):
    '''
    Parse command line arguments.
    '''
    parser = argparse.ArgumentParser(
        description='Generate a helper DCDM PBCore based on the required technical metadata for DCDM PBCore.\n'
        'This script takes the AIP folder (named \'aaaxxxx\') as input. Either a single file or multiple objects will be described.\n'
        'This will produce a single helper PBCore CSV record to Desktop/ifiscripts_logs/, and does NOT work for multiple AIPs.'
        ' Written by Yazhou He.'
    )
    parser.add_argument(
        'input', help='Input directory'
    )
    parser.add_argument(
        '-user',
        help='Declare who you are. If this is not set, you will be prompted.'
    )
    parsed_args = parser.parse_args(args_)
    return parsed_args

def main(args_):
    args = parse_args(args_)
    
    if args.user:
        user = args.user
    else:
        user = ififuncs.get_user()
    Edited_By = user
    EditedNew = user
    Created_By = user
    
    if os.path.isdir(args.input) and os.path.basename(args.input)[:3] == 'aaa':
        source = args.input
        Accession_Number = os.path.basename(source)
    else:
        print("the input is not an AIP! Exiting...")
        sys.exit()

    Film_Or_Tape = 'Digital AV Object'
    dig_object_descrip = 'DCDM'
    InstantMediaty = 'Moving Image'
    instantiationIdentif = ''
    for dirs in os.listdir(source):
        if ififuncs.validate_uuid4(dirs) is None:
            instantiationIdentif = dirs

    Date_Of_Donation = ''
    log_dir = os.path.join(source, instantiationIdentif, 'logs')
    for files in os.listdir(log_dir):
        if files.endswith('.log'):
            log = os.path.join(log_dir, files)
    with open(log, 'r', encoding='utf-8') as log_object:
        log_lines = log_object.readlines()
        for lines in log_lines:
            if 'donation_date' in lines:
                Date_Of_Donation = lines.split('donation_date=\'')[1].split('\'')[0]

    filmo_csv_dir = os.path.join(source, instantiationIdentif, 'metadata')
    for files in os.listdir(filmo_csv_dir):
        if files.endswith('_filmographic.csv'):
            Reference_Number = os.path.basename(files).split('_')[0]
    
    mediainfo_dir = os.path.join(source, instantiationIdentif, 'metadata', 'supplemental')
    mediainfo_xml = ''
    for files in os.listdir(mediainfo_dir):
        if files.endswith('_source_mediainfo.xml'):
            mediainfo_xml = os.path.join(mediainfo_dir,files)
    if not mediainfo_xml:
        print("the input AIP is not completed!\n\tDetail: source_mediainfo.xml missing in %s\n\tCheck fixity required. Exiting..." % mediainfo_dir)
        sys.exit()            
    
    instantiationDate_mo = datetime.datetime.fromtimestamp(os.path.getmtime(mediainfo_xml)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    mediainfo_xml_tree = ET.parse(mediainfo_xml)
    mediainfo_root = mediainfo_xml_tree.getroot()
    mediainfo_root.findall("./File/track/[@type='Image']...")
    FrameCount = str(len(mediainfo_root.findall("./File/track/[@type='Image']")))
    for track_format in mediainfo_root.findall("./File/track/[@type='Image']..."):
        instantiationStandar = track_format.find("track/[@type='General']/Format").text
        essenceTrackEncodvid = track_format.find("track/[@type='General']/Image_Codec_List").text.upper()
        essenceBitDepth_vid = track_format.find("track/[@type='Image']/BitDepth").text
        Width = track_format.find("track/[@type='Image']/Width").text
        Height = track_format.find("track/[@type='Image']/Height").text
        essenceFrameSize = Width + 'x' + Height
        essenceAspectRatio = getRatio(Width, Height)
        ColorSpace= track_format.find("track/[@type='Image']/ColorSpace").text
        break
    for track_format in mediainfo_root.findall("./File/track/[@type='Audio']..."):
        essenceTrackSampling = track_format.find("track/[@type='Audio']/SamplingRate_String").text
        essenceTrackEncod_au = track_format.find("track/[@type='Audio']/Format").text
        essenceBitDepth_au = track_format.find("track/[@type='Audio']/BitDepth").text
        break
    
    instantFileSize_byte = 0
    for r, d, f in os.walk(os.path.join(source, instantiationIdentif, 'objects')):
        for files in f:
            instantFileSize_byte += os.path.getsize(os.path.join(r,files))
    instantFileSize_gigs = round(
        float(instantFileSize_byte)  / 1024 / 1024 / 1024, 3
    )

    Pix_fmt = 'rgb48le'
    Donor = 'Screen Ireland (previously Irish Film Board/IFB)'
    Restrictions = 'Screen Ireland (previously Irish Film Board/IFB)'
    Depositor_Reference = '67'
    Type_Of_Deposit = 'Deposit via overarching agreements'
    Master_Viewing = 'Preservation Object'
    CollectionTitle = 'Irish Film Board (IFB) aka Screen Ireland'
    
    Date_Created = ''
    Date_Last_Modified = ''
    Habitat =''
    backup_habitat = ''
    TTape_Origin = ''
    Language_Version = ''
    Condition_Rating = ''
    Companion_Elements = ''
    FIO = 'In'
    instantDate_other = 'n/a'
    instantDate_type = 'n/a'

    desktop_logs_dir = ififuncs.make_desktop_logs_dir()
    csv_filename = os.path.join(desktop_logs_dir, Accession_Number + '_%s_DCDM_helperpbcore.csv' % Reference_Number)
    make_csv(csv_filename)
    
    ififuncs.append_csv(csv_filename, [
        '',
        Reference_Number,
        Donor,
        Edited_By,
        Date_Created,
        Date_Last_Modified,
        Film_Or_Tape,
        Date_Of_Donation,
        Accession_Number,
        Habitat,
        backup_habitat,
        TTape_Origin,
        Type_Of_Deposit,
        Depositor_Reference,
        Master_Viewing,
        Language_Version,
        Condition_Rating,
        Companion_Elements,
        EditedNew,
        FIO,
        CollectionTitle,
        Created_By,
        instantiationIdentif,
        instantDate_other,
        instantDate_type,
        instantiationDate_mo,
        instantiationStandar,
        InstantMediaty,
        instantFileSize_byte,
        instantFileSize_gigs,
        essenceTrackEncodvid,
        essenceTrackSampling,
        essenceBitDepth_vid,
        essenceFrameSize,
        essenceAspectRatio,
        essenceTrackEncod_au,
        essenceBitDepth_au,
        FrameCount,
        ColorSpace,
        Pix_fmt,
        dig_object_descrip,
        Restrictions
    ])
    
    print(csv_filename + " has been created.")

if __name__ == '__main__':
    main(sys.argv[1:])



#!/usr/bin/env python3
'''
VALIDATE AS-11 UK DPP MXF BY COMPARING 
ITS CHECKSUMS FROM BOTH PACKAGE MANIFEST
AND DPP XML <MediaChecksumValue>
'''

import sys
import os
import csv
import hashlib
from datetime import datetime
from lxml import etree
import unidecode
import ififuncs

def digest_with_progress(filename, chunk_size):
    read_size = 0
    last_percent_done = 0
    digest = hashlib.md5()
    total_size = os.path.getsize(filename)
    data = True
    f = open(filename, 'rb', encoding= 'utf-8')
    while data:
        # Read and update digest.
        data = f.read(chunk_size)
        read_size += len(data)
        digest.update(data)
        # Calculate progress.
        percent_done = 100 * read_size / total_size
        if percent_done > last_percent_done:
            sys.stdout.write('[%d%%]\r' % percent_done)
            sys.stdout.flush()
            last_percent_done = percent_done
    f.close()
    return digest.hexdigest()

def count_files(starting_dir):
    dicto = {}
    previous_oe = ''
    for dirpath, dirss, filenames in os.walk(starting_dir):
        oe = False
        aaa = False
        try:
            current_oe = dirpath.split('oe')[1][:5]
            if current_oe[-1] == '/' or current_oe[-1] == '\\':
                current_oe = current_oe[:-1]
            oe = True
        except IndexError:
            try:
                current_oe = dirpath.split('aaa')[1][:4]
                aaa = True
            except IndexError:
                continue
        if previous_oe != current_oe:
            filename_counter = 0
            dir_counter = 0
        for filename in filenames:
            if filename[0] != '.':
                filename_counter += 1
        dir_counter += len(dirss)
        previous_oe = current_oe
        if oe:
            dicto['oe' + previous_oe] = [filename_counter, dir_counter]
        elif aaa:
            dicto['aaa' + previous_oe] = [filename_counter, dir_counter]
        ''''
        except KeyError:
            print 'hi'
            dicto['aaa' + previous_oe] = [filename_counter, dir_counter]
        '''
    print('SIP/AIP found:')
    for i in dicto:
        print(i, " | filecount: ", dicto[i][0], " | folder_count: ", dicto[i][1])
    print()
    return dicto

def main():
    starting_dir = sys.argv[1]
    dicto = count_files(starting_dir)
    startTime = datetime.now()
    csv_report_filename = os.path.basename(starting_dir) + "_report"
    csv_report = os.path.expanduser("~/Desktop/%s.csv") % csv_report_filename
    checkfile = os.path.isfile(csv_report)
    if checkfile is True:
        print("CSV file already exists.\nThis will overwrite the existed CSV.\n")
    ififuncs.create_csv(
        csv_report,
        (
            'ID',
            'oe',
            'accessionnumber',
            'files_count',
            'directory_count',
            'Filename',
            'Series_Title',
            'Prog_Title',
            'Episode_Number',
            'Md5_From_Xml',
            'Md5_from_Mxf',
            'Checksum_Result'
        )
    )
    
    xml_flag = 0
    for dirpath, dirss, filenames in sorted(os.walk(starting_dir)):
        if len(os.path.basename(dirpath)) == 36:
            uuid_dir = dirpath
            logs_dir = os.path.join(uuid_dir, 'logs')
            log = os.path.join(logs_dir, os.path.basename(uuid_dir) + '_sip_log.log')
            objects_dir = os.path.join(uuid_dir, 'objects')
            objects_list = os.listdir(objects_dir)
            manifest_basename = os.path.basename(uuid_dir) + '_manifest.md5'
            manifest = os.path.join(os.path.dirname(uuid_dir), manifest_basename)
        if os.path.basename(dirpath) == 'supplemental':
            for filename in filenames:
                if filename.endswith('.xml') and not filename.endswith('_MediaConchReport.xml'):
                    full_xml_path = os.path.join(dirpath, filename)
                    xml_flag = 1
                    with open(manifest, 'r', encoding='utf-8') as fo:
                        manifest_lines = fo.readlines()
                        for line in manifest_lines:
                            if line.lower().replace('\n', '').endswith('.mxf'):
                                mxf_checksum = line[:32]
                                #mxf_checksum = str(digest_with_progress(mxf, 1024))
                                print(mxf_checksum + ' - mxf checksum from package manifest')
                    try:
                        dpp_xml_parse = etree.parse(full_xml_path)
                        dpp_xml_namespace = dpp_xml_parse.xpath('namespace-uri(.)')
                        #parsed values from dpp xml
                        series_title = dpp_xml_parse.findtext(
                            '//ns:SeriesTitle',
                            namespaces={'ns':dpp_xml_namespace}
                        )
                        prog_title = dpp_xml_parse.findtext(
                            '//ns:ProgrammeTitle',
                            namespaces={'ns':dpp_xml_namespace}
                        )
                        ep_num = dpp_xml_parse.findtext(
                            '//ns:EpisodeTitleNumber',
                            namespaces={'ns':dpp_xml_namespace}
                        )
                        checksum = dpp_xml_parse.findtext(
                            '//ns:MediaChecksumValue',
                            namespaces={'ns':dpp_xml_namespace}
                        )
                        print(checksum + ' - mxf checksum from DPP XML')
                        accession_number_id = ''
                        if os.path.isfile(log):
                            with open(log, 'r', encoding='utf-8') as log_object:
                                log_lines = log_object.readlines()
                                for lines in log_lines:
                                    if 'eventIdentifierType=object entry number,' in lines:
                                        source_oe = lines.split('=')[-1].replace('\n', '')
                                    if 'eventIdentifierType=accession number,' in lines:
                                        accession_number_id = lines.split('=')[-1].replace('\n', '')
                        print('Generating Report.... ')
                        if mxf_checksum == checksum:
                            print(source_oe + 'Checksum MATCHES!\n---')
                            ififuncs.append_csv(
                                csv_report,
                                (
                                    os.path.basename(os.path.dirname(uuid_dir)),
                                    source_oe,
                                    accession_number_id,
                                    dicto[os.path.basename(os.path.dirname(uuid_dir))][0],
                                    dicto[os.path.basename(os.path.dirname(uuid_dir))][1],
                                    filename,
                                    unidecode.unidecode(series_title),
                                    unidecode.unidecode(prog_title),
                                    unidecode.unidecode(ep_num),
                                    checksum,
                                    mxf_checksum,
                                    'CHECKSUM MATCHES!'
                                    )
                            )
                        else:
                            print(source_oe + 'Checksum does NOT MATCH!\n---'),
                            ififuncs.append_csv(
                                csv_report,
                                (
                                    os.path.basename(os.path.dirname(uuid_dir)),
                                    source_oe,
                                    accession_number_id,
                                    dicto[os.path.basename(os.path.dirname(uuid_dir))][0],
                                    dicto[os.path.basename(os.path.dirname(uuid_dir))][1],
                                    filename,
                                    unidecode.unidecode(series_title),
                                    unidecode.unidecode(prog_title),
                                    unidecode.unidecode(ep_num),
                                    checksum,
                                    mxf_checksum,
                                    'CHECKSUM DOES NOT MATCH!'
                                    )
                            )
                    except AttributeError:
                        print(source_oe + 'Checksum does NOT MATCH or wrong source!\n---')
                        ififuncs.append_csv(
                            csv_report,
                            (
                                os.path.basename(os.path.dirname(uuid_dir)),
                                source_oe,
                                accession_number_id,
                                dicto[os.path.basename(os.path.dirname(uuid_dir))][0],
                                dicto[os.path.basename(os.path.dirname(uuid_dir))][1],
                                filename,
                                'error',
                                'error',
                                'error',
                                'error',
                                'error',
                                'CHECKSUM DOES NOT MATCH or WRONG SOURCE!'
                                )
                            )
                else:
                    continue
            if xml_flag == 0:
                print(dirpath + '\n*****There is no metadata xml file in the supplement directory!\n*****Check if the structure is correct.\n---')
                continue
    print("Report complete\nTime elaspsed : ", datetime.now() - startTime)
    print("Location: " + csv_report)


if __name__ == '__main__':
    main()
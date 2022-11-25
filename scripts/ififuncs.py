'''
A collection of functions that other scripts can use.

'''
from __future__ import print_function

import subprocess
import sys
import time
import smtplib
import mimetypes
import getpass
import os
import filecmp
import hashlib
import datetime
import uuid
import tempfile
import csv
import operator
import json
import ctypes
import platform
import itertools
import unicodedata
import shutil
from builtins import input
import makedfxml
from glob import glob
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
try:
    from lxml import etree
except ImportError:
    print('ERROR - lxml is not installed - try pip install lxml')
    sys.exit()

def diff_textfiles(source_textfile, other_textfile):
    '''
    Compares two textfiles. Returns strings that indicate losslessness.
    '''
    if filecmp.cmp(source_textfile, other_textfile, shallow=False):
        print(" - YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!")
        return 'lossless'

    else:
        print(" - CHECKSUM MISMATCH - Further information on the next line!!!")
        return 'lossy'


def make_mediainfo(xmlfilename, xmlvariable, inputfilename):
    '''
    Writes a verbose mediainfo XML output using the OLDXML schema.
    '''
    mediainfo_cmd = [
        'mediainfo',
        '-f',
        '--language=raw',
        '--File_TestContinuousFileNames=0',
        '--output=OLDXML',
        inputfilename
    ]
    with open(xmlfilename, "w") as fo:
        # https://stackoverflow.com/a/21486747
        try:
            xmlvariable = subprocess.check_output(mediainfo_cmd).decode(sys.stdout.encoding)
        except UnicodeDecodeError:
            xmlvariable = subprocess.check_output(mediainfo_cmd).decode('cp1252')
        fo.write(xmlvariable)

def make_exiftool(xmlfilename, inputfilename):
    '''
    Writes an exiftool json output.
    '''
    exiftool_cmd = [
        'exiftool',
        '-j',
        inputfilename
    ]
    with open(xmlfilename, "w", encoding='utf8') as fo:
        try:
            xmlvariable = subprocess.check_output(exiftool_cmd).decode(sys.stdout.encoding)
        # exiftool has difficulties with unicode support on windows.
        # instead of exiftool reading the file, the file is loading into memory
        # and exiftool anaylses that instead.
        # https://exiftool.org/exiftool_pod.html#WINDOWS-UNICODE-FILE-NAMES
        except subprocess.CalledProcessError:
            with open(inputfilename, 'rb') as file_object:
                xmlvariable = subprocess.check_output(['exiftool', '-j', '-'], stdin=file_object).decode("utf-8")
        fo.write(xmlvariable)
def make_siegfried(xmlfilename, inputfilename):
    '''
    Writes a Siegfried/PRONOM json report.
    '''
    siegfried_cmd = [
        'sf',
        '-json',
        inputfilename
    ]
    
    with open(xmlfilename, "w+") as fo:
        xmlvariable = subprocess.check_output(siegfried_cmd).decode(sys.stdout.encoding)
        parsed = json.loads(xmlvariable)
        fo.write(json.dumps(parsed, indent=4, sort_keys=True))

def make_mediaconch(full_path, mediaconch_xmlfile):
    '''
    Creates a mediaconch implementation check XML report.
    '''
    mediaconch_cmd = [
        'mediaconch',
        '-fx',
        full_path
    ]
    print(' - Mediaconch is analyzing %s' % full_path)
    mediaconch_output = subprocess.check_output(mediaconch_cmd).decode(sys.stdout.encoding)
    with open(mediaconch_xmlfile, 'w') as xmlfile:
        xmlfile.write(mediaconch_output)

def extract_provenance(filename, output_folder, output_uuid):
    '''
    This will extract dfxml, mediainfo and mediatrace XML
    Need to add a workaround for TIFF as folders are not
    processed as a whole.
    '''
    inputxml = "%s/%s_source_mediainfo.xml" % (output_folder, output_uuid)
    inputtracexml = "%s/%s_source_mediatrace.xml" % (output_folder, output_uuid)
    dfxml = "%s/%s_source_dfxml.xml" % (output_folder, output_uuid)
    print(' - Generating mediainfo xml of input file and saving it in %s' % inputxml)
    make_mediainfo(inputxml, 'mediaxmlinput', filename)
    print(' - Generating mediatrace xml of input file and saving it in %s' % inputtracexml)
    make_mediatrace(inputtracexml, 'mediatracexmlinput', filename)
    if os.path.isfile(filename):
        filename = os.path.dirname(filename)
        # check if file without extension is provided
        if filename == '':
            filename = os.path.abspath(filename)
    print(' - Generating Digital Forensics xml of input directory and saving it in %s' % dfxml)
    makedfxml.main([filename, '-n', '-o', dfxml])
    return inputxml, inputtracexml, dfxml

def generate_mediainfo_xmls(filename, output_folder, output_uuid, log_name_source):
    '''
    This will add the mediainfo xmls to the package
    '''
    inputxml, inputtracexml, dfxml = extract_provenance(filename, output_folder, output_uuid)
    mediainfo_version = get_mediainfo_version()
    generate_log(
        log_name_source,
        'EVENT = Metadata extraction - eventDetail=Technical metadata extraction via mediainfo, eventOutcome=%s, agentName=%s' % (inputxml, mediainfo_version)
    )
    generate_log(
        log_name_source,
        'EVENT = Metadata extraction - eventDetail=Mediatrace technical metadata extraction via mediainfo, eventOutcome=%s, agentName=%s' % (inputtracexml, mediainfo_version)
    )
    generate_log(
        log_name_source,
        'EVENT = Metadata extraction - eventDetail=File system metadata extraction using Digital Forensics XML, eventOutcome=%s, agentName=makedfxml' % (dfxml)
    )
    return inputxml, inputtracexml, dfxml
def make_qctools(input):
    '''
    Runs an ffprobe process that stores QCTools XML info as a variable.
    A file is not actually created here.
    '''
    qctools_args = ['ffprobe', '-f', 'lavfi', '-i',]
    qctools_args += ["movie=%s:s=v+a[in0][in1],[in0]signalstats=stat=tout+vrep+brng,cropdetect=reset=1:round=1,split[a][b];[a]field=top[a1];[b]field=bottom[b1],[a1][b1]psnr[out0];[in1]ebur128=metadata=1,astats=metadata=1:reset=1:length=0.4[out1]" % input]
    qctools_args += ['-show_frames', '-show_versions', '-of', 'xml=x=1:q=1', '-noprivate']
    print(qctools_args)
    qctoolsreport = subprocess.check_output(qctools_args)
    return qctoolsreport


def write_qctools_gz(qctoolsxml, sourcefile):
    '''
    This accepts a variable containing XML that is written to a file.
    '''
    with open(qctoolsxml, "w+") as fo:
        fo.write(make_qctools(sourcefile))
    subprocess.call(['gzip', qctoolsxml])


def get_audio_stream_count():
    '''
    Returns the number of audio streams in the form of an INT.
    '''
    ffprobe_cmd = [
        'ffprobe', '-v',
        'error', '-select_streams', 'a',
        '-show_entries', 'stream=index', '-of', 'flat',
        sys.argv[1]
    ]
    audio_stream_count = subprocess.check_output(ffprobe_cmd).splitlines()
    return len(audio_stream_count)


def get_mediainfo(var_type, type, filename):
    '''
    Uses mediainfo to extract a single item of metadata
    example:
    duration =  get_mediainfo(
        'duration', '--inform=General;%Duration_String4%', sys.argv[1]
    )
    '''
    mediainfo_cmd = [
        'mediainfo',
        '--Language=raw',
        '--Full',
        type,
        filename
    ]
    var_type = subprocess.check_output(mediainfo_cmd).decode(sys.stdout.encoding).replace('\n', '').replace('\r', '')
    return var_type


def get_milliseconds(filename):
    '''
    Returns a float with the duration of a file in milliseconds.
    '''
    milliseconds = get_mediainfo(
        'miliseconds',
        '--inform=General;%Duration%',
        filename
    )
    try:
        return float(milliseconds)
    except Exception as e:
            print("\nDuration ERROR\n\t-> get_mediainfo(miliseconds) not support\n\t-> %s\n\t-> ififuncs.py line: 219" % e)

def convert_millis(milli):
    '''
    Accepts milliseconds and returns this value as HH:MM:SS.NNN
    '''
    a = datetime.timedelta(milliseconds=milli)
    b = str(a)
    # no millseconds are present if there is no remainder. We need milliseconds!
    if len(b) == 7:
        b += '.000000'
    timestamp = datetime.datetime.strptime(b, "%H:%M:%S.%f").time()
    c = str(timestamp)
    if len(c) == 8:
        c += '.000000'
    return str(c)[:-3]


def send_gmail(email_to, attachment, subject, email_body, email_address, password):
    '''
    Rarely used but working emailer.
    '''
    emailfrom = ""
    emailto = email_to
    #emailto = ", ".join(emailto)
    fileToSend = attachment
    username = email_address
    password = password
    msg = MIMEMultipart()
    msg["From"]    = emailfrom
    msg["To"]      = ", ".join(emailto)
    msg["Subject"] = subject
    msg.preamble   = "testtesttest"
    body = MIMEText(email_body)
    msg.attach(body)
    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    if maintype == "text":
        fp = open(fileToSend)
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "image":
        fp = open(fileToSend, "rb")
        attachment = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "audio":
        fp = open(fileToSend, "rb")
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)
    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.ehlo() # optional, called by login()
    server_ssl.login(username, password)
    # ssl server doesn't support or need tls, so don't call server_ssl.starttls()
    server_ssl.sendmail(emailfrom, emailto, msg.as_string())
    print(msg.as_string())
    #server_ssl.quit()
    server_ssl.close()
    print(' - successfully sent the mail')

def frames_to_seconds(audio_entry_point):
    audio_frame_count = float(audio_entry_point)
    audio_frame_count = float(audio_frame_count) / 24.000 # Change to EditRate variable.
    audio_frame_count = round(audio_frame_count, 3)
    return audio_frame_count


def set_environment(logfile):
    env_dict = os.environ.copy()
    # https://github.com/imdn/scripts/blob/0dd89a002d38d1ff6c938d6f70764e6dd8815fdd/ffmpy.py#L272
    env_dict['FFREPORT'] = 'file={}:level=48'.format(logfile)
    return env_dict


def generate_log(log, what2log):
    if not os.path.isfile(log):
        with open(log, "w", encoding='utf-8') as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ")
                     + getpass.getuser()
                     + ' ' + what2log + ' \n')
    else:
        with open(log, "a", encoding='utf-8') as fo:
            fo.write(time.strftime("%Y-%m-%dT%H:%M:%S ")
                     + getpass.getuser()
                     + ' ' + what2log + ' \n')


def hashlib_md5(filename):
    '''
    uses hashlib to return an MD5 checksum of an input filename
    '''
    read_size = 0
    last_percent_done = 0
    m = hashlib.md5()
    total_size = os.path.getsize(filename)
    with open(str(filename), 'rb') as f:
        while True:
            buf = f.read(2**20)
            if not buf:
                break
            read_size += len(buf)
            m.update(buf)
            percent_done = 100 * read_size / total_size
            if percent_done > last_percent_done:
                sys.stdout.write('[%d%%]\r' % percent_done)
                sys.stdout.flush()
                last_percent_done = percent_done
    md5_output = m.hexdigest()
    return md5_output


def hashlib_sha512(filename):
    '''
    Note, this should eventually merged with the hashlib_md5 function.
    uses hashlib to return an sha512 checksum of an input filename
    '''
    read_size = 0
    last_percent_done = 0
    m = hashlib.sha512()
    total_size = os.path.getsize(filename)
    with open(str(filename), 'rb') as f:
        while True:
            buf = f.read(2**20)
            if not buf:
                break
            read_size += len(buf)
            m.update(buf)
            percent_done = 100 * read_size / total_size
            if percent_done > last_percent_done:
                sys.stdout.write('[%d%%]\r' % percent_done)
                sys.stdout.flush()
                last_percent_done = percent_done
    sha512_output = m.hexdigest()
    return sha512_output

def hashlib_manifest(manifest_dir, manifest_textfile, path_to_remove):
    '''
    Creates an MD5 manifest with relative filepaths.
    '''
    file_count = 0
    for root, directories, filenames in os.walk(manifest_dir):
        filenames = [f for f in filenames if not f[0] == '.']
        directories[:] = [d for d in directories if not d[0] == '.']
        for files in filenames:
            #print(" - Calculating number of files to process in current directory -  %s files        \r "% file_count)
            print("- Calculating number of files to process in current directory - {0} files ".format(file_count), end="\r")
            file_count += 1
    manifest_generator = ''
    md5_counter = 1
    for root, directories, filenames in os.walk(manifest_dir):
        filenames = [f for f in filenames if f[0] != '.']
        directories[:] = [d for d in directories if d[0] != '.']
        for files in filenames:
            print(' - Generating MD5 for %s - file %d of %d' % (os.path.join(root, files), md5_counter, file_count))
            md5 = hashlib_md5(os.path.join(root, files))
            md5_counter += 1
            root2 = os.path.abspath(root).replace(path_to_remove, '')
            try:
                if root2[0] == '/':
                    root2 = root2[1:]
                if root2[0] == '\\':
                    root2 = root2[1:]
            except: IndexError
            manifest_generator += md5[:32] + '  ' + os.path.join(root2, files).replace("\\", "/") + '\n'
    manifest_list = manifest_generator.splitlines()
    files_in_manifest = len(manifest_list)
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list, key=lambda x: (x[34:]))
    with open(manifest_textfile, "w", encoding='utf-8') as fo:
        for i in manifest_list:
            fo.write((unicodedata.normalize('NFC', i) + '\n'))

def sha512_manifest(manifest_dir, manifest_textfile, path_to_remove):
    '''
    Note: This should be merged with hashlib_manifest()
    Creates a sha512 manifest with relative filepaths.
    '''
    file_count = 0
    for root, directories, filenames in os.walk(manifest_dir):
        filenames = [f for f in filenames if not f[0] == '.']
        directories[:] = [d for d in directories if not d[0] == '.']
        for files in filenames:
            print(" - Calculating number of files to process in current directory -  %s files        \r"% file_count,)
            file_count += 1
    manifest_generator = ''
    md5_counter = 1
    for root, directories, filenames in os.walk(manifest_dir):
        filenames = [f for f in filenames if f[0] != '.']
        directories[:] = [d for d in directories if d[0] != '.']
        for files in filenames:
            print(' - Generating SHA512 for %s - file %d of %d' % (os.path.join(root, files), md5_counter, file_count))
            sha512 = hashlib_sha512(os.path.join(root, files))
            md5_counter += 1
            root2 = os.path.abspath(root).replace(path_to_remove, '')
            try:
                if root2[0] == '/':
                    root2 = root2[1:]
                if root2[0] == '\\':
                    root2 = root2[1:]
            except: IndexError
            manifest_generator += sha512[:128] + '  ' + os.path.join(root2, files).replace("\\", "/") + '\n'
    manifest_list = manifest_generator.splitlines()
    files_in_manifest = len(manifest_list)
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list, key=lambda x: (x[130:]))
    with open(manifest_textfile, "w", encoding='utf-8') as fo:
        for i in manifest_list:
            fo.write((unicodedata.normalize('NFC', i) + '\n'))

def hashlib_append(manifest_dir, manifest_textfile, path_to_remove):
    '''
    Lazy rehash of hashlib_manifest, except this just adds files to an existing manifest.
    '''
    file_count = 0
    for root, directories, filenames in os.walk(manifest_dir):
        filenames = [f for f in filenames if not f[0] == '.']
        directories[:] = [d for d in directories if not d[0] == '.']
        for files in filenames:
            print(" - Calculating number of files to process in current directory -  %s files        \r"% file_count,)
            file_count += 1
    manifest_generator = ''
    md5_counter = 1
    for root, directories, filenames in os.walk(manifest_dir):
        filenames = [f for f in filenames if not f[0] == '.']
        directories[:] = [d for d in directories if not d[0] == '.']
        for files in filenames:
            print(' - Generating MD5 for %s - file %d of %d' % (os.path.join(root, files), md5_counter, file_count))
            md5 = hashlib_md5(os.path.join(root, files))
            md5_counter += 1
            root2 = os.path.abspath(root).replace(path_to_remove, '')
            try:
                if root2[0] == '/':
                    root2 = root2[1:]
                if root2[0] == '\\':
                    root2 = root2[1:]
            except: IndexError
            manifest_generator += md5[:32] + '  ' + os.path.join(root2, files).replace("\\", "/") + '\n'
    manifest_list = manifest_generator.splitlines()
    files_in_manifest = len(manifest_list)
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list, key=lambda x: (x[34:]))
    with open(manifest_textfile, "a", encoding='utf-8') as fo:
        for i in manifest_list:
            fo.write((unicodedata.normalize('NFC', i) + '\n'))


def make_manifest(manifest_dir, relative_manifest_path, manifest_textfile):
    os.chdir(manifest_dir)
    if not os.path.isfile(manifest_textfile):
        manifest_generator = subprocess.check_output(['md5deep', '-ler', relative_manifest_path])
        manifest_list = manifest_generator.splitlines()
        files_in_manifest = len(manifest_list)
        # http://stackoverflow.com/a/31306961/2188572
        manifest_list = sorted(manifest_list, key=lambda x: (x[34:]))
        with open(manifest_textfile, "w", encoding='utf-8') as fo:
            for i in manifest_list:
                fo.write((unicodedata.normalize('NFC', i) + '\n'))
        return files_in_manifest
    else:
        print(' - Manifest already exists')
        sys.exit()
def make_mediatrace(tracefilename, xmlvariable, inputfilename):
    mediatrace_cmd = [
            'mediainfo',
            '-f',
            '--Details=1', '--File_TestContinuousFileNames=0', # Use verbose output.
            '--output=XML',
            inputfilename
        ]
    with open(tracefilename, "w") as fo:
        # https://stackoverflow.com/a/21486747
        try:
            xmlvariable = subprocess.check_output(mediatrace_cmd).decode(sys.stdout.encoding)
        except UnicodeDecodeError:
            try:
                xmlvariable = subprocess.check_output(mediatrace_cmd).decode('cp1252')
            except UnicodeDecodeError:
                # Some N19/STL files seem to produce characters which are incompatible with uff-8 and cp1252.
                xmlvariable = 'None'
        fo.write(xmlvariable)



def check_overwrite(file2check):
    if os.path.isfile(file2check):
        print(' - A manifest already exists at your destination. Overwrite? Y/N?')
        overwrite_destination_manifest = ''
        while overwrite_destination_manifest not in ('Y', 'y', 'N', 'n'):
            overwrite_destination_manifest = input()
            if overwrite_destination_manifest not in ('Y', 'y', 'N', 'n'):
                print(' - Incorrect input. Please enter Y or N')
        return overwrite_destination_manifest
def manifest_file_count(manifest2check):
    '''
    Checks how many entries are in a manifest
    '''
    if os.path.isfile(manifest2check):
        print(' - A manifest already exists')
        with open(manifest2check, "r") as fo:
            manifest_lines = [line.split(',') for line in fo.readlines()]
            count_in_manifest = len(manifest_lines)
    return count_in_manifest


def create_csv(csv_file, *args):
    f = open(csv_file, 'w', newline='')
    try:
        writer = csv.writer(f)
        writer.writerow(*args)
    finally:
        f.close()


def append_csv(csv_file, *args):
    f = open(csv_file, 'a', newline='')
    try:
        writer = csv.writer(f)
        writer.writerow(*args)
    finally:
        f.close()

def sort_csv(csv_file, key):
    '''
    Sorts a csv_file by a key. The key being a field heading.
    '''
    new_filename = os.path.splitext(os.path.basename(csv_file))[0] + '_sorted.csv'
    sorted_filepath = os.path.join(os.path.dirname(csv_file), new_filename)
    values, fieldnames = extract_metadata(csv_file)
    with open(sorted_filepath, 'w') as csvfile:
        newlist = sorted(values, key=operator.itemgetter(key))
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in newlist:
            writer.writerow(i)
    return sorted_filepath

def make_desktop_manifest_dir():
    desktop_manifest_dir = os.path.expanduser("~/Desktop/moveit_manifests")
    if not os.path.isdir(desktop_manifest_dir):
        #I should probably ask permission here, or ask for alternative location
        os.makedirs(desktop_manifest_dir)
        os.makedirs(os.path.join(desktop_manifest_dir, 'old_manifests'))
    else:
        if not os.path.isdir(os.path.join(desktop_manifest_dir, 'old_manifests')):
            os.makedirs(os.path.join(desktop_manifest_dir, 'old_manifests'))
    return desktop_manifest_dir


def make_desktop_logs_dir():
    desktop_logs_dir = os.path.expanduser("~/Desktop/ifiscripts_logs")
    if not os.path.isdir(desktop_logs_dir):
        #I should probably ask permission here, or ask for alternative location
        os.makedirs(desktop_logs_dir)
    return desktop_logs_dir

def get_image_sequence_files(directory):
    # This function accepts a directory as input, and checks returns a list of files in an image sequence.
    os.chdir(directory)
    tiff_check = glob('*.tiff')
    dpx_check = glob('*.dpx')
    tif_check = glob('*.tif')
    if len(dpx_check) > 0:
        images = dpx_check
        images.sort()
    elif len(tiff_check) > 0:
        images = tiff_check
        images.sort()
    elif len(tif_check) > 0:
        images = tif_check
        images.sort()
    else:
        return 'none'
    return images

def check_multi_reel(directory):
    # This function accepts a directory as input. It checks if there are
    # subdirectories that contain image sequences.
    image_sequences = []
    for dirs in os.listdir(directory):
        full_path = (os.path.join(directory, dirs))
        if os.path.isdir(full_path):
            if get_image_sequence_files(full_path) != 'none':
                image_sequences.append(full_path)
    return sorted (image_sequences)


def get_ffmpeg_friendly_name(images):
    '''
    Parses image sequence filenames so that they are easily passed to ffmpeg.
    '''
    if '864000' in images[0]:
        start_number = '864000'
    elif len(images[0].split("_")[-1].split(".")) > 2:
        start_number = images[0].split("_")[-1].split(".")[1]
    else:
        start_number = images[0].split("_")[-1].split(".")[0]
    container = images[0].split(".")[-1]
    if len(images[0].split("_")[-1].split(".")) > 2:
        numberless_filename = images[0].split(".")
    else:
        numberless_filename = images[0].split("_")[0:-1]
    ffmpeg_friendly_name = ''
    counter = 0
    if len(images[0].split("_")[-1].split(".")) > 2:
        numberless_filename = images[0].split(".")[0:-1]
        for i in numberless_filename[:-1]:
            ffmpeg_friendly_name += i + '.'
        print(ffmpeg_friendly_name)
    else:
        while  counter < len(numberless_filename):
            ffmpeg_friendly_name += numberless_filename[counter] + '_'
            counter += 1
    return ffmpeg_friendly_name, container, start_number

def parse_image_sequence(images):
    '''
    Parses image sequence filenames so that they are easily passed to ffmpeg.
    '''
    if '864000' in images[0]:
        start_number = '864000'
    elif len(images[0].split("_")[-1].split(".")) > 2:
        start_number = images[0].split("_")[-1].split(".")[1]
    else:
        start_number = images[0].split("_")[-1].split(".")[0]
    container = images[0].split(".")[-1]
    numberless_filename = images[0].split("_")[0:-1]
    ffmpeg_friendly_name = ''
    counter = 0
    if len(images[0].split("_")[-1].split(".")) > 2:
        numberless_filename = images[0].split(".")[0:-1]
        for i in numberless_filename[:-1]:
            ffmpeg_friendly_name += i + '.'
    else:
        while counter < len(numberless_filename):
            ffmpeg_friendly_name += numberless_filename[counter] + '_'
            counter += 1

    if len(images[0].split("_")[-1].split(".")) > 2:
        image_seq_without_container = ffmpeg_friendly_name[:-1] + ffmpeg_friendly_name[-1].replace('_', '.')
        ffmpeg_friendly_name = image_seq_without_container
    start_number_length = len(start_number)
    number_regex = "%0" + str(start_number_length) + 'd.'
    # remove trailing underscore
    root_filename = ffmpeg_friendly_name[:-1]
    ffmpeg_friendly_name += number_regex + '%s' % container
    fps = get_mediainfo('duration', '--inform=Image;%FrameRate%', images[0])
    if fps == '':
        fps = 24
    return ffmpeg_friendly_name, start_number, root_filename, fps


def get_date_modified(filename):
    """Gets the date modified date of a filename in ISO8601 style.

    Date created values seem to be difficult to grab in a cross-platform way.


        Args:
            filename: Path of filename to check.

        Returns:
            date_modified: string, for example '2016-12-19T21:30:43'

        """
    epoch_time = os.path.getmtime(filename)
    date_modified = datetime.datetime.fromtimestamp(epoch_time).strftime("%Y-%m-%dT%H:%M:%S")
    return date_modified


def create_uuid():
    '''
    Returns a randonly generated UUID as a string
    '''
    new_uuid = str(uuid.uuid4())
    return new_uuid

def make_folder_structure(path):
    '''
    Makes logs, objects, metadata directories in the supplied path
    UNITTEST - do paths exist
    '''
    metadata_dir = "%s/metadata" % path
    log_dir = "%s/logs" % path
    data_dir = "%s/objects" % path
    # Actually create the directories.
    os.makedirs(metadata_dir)
    os.makedirs(data_dir)
    os.makedirs(log_dir)


def get_user():
    '''
    Asks user who they are. Returns a string with their name
    '''
    user = ''
    if user not in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'):
        user = input(
            '\n\n**** Who are you?\nPress 1,2,3,4,5,6,7,8,9,10,11,12,13,14\n\n1.\tKieran O\'Leary\n2.\tRaelene Casey\n3.\tAoife Fitzmaurice\n4.\tYujing Huang\n5.\tNoelia Romero\n6.\tAna Truchanova\n7.\tEoin O\'Donohoe\n8.\tGavin Martin\n9.\tNiamh Murphy\n10.\tRaven Cooke\n11.\tNiall Anderson\n12.\tYazhou He\n13.\tCaroline Crowther\n14.\tMark Keleghan\n'
        )
        while user not in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'):
            user = input(
                '\n\n**** Who are you?\nPress 1,2,3,4,5,6,7,8,9,10,11,12,13,14\n\n1.\tKieran O\'Leary\n2.\tRaelene Casey\n3.\tAoife Fitzmaurice\n4.\tYujing Huang\n5.\tNoelia Romero\n6.\tAna Truchanova\n7.\tEoin O\'Donohoe\n8.\tGavin Martin\n9.\tNiamh Murphy\n10.\tRaven Cooke\n11.\tNiall Anderson\n12.\tYazhou He\n13.\tCaroline Crowther\n14.\tMark Keleghan\n'
            )
    if user == '1':
        user = 'Kieran O\'Leary'
        time.sleep(1)
    elif user == '2':
        user = 'Raelene Casey'
        time.sleep(1)
    elif user == '3':
        user = 'Aoife Fitzmaurice'
        time.sleep(1)
    elif user == '4':
        user = 'Yujing Huang'
        time.sleep(1)
    elif user == '5':
        user = 'Noelia Romero'
        time.sleep(1)
    elif user == '6':
        user = 'Ana Truchanova'
        time.sleep(1)
    elif user == '7':
        user = 'Eoin O\'Donohoe'
        time.sleep(1)
    elif user == '8':
        user = 'Gavin Martin'
        time.sleep(1)
    elif user == '9':
        user = 'Niamh Murphy'
        time.sleep(1)
    elif user == '10':
        user = 'Raven Cooke'
        time.sleep(1)
    elif user == '11':
        user = 'Niall Anderson'
        time.sleep(1)
    elif user == '12':
        user = 'Yazhou He'
        time.sleep(1)
    elif user == '13':
        user = 'Caroline Crowther'
        time.sleep(1)
    elif user == '14':
        user = 'Mark Keleghan'
        time.sleep(1)
    return user


def determine_user(args):
    '''
    Determine who is the user.
    UNITTEST - check if user is a string. Use mock to simulate input.
    '''
    if args.user:
        user = args.user
    else:
        user = get_user()
    return user


def get_acquisition_type(acquisition_type):
    '''
    Asks user for the type of acquisition
    '''
    if acquisition_type not in ('1', '2', '4', '5', '7', '8', '13', '14'):
        acquisition_type = input(
            '\n\n**** What is the type of acquisition? - This will not affect Reproductions that have been auto-detected.\nPress 1,2,4,5,7,8,13,14\n\n1. IFB -  deposited  in compliance with IFB delivery requirements\n2. BAI  - deposited  in compliance with BAI delivery requirements\n4. Deposit\n5. Purchased for collection\n7. Unknown at present\n8. Arts Council- deposited in compliance with Arts council delivery requirements\n13. Reproduction\n14. Donation\n'
        )
        while acquisition_type not in ('1', '2', '4', '5', '7', '8', '13', '14'):
            acquisition_type = input(
                '\n\n**** What is the type of acquisition? - This will not affect Reproductions that have been auto-detected.\nPress 1,2,4,5,7,8,13,14\n\n1. IFB -  deposited  in compliance with IFB delivery requirements\n2. BAI  - deposited  in compliance with BAI delivery requirements\n4. Deposit\n5. Purchased for collection\n7. Unknown at present\n8. Arts Council- deposited in compliance with Arts council delivery requirements\n13. Reproduction\n14. Donation\n'
            )
    if acquisition_type == '1':
        acquisition_type = ['1. IFB -  deposited  in compliance with IFB delivery requirements', 'Deposit', '1']
        time.sleep(1)
    elif acquisition_type == '2':
        acquisition_type = ['2. BAI  - deposited  in compliance with BAI delivery requirements', 'Deposit', '2']
        time.sleep(1)
    elif acquisition_type == '4':
        acquisition_type = ['4. Deposit', 'Deposit', '4']
        time.sleep(1)
    elif acquisition_type == '5':
        acquisition_type = ['5. Purchased for collection', 'Purchase', '5']
        time.sleep(1)
    elif acquisition_type == '7':
        acquisition_type = ['7. Unknown at present', 'Unknown', '7']
        time.sleep(1)
    elif acquisition_type == '8':
        acquisition_type = ['Arts Council- deposited in compliance with Arts council delivery requirements', 'Deposit', '8']
        time.sleep(1)
    elif acquisition_type == '13':
        acquisition_type = ['Reproduction', 'Reproduction', '13']
        time.sleep(1)
    elif acquisition_type == '14':
        acquisition_type = ['Donation', 'Donation', '14']
        time.sleep(1)
    return acquisition_type
def sort_manifest(manifest_textfile):
    '''
    Sorts an md5 manifest in alphabetical order.
    Some scripts like moveit.py will require a manifest to be ordered like this.
    '''
    with open(manifest_textfile, "r", encoding='utf-8') as fo:
        manifest_lines = fo.readlines()
        with open(manifest_textfile, "w", encoding='utf-8') as ba:
            manifest_list = sorted(manifest_lines, key=lambda x: (x[34:]))
            for i in manifest_list:
                ba.write(i)

def concat_textfile(video_files, concat_file):
    '''
    Create concat textfile for all files in video_files
    a condition is needed elsewhere to ensure concat_file is empty
    '''
    for video in video_files:
        with open(concat_file, 'a') as textfile:
            textfile.write('file \'%s\'\n' % video)


def sanitise_filenames(video_files):
    '''
    this just replaces quotes with underscores.
    only used right now to make concat scripts work.
    The change should only happen if user says YES
    previous and current filename should be logged.
    Also there should be a better way of returning the list.
    '''
    overwrite = ''
    renamed_files = []
    for video in video_files:
        if '\'' in video:
            print(' - A quote is in your filename %s , replace with underscore?' % video)
            while overwrite not in ('Y', 'y', 'N', 'n'):
                overwrite = input()
                if overwrite not in ('Y', 'y', 'N', 'n'):
                    print(' - Incorrect input. Please enter Y or N')
                if overwrite in ('Y', 'y'):
                    rename = video.replace('\'', '_')
                    os.rename(video, rename)
                    renamed_files.append(rename)
        else:
            renamed_files.append(video)
    return renamed_files


def get_temp_concat(root_name):
    '''
    generates a temp file as a textfile for ffmpeg concatenation.
    '''
    temp_dir = tempfile.gettempdir()
    video_concat_filename = os.path.basename(
        root_name) + '_video_concat' + time.strftime("_%Y_%m_%dT%H_%M_%S")
    # Slashes are significant for ffmpeg concat files.
    if sys.platform == "win32":
        video_concat_textfile = temp_dir + "\%s.txt" % video_concat_filename
    else:
        video_concat_textfile = temp_dir + "/%s.txt" % video_concat_filename
    return video_concat_textfile

def get_script_version(scriptname):
    '''
    uses git to get SHA:DATETIME for a script
    '''
    current_dir = os.getcwd()
    home = os.path.expanduser("~/")
    os.chdir(home)
    pypi = ''
    try:
        if platform.system() == 'Windows':
            pypi_cmd = ['pip', 'show', 'ifiscripts']
        else:
            pypi_cmd = ['pip3', 'show', 'ifiscripts']
        pypi = subprocess.check_output(pypi_cmd)
        pypi = pypi.decode()
    except Exception as e:
        print(e)
    if pypi:
        v = 'Version'
        v_end = 'Summary'
        script_version = pypi[pypi.index(v):pypi.index(v_end)].replace('\n', '').replace('\r', '')
        print("ifiscripts installed from pypi - %s" % script_version)
    elif os.path.isdir('ifigit/ifiscripts/scripts'):
        os.chdir('ifigit/ifiscripts/scripts')
        print("Changing directory to %s to extract script version`" % os.getcwd())
        script_version = subprocess.check_output([
            'git', 'log', '-n', '1', '--pretty=format:%H:%aI', scriptname
        ])
    else:
        script_version = 'Script version unavailable as the ifiscripts repository is not installed in $HOME/ifigit/ifiscripts'
    os.chdir(current_dir)
    return script_version


def validate_uuid4(uuid_string):

    """
    Validate that a UUID string is in
    fact a valid uuid4.

    Written by ShawnMilo
    https://gist.github.com/ShawnMilo/7777304#file-validate_uuid4-py
    """

    try:
        uuid.UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False

def get_source_uuid():
    '''
    Asks user for uuid. A valid uuid must be provided.
    '''
    source_uuid = False
    while source_uuid is False:
        uuid_ = input(
            '\n\n**** Please enter the UUID of the source representation\n\n'
        )
        source_uuid = validate_uuid4(uuid_)
    return uuid_


def ask_question(question):
    '''
    Asks user a question. Return answer.
    '''
    answer = ''
    while answer == '':
        answer = input(
            '\n\n**** %s\n\n'
         % question)
    proceed = 'n'
    while proceed.lower() == 'n':
        proceed = ask_yes_no('Are you really sure?')
    return answer

def get_object_entry():
    '''
    Asks user for an Object Entry number. A valid Object Entry (OE####) must be provided.
    '''
    object_entry = False
    while object_entry is False:
        object_entry = input(
            '\n\n**** Please enter the object entry number of the representation\n\n'
        )
        if object_entry[:4] == 'scoe':
            return object_entry
        if object_entry[:2] != 'oe':
            print(' - First two characters must be \'oe\' and last four characters must be four digits')
            object_entry = False
        elif len(object_entry[2:]) not in range(4, 6):
            object_entry = False
            print(' - First two characters must be \'oe\' and last four characters must be four digits')
        elif not object_entry[2:].isdigit():
            object_entry = False
            print(' - First two characters must be \'oe\' and last four characters must be four digits')
        else:
            return object_entry

def get_accession_number():
    '''
    Asks user for an accession number. A valid number (OE####) must be provided.
    '''
    accession_number = False
    while accession_number is False:
        accession_number = input(
            '\n\n**** Please enter the accession number of the representation\n\n'
        )
        if accession_number[:3] != 'aaa':
            print(' - First three characters must be \'aaa\' and last four characters must be four digits')
            accession_number = False
        elif len(accession_number[3:]) != 4:
            accession_number = False
            print(' - First three characters must be \'aaa\' and last four characters must be four digits')
        elif not accession_number[3:].isdigit():
            accession_number = False
            print(' - First three characters must be \'aaa\' and last four characters must be four digits')
        else:
            return accession_number

def get_reference_number():
    '''
    Asks user for a Filmographic reference number. Due to the variety of reference numbers, validation
    will be removed for now.
    '''
    reference_number = input(
        '\n\n**** Please enter the Filmographic reference number of the representation- if there is more than one work that is represented, seperate them with an ampersand, eg af1234&aa675\n\n'
    )
    return reference_number.upper()

def get_contenttitletext(cpl):
    '''
    Returns the <ContentTitleText> element text from a DCP CPL.xml
    '''
    cpl_parse = etree.parse(cpl)
    cpl_namespace = cpl_parse.xpath('namespace-uri(.)')
    contenttitletext = cpl_parse.findtext('//ns:ContentTitleText', namespaces={'ns': cpl_namespace})
    return contenttitletext


def find_cpl(source):
    '''
    Recursively searchs through all files in order to find a DCI DCP CPL XML.
    '''
    for root, _, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith('.xml'):
                if filename[0] != '.':
                    cpl_parse = etree.parse(os.path.join(root, filename))
                    cpl_namespace = cpl_parse.xpath('namespace-uri(.)')
                    if 'CPL' in cpl_namespace:
                        return os.path.join(root, filename)

def ask_yes_no(question):
    '''
    Returns Y or N. The question variable is just a string.
    '''
    answer = ''
    print(' - \n', question, '\n', 'enter Y or N')
    while answer not in ('Y', 'y', 'N', 'n'):
        answer = input()
        if answer not in ('Y', 'y', 'N', 'n'):
            print(' - Incorrect input. Please enter Y or N')
        if answer in ('Y', 'y'):
            return 'Y'
        elif answer in ('N,' 'n'):
            return 'N'

def manifest_replace(manifest, to_be_replaced, replaced_with):
    '''
    Replace strings in a checksum manifest (or any textfile)
    Ideally, this should never replace the checksum, just a path alteration.
    Although this could be useful for changing the logs checksum value.
    '''
    with open(manifest, 'r') as fo:
        original_lines = fo.readlines()
    with open(manifest, 'w') as ba:
        for lines in original_lines:
            new_lines = lines.replace(to_be_replaced, replaced_with)
            ba.write(new_lines)

def manifest_update(manifest, path):
    '''
    Adds a new entry to your manifest and sort.
    '''
    manifest_generator = ''
    with open(manifest, 'r', encoding='utf-8') as fo:
        original_lines = fo.readlines()
        md5 = hashlib_md5(path)
        path_to_remove = os.path.dirname(os.path.dirname(os.path.dirname(path)))
        root2 = os.path.abspath(path).replace(path_to_remove, '')
        try:
            if root2[0] == '/':
                root2 = root2[1:]
            if root2[0] == '\\':
                root2 = root2[1:]
        except: IndexError
        manifest_generator += md5[:32] + '  ' + root2.replace("\\", "/") + '\n'
        for i in original_lines:
            manifest_generator += i
    manifest_list = manifest_generator.splitlines()
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list, key=lambda x: (x[34:]))
    with open(manifest, "w", encoding='utf-8') as fo:
        for i in manifest_list:
            fo.write((unicodedata.normalize('NFC', i) + '\n'))

def sha512_update(manifest, path):
    '''
    Adds a new entry to your sha512 manifest and sort.
    Yet another SHA512 script that needs to be merged with the MD5 functions.
    '''
    manifest_generator = ''
    with open(manifest, 'r', encoding='utf-8') as fo:
        original_lines = fo.readlines()
        sha512 = hashlib_sha512(path)
        path_to_remove = os.path.dirname(os.path.dirname(os.path.dirname(path)))
        root2 = os.path.abspath(path).replace(path_to_remove, '')
        try:
            if root2[0] == '/':
                root2 = root2[1:]
            if root2[0] == '\\':
                root2 = root2[1:]
        except: IndexError
        manifest_generator += sha512[:128] + '  ' + root2.replace("\\", "/") + '\n'
        for i in original_lines:
            manifest_generator += i
    manifest_list = manifest_generator.splitlines()
    # http://stackoverflow.com/a/31306961/2188572
    manifest_list = sorted(manifest_list, key=lambda x: (x[130:]))
    with open(manifest, "w", encoding='utf-8') as fo:
        for i in manifest_list:
            fo.write((unicodedata.normalize('NFC', i) + '\n'))
def check_for_uuid(args):
    '''
    Tries to check if a filepath contains a UUID.
    Returns false if an invalid UUID is found
    Returns the UUID if a UUID is found.
    TO_BE_DEPRECATED in favour of check_for_uuid_generic
    '''
    source_uuid = False
    while source_uuid is False:
        if validate_uuid4(os.path.basename(args.i[0])) != False:
            return os.path.basename(args.i[0])
        else:
            returned_dir = check_for_sip(args.i)
            if returned_dir is None:
                return False
            uuid_check = os.path.basename(returned_dir)
            if validate_uuid4(uuid_check) != False:
                return uuid_check
            else:
                return source_uuid

def check_for_uuid_generic(source):
    '''
    Tries to check if a filepath contains a UUID.
    Returns false if an invalid UUID is found
    Returns the UUID if a UUID is found.
    Duplicate of the previous function without the silly
    args object hardcoding.
    '''
    source_uuid = False
    while source_uuid is False:
        if validate_uuid4(os.path.basename(source)) != False:
            return os.path.basename(source)
        else:
            return False
        '''
        else:
            returned_dir = check_for_sip_generic(source)
            if returned_dir is None:
                return False
            uuid_check = os.path.basename(returned_dir)
            if validate_uuid4(uuid_check) != False:
                return uuid_check
            else:
                return source_uuid
        '''


def check_for_sip(args):
    '''
    This checks if the input folder contains the actual payload, eg:
    the UUID folder(containing logs/metadata/objects) and the manifest sidecar.
    Just realised that args.i can be a list, but for our main concat workflow, a single dir will be passed.
    Hence the args[0]
    Also choose a better variable name than args as args=/a/path here.
    '''
    for filenames in os.listdir(args[0]):
        if 'manifest.md5' in filenames:
            dircheck = filenames.replace('_manifest.md5', '')
            if os.path.isdir(os.path.join(args[0], dircheck)):
                return os.path.join(args[0], dircheck)

def check_for_sip_generic(source):
    '''
    This checks if the input folder contains the actual payload, eg:
    the UUID folder(containing logs/metadata/objects) and the manifest sidecar.
    Just realised that args.i can be a list, but for our main concat workflow, a single dir will be passed.
    Hence the args[0]
    Also choose a better variable name than args as args=/a/path here.
    '''
    for filenames in os.listdir(source):
        if 'manifest.md5' in filenames:
            dircheck = filenames.replace('_manifest.md5', '')
            if os.path.isdir(os.path.join(source, dircheck)):
                return os.path.join(source, dircheck)

def checksum_replace(manifest, logname, algorithm):
    '''
    Update a value in a checksum manifest.
    Variables just refer to lognames right now, which is the only thing that needs to change at the moment.
    '''
    updated_manifest = []
    if algorithm == 'md5':
        new_checksum = hashlib_md5(logname)
    elif algorithm == 'sha512':
        new_checksum = hashlib_sha512(logname)
    with open(manifest, 'r', encoding='utf-8') as manifesto:
        manifest_lines = manifesto.readlines()
        for lines in manifest_lines:
            if os.path.basename(logname) in lines:
                if algorithm == 'md5':
                    lines = lines[31:].replace(lines[31:], new_checksum + lines[32:])
                elif algorithm == 'sha512':
                    lines = lines[127:].replace(lines[127:], new_checksum + lines[128:])
            updated_manifest.append(lines)
    with open(manifest, 'w', encoding='utf-8') as fo:
        for lines in updated_manifest:
            fo.write(lines)

def img_seq_pixfmt(start_number, path):
    '''
    Determine the pixel format of an image sequence
    '''
    ffprobe_cmd = [
        'ffprobe',
        '-start_number', start_number,
        '-i', path,
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries',
        'stream=pix_fmt',
        '-of', 'default=noprint_wrappers=1:nokey=1'
    ]
    pix_fmt = subprocess.check_output(ffprobe_cmd).rstrip().decode(sys.stdout.encoding)
    return pix_fmt

def get_ffmpeg_fmt(path, file_type):
    '''
    Determine the pixel format or audio format of a file
    '''
    if file_type == 'audio':
        stream = 'a'
        metadata = 'stream=codec_name'
    if file_type == 'video':
        stream = 'v:0'
        metadata = 'stream=pix_fmt'
    ffprobe_cmd = [
        'ffprobe',
        '-i', path,
        '-v', 'error',
        '-select_streams', stream,
        '-show_entries',
        metadata,
        '-of', 'default=noprint_wrappers=1:nokey=1'
    ]
    pix_fmt = subprocess.check_output(ffprobe_cmd).rstrip().decode(sys.stdout.encoding).replace("\n", '|').replace("\r", '')
    return pix_fmt

def get_number_of_tracks(path):
    '''
    Get number of tracks in a instantationTracks style output
    http://pbcore.org/pbcoreinstantiation/instantiationtracks/
    '''
    ffprobe_cmd = [
        'ffprobe',
        '-i', path,
        '-v', 'error',
        '-show_entries',
        'stream=codec_type',
        '-of', 'default=noprint_wrappers=1:nokey=1'
    ]
    type_list = subprocess.check_output(ffprobe_cmd).rstrip().decode(sys.stdout.encoding).splitlines()
    types = {}
    final_count = ''
    for i in type_list:
        if not i in types:
            types[i] = 1
        else:
            types[i] += 1
    for x in types:
        if types[x] > 1:
            final_count += '%s %s tracks|' % (types[x], x)
        else:
            final_count += '%s %s track|' % (types[x], x)
    return final_count[:-1]


def read_lines(infile):
    '''
    Returns line number and text from an textfile.
    '''
    for lineno, line in enumerate(infile):
        yield lineno, line


def merge_logs(log_name_source, sipcreator_log, sipcreator_manifest):
    '''
    merges the contents of one log with another.
    updates checksums in your manifest.
    '''
    with open(log_name_source, 'r') as concat_log:
        concat_lines = concat_log.readlines()
    with open(sipcreator_log, 'r') as sipcreator_log_object:
        sipcreator_lines = sipcreator_log_object.readlines()
    with open(sipcreator_log, 'w') as fo:
        for lines in concat_lines:
            fo.write(lines)
        for remaining_lines in sipcreator_lines:
            fo.write(remaining_lines)
    checksum_replace(sipcreator_manifest, sipcreator_log, 'md5')

def merge_logs_append(log_name_source, sipcreator_log, sipcreator_manifest):
    '''
    merges the contents of one log with another.
    updates checksums in your manifest.
    This is almost identical to the merge_logs function,except that log_name_source
    is appended to sipcreator_log,not prepended.
    '''
    with open(log_name_source, 'r', encoding='utf-8') as concat_log:
        concat_lines = concat_log.readlines()
    with open(sipcreator_log, 'r', encoding='utf-8') as sipcreator_log_object:
        sipcreator_lines = sipcreator_log_object.readlines()
    with open(sipcreator_log, 'w', encoding='utf-8') as fo:
        for lines in sipcreator_lines:
            fo.write(lines)
        for remaining_lines in concat_lines:
            fo.write(remaining_lines)
    checksum_replace(sipcreator_manifest, sipcreator_log, 'md5')
def logname_check(basename, logs_dir):
    '''
    Currently we have a few different logname patterns in our packages.
    This attempts to return the appropriate one.
    '''
    makeffv1_logfile = os.path.join(
        logs_dir, basename +'.mov_log.log')
    generic_logfile = os.path.join(
        logs_dir, basename +'_log.log')
    mxf_logfile = os.path.join(
        logs_dir, basename +'.mxf_log.log')
    sipcreator_logfile = os.path.join(
        logs_dir, basename + '_sip_log.log')
    mkv_log = os.path.join(
        logs_dir, basename +'.mkv_log.log')
    if os.path.isfile(makeffv1_logfile):
        return makeffv1_logfile
    if os.path.isfile(generic_logfile):
        return generic_logfile
    if os.path.isfile(mxf_logfile):
        return mxf_logfile
    if os.path.isfile(sipcreator_logfile):
        return sipcreator_logfile
    if os.path.isfile(mkv_log):
        return mkv_log


def log_results(manifest, log, parent_dir):
    '''
    Updates the existing log file.
    '''
    updated_manifest = []
    basename = os.path.basename(manifest).replace('_manifest.md5', '')
    sip_dir = parent_dir
    logs_dir = os.path.join(sip_dir, 'logs')
    logname = logname_check(basename, logs_dir)
    logfile = os.path.join(logs_dir, logname)
    ififuncs.generate_log(
        log,
        'EVENT = Logs consolidation - Log from %s merged into %s' % (log, logfile)
    )
    if os.path.isfile(logfile):
        with open(log, 'r') as fo:
            validate_log = fo.readlines()
        with open(logfile, 'a') as ba:
            for lines in validate_log:
                ba.write(lines)
    with open(manifest, 'r') as manifesto:
        manifest_lines = manifesto.readlines()
        for lines in manifest_lines:
            if os.path.basename(logname) in lines:
                lines = lines[:31].replace(lines[:31], ififuncs.hashlib_md5(logfile)) + lines[32:]
            updated_manifest.append(lines)
    with open(manifest, 'w') as fo:
        for lines in updated_manifest:
            fo.write(lines)

def find_parent(sipcreator_log,oe_uuid_dict):
    '''
    Looks through a concat logfile in order to determine the parent OE number.
    This will also tell you if an object has no parent.
    '''
    with open(sipcreator_log, 'r') as log_object:
        line_check = ''
        log_lines = log_object.readlines()
        for line in log_lines:
            if "source=" in line:
                if validate_uuid4(line.rstrip()[-36:]) is not False:
                    line_check = 'has_source'
                    for oe, uuid in oe_uuid_dict.iteritems():
                        if uuid == line.rstrip()[-36:]:
                            source = oe
                            return '%s has a parent: %s ' % (os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(sipcreator_log)))), source)
        if line_check == '':
            return '%s not a child of another package' % os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(sipcreator_log))))

def find_concat_user(sipcreator_log):
    '''
    Looks through a concat logfile in order to determine the user.
    '''
    with open(sipcreator_log, 'r') as log_object:
        line_check = ''
        log_lines = log_object.readlines()
        for line in log_lines[:5]:
            if "EVENT = agentName=" in line:
                line_check = line.split('agentName=')[1].rstrip()
            else:
                continue
        return line_check


def group_ids(source):
    '''''
    groups a uuid with its parent uuid in a dictionary
    '''
    uuid_oe_dict = {}
    for root, dirnames, _ in os.walk(source):
        if os.path.basename(root)[:2] == 'oe':
            if validate_uuid4(dirnames[0]) is not False:
                uuid_oe_dict[os.path.basename(root)] = dirnames[0]
        # check for accessioned packages
        elif os.path.basename(root)[:3] == 'aaa':
            if validate_uuid4(dirnames[0]) is not False:
                uuid_oe_dict[os.path.basename(root)] = dirnames[0]
    return uuid_oe_dict

def convert_ms2frames(fps, ms):
    # taken from https://github.com/atvKumar/Scene_Cut_Detection/blob/93622d250dc38907ee7d3ee8d925c4bfb76129b6/timecode_utils.py'
    # I am worried that this does not produce 100% accurate values, however
    # when the returned value is used as the source for convert_timecode(), 
    # then the HH:MM:SS:FF value seems accurate.
    """Converts Milliseconds to frames
    :param: Video Frame Rate e.g '25'
    :return: Integer (framerate)"""
    return int(round(float(fps) / 1000 * float(ms)))


def convert_timecode(fps, timecode):
    #taken  fromhttps://github.com/atvKumar/Scene_Cut_Detection/blob/93622d250dc38907ee7d3ee8d925c4bfb76129b6/timecode_utils.py
    """Converts HH:MM:SS.mm to HH:MM:SS:FF"""
    timecode = timecode.strip()
    hh, mm, ss_ms = timecode.split(':')
    ss, ms = ss_ms.split('.')
    ff = convert_ms2frames(fps, ms)
    if len(str(ff)) < 2:
        ff = str(ff).zfill(2)
    return str(hh) + ':' + str(mm) + ':' + str(ss) + ':' + str(ff)


def recursive_file_list(video_files):
    '''
    Recursively searches through directories for AV files and adds to a list.
    '''
    recursive_list = []
    for root, _, filenames in os.walk(video_files):
        for filename in filenames:
            if filename.endswith(('.MP4', '.mp4', '.mov', '.mkv', '.mxf', '.MXF', '.WAV', '.wav', '.aiff', '.AIFF', 'mp3', 'MP3', 'm2t', '.dv', '.DV', '.iso', '.ISO')):
                recursive_list.append(os.path.join(root, filename))
    return recursive_list


def get_video_files(source):
    '''
    Generates a list of video files.
    '''
    file_list = []
    if os.path.isdir(source):
        folder_list = os.listdir(source)
        for filename in folder_list:
            if not filename[0] == '.':
                if filename.lower().endswith(('.mov', 'MP4', '.mp4', '.mkv', '.MXF', '.mxf', '.dv', '.DV', '.3gp', '.webm', '.swf', '.avi', '.m2t', '.iso', '.ISO')):
                    file_list.append(os.path.join(source, filename))
    elif os.path.isfile(source):
        file_list = [source]
    return file_list

def extract_metadata(csv_file):
    '''
    Read the csv and store the data in a list of dictionaries.
    '''
    object_dictionaries = []
    input_file = csv.DictReader(open(csv_file, encoding='utf-8'))
    headers = input_file.fieldnames
    for rows in input_file:
        object_dictionaries.append(rows)
    return object_dictionaries, headers

def check_dependencies(dependencies):
    '''
    Checks a list of external subprocess dependencies and informs the user
    if anything is missing.
    '''
    for dependency in dependencies:
        try:
            a = subprocess.check_output([dependency, '-h'], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            # Currently this is just a workaround for Siegfried.
            if e.returncode == 2:
                continue
        except OSError:
            print('%s is not installed, so this script can not run!' % dependency)
            sys.exit()


def get_folder_size(folder):
    '''
    Get the size fo all files in a folder. Recursive process.
    https://stackoverflow.com/a/1392549/2188572
    '''
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except OSError:
                continue
    return total_size


def get_free_space(dirname):
    '''
    https://stackoverflow.com/a/2372171/2188572
    Return folder/drive free space (in bytes).
    '''
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(dirname)
        return st.f_bavail * st.f_frsize


def get_digital_object_descriptor(source_folder):
    '''
    Returns high level identifier for simple identification purposes in our
    database. Values include 'XDCAM EX', 'Matroska', 'QuickTime', 'Multiple Quicktimes'
    '''
    mov_count = 0
    mkv_count = 0
    mp4_count = 0
    wav_count = 0
    aiff_count = 0
    mp3_count = 0
    stl_count = 0
    mxf_count = 0
    m2t_count = 0
    BPAV = False
    as11 = False
    dig_object_descriptor = ''
    for root, _, filenames in os.walk(source_folder):
        if os.path.basename(root) == 'BPAV':
            BPAV = True
        for filename in filenames:
            if filename.lower().endswith('mkv'):
                mkv_count += 1
            elif filename.lower().endswith('mov'):
                mov_count += 1
            elif filename.lower().endswith('mp4'):
                mp4_count += 1
            elif filename.lower().endswith('wav'):
                wav_count += 1
            elif filename.lower().endswith('aiff'):
                aiff_count += 1
            elif filename.lower().endswith('mp3'):
                mp3_count += 1
            elif filename.lower().endswith('stl'):
                stl_count += 1
            elif filename.lower().endswith('m2t'):
                m2t_count += 1
            elif filename.lower().endswith('mxf'):
                mxf_count += 1
                try:
                    as_11_check = subprocess.check_output(['mediainfo', os.path.join(root, filename)]).decode(sys.stdout.encoding)
                except UnicodeDecodeError:
                    as_11_check = str(subprocess.check_output(['mediainfo', os.path.join(root, filename)]))
                if 'as-11' in as_11_check.lower():
                    as11 = True
    if mkv_count == 1:
        dig_object_descriptor = 'Matroska'
    elif stl_count == 1:
        if mxf_count == 1:
            if as11 == True:
                dig_object_descriptor = 'AS-11 package (STL)'
    elif mxf_count == 1:
        if stl_count == 0:
            if as11 == True:
                dig_object_descriptor = 'AS-11 package'
    elif mov_count == 1:
        dig_object_descriptor = 'QuickTime'
    elif wav_count == 1:
        dig_object_descriptor = 'Wave'
    elif aiff_count == 1:
        dig_object_descriptor = 'AIFF'
    elif mp3_count == 1:
        dig_object_descriptor = 'MP3'
    elif mov_count > 1:
        dig_object_descriptor = 'Multiple QuickTimes'
    elif mp4_count >= 1:
        if BPAV is True:
            dig_object_descriptor = 'XDCAM EX'
    elif m2t_count >= 1:
        dig_object_descriptor = 'MPEG-2 Transport Stream'
    return dig_object_descriptor

def check_for_fcp(filename):
    '''
    Final Cut Pro 7 Capture files have some significant missing metadata that
    seriously affect how the image is presented. This function will check to see
    if PAL video does not have field order and aspect ratio metadata stored in the
    container.
    '''
    par = subprocess.check_output(
        [
            'mediainfo', '--Language=raw', '--Full',
            "--Inform=Video;%PixelAspectRatio%", filename
        ]
        ).rstrip()
    field_order = subprocess.check_output(
        [
            'mediainfo', '--Language=raw',
            '--Full', "--Inform=Video;%ScanType%", filename
        ]
        ).rstrip()
    height = subprocess.check_output(
        [
            'mediainfo', '--Language=raw',
            '--Full', "--Inform=Video;%Height%",
            filename
        ]
        ).rstrip()
    width = subprocess.check_output(
        [
            'mediainfo', '--Language=raw',
            '--Full', "--Inform=Video;%Width%",
            filename
        ]
        ).rstrip()
    if par == '1.000':
        if field_order == '':
            if height == '576':
                if width == '720':
                    return True

def check_for_blackmagic(filename):
    '''
    Blackmagic Media Express writes a lot of significant metadata
    to a MOV file that needs to be specified or altered when migrating
    to FFV1/Matroska. For example, BME writes a clap atom and a pasp
    atom in the mov file that sipulates a clean aperture width of 702
    along with a pixel aspect ratio of 1.093. This will result in the MKV
    file having a DAR of 1.38 rather than 1.33.
    '''
    par_clap = subprocess.check_output(
        [
            'mediainfo', '--Language=raw', '--Full',
            "--Inform=Video;%PixelAspectRatio_CleanAperture%", filename
        ]
        ).rstrip()
    scan_order = subprocess.check_output(
        [
            'mediainfo', '--Language=raw',
            '--Full', "--Inform=Video;%ScanOrder%", filename
        ]
        ).rstrip()
    height_clap = subprocess.check_output(
        [
            'mediainfo', '--Language=raw',
            '--Full', "--Inform=Video;%Height_CleanAperture%",
            filename
        ]
        ).rstrip()
    width_clap = subprocess.check_output(
        [
            'mediainfo', '--Language=raw',
            '--Full', "--Inform=Video;%Width_CleanAperture%",
            filename
        ]
        ).rstrip()
    print(par_clap, scan_order, height_clap, width_clap)
    if par_clap == '1.093':
        if scan_order == 'TFF':
            if height_clap == '576':
                if width_clap == '702':
                    return True
def read_non_comment_lines(infile):
    '''
    This was pulled from makeffv1, and it looks like the key line has actually been commented out.
    So not sure what's going on here exactly :(
    '''
    # Adapted from Andrew Dalke - http://stackoverflow.com/a/8304087/2188572
    for lineno, line in enumerate(infile):
        #if line[:1] != "#":
        yield lineno, line


def diff_framemd5s(fmd5, fmd5ffv1):
    '''
    Generates a basic report on the differences between two framemd5 files,
    which should determine losslessness.
    '''

    checksum_mismatches = []
    with open(fmd5) as f1:
        with open(fmd5ffv1) as f2:
            for (lineno1, line1), (lineno2, line2) in zip(
                    read_non_comment_lines(f1),
                    read_non_comment_lines(f2)
                    ):
                if line1 != line2:
                    if 'sar' in line1:
                        checksum_mismatches.append('sar')
                    else:
                        checksum_mismatches.append(1)
    return checksum_mismatches

def get_mediainfo_version():
    '''
    Returns the version of mediainfo.
    If this is not possible, the string 'mediainfo' is returned.
    '''
    mediainfo_version = 'mediainfo'
    try:
        mediainfo_version = subprocess.check_output([
            'mediainfo', '--Version'
        ]).rstrip()
    except subprocess.CalledProcessError as grepexc:
        mediainfo_version = grepexc.output.rstrip().splitlines()[1]
    return mediainfo_version

def get_rawcooked_version():
    '''
    Returns the version of rawcooked.
    If this is not possible, the string 'RAWcooked' is returned.
    '''
    rawcooked_version = 'RAWcooked'
    try:
        rawcooked_version = subprocess.check_output([
            'rawcooked', '--version'
        ]).rstrip()
    except subprocess.CalledProcessError as grepexc:
        rawcooked_version = grepexc.output.rstrip().splitlines()[1]
    return rawcooked_version

def get_ffprobe_dict(source):
    '''
    Returns a dictionary via the ffprobe JSON output
    '''
    cmd = ['ffprobe', '-v', '0', '-show_versions', '-show_streams', '-show_format', '-print_format', 'json', source]
    ffprobe_json = subprocess.check_output(cmd)
    ffprobe_dict = json.loads(ffprobe_json)
    return ffprobe_dict

def get_colour_metadata(ffprobe_dict):
    '''
    Parses through a ffprobe dictionary and extracts colour metadata.
    FFmpeg options are returned. Basically, the source metadata will be respected,
    but if certain criteria are found (720/576/25fps), then if values are missing,
    they will be populated with the bt601 recommendations.
    This is currently needed as this kind of metadata is lost when normalsing from MOV
    to Matroska. If we extract the values here, we can specify what they should be in the
    normalised file.
    The multiple try except clauses here are inefficient - it would be great to make
    this better, but due to time constraints, I'm taking the sloppy way out.
    example values that are extracted from the ffprobe_dict:
    u'color_space': u'smpte170m', u'color_primaries': u'bt470bg', u'color_transfer': u'bt709'
    '''
    ffmpeg_colour_list = []
    for stream in ffprobe_dict['streams']:
        if stream['codec_type'] == 'video':
            try:
                color_trc = stream['color_transfer']
                ffmpeg_colour_list.extend(['-color_trc', color_trc])
            except KeyError:
                color_trc = ''
            try:
                colorspace = stream['color_space']
                ffmpeg_colour_list.extend(['-colorspace', colorspace])
            except KeyError:
                colorspace = ''
            try:
                color_primaries = stream['color_primaries']
                ffmpeg_colour_list.extend(['-color_primaries', color_primaries])
            except KeyError:
                color_primaries = ''
        else:
            continue
    return ffmpeg_colour_list

def get_metadata(xpath_path, root, pbcore_namespace):
    '''
    Extracts values from PBCore2 XML MediaInfo outputs.
    '''
    value = root.xpath(
        xpath_path,
        namespaces={'ns':pbcore_namespace}
    )
    if value == []:
        value = 'n/a'
    elif len(value) > 1:
        mixed_values = ''
        value_list = []
        for i in value:
            # Checks if multiple audio tracks have different values.
            '''
            if i.getparent().getparent().find(
                'ns:track',
                namespaces={'ns':pbcore_namespace}
            ).attrib['type'] == 'Audio':
            '''
            value_list.append(i.text)
        # Checks if values in the list are the same(1) or different (2)
        if len(set(value_list)) == 1:
            value = value[0].text
        else:
            # Return the mixed values with pipe delimiter.
            for x in value_list:
                mixed_values += x + '|'
            if mixed_values[-1] == '|':
                mixed_values = mixed_values[:-1]
            value = mixed_values

    else:
        value = value[0].text
    return value

def choose_cpl(cpl_list):
    # Some DCPs have multiple CPLs!
    cpl_number = 1
    print('Multiple CPL files found')
    for i in cpl_list:
        print(cpl_number,  i)
        cpl_number += 1
    print( 'Please select which CPL you would like to process')
    chosen_cpl = input()
    cpl_parse = etree.parse(cpl_list[int(chosen_cpl) - 1]) # The -1 is due to python zero-indexing.
    return cpl_list[int(chosen_cpl) - 1]


def find_cpl(source):
    # Generate an empty list as there may be multiple CPLs.
    # Get a list of all XML files in the main DCP directory.
    cpl_parse = None
    cpl_list = []
    # Loop through xmlfiles in order to find any CPLL files.
    for root, dirnames, filenames in os.walk(source):
        for i in filenames:
            if i.endswith('.xml'):
                full_path = os.path.join(root, i)
                try:
                    xmlname = etree.parse(full_path)
                except SyntaxError:
                    print( 'not a valid CPL!')
                    continue
                except KeyError:
                    print( 'Missing CPL!')
                    continue
                xml_namespace = xmlname.xpath('namespace-uri(.)')
                # Create list of CPLs.
                if 'CPL' in xml_namespace:
                    cpl_list.append(full_path)
                if len(cpl_list) == 0:
                    continue
                elif len(cpl_list) == 1:
                    cpl_parse = etree.parse(cpl_list[0])
    if len(cpl_list) > 1:
        cpl_parse = choose_cpl(cpl_list)
        # As there can be multiple subtitles, This options gives some info/choice.
        subs_confirmation  = input('Y/N')
        while subs_confirmation not in ['Y','y']:
            cpl_parse = choose_cpl()
            subs_confirmation  = input('Y/N')
            return cpl_parse
        return cpl_parse
    elif len(cpl_list) == 0:
        return None
    else:
        return cpl_list[0]


def check_av_or_doc(input):
    '''
    Checks if the input is AV or a document.
    This is a file extension check for very basic sorting.
    '''
    format = ''
    if input.lower().endswith(('.mov', 'MP4', '.mp4', '.mkv', '.MXF', '.mxf', '.dv', '.DV', '.3gp', '.webm', '.swf', '.avi', '.wav', '.WAV', '.stl', '.STL', 'm2t')):
        format = 'av'
    elif input.lower().endswith(('.tif', 'tiff', '.doc', '.txt', '.docx', '.pdf', '.jpg', '.jpeg', '.png', '.rtf', '.xml', '.odt', '.cr2', '.epub', '.ppt', '.pptx', '.xls', '.xlsx', '.gif', '.bmp', '.csv', '.zip')):
        format = 'doc'
    return format


def get_technical_metadata(path, new_log_textfile):
    '''
    Recursively create mediainfos and mediatraces for AV files.

    '''
    mediainfo_version = 'mediainfo'
    try:
        mediainfo_version = subprocess.check_output([
            'mediainfo', '--Version'
        ]).rstrip()
    except subprocess.CalledProcessError as grepexc:
        mediainfo_version = grepexc.output.rstrip().splitlines()[1]
    for root, directories, filenames in os.walk(path):
        directories[:] = [
            d for d in directories if d != 'metadata'
        ]
        for av_file in filenames:
            if check_av_or_doc(av_file.lower()) == 'av':
                if av_file[0] != '.':
                    inputxml = "%s/%s_mediainfo.xml" % (
                        os.path.join(path, 'metadata'), os.path.basename(av_file)
                        )
                    inputtracexml = "%s/%s_mediatrace.xml" % (
                        os.path.join(path, 'metadata'), os.path.basename(av_file)
                        )
                    print(' - Generating mediainfo xml of input file and saving it in %s' % inputxml)
                    make_mediainfo(
                        inputxml, 'mediaxmlinput', os.path.join(root, av_file)
                    )
                    generate_log(
                        new_log_textfile,
                        'EVENT = Metadata extraction - eventDetail=Technical metadata extraction via mediainfo, eventOutcome=%s, agentName=%s' % (inputxml, mediainfo_version)
                    )
                    print(' - Generating mediatrace xml of input file and saving it in %s' % inputtracexml)
                    make_mediatrace(
                        inputtracexml,
                        'mediatracexmlinput',
                        os.path.join(root, av_file)
                    )
                    with open(inputtracexml, 'r') as fo:
                        none_test = fo.read()
                    if none_test == 'None':
                        os.remove(inputtracexml)
                        generate_log(
                            new_log_textfile,
                            'EVENT = Metadata extraction - eventDetail=Mediatrace technical metadata extraction via mediainfo, eventDetail=Failure, mediatrace could not be created due to characters not compatible with UTF-8 and cp1252. mediatrace XML not included in package as a result, agentName=%s'
                        )
                    else:
                        generate_log(
                            new_log_textfile,
                            'EVENT = Metadata extraction - eventDetail=Mediatrace technical metadata extraction via mediainfo, eventOutcome=%s, agentName=%s' % (inputtracexml, mediainfo_version)
                        )
            elif check_av_or_doc(av_file.lower()) == 'doc':
                if av_file[0] != '.':
                    if not av_file.lower().endswith(('.txt', '.csv')):
                        exiftool_version = 'exiftool'
                        try:
                            exiftool_version = subprocess.check_output([
                                'exiftool', '-ver'
                            ])
                        except subprocess.CalledProcessError as grepexc:
                            exiftool_version = grepexc.output.rstrip().splitlines()[1]
                        inputxml = "%s/%s_exiftool.json" % (
                            os.path.join(path, 'metadata'), os.path.basename(av_file)
                        )
                        generate_log(
                            new_log_textfile,
                            'EVENT = Metadata extraction - eventDetail=Technical metadata extraction via exiftool, eventOutcome=%s, agentName=%s' % (inputxml, exiftool_version)
                        )
                        print(' - Generating exiftool json of input file and saving it in %s' % inputxml)
                        make_exiftool(
                            inputxml,
                            os.path.join(root, av_file)
                        )
                    siegfried_version = 'siegfried'
                    try:
                        siegfried_version = subprocess.check_output([
                            'sf', '-version'
                        ])
                    except subprocess.CalledProcessError as grepexc:
                        siegfried_version = grepexc.output.rstrip().splitlines()[1]
                    inputtracexml = "%s/%s_siegfried.json" % (
                        os.path.join(path, 'metadata'), os.path.basename(av_file)
                        )
                    print(' - Generating Siegfried json of input file and saving it in %s' % inputtracexml)
                    make_siegfried(
                        inputtracexml,
                        os.path.join(root, av_file)
                    )
                    generate_log(
                        new_log_textfile,
                        'EVENT = Format identification - eventType=format identification, eventDetail=Format identification via PRONOM signatures using Siegfried, eventOutcome=%s, agentName=%s' % (inputtracexml, siegfried_version)
                    )
                    
def check_if_manifest(manifest):
    '''
    Basic check to see if a file is an md5 manifest
    '''
    if '_manifest' in manifest:
        if manifest.endswith('.md5'):
            if manifest[0] != '.':
                # sloppy code to prevent manifests made with manifest_normalise.py from breaking scripts
                if not manifest.endswith('_modified_manifest.md5'):
                    return True

def count_stuff(source):
    '''
    Counts total files to be processed.
    '''
    source_count = 0
    file_list = []
    for root, directories, filenames in os.walk(source):
        filenames = [f for f in filenames if f[0] != '.']
        directories[:] = [d for d in directories if d[0] != '.']
        for files in filenames:
            source_count += 1
            relative_path = unicodedata.normalize('NFC', os.path.join(root, files).replace(os.path.dirname(source), ''))[1:]
            file_list.append(relative_path.replace("\\", "/"))
    print(file_list)
    if os.path.isfile(source):
        if len(file_list) == 0:
            source_count = 1
    return source_count, file_list

def check_existence(dependency_list):
    '''
    Process a list of subprocess strings and check if they're installed
    '''
    missing = False
    for dependency in dependency_list:
        if shutil.which(dependency) is None:
            print('This script requires %s, please install it.' % dependency)
            missing = True
    if missing is True:
        print('Exiting')
        sys.exit()


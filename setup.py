#!/usr/bin/env python3

import sys
from setuptools import setup

if sys.version_info < (3, 8):
    print("Python 3.8 or higher is required - earlier python 3 versions may work but were not tested.")
    sys.exit(1)
setup(
    author='Kieran O\'Leary',
    author_email='kieran.o.leary@gmail.com',
    maintainer='Yazhou He',
    maintainer_email='yhe@irishfilm.ie',
    description="Scripts for processing moving image material in the Irish Film Institute/Irish Film Archive",
    long_description=("""\
Scripts for use in the IFI Irish Film Archive. Scripts have been tested in OSX/Windows 7/10 and Ubuntu 18.04. The aim is to make cross-platform scripts, but please get in touch with any issues. It is best to download all scripts, as some of them share code.

Most scripts take either a file or a directory as their input, for example makeffv1.py filename.mov or premis.py path/to/folder_of_stuff. (It's best to just drag and drop the folder or filename into the terminal)

Note: Documentation template has been copied from mediamicroservices

NOTE: Objects.py has been copied from https://github.com/simsong/dfxml. walk_to_dfxml.py has also been copied but has been customised in order to add command line arguments for optionally turning off checksum generation. For more context, see https://github.com/simsong/dfxml/pull/28
"""),
    scripts=[
        'scripts/accession_register.py',
        'scripts/aipcreator.py',
        'scripts/as11fixity.py',
        'scripts/batchaipcreator.py',
        'scripts/batchdiff_framemd5.py',
        'scripts/batchmakeshell.py',
        'scripts/batchsc_aip_update.py',
        'scripts/batchsc_checkdir.py',
        'scripts/batchsc_organise.py',
        'scripts/batchsc_validate.py',
        'scripts/batchsipcreator.py',
        'scripts/batchvalidate.py',
        'scripts/bitc.py',
        'scripts/check_register.py',
        'scripts/concat.py',
        'scripts/copyit.py',
        'scripts/dcpaccess.py',
        'scripts/dcpfixity.py',
        'scripts/deletefiles.py',
        'scripts/dfxml.py',
        'scripts/durationcheck.py',
        'scripts/ffv1mkvvalidate.py',
        'scripts/framemd5.py',
        'scripts/get_ps_list.py',
        'scripts/getdip.py',
        'scripts/ififuncs.py',
        'scripts/loopline_repackage.py',
        'scripts/lossy_check.py',
        'scripts/make_mediaconch.py',
        'scripts/makedfxml.py',
        'scripts/makedip.py',
        'scripts/makeffv1.py',
        'scripts/makepbcore.py',
        'scripts/makeuuid.py',
        'scripts/makezip.py',
        'scripts/manifest.py',
        'scripts/masscopy.py',
        'scripts/massqc.py',
        'scripts/mergepbcore.py',
        'scripts/merge_csv.py',
        'scripts/multicopy.py',
        'scripts/normalise.py',
        'scripts/Objects.py',
        'scripts/order.py',
        'scripts/package_update.py',
        'scripts/packagecheck.py',
        'scripts/prores.py',
        'scripts/renamefiles.py',
        'scripts/seq2ffv1.py',
        'scripts/sipcreator.py',
        'scripts/strongbox_fixity.py',
        'scripts/structure_check.py',
        'scripts/subfolders.py',
        'scripts/testfiles.py',
        'scripts/validate.py',
        'scripts/walk_to_dfxml.py'
    ],
    license='MIT',
    install_requires=[
        'lxml',
        'bagit',
        'dicttoxml',
        'future',
        'clairmeta'
    ],
    data_files=[('', ['film_scan_aip_documentation.txt', '26_XYZ-22_Rec709.cube'])],
    include_package_data=True,
    name='ifiscripts',
    version='2024.02.06',
    python_requires='>=3.8'
)

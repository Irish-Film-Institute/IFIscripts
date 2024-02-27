Usage
========================

Arrangement
-----------

sipcreator.py
~~~~~~~~~~~~~

-  Accepts one or more files or directories as input and wraps them up
   in a directory structure in line with IFI procedures using
   ``copyit.py``.
-  Source objects will be stored in an /objects directory. Directory
   structure is: parent directory named with a UUID, with three child
   directories (objects, logs metadata):
-  Metadata is extracted for the AV material and MD5 checksums are
   stored for the entire package. A log records the major events in the
   process.
-  Usage for one directory -
   ``sipcreator.py -i /path/to/directory_name -o /path/to/output_folder``
-  Usage for more than one directory -
   ``sipcreator.py -i /path/to/directory_name1 /path/to/directory_name2 -o /path/to/output_folder``
-  Run ``sipcreator.py -h`` for all options.

batchsipcreator.py
~~~~~~~~~~~~~~~~~

-  Batch process packages by running ``sipcreator.py``
-  The script will only process files within subfolders.
-  The script will ask for the starting OE number, and each further package
   will auto-increment by one.
-  Usage for processing all subdirectories that (for example) places all XML/PDF/TXT 
   files in the supplemental metadata subdirectory, and place all MF and STL files within objects-
   ``batchsipcreator.py -i  /path/to/directory_name -o /path/to/output_folder -supplement_extension_pattern xml pdf txt -object_extension_pattern mxf stl``
-  Run ``batchsipcreator.py -h`` for all options.

aipcreator.py
~~~~~~~~~~~~

-  Turns a SIP that has passed QC procedures into an AIP.
-  Currently this just works with packages that have been generated
   using ``sipcreator.py`` and ``seq2ffv1.py``. SHA512 manifests are 
   created,the OE number is replaced by an accession number, and the sipcreator
   logfile is updated with the various events that have taken place.
-  Usage for one directory - ``aipcreator.py /path/to/directory_name``
-  Run ``aipcreator.py -h`` for all options.

batchaipcreator.py
~~~~~~~~~~~~~~~~~

-  Batch process packages by running ``aipcreator.py`` and
   ``makepbcore.py``
-  The script will only process files with ``sipcreator.py`` style
   packages. ``makeffv1.py`` and ``dvsip.py`` packages will be ignored.
-  Usage for processing all subdirectories -
   ``batchaipcreator.py /path/to/directory_name``
-  Run ``batchaipcreator.py -h`` for all options.

order.py
~~~~~~~~

-  Audits logfiles to determine the parent of a derivative package.
-  This script can aid in automating large accessioning procedures that
   involve the accessioning of derivatives along with masters, eg a
   Camera Card and a concatenated derivative, or a master file and a
   mezzanine.
-  Currently, this script will return a value :``None``, or the parent
   ``OE`` number. It also prints the OE number in its ``OE-XXXX`` just
   for fun.
-  Usage for one directory - ``order.py /path/to/directory_name``

makepbcore.py
~~~~~~~~~~~~~

-  Describes AV objects using a combination of the PBCore 2 metadata
   standard and the IFI technical database.
-  This script takes a folder as input. Either a single file or multiple
   objects will be described.
-  This will produce a single PBCore CSV record per package, even if
   multiple objects are within a package. The use case here is complex
   packages such as XDCAM/DCP, where we want a single metadata record
   for a multi-file object.
-  The CSV headings are written in such a way to allow for direct import
   into our SQL database.
-  Usage for one directory - ``makepbcore.py /path/to/directory_name``
-  Run ``makepbcore.py -h`` for all options.

mergepbcore.py
~~~~~~~~~~~~~~

-  Collates PBCore CSV records into a single merged CSV.
-  The merged csv will be stored in the Desktop ifiscripts_logs folder.
-  This script takes a parent folder containing AIPs as input.
-  Usage ``mergepbcore.py /path/to/folder_that_contains_AIPs_as_input``
-  Run ``mergepbcore.py -h`` for all options.

merge_csv.py
~~~~~~~~~~~~~~

-  Collates CSV records into a single merged CSV.
-  The merged csv will be stored in the Desktop ifiscripts_logs folder. There is no error checking.
-  This script takes as many as CSV files with the same titles as needed as input.
-  Usage ``merge_csv.py /path/to/csv_1 /path/to/csv_2 /path/to/csv_x``
-  Run ``merge_csv.py -h`` for all options.

deletefiles.py
~~~~~~~~~~~~~~

-  Deletes files after ``sipcreator.py`` has been run, but before
   ``aipcreator.py`` has been run.
-  Manifests are updated, metadata is deleted and the events are all
   logged in the logfile.
-  This script takes the parent OE folder as input. Use the ``-i``
   argument to supply the various files that should be deleted from the
   package.
-  Usage for deleting two example files -
   ``deletefiles.py /path/to/oe_folder -i path/to/file1.mov path/to/file2.mov``
-  Run ``deletefiles.py -h`` for all options.

package_update.py
~~~~~~~~~~~~

-  Rearranges files into a subfolder files after ``sipcreator.py`` has
   been run, but before ``aipcreator.py`` has been run.
-  Manifests are updated, files are moved, and the events are all logged
   in the logfile.
-  This is useful in conjunction with ``sipcreator.py`` and
   ``deletefiles.py``, in case a user wishes to impose a different
   ordering of the files within a large package. For example, from a
   folder with 1000 photographs, you may wish to create some sufolders
   to reflect different series/subseries within this collection. This
   script will track all these arrangement decisions.
-  This script takes the parent OE folder as input. Use the ``-i``
   argument to supply the various files that should be moved. The
   ``new_folder`` argument declares which folder the files should be
   moved into. Run ``validate.py`` to verify that all went well.
-  Usage for moving a single file into a subfolder -
   ``package_update.py /path/to/oe_folder -i path/to/uuid/objects/file1.mov -new_folder path/to/uuid/objects/new_foldername``
-  Run ``package_update.py -h`` for all options.

subfolders.py
~~~~~~~~~~~~~~

-  Generates subfolders based on filenames within the input directory
   and if ``-move`` is used, moves the relevant files into these new directories.
-  Eg. An input directory contains file1.mkv, file1.xml file2.mkv, file2.xml
   This will result in directories called file1 and file2 being created, and
   file1.mkv and file1.xml will be moved into the file1 directory, with a similar action
   for file2
-  Usage to just make subfolders: ``subfolders.py -i path/to/input``
-  Usage to make subfolders and move files: ``subfolders.py -move -i path/to/input``

accession_register.py
~~~~~~~~~~~~~~~~~~~~~

-  Generates a helper accession register based on the metadata in other spreadsheets.
-  Usage: ``accession_register.py -pbcore_csv /path/to/pbcore_csv -sorted_csv /path/to/sorted_csv -filmo_csv /path/to/filmo_csv``


Transcodes
----------

normalise.py
~~~~~~~~~~~

-  Transcodes to FFV1/Matroska and performs framemd5 validation. Accepts
   single files only. Batch functionality may be added at a later date.
   For IFI purposes, the ``-sip`` option is needed as this will also launch
   ``sipcreator.py`` and generate the IFI package structure. If this ``-sip`` flag is not
   used, then the script will not impose a folder structure.
   You may wish to add some supplemtal metadata to the package, such as an EDL or
   some capture notes, so these can be added with the ``-supplement`` option.
-  Currently, the lossless report is displayed in the middle of the process, so care is needed
   to ensure that the losslessness is verified before moving on to accessioning.
-  Usage within IFI - ``normalise.py -i filename.mov -o /path/to/output_directory -sip``
-  Usage within IFI with supplement option - ``normalise.py -i filename.mov -o /path/to/output_directory -sip -supplement path/to/supplemental_1.txt path/to/supplemental2.edl``
-  Usage for single file in a general usage - ``normalise.py -i filename.mov -o /path/to/output_directory``


makeffv1.py
~~~~~~~~~~~

-  Transcodes to FFV1.mkv and performs framemd5 validation. Accepts
   single files or directories (all video files in a directory will be
   processed). CSV report is generated which gives details on
   losslessness and compression ratio.
-  Usage for single file - ``makeffv1.py filename.mov``
-  Usage for batch processing all videos in a directory -
   ``makeffv1.py directory_name``

bitc.py
~~~~~~~

-  Create timecoded/watermarked h264s for single files or a batch
   process.
-  Usage for single file - ``bitc.py filename.mov``
-  Usage for batch processing all videos in a directory -
   ``bitc.py directory_name``
-  This script has many extra options, such as deinterlacing, quality
   settings, rescaling. Use ``bitc.py -h`` to see all options

prores.py
~~~~~~~~~

-  Transcode to prores.mov for single/multiple files.
-  Usage for single file - ``prores.py filename.mov``
-  Usage for batch processing all videos in a directory -
   ``prores.py directory_name``
-  This script has many extra options, such as deinterlacing, quality
   settings, rescaling. Use ``prores.py -h`` to see all options

makedip.py
~~~~~~~~~

-  Runs bitc.py or prores.py.
-  Usage for running bitc.py on all objects in a batch of information packages -
   ``makedip.py path/to/batch_directories -o path/to/output``
-  The ``-prores`` option will use run ``prores.py`` instead of ``bitc.py``
-  The script will rename the output file so that it contains either the OE number or the accession number.
-  If it sees that a proxy already exists, then it will skip the video.
-  Use ``makedip.py -h`` to see all options

concat.py
~~~~~~~~~

-  Concatenate/join video files together using ffmpeg stream copy into a
   single Matroska container. Each source clip will have its own chapter
   marker. As the streams are copied, the speed is quite fast.
-  Usage:
   ``concat.py -i /path/to/filename1.mov /path/to/filename2.mov -o /path/to/destination_folder``
-  A lossless verification process will also run, which takes stream
   level checksums of all streams and compares the values. This is not
   very reliable at the moment.
-  Warning - video files must have the same technical attributes such as
   codec, width, height, fps. Some characters in filenames will cause
   the script to fail. Some of these include quotes. The script will ask
   the user if quotes should be renamed with underscores. Also, a
   temporary concatenation textfile will be stored in your temp folder.
   Currently only tested on Ubuntu.
-  Dependencies: mkvpropedit, ffmpeg. ## Digital Cinema Package Scripts
   ##

dcpaccess.py
~~~~~~~~~~~~

-  Create h264 (default) or prores transcodes (with optional subtitles)
   for unencrypted, single/multi reel Interop/SMPTE DCPs. The script
   will search for all DCPs in subdirectories, process them one at a
   time and export files to your Desktop.
-  Usage: ``dcpaccess.py dcp_directory``
-  Use ``-p`` for prores output, and use ``-hd`` to rescale to 1920:1080
   while maintaining the aspect ratio.
-  Dependencies: ffmpeg must be compiled with libopenjpeg -
   ``brew install ffmpeg --with-openjpeg``.
-  Python dependencies: lxml required.
-  Further options can be viewed with ``dcpaccess.py -h``

dcpfixity.py
~~~~~~~~~~~~

-  Verify internal hashes in a DCP and write report to CSV. Optional
   (experimental) bagging if hashes validate. The script will search for
   all DCPs in subdirectories, process them one at a time and generate a
   CSV report.
-  Usage: ``dcpfixity.py dcp_directory``
-  Further options can be viewed with ``dcpfixity.py -h``

dcpsubs2srt.py
~~~~~~~~~~~~~~

-  Super basic but functional DCP XML subtitle to SRT conversion. This
   code is also contained in dcpaccess.py
-  Usage: ``dcpsubs2srt.py subs.xml``

Fixity Scripts
--------------

copyit.py
~~~~~~~~~

-  Copies a file or directory, creating a md5 manifest at source and
   destination and comparing the two. Skips hidden files and
   directories.
-  Usage: ``copyit.py source_dir destination_dir``
-  Dependencies: OSX requires gcp - ``brew install coreutils``

manifest.py
~~~~~~~~~~~

-  Creates relative md5 or sha512 checksum manifest of a directory.
-  Usage: ``manifest.py directory`` or for sha512 hashes:
   ``manifest.py -sha512 directory``
-  By default, these hashes are stored in a desktop directory, but use
   the ``-s`` option in order to generate a sidcecar in the same
   directory as your source.
-  Run ``manifest.py -h`` to see all options.

makedfxml.py
~~~~~~~~~~~~

-  WARNING - until this issue is resolved, this script can not work with
   Windows: https://github.com/simsong/dfxml/issues/29
-  Prints Digital Forensics XML to your terminal. Hashes are turned off
   for now as these will usually already exist in a manifest. The main
   purpose of this script is to preserve file system metadata such as
   date created/date modified/date accessed.
-  This is a launcher script for an edited version of
   'https://github.com/simsong/dfxml/blob/master/python/walk\_to\_dfxml.py'.
   The edited version of ``walk_to_dfxml.py`` and the ``Objects.py``
   library have been copied into this repository for the sake of
   convenience.
-  Usage: ``makedfxml.py directory``.
-  NOTE: This is currently a proof of concept. Further options, logging
   and integration into other scripts will be needed.
-  There may be a python3 related error on OSX if python is installed
   via homebrew. This can be fixed by typing ``unset PYTHONPATH`` in the
   terminal.


shadfxml.py
~~~~~~~~~~~~~

-  Creates DFXML and sha512 manifests but only in sipcreator/uuid packages.
-  This will work recursively so all packages within a directory will be processed.
-  Usage: ``shadfxml.py directory``

validate.py
~~~~~~~~~~~

-  Validate md5 or SHA512 sidecar manifests. Currently the script
   expects two spaces between the checksum and the filename.
-  In packages that have been generated with sipcreator.py, the results
   of the process will be added to the logfile and the checksum for the
   logfile will update within the md5 and sha512 manifests
-  Usage: ``validate.py /path/to/manifest.md5`` or
   ``validate.py /path/to/_manifest-sha512.txt``

batchdiff_framemd5.py
~~~~~~~~~~~

-  Creates framemd5 sidecars on a batch of SIPs powered by `framemd5.py`;
   Compares the hashes in framesmd5 and those in md5 files in PSM directory;
   Once mismatch was found, it will skip the rest of the hashes and 
   skip to the next object; It will delete all framemd5 files after 
   the batch of the comparsions have finished.
-  Usage: ``batchdiff_framemd5.py -sip /path/to/parent_folder/of/SIPs 
   -psm /path/to/parent_folder/of/PSMs``
-  NB: The script will default to only one md5 manifest file per PSM. If 
   there are repeated manifest in the directory, users may need to add bloack 
   in the script manually.

Image Sequences
---------------


seq2ffv1.py
~~~~~~~~~~~

-  Work in progress -more testing to be done.
-  Recursively batch process image sequence folders and transcode to a
   single ffv1.mkv.
-  Framemd5 files are generated and validated for losslessness.
-  Whole file manifests are also created.
-  Usage - ``seq2ffv1.py parent_folder``

seq2prores.py
~~~~~~~~~~~~~

-  Specific IFI workflow that expects a particular folder path:
-  Recursively batch process image sequence folders with seperate WAV
   files and transcode to a single Apple Pro Res HQ file in a MOV
   container. PREMIS XML log files are generated with hardcoded IFI
   values for the source DPX sequence and the transcoded mezzanine file
   in the respective /metadata directory
-  A whole file MD5 manifest of everything in the SIP are also created.
   Work in progress - more testing to be done.
-  Usage - ``seq2prores.py directory``
-  seq2prores accepts multiple parent folders, so one can run
   ``seq2prores.py directory1 directory2 directory3`` etc


seq.py
~~~~~~

-  Transcodes a TIFF sequence to 24fps v210 in a MOV container.
-  Usage: ``seq.py path/to/tiff_folder`` and output will be stored in
   the parent directory.
-  Further options can be viewed using ``seq.py -h``


oeremove.py
~~~~~~~~~~~

-  IFI specific script that removes OE### numbers from the head of an
   image sequence filename.
-  Usage - ``oeremove.py directory``.

seq2dv.py
~~~~~~~~~

-  Transcodes a TIFF sequence to 24fps 720x576 DV in a MOV container.
-  Usage: ``seq.py path/to/tiff_folder`` and output will be stored in
   the parent directory.

batchmetadata.py
~~~~~~~~~~~~~~~~

-  Traverses through subdirectories trying to find DPX and TIFF files
   and creates mediainfo and mediatrace XML files.
-  Usage: ``batchmetadata.py path/to/parent_directory`` and output will
   be stored in the parent directory.

batchrename.py
~~~~~~~~~~~~~~

-  Renames TIFF files in an image sequence except for numberic sequence
   and file extension.
-  Usage - ``batchrename.py directory`` - enter new filename when
   prompted

Quality Control
---------------

massqc.py
~~~~~~~~~~

-  Generate QCTools xml.gz sidecar files via ``qcli`` which will load immediately in
   QCTools.
-  Usage for single file - ``massqc.py filename.mov``
-  Usage for batch processing all videos in a directory -
   ``massqc.py directory_name``

videoerror.py
~~~~~~~~~~~~~~~~~~

-  Detect corrupted frames in m2t/HDV captures.
-  Generates a CSV report in ~/Desktop/ifiscripts_logs
-  Usage for batch processing all m2t videos recursively in a directory -
   `` videoerror.py directory_name``

framemd5.py
~~~~~~~~~~

-  Creates framemd5 sidecars on all mov/mkv files in all subfolders beneath your input.
-  If the input is a file, then ``framemd5.py`` will just generate a sidecar for this one file.
-  Usage for single file - ``framemd5.py -i filename.mov``
-  Usage for batch processing all videos in a directory -
   ``framemd5.py -i directory_name``

ffv1mkvvalidate.py
~~~~~~~~~~~~~~~~~~

-  Validates Matroska files using mediaconch.
-  An XML report will be written to the metadata directory.
-  A log will appear on the desktop, which will be merged into the SIP
   log in /logs.
-  Usage for batch processing all videos in a directory -
   ``ffv1mkvvalidate.py directory_name``

lossy_check.py
~~~~~~~~~~~~~~~~~~

-  This script is to check losslessness for a batch of sipped image sequence objects
-  It will check the losslessness from package/$uuid/logs/$uuid_seq2ffv1_log.log
-  It will return the result of 'lossless' or 'lossy' for each information package
-  Usage for batch processing all videos in a directory -
   ``lossy_check.py -i directory_name``

structure_check.py
~~~~~~~~~~~~~~~~~~

-  This script is to check the structure of a batch of SIPs/AIPs(and AIP shells)
-  It will show the directory tree of each information package
-  Users are able to manually record if the structure is right or not 
-  The script will list a summary at the end
-  Usage: ``structure_check.py -i directory_name``

Specific Workflows
------------------


masscopy.py
~~~~~~~~~~~

-  Copies all directories in your input location using copyit.py ONLY if
   a manifest sidecar already exists.
-  This is useful if a lot of SIPs produced by makeffv1 are created and
   you want to move them all to another location while harnessing the
   pre-existing checksum manifest.
-  WARNING - It is essential to check the log file on the
   desktop/ifiscripts\_logs for each folder that transferred!!
-  Usage:
   ``masscopy.py /path/to/parent_folder -o /path/to/destination_folder``


makefolders.py
~~~~~~~~~~~~~~

-  Creates a logs/objects/metadata folder structure with a UUID parent
   folder. This is specific to a film scanning workflow as there are
   seperate audio and image subfolders. You can specifiy the values on
   the command line or a terminal interview will appear which will
   prompt you for filmographic URN, source accession number
   and title. Use ``makefolders.py -h`` for the full list of options.
-  Usage: ``makefolders.py -o /path/to/destination``

loopline\_repackage.py
~~~~~~~~~~~~~~~~~~~~~~

-  Retrospectively updates older FFV1/DV packages in order to meet our
   current packaging requirements. This should allow aipcreator.py and
   makepbcore.py to run as expected. This will process a group of
   packages and each loop will result in the increment by one of the
   starting OE number. Use with caution.
-  This script should work on files created by
   ``makeffv1.py dvsip.py loopline.py``
-  Usage: ``loopline_repackage``

batchmakeshell.py
~~~~~~~~~~~~~~~~~

-  Creates shells for the AIPs under a batch (or SIP shells of large-size 
   materials for backup use). This is used for the accessioning closing steps. 
   The script will recognise all the folders named with "aaa[0-9]{4}" digital 
   accession number format. Then created their shell folders named 
   "aaa[0-9]{4}_shell" and clone all the subcontent except the content inside the 
   'objects' folder into them. The shells will be created into the targeted output path.
-  Usage: ``batchmakeshell.py path/to/batch_directories -o /path/to/destination``
-  This script has extra options, including making shells for AS-11 UK DPP and
   DCP, and making SIP shells for DCDM and other large-size materials. 
   Use ``batchmakeshell.py -h`` to see all options.
    
getdip.py
~~~~~~~~~

-  Retrieves DIPs (shells, proxies or mezzanines) from storage by accession numbers.
   The script checks if the required AIPs are in the storage for a form of DIPs and
   copied to destination if needed. The accession numbers can be either input manually
   or imported by a formatted csv including the required accession numbers.
-  Usage: ``getdip.py -t DIP_type -n accession_numbers -i /root/of/DIP/dir -o 
   path/to/destination`` for manually typing the accession numbers in and copy the DIPs.
   ``getdip.py -t DIP_type -csv path/to/accession_numbers/csv -i /root/of/DIP/dir 
   -justcheck`` for importing access numbers from csv and just checking if the required
   accession numbers have related DIP in the storage.
-  Use ``getdip.py -h`` to see all options.


Special Collections
~~~~~~~~~~~~~~~~~~~

batchsc\_checkdir.py
********************

-  Checks if each special collections package in the storage is an AIP (processed package) or 
   a RAW (unprocessed package) has been processed, and then move either
   to a separate folder.'
-  This script doesn't have any arguments. It prints 2 functions for selection.
-  Usage: ``batchsc_checkdir.py``


batchsc\_validate.py
********************
-  Runs ``validate.py`` for a batch of special collections unprocessed packages under the same 
   directory. All validated packages will be moved to required destination.
-  All packages failed validation remain in the source location. The script will return the
   directory for the running data for all failed validations after it finishes.
-  For all the backlogs having logs and md5 manifests, the script will remove the logs and
   manifests after they passed validation and moved to the destination.
-  This script doesn't have any arguments. It prints the steps the script will do and ask for
   the source and the destination at the beginning.
-  Usage: ``batchsc_validate.py``


batchsc\_organise.py
********************
-  Use with caution! It will change the files matadata and package structure and there is
   no log for this.
-  Function 1 - (Use with caution) Rename folders/files - replace all spaces and special
   characters to '_'
-  Function 2 - Rename packages - replace spaces to '_' and remove all special characters
-  Function 3 - Move subfiles - move all files to the root of the packages
-  Function 4 - (Use only after 3.) Delete subfolders - Delete all subfolders in each packages
-  This scripts doesn't have any arguments. It asks for the source and lists all the packages.
   Then it prints above 4 functions for selection.


batchsc\_aip\_update.py
***********************
-  Moves all subfiles in the objects folder in the AIPs (processed packages) to the root,
   or renames (removes special characters) all the subfiles. It does update the log for AIPs
   when each AIP completes processing. It will returns AIPs cannot update the log at the end.
-  Usage: ``batchsc_aip_update.py -movetoobjects /path/to/parent/folder``
   or ``batchsc_aip_update.py -rename /path/to/parent/folder``


Misc
----

update.py
~~~~~~~~~

-  Updates IFIscripts to the latest git head if the following directory
   structure exists in the home directory: ``ifigit/ifiscripts``
-  Usage: ``update.py``


makeuuid.py
~~~~~~~~~~~

-  Prints a new UUID to the terminal via the UUID python module and the
   create\_uuid() helper function within ififuncs.
-  Usage: ``makeuuid.py``

durationcheck.py
~~~~~~~~~~~~~~~~

-  Recursive search through subdirectories and provides total duration
   in minutes. Accepts multiple inputs but provides the total duration
   of all inputs.
-  Usage: ``durationcheck.py /path/to/parent_folder`` or
   ``durationcheck.py /path/to/parent_folder1 /path/to/parent_folder2 /path/to/parent_folder3``

fakexdcam.py
~~~~~~~~~~~~

-  Creates a fake XDCAM EX structure for testing purposes
-  Usage: ``fakexdcam.py /path/to/output_folder``

get_ps_list.py
~~~~~~~~~~~~~~

-  Create a csv file from mounted 'preservation storage' directory,
   including accession numbers from package title, object entry number
   from log file, and accession numbers from log file for all preserved AIPs.
-  Usage: ``get_ps_list.py -i /path/to/preservation_storage``

check_register.py
~~~~~~~~~~~~~~~~~

-  Print mismatch accession numbers and object entry numbers.
-  Compare between csv files from preservation list by `get_ps_list.py`
   and from (partly) digital accession register or help register, etc.
-  Usage: ``check_register.py -preservation_storage_csv /path/to/csv_made_by_get_ps_list_py
   -register_csv /path/to/accession_register``

Experimental-Premis
-------------------

premis.py
~~~~~~~~~

-  Work in progress PREMIS implementation. This PREMIS document will
   hopefully function as a growing log file as an asset makes its way
   through a workflow.
-  Requries pyqt4 (GUI) and lxml (xml parsing)
-  Usage - ``premis.py filename``.


as11fixity.py
~~~~~~~~~~~~~

-  Work in progress script by @mahleranja and @ecodonohoe
-  There is a bash script in a different repository that works quite
   well for this purpose but that is OSX only.

viruscheck.py
~~~~~~~~~~~~~

-  Work in progress script by @ecodonohoe
-  Scans directories recursively using ClamAV


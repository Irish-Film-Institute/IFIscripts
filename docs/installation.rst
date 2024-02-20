Installation
============

General
-------

This is a python 3.8 project.

In general, you can install the scripts from Pypi (installed along with Python) by running ``python -m pip install ifiscripts`` on Windows or ``python3 -m pip install ifiscripts`` on Mac OS.

You can also clone or download the whole repository (https://github.com/Irish-Film-Institute/IFIscripts) and run the scripts from your cloned path. 

For our developer, on Mac OS and Windows, we create a folder in the home directory called ``ifigit``, then we run ``git clone https://github.com/Irish-Film-Institute/IFIscripts.git``. Then we add the ``ifiscripts`` folder to ``$PATH`` which allows us to access the scripts from any directory, not just from ``ifigit/ifiscripts``.

Alternatively, some folks prefer to locate (``cd``) into the cloned repository and run the scripts from there, for example to run ``makeffv1.py`` 
``python makeffv1.py path/to.filename.mov``.


External Dependencies
---------------------

External dependencies are listed below.

Some vital dependencies are for the library or the common tools used for the materials.
They can be found in the ``pyproject.toml`` dependencies list and will be installed when installing ifiscripts using ``pip``.
If you are cloning the repository, you can manually install the dependencies, such as ``pip install lxml``.

* bagit
* clairmeta
* dicttoxml
* future
* lxml
* psutil

Some essential ``subprocess`` dependencies not in Pypi for most of the scripts will have to be installed manually.

* ffmpeg
* ffprobe
* mediainfo

The following dependencies are also needed for many scripts:

* 7zip aka 7za aka p7zip-full
* asdcplib (https://github.com/cinecert/asdcplib, required by clairmeta for checking DCP)
* exiftool (https://exiftool.org/install.html)
* md5deep
* mediaconch
* qcli
* rawcooked
* rsync
* siegfried aka sf (https://www.itforarchivists.com/siegfried)
* sox (SoundeXchange, https://sourceforge.net/projects/sox/, required by clairmeta)

Some dependencies below are not our common dependencies but could be needed for specific purpose:

* gcp (copy from/to LTO, installed via gnu-coreutils on OSX)
* git (for update.py, no longer in use for updating scripts)
* mkvpropedit (for concat.py, installed via mkvtoolnix)
* openssl

Specific Instructions - Windows
-------------------------------

* install 64-bit git-bash using all the default settings https://git-scm.com/downloads - make sure it's the 64-bit version!
* install 64-bit python3, making sure to tick the option to ADD TO PATH https://www.python.org/downloads/
* open cmd and ``mkdir ifiscripts`` and ``git clone https://github.com/Irish-Film-Institute/IFIscripts.git``
* add this ifiscripts path  (eg ``C:\Users\$USER\ifigit\ifiscripts``)to the environmental path, following these steps: https://www.computerhope.com/issues/ch000549.htm
* ffmpeg the default option works well - 64-bit static https://ffmpeg.zeranoe.com/builds/ and place in scripts folder
  * OR install media-autobuild-suite but extract to the C:\mas folder due to long path issues
* mediainfo - get the 64-bit CLI version https://mediaarea.net/en/MediaInfo/Download/Windows
* install lxml with ``pip install lxml`` if not installing ifiscripts by pip
* install siegfried exe (https://www.itforarchivists.com/siegfried/)file to the ifiscripts folder and run ``sf -update`` in cmd 
* download exiftool installer and select the 'latest build' option - make sure that the option to add to path is ticked - https://oliverbetz.de/pages/Artikel/ExifTool-for-Windows
* install notepad++ - https://notepad-plus-plus.org/downloads/
* install libreoffice for accessing and editing csv files - https://www.libreoffice.org/download/download/


Specific Instructions - Ubuntu
---------------------

(We no longer support Ubuntu but the scripts are still working)

A lot of these can be installed on Ubuntu with a single line:
``sudo apt update && sudo apt install python3-pip ffmpeg mkvtoolnix exiftool git md5deep p7zip-full``

In order to add the rest, refer to the installation instructions of the relevant tools.
For mediaarea tools, it can be easiest to use their own snapshot repository:

``wget https://mediaarea.net/repo/deb/repo-mediaarea-snapshots_1.0-13_all.deb && sudo dpkg -i repo-mediaarea-snapshots_1.0-13_all.deb && sudo apt update && sudo apt install mediainfo dvrescue qcli rawcooked mediaconch``



Contributing
============

Issues
------

Contributions are very much welcome in any form. Feel free to raise an issue requesting a new feature, or to report a bug. If requesting a new feature, please describe the workflow which the feature will be used, the required input & output data, and the output form of that. If reporting a bug, please copy/paste the full, complete, uncut terminal output.

For the issues requested by IFI Irish Film Archive staff, please raise tickets in the Teams/Script work group/Script_maintenance_log.xlsx. All tickets will be assessed with workflow first and then uploaded on GitHub in new branches or issues if needed.

For issues we are going to solve, we will create a relative pull request and quote each other.

Pull Requests
-------------

Pull requests are welcome. If contribution is on existing scripts, please follow the coding style and leave comments for short descriptions. If contributing new script, it can be nice to run it through ``pylint`` first, as this will check for PEP-08 compliance.

We are trying to limit the use of external dependencies unless it is necessary for the workflows and materials. While if you add any external dependencies, please specify in the pull request and add them in ``setup.py``.

*Please commit as '$script.py - $description' for a clear review.*
*Please also leave the test instances and results with the full, complete, uncut terminal output. If it generates any files, please specify the filename and format, and content if applicable.*

For pull requests by IFI Irish Film Archive staff, please follow the script work group policy and contributing after testing in the local workspace. For any edits of re-phrasing or typo, force-push would be better in case of unnecessary commits. 

Contributions Needed
--------------------

Some good first contributions could be adding explanatory docstrings to libraries like ``ififuncs.py``, or revising older scripts, such as ``validate.py`` so that they are more in line with the coding style of recent scripts. Some of our ``main()`` functions are far too long and are doing too much, so they are in need of being split up into smaller functions.

Overall, the project needs to grow in the following ways:

* Reduce code duplication across scripts. These duplications continue to be difficult to maintain. Moving regularly used functions to ififuncs definitely helps.
* ``unittests`` are desperately needed! Scripts are becoming more and more linked, so automated testing is needed in order to find errors in  areas that we might not expect. This should also allow integration with something like ``Travis``.
* A config file is needed in some way shape or form. For example, logs and old manifests are stored on the desktop. It isn't really cool that these folders just appear without the user even knowing. This could also allow the scripts to be more generic, as IFI specific options could be enabled here.
* It would probably be a good idea to introduce classes into IFIscripts. Some functions return and call an embarrasing number of values.
* Have some sort of integration with a mysql database for tracking objects and logging events.

## buildchimp

This is a program built using PySide (Python + Qt). The purpose is to enable a series of processes to be run, 
specified as bash or windows cmd scripts, with the output displayed in separate tabs. The scripts are specified 
in a single yaml configuration file.

The original purpose of the program was to allow a build process to be described in file that can be stored 
in a version control system and shared and run by the members of the team.

## Requirements (Python)

* Python 2.7 with pip
* pip > PySide
* pip > yaml

## TODO / Ideas

Things still to do and ideas:

* Recent File List
  * Remove item when an attempt to open a recent file fails.
  * Limit most recent item list to, say, 10 items.
  * Add Clear Recent Items menu in File > Open Recent.

## Features:

* Recent File List
* user.yaml config files
  * For the file BuildIt.yaml the user can put a file BuildIt.user.yaml in the same folder.
  * When processing BuildIt.yaml in buildchimp, BuildIt.user.yaml is loaded second and any settings within BuildIt.user.yaml *replace* the equivalent BuildIt.yaml settings.
  * Uses:
    * Replace settings in the globals > environment area.
    * Another use might be to add additional *buildsteps* for special purposes. 

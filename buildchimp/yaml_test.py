#!/bin/python

import yaml		# pip install pyyaml
from pprint import pprint

yaml_test = R"""
a_dict:
  a: 3
  b: 4

a_list:
  - one thing
  - another thing

a_text_literal: |
    this
    is
    some literal text over multiple lines

a_text_literal_folded_style: >
    this
    is
    some literal text over multiple lines
"""

pprint( yaml.load(yaml_test) )

print("")

example_config = R"""
_magic_: buildchimp_project

buildsteps:

  - id: fv
    name: FileVersions
    description: Run a script to bump file versions
    inline_script_py: |
        import blah
        print("blah")
    dependencies:

  - id: buildcc_dbx
    name: BuildCC-Debug
    description: Build CommonCode in Debug mode.
    inline_script_sh: |
        echo hey
    dependencies:
      - fv

"""

pprint( yaml.load(example_config) )
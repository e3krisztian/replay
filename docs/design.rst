Abstract
========

This document is to describe how to achieve reproducibility of data files.


Rationale
=========

Currently we are unable to easily reproduce data files from inputs.
Goal: reliably produce data files from given inputs


Analysis
========

We are working with files as inputs and producing files as outputs.

The basic building blocks are scripts that take some input and produce some output.
Scripts might also require existence of certain other tools (stata, python modules, database engine, etc.).

There is a natural dependency between scripts, as one script's output can be another's input.

Scripts must run isolated, communicating only via their specified input-output.
One potential problem here is scripts using databases as input/leaving behind auxiliary output.

Given the set of specification of scripts, we could automatically run them in a proper order and thus compute the outputs.

---

- versioning of data/scripts
- non-file dependencies? (/db)


Currently we do not have
------------------------

- list of external inputs
- isolated scripts (they might use database as data exchange)
- script specifications
- a tool to build the dependency graph
- a tool to run the scripts in the proper order using the dependency graph


Requirements
============

The solution must

- cover the existing process
- be easy to use
- be easy to develop further
- provide guidelines for organizing the code
- provide tools for common tasks
  (e.g. accessing files in script specification, running command line tools, using the database)


Nice to have features
---------------------

- restrict script's access to resources to those defined in its specification
- verify script specifications (do all output created?)
- parallel execution of scripts


project types:
    tool:
        produce data, directly callable
        (e.g. parse_addresses, parse_names, color_parties, csvtools, psql, mETL)

    lib:
        python modules/packages (e.g. tarr, csvx)

    script:
        use tools and libs to produce some concrete data
        scripts are NOT intended to be reusable,
        however parts of them can evolve and be extracted into tools or libs


versioning:
    tools, libs

projects (especially scripts!) depend on exact versions of libs and tools
(requirements.txt)


supporting lib for scripts:
    - method to read input file by name (open stream by name for reading)
    - method to save output file by name (open stream by name for writing)
    - run a command line tool


script:
    description of a script:
        - input files
        - output files
        - python-dependencies (equivalent to pip freeze output (requirements.txt))
        - script type (python | shell | stata | ...?)
        - entry point (name of script to run)
        - description

    see sample_spec.yaml for an example


reproducing tools - in two layers:
    - tool to run scripts in proper order
        - inputs:
            - input data files
            - scripts
        - generate "makefile" from script descriptions
            (or similar config file for a build tool)
    - tool to run a script
        - inputs:
            - input data files
            - script
        - in a temporary directory, that is removed after script execution
        - in a new virtual environment
        - with a new database
        - provide a tool to connect to the database without any parameters
        - restrict access to files that are defined in the script's description
        - verify that the script indeed produced all of its output files


Solution plan[s]
================

1. Generate an input file to some build tool (e.g. for make) to build the missing/out of date data files
2. Integrate existing scripts with a workflow management software.


Scripts
=======

import complex xmls
    - write .csv-s per rovats

company frame
    - basic frame (sql? -> csv)
    - put_together_frame.py

locations
    - whitelists (ksh, posta, etc)
    - addresses from complex

name

ebuild


References
==========

- https://github.com/spotify/luigi#readme
  (professional looking code)
- http://pydoit.org/
- https://github.com/apenwarr/redo

Workflow [management] systems:

- http://www.taverna.org.uk/introduction/why-use-workflows/
- https://kepler-project.org/
- http://ptolemy.eecs.berkeley.edu/ptolemyII/


Acknowledgments
===============

Dániel mentioned both `make` and `luigi`.

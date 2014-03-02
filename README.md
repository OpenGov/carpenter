# Carpenter
A Python repository which repairs and analyzes tablular data

## Description
This module provides the capability to extract and repair blocks of
data from 2D tables. These blocks can then be individually processed,
stitched together, or filtered as needed by a particular program.

Autoconversions of cells along with a multi-tier flagging system for
each magnitude of change allows for a wide variety of error handling.
Additionally missing titles can be repaired from surrounding cells in
order to generate compelete blocks from implied headings.

## Dependencies
* allset
* pydatawrap

## Setup
### Installation
From source:

    python settup.py install

From pip:

    pip install carpenter

## Features
* Block detection
* Title repairing
* Tunable cell conversions
* Column re-orienting

## Navigating the Repo
### carpenter
The top level/front facing objects/functions

### carpenter/blocks
The block processing implementation detail files for the repository

### carpenter/regex
The regex suite used to perform cell type identification

### tests
All unit tests for the repo.  

## Language Preferences
* Google Style Guide
* Object Oriented (with a few exceptions)

## TODO
* Add refactor top-level functionality
* Add new usable functions
* Separate flagging some from block iteration code

## Author
Author(s): Matthew Seal

&copy; Copyright 2013, [OpenGov](http://opengov.com)

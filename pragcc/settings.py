# -*- encoding: utf-8 -*-

import os

# Project Directory
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

TEMPLATES_DIR = 'templates'

PARALLEL_FILE_NAME = 'parallel.yml'
PARALLEL_FILE_DIR = os.path.join(BASE_DIR,TEMPLATES_DIR)
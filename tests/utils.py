# -*- encoding: utf-8 -*-

import os
import re

def purge(dir, pattern):
    """
    https://stackoverflow.com/questions/1548704/delete-multiple-files-matching-a-pattern
    """
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))
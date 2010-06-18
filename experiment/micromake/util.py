class Recipe:
    def make(self, goal, dependencies):
        pass

from itertools import imap
import logging

import os
def walk_on_files(toppath):
    return (os.path.join(base, file)\
            for (base, subdirs, files) in os.walk(toppath)\
            for file in files)

def _modification_time(filepath):
    return os.stat(filepath).st_mtime

def older_than_dependencies(goal, dependencies):
    '''
    @var goal: filepath
    @var dependencies: iterable of filepaths
    '''
    goal_mtime = _modification_time(goal)
    for dep_mtime in imap(_modification_time, dependencies):
        if dep_mtime > goal_mtime:
            return True
    return False

def need_rebuild(goal, dependencies):
    '''
    @var goal: filepath
    @var dependencies: iterable of filepaths
    '''

    if os.access(goal, os.F_OK):
        return older_than_dependencies(goal, dependencies)
    else:
        return True

def dir_is_older(target_path, path):
    try:
        last_in_target, path_to_last = max(
            imap(lambda x: (_modification_time(x), x),
            walk_on_files(target_path)))
    except ValueError: # seems that target path have no files yet (max got empty sequence)
        return True

    logging.debug("Last modified in %s is %s (%s)", target_path, path_to_last, last_in_target)

    for x in walk_on_files(path):
        if _modification_time(x) > last_in_target:
            logging.debug("Found even more recent: %s", x)
            return True
    return False


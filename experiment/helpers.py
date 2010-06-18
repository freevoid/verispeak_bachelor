import os
def relative_path_generator(abspath):
    basedir = os.path.dirname(abspath)
    return lambda relpath: os.path.join(basedir, relpath)


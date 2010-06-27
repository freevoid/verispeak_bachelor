from matplotlib import rc, pyplot, font_manager

FONT_FILENAME = '/usr/share/fonts/corefonts/times.ttf'

#FONT_FILENAME = '/usr/share/fonts/corefonts/comic.ttf'

rc('text', usetex=False)
rc('font',
        family='serif',
        serif='Times New Roman, Times, Computer Modern Roman')#True)
rc('text.latex',unicode=True)
rc('text.latex',preamble='''\usepackage[utf8x]{inputenc}''')


fp = font_manager.FontProperties(fname=FONT_FILENAME)

from functools import partial

FUNCS_TO_REPLACE = ('set_xlabel', 'set_ylabel', 'text', 'legend')
def russify(subplot, attrs_to_replace=FUNCS_TO_REPLACE):
    for funcname in attrs_to_replace:
        f = getattr(subplot, funcname)
        setattr(pyplot, funcname, partial(f, fontproperties=fp))

russify(pyplot, ('xlabel', 'ylabel', 'title', 'text', 'legend'))

from matplotlib import rc, pyplot, font_manager

FONT_FILENAME = '/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf'

rc('text', usetex=False)
rc('text.latex',unicode=True)
rc('text.latex',preamble='\usepackage[utf8]{inputenc}')
rc('text.latex',preamble='\usepackage[russian]{babel}')

fp = font_manager.FontProperties(fname=FONT_FILENAME)

from functools import partial

FUNCS_TO_REPLACE = ('xlabel', 'ylabel', 'title', 'text')
for funcname in FUNCS_TO_REPLACE:
    f = getattr(pyplot, funcname)
    setattr(pyplot, funcname, partial(f, fontproperties=fp))


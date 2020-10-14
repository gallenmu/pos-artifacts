#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
rprint=print
from pprint import pprint as print
import codecs
import tikzplotlib


# In[ ]:


import import_ipynb
try:
    try:
        from tumcolor import TUMCOLOR, TUMCOLOR_RGB_STRINGS
    except ModuleNotFoundError:
        from util.tumcolor import TUMCOLOR, TUMCOLOR_RGB_STRINGS
except NameError:
    # ModuleNotFoundError was added with python3.6, prior versions throw NameError here
    from util.tumcolor import TUMCOLOR, TUMCOLOR_RGB_STRINGS


# In[ ]:


tikz_header = r"""\documentclass[tikz]{standalone}

\usepackage[utf8]{inputenc}
\usepackage{tumcolor}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.13}

\pgfplotsset{
    table/search path={data/},
}

\usepackage[binary-units=true]{siunitx}                                                                                                 
\sisetup{%                                                                                                              
        per-mode = symbol-or-fraction,                                                                                  
        math-micro = \ensuremath\mu,                                                                                    
%       text-rm=\fontsize{.9em}{1em}\selectfont,                                                                        
}                                                                                                                       
\DeclareSIUnit\byte{B}                                                                                                  
\DeclareSIUnit\bit{bit}                                                                                                 
\DeclareSIUnit\packets{pkts}                                                                                            
\DeclareSIUnit\packet{pkt}                                                                                              
\DeclareSIUnit\pps{pps}

\begin{document}%
"""

tikz_footer = r"""
\end{document}
"""

# replace mpl definitions and exports of tumcolors with actual tumcolors
# add data/ to all tsv paths
def post_process(code):
    mapping = {}
    new_code = []
    for line in code.split('\n'):
        # look for color definitions
        if 'definecolor' in line and 'rgb' in line:
            parts = line.split('rgb')
            rgb_string = parts[1].strip().strip('{}')
            name = parts[0].split('definecolor')[1].strip('{}')
            if rgb_string in TUMCOLOR_RGB_STRINGS:
                color = TUMCOLOR_RGB_STRINGS[rgb_string]
                mapping[name] = color
                continue
        # look for color usage
        for name, tumcolor in mapping.items():
            if name in line:
                line = line.replace(name, tumcolor)
                
        # look for externalized tsvs
        if '.tsv};' in line:
            line = 'data/' + line
        new_code.append(line) 
    return '\n'.join(new_code)


# taken from https://github.com/nschloe/tikzplotlib/blob/master/tikzplotlib/_save.py
# newer commit already allow context manipulation, but not yet deployed with pip
# we also do some other magic in post proessing
def get_tikz_code(*args, axis_width='10cm', axis_height='5cm',
                  clean_figure=False, target_resolution=600, scale_precision=1.0, **kwargs):
    if clean_figure:
        tikzplotlib.clean_figure(target_resolution=target_resolution,
                                 scale_precision=scale_precision)
    code = tikzplotlib.get_tikz_code(*args, 
                                     externalize_tables=True, 
                                     override_externals=True, 
                                     strict=True,
                                     axis_width=axis_width,
                                     axis_height=axis_height,
                                     **kwargs)
    code = post_process(code)
    code = '{}{}{}'.format(tikz_header, code, tikz_footer)
    return code


# In[ ]:


# need to copy this as well so that it uses our own get_tikz_code function
def save_plt(filepath, *args, name='', encoding=None, **kwargs):
    if name:
        name = name + '-'

    filepath_neutral = '{}{}.tex'.format(name, filepath)
    # we want our tsv files to end up in data/, the .tex in figures/
    filepath = 'data/' + filepath_neutral
    filepath_end = 'figures/' + filepath_neutral
    
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists('figures'):
        os.makedirs('figures')
    
    code = get_tikz_code(*args, filepath=filepath, **kwargs)
    with codecs.open(filepath, "w", encoding) as fh:
        fh.write(code)
        
    # move this .tex back to parent (from data/)
    os.rename(filepath, filepath_end)
    rprint('Generated ' + filepath_end)
    return


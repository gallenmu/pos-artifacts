#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from matplotlib.colors import _colors_full_map, ListedColormap
from matplotlib.cm import register_cmap
from cycler import cycler


# In[ ]:


# allow using tumcolors
TUMCOLOR = dict()
TUMCOLOR['TUMBlue'] = (0.00,0.40,0.74)
TUMCOLOR['TUMWhite'] = (1.00,1.00,1.00)
TUMCOLOR['TUMBlack'] = (0.00,0.00,0.00)
TUMCOLOR['TUMDarkerBlue'] = (0.00,0.32,0.58)
TUMCOLOR['TUMDarkBlue'] = (0.00,0.20,0.35)
TUMCOLOR['TUMDarkGray'] = (0.20,0.20,0.20)
TUMCOLOR['TUMMediumGray'] = (0.50,0.50,0.50)
TUMCOLOR['TUMLightGray'] = (0.80,0.80,0.80)
TUMCOLOR['TUMIvony'] = (0.85,0.84,0.80)
TUMCOLOR['TUMOrange'] = (0.89,0.45,0.13)
TUMCOLOR['TUMGreen'] = (0.64,0.68,0.00)
TUMCOLOR['TUMLightBlue'] = (0.60,0.78,0.92)
TUMCOLOR['TUMLighterBlue'] = (0.39,0.63,0.78)
TUMCOLOR['TUMPurple'] = (0.41,0.03,0.35)
TUMCOLOR['TUMDarkPurple'] = (0.06,0.11,0.37)
TUMCOLOR['TUMTurquois'] = (0.00,0.47,0.54)
TUMCOLOR['TUMDarkGreen'] = (0.00,0.49,0.19)
TUMCOLOR['TUMDarkerGreen'] = (0.40,0.60,0.11)
TUMCOLOR['TUMYellow'] = (1.00,0.86,0.00)
TUMCOLOR['TUMDarkYellow'] = (0.98,0.73,0.00)
TUMCOLOR['TUMLightRed'] = (0.84,0.30,0.07)
TUMCOLOR['TUMRed'] = (0.77,0.03,0.11)
TUMCOLOR['TUMDarkRed'] = (0.61,0.05,0.09)
TUMCOLOR['TUM150LightMustard'] = (0.91,0.78,0.22)
TUMCOLOR['TUM150Mustard'] = (0.79,0.67,0.16)
TUMCOLOR['TUM150LightOrange'] = (0.97,0.65,0.00)
TUMCOLOR['TUM150Orange'] = (0.95,0.57,0.00)
TUMCOLOR['TUM150LightGreen'] = (0.74,0.81,0.12)
TUMCOLOR['TUM150Green'] = (0.64,0.75,0.09)
TUMCOLOR['TUM150LighterBlue'] = (0.57,0.83,0.95)
TUMCOLOR['TUM150LightBlue'] = (0.36,0.77,0.95)
TUMCOLOR['TUM150LightPink'] = (0.95,0.56,0.58)
TUMCOLOR['TUM150Pink'] = (0.89,0.51,0.56)

# old matplotlib only checks color names using .lower()
lower_case = dict()
for color, rgb in TUMCOLOR.items():
    lower_case[color.lower()] = rgb

# add to mpl internal structure
_colors_full_map.update(TUMCOLOR)
_colors_full_map.update(lower_case)

# create strings that we search for in the exported code
TUMCOLOR_RGB_STRINGS = dict()
for color, rgb in TUMCOLOR.items():
    vals = []
    for val in rgb:
        if val == 0.0:
            val = 0
        if val == 1.0:
            val = 1
        vals.append(str(val))
    rgb_string = ','.join(vals)
    TUMCOLOR_RGB_STRINGS[rgb_string] = color


# In[ ]:


# cycler that should be used for mpl axis environment
tumcolor_cycler = (cycler(linewidth=[1, 2, 3, 4]) *
                   cycler(linestyle=['-', '--', '-.']) *
                   #cycler(marker=['*', 'o', 'x']) *
                   cycler(color=['TUMBlue', 'TUMOrange', 'TUMGreen',
                                 'TUMLightBlue', 'TUMDarkYellow', 'TUMPurple',
                                 'TUMRed', 'TUMDarkGreen'])
                  )


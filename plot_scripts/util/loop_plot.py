#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json
import os
from glob import glob
rprint=print
from pprint import pprint as print


# In[ ]:


def read_loopfile(loopfile):
    data = None
    with open(loopfile) as infile:
        try:
            data = json.load(infile)
        except json.JSONDecodeError:
            # for old posd files, delete
            infile.seek(0)
            content = infile.read()
            content = content.replace("'", '"')
            data = json.loads(content)
    return data


# In[ ]:


def extract_loop_data(paths, loop_filename, basepath='/'):
    data = {}
    if not isinstance(paths, list):
        paths = [paths]

    for path in paths:
        name = None
        if not isinstance(path, tuple):
            name = path.replace('_', '-') # tex friendly path
        else:
            name = path[1]
            path = path[0]
        
        data[name] = {}
        
        extended_path = os.path.join(basepath, path)
        loopfile = os.path.join(extended_path, loop_filename)
        rprint('Processing loopfiles ' + loopfile)
        
        loopfiles = glob(loopfile)
        for loop in sorted(loopfiles):
            rprint('Loopfile ' + loop)
            run = int(loop.split('_run')[1].split('.loop')[0])
                
            # load data
            try:
                raw_data = read_loopfile(loop)
            except FileNotFoundError as exce:
                rprint('Skipping {} - {}'.format(loop, exce), file=sys.stderr)
                continue
            data[name][run] = raw_data

    return data


# In[ ]:


def _plot_loop(paths, name, tp_data, loop_file, loop_order, metrics, function, ape, **kwargs):
    print('---------------- plotting using loop variables ----------------------')
    loop_data = extract_loop_data(paths, loop_file, **kwargs)
    
    # group data by loop params
    groups = {}
    # first key
    key = loop_order[0]
    keys = [key]
    for exp, l_data in loop_data.items():
        for run, data in l_data.items():
            value = str(data[key])
            del data[key]
            tup = (exp, run, data)
            value = '{}-{}'.format(key, value)
            try:
                groups[value].append(tup)
            except KeyError:
                groups[value] = [tup]
                
    # if we have more keys sort the new subgroups
    for key in loop_order[1:-1]:
        new_groups = {}
        for old_name, group in groups.items():
            for item in group:
                test, run, rest = item
                current = rest[key]
                del rest[key]
                new_name = '{}-{}-{}'.format(old_name, key, current)
                if new_name not in new_groups:
                    new_groups[new_name] = []
                new_groups[new_name].append((test, run, rest))
        groups = new_groups
                    
    # names to {exp: {number: name}}
    mapping = {}
    for key in tp_data.keys():
        exp = '/'.join(key.split('/')[:-1])
        number = int(key.split('_run')[1].split('.')[0])
        if exp not in mapping:
            mapping[exp] = {}
        mapping[exp][number] = key        

    # plot groups
    for key, content in groups.items():
        plotname = key
        if name:
            plotname = '{}_{}'.format(name, key)
        for metric in metrics:
            function(plotname, content, mapping, tp_data, key=metric, additional_plot_exports=ape)


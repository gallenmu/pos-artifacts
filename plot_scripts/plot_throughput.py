#!/usr/bin/env python
# coding: utf-8

# ## Generating throughput and packet rate plots from MoonGen data
# 
# ### Input format
# * MoonGen stdout or csv (tx and rx split to different files)
# * line every second containing the RX or TX data per core
# ```
# ...
# [Packets counted] RX: 0.10 Mpps, 51 Mbit/s (67 Mbit/s with framing)
# [Device: id=0] TX: 0.10 Mpps, 51 Mbit/s (67 Mbit/s with framing)
# [Packets counted] RX: 0.10 Mpps, 51 Mbit/s (67 Mbit/s with framing)
# [Device: id=0] TX: 0.10 Mpps, 51 Mbit/s (67 Mbit/s with framing)
# ...
# ```
# 
# ### Features
# * througput (with and without framing), packet rate
# * min, max, avg of the above
# * plots loop experiment
#   * define the order of loop variables
# * figures created in figures/*.tex
# * externalized data into data/*.tsv
# * makefile to generate pdfs
# 
# ## You should not have to edit any of the following cells besides the last one
# * However you might want to tweak some plots manually
# 
# ## errors
# * if you get tex capacity exceeded when trying to compile the figures you have too many data points

# In[ ]:


import os
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.pyplot import savefig
from glob import glob
rprint=print
from pprint import pprint as print
import numpy as np


# In[ ]:


# import other utility notebooks
import import_ipynb
# NOTE: tumcolors only work with python 3.6 and newer
from util.tumcolor import tumcolor_cycler
from util.i8_tikzplotlib import save_plt
from util.loop_plot import _plot_loop


# In[ ]:


# for command line invocation
def run_from_cli():
    import argparse

    parser = argparse.ArgumentParser(description='Generating plots from histogram data')
    parser.add_argument('basepath', metavar='BASEPATH', type=str,
                        help='Base path for all experiments')
    parser.add_argument('path', metavar='PATH', type=str, nargs='+',
                        help='path to one or more csv file(s), will be RESULTS/<path>/HIST_FILENAME')
    parser.add_argument('--label', metavar='LABEL', type=str, action='append',
                        help='Nicer name for experiments')
    parser.add_argument('--name', type=str, default='',
                        help='suffix for generated files, e.g. hdr-NAME.tex')
    
    parser.add_argument('--metric', metavar='METRICS', type=str, action='append',
                        help='Metric(s) that shall be plotted')
    parser.add_argument('--additional-export', metavar='EXTRA_EXPORT_FORMAT', type=str, action='append',
                        help='Additional export format')
    
    parser.add_argument('--throughput-filename', metavar='TP_FILENAME', type=str, default='throughput.csv',
                        help='name of the throughput data file, wildcard possible')
    parser.add_argument('--throughput-strip', metavar='TP_STRIP', type=int, default=0,
                        help='the amount of lines from moongen stdout that should be skipped (tail AND head)')

    parser.add_argument('--loop-filename', metavar='LOOP_FILENAME', type=str,
                        help='name of the throughput data file, wildcard possible')
    parser.add_argument('--loop-order', metavar='LOOP_ORDER', type=str, action='append',
                        help='Order of the loop variables')

    args = parser.parse_args()
    if args.label and not len(args.label) == len(args.path):
        raise argparse.ArgumentTypeError('Must provide a label for either no or all paths')
        
    experiments = []
    if args.label:
        experiments = list(zip(args.path, args.label))
    else:
        experiments = args.path
        
    plot(experiments,
         basepath=args.basepath,
         name=args.name,
         additional_plot_exports=args.additional_export,
         throughput_file=args.throughput_filename,
         throughput_strip=args.throughput_strip,
         
         metrics=args.metric,
         
         loop_file=args.loop_filename,
         loop_order=args.loop_order
    )
        
    sys.exit()


# In[ ]:


MOONGEN_DATA_OUTPUT = ['mpps', 'mbit', 'mbitcrc']

class ParsingError(Exception):
    pass

def read_moongen_stdout(exp, strip):
    data = dict()
    valid_file = dict()
    # id, direction, mpps, mbit, mbit with framing
    with open(exp) as infile:
        # [Packets counted] RX: 0.10 Mpps, 49 Mbit/s (65 Mbit/s with framing)
        # [Device: id=0] TX: 0.10 Mpps, 51 Mbit/s (67 Mbit/s with framing)
        for line in infile:
            # filter unwanted lines
            if not (('[Packets counted]' in line or '[Device: id=' in line) and ('RX' in line or 'TX' in line)):
                continue
                
            # check if we reached the last lines containing the summary
            summary = False
            if 'StdDev' in line and 'total' in line:
                summary = True
                
            cid = 0
            direction = 'rx'
            mpps = 0 
            mbit = 0
            mbitcrc = 0
            
            parts = line.split('] ')            
            # get ID
            if parts[0].endswith('Packets counted'):
                #TODO does this make sense?
                cid = 0
            else:
                cid = int(parts[0].split('=')[-1])
                
            # get direction
            parts = parts[1].split(' ')
            if parts[0].startswith('RX'):
                direction = 'rx'
            elif parts[0].startswith('TX'):
                direction = 'tx'
            else:
                raise ValueError('Unable to parse direction: {}'.format(line))
            
            # prepare structure
            if not cid in data:
                data[cid] = dict()
            if not direction in data[cid]:
                data[cid][direction] = dict()
            for item in MOONGEN_DATA_OUTPUT:
                if not item in data[cid][direction]:
                    data[cid][direction][item] = list()
                
            # get other data
            if not summary:
                mpps = float(parts[1])
                mbit = float(parts[3])
                mbitcrc = float(parts[5][1:])
                
                data[cid][direction]['mpps'].append(mpps)
                data[cid][direction]['mbit'].append(mbit)
                data[cid][direction]['mbitcrc'].append(mbitcrc)
                valid_file[direction] = True
            else:
                mpps = float(parts[1])
                mbit = float(parts[5])
                mbitcrc = float(parts[9][1:])
                
                data[cid][direction]['avg_mg_mpps'] = mpps
                data[cid][direction]['avg_mg_mbit'] = mbit
                data[cid][direction]['avg_mg_mbitcrc'] = mbitcrc
                
                # add self calculated averages with skips as default
                data[cid][direction]['avg_mpps'] = np.mean(data[cid][direction]['mpps'][strip:-(strip+1)])
                data[cid][direction]['avg_mbit'] = np.mean(data[cid][direction]['mbit'][strip:-(strip+1)])
                data[cid][direction]['avg_mbitcrc'] = np.mean(data[cid][direction]['mbitcrc'][strip:-(strip+1)])
                
                valid_file[direction + '_summary'] = True
        if not len(valid_file.keys()) == 4:
            raise ParsingError('Invalid file: {}'.format(valid_file))
                
    return data


# In[ ]:


def add_values(data, prefix, func, strip):
    for cid, data2 in data.items():
        for direction, data3 in data2.items():
            for item in MOONGEN_DATA_OUTPUT:
                data[cid][direction][prefix + '_' + item] = func(data3[item][strip:-(strip+1)])


# In[ ]:


def extract_tp_data(paths, basepath='/', throughput_file='histogram.csv', throughput_strip=0):
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
            
        extended_path = os.path.join(basepath, path)
        experiment = os.path.join(extended_path, throughput_file)
        rprint('Processing ' + extended_path)
        
        subexperiments = glob(experiment)
        update_name = False
        base_name = name
        if len(subexperiments) > 1:
            update_name = True
        
        for exp in sorted(subexperiments):
            # replace everything that is not wildcard
            if not (basepath == '.' or basepath == '..'):
                histo = exp.replace(basepath, '')
            histo = histo.replace(path, '')
            histo = histo.replace(throughput_file, '')
            histo = histo.replace('//', '/')
            histo = histo[:-1]
            
            rprint('Subexperiment ' + histo)
            if update_name:
                name = base_name + histo
                
            # load data
            try:
                raw_data = read_moongen_stdout(exp, throughput_strip)
            except (FileNotFoundError, ParsingError) as exce:
                rprint('Skipping {} - {}'.format(histo, exce), file=sys.stderr)
                continue
                
            # different processing steps
            add_values(raw_data, 'max', max, throughput_strip)
            add_values(raw_data, 'min', min, throughput_strip)
            
            # store data
            data[name] = {}
            data[name]['tp'] = raw_data

    return data


# In[ ]:


def plot_loop(name, content, mapping, tp_data, key='max_mbit', additional_plot_exports=None):
    if not additional_plot_exports:
        additional_plot_exports = []
        
    fig, ax = plt.subplots(figsize=(9,6))
    ax.set_prop_cycle(tumcolor_cycler)
    
    axis_label = None
    xss = {}
    yss = {}
    mapped = {}
    
    # gather data based on mapping
    for exp, run, type in content:
        axis_label = list(type.keys())[0]
        if exp not in xss:
            xss[exp] = []
            yss[exp] = {}
        xss[exp].append(list(type.values())[0])
        try:
            mapped[exp] = tp_data[mapping[exp][run]]
        except KeyError as exce:
            continue
        else:
            mapped[exp] = mapped[exp]['tp']
            for cid, data in mapped[exp].items():
                for direction, data in data.items():
                    y = data[key]
                    full = '{}-{}-{}'.format(exp, cid, direction)
                    try:
                        yss[exp][full].append(y)
                    except KeyError:
                        yss[exp][full] = [y]
        
    for exp, data in sorted(mapped.items()):
        for cid, data in sorted(data.items()):
            for direction, data in sorted(data.items()):
                full = '{}-{}-{}'.format(exp, cid, direction)
                ys = yss[exp][full]
                xs = xss[exp]
                zipped = list(zip(xs, ys))
                zipped.sort(key=lambda tup: tup[0])
                xs, ys = zip(*zipped)
                
                ax.plot(xs, ys, marker='x', label = full)
    
    plt.ylim(bottom=0)
    #plt.xlim(left=min_x_value)
    #plt.xlim(right=max_x_value)
                
    ax.grid()
    ax.set(ylabel=METRIC_TO_LABEL[key],
           xlabel=axis_label)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    save_plt('loop_{}'.format(key), name=name)
    for ape in additional_plot_exports:
        rprint('Additional export as {}'.format(ape))
        savefig('figures/{}_loop_{}.{}'.format(name, key, ape), format=ape)
    plt.show()


# In[ ]:


def plot(paths, name=None, throughput_file=None, throughput_strip=0,
         additional_plot_exports=None, metrics=None,
         loop_file=None, loop_order=None,
         **kwargs):
    
    # extract throughput data
    tp_data = extract_tp_data(paths, throughput_file=throughput_file, throughput_strip=throughput_strip, **kwargs)
    
    if not tp_data:
        rprint('No throughput data found', file=sys.stderr)
        return
    
    if not metrics:
        print('you need to define the metrics of interest (METRIC_TO_LABEL.keys())')
        return
    if (loop_file and not loop_order) or (loop_order and not loop_file):
        raise RuntimeError('must define loop_file AND loop_order if using loop variables')
    if loop_file and loop_order:
        _plot_loop(paths, name, tp_data, loop_file, loop_order, metrics, plot_loop, additional_plot_exports, **kwargs)


# In[ ]:


METRIC_TO_LABEL = {
    'max_mbit'   : 'Maximum Throughput [Mbit/s]',
    'max_mbitcrc': 'Maximum Throughput (with Framing) [Mbit/s]',
    'max_mpps'   : 'Maximum Packet Rate [Mpps]',
    'avg_mbit'   : 'Average Throughput [Mbit/s]',
    'avg_mbitcrc': 'Average Throughput (with Framing) [Mbit/s]',
    'avg_mpps'   : 'Average Packet Rate [Mpps]',
    'min_mbit'   : 'Minimum Throughput [Mbit/s]',
    'min_mbitcrc': 'Minimum Throughput (with Framing) [Mbit/s]',
    'min_mpps'   : 'Minimum Packet Rate [Mpps]',
    'avg_mg_mbit'   : 'Average Throughput [Mbit/s]',
    'avg_mg_mbitcrc': 'Average Throughput (with Framing) [Mbit/s]',
    'avg_mg_mpps'   : 'Average Packet Rate [Mpps]',
}


# In[ ]:


# this will only be triggered if invoked from command-line
if not sys.argv[0].endswith('ipykernel_launcher.py'):
    run_from_cli()


# # Make your edits in the cell below

# In[ ]:


RESULTS='/srv/testbed/results/gallenmu/default/'
THROUGHPUT_FILENAME = 'throughput_run*.log'
METRICS = ['avg_mpps', 'max_mpps']

# can include wildcards
LOOP_FILENAME = '*_unknown_run*.loop'

# using a pos loop experiment
# define the format of the loopfile
# and define the order of the loop parameters
plot([
      ('2020-10-07_23-22-39_868017/intelexp1', 'Test1'),
     ],
     basepath=RESULTS,
     name='hardware',
     throughput_file=THROUGHPUT_FILENAME,
     throughput_strip=2,
    
     metrics=METRICS,
    
     loop_file=LOOP_FILENAME,
     loop_order=['pkt_sz', 'pkt_rate'],
)

# invocation from CLI
# python3 plot_throughput.py /srv/testbed/results/gallenmu/default/ \
#   2020-10-07_23-22-39_868017/intelexp1 --label Test1
#  --name hardware --throughput-filename 'throughput_run*.log' --throughput-strip 2 --metric avg_mpps --metric max_mpps \
#   --loop-filename '*_unknown_run*.loop' --loop-order pkt_sz --loop-order pkt_rate --additional-export svg


# In[ ]:





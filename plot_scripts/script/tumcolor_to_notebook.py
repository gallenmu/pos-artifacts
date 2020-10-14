#! /usr/local/bin/python3

with open('tumcolor.sty') as fh:
    for line in fh:
        if 'definecolor' in line and 'rgb' in line:
            parts = line.split('{')
            name  = parts[1].strip().strip('}')
            rgb = parts[-1].split('}')[0]
            print("TUMCOLOR['{}'] = ({})".format(name, rgb))

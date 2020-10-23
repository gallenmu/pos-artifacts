import argparse
import glob
import json
import os
from pathlib import Path
from string import Template
import subprocess
import distutils.core
import sys

parser = argparse.ArgumentParser(description='Pos publisher publishes pos experiments')
parser.add_argument('-x', '--experiment_path', required=True,
                    help='path to main folder containing the pos experiment scripts')
parser.add_argument('-r', '--result_path', nargs='+', action='append', required=True,
                    help='paths to main folder containing the pos results')
parser.add_argument('-o', '--output_path', default='.',
                    help='path to main folder of the output (default path: .)')
parser.add_argument('-g', '--git_repo', required=True,
                    help='git repo where to publish the artifacts')
args = parser.parse_args()

EXPERIMENT_PATH = args.experiment_path
RESULT_PATHS = flat_list = [item for sublist in args.result_path for item in sublist]
OUTPUT_PATH = args.output_path
WEB_PATH = 'web'
NAV_PATH = '_includes/nav.html'
EX_PATH = WEB_PATH + '/' + 'experiment.html'

ALLOCATIONS_PATH = 'config/allocation.json'

REPO_EXPLANATION = "All available experiment artifacts are publicly available in a <a href=\"" + args.git_repo + "\">git repository</a>."
EXPERIMENT_FILE = 'experiment.sh'
EXPERIMENT_EXPLANATION = """The task of this script is the initialization and preparation of the experiment execution. It is executed on the management host."""
DUT_SETUP_FILE = 'dut/setup.sh'
DUT_MEASUREMENT_FILE = 'dut/measurement.sh'
LOADGEN_SETUP_FILE = 'loadgen/setup.sh'
LOADGEN_MEASUREMENT_FILE = 'loadgen/measurement.sh'

DUT_NODE_EXPLANATION = """The task of this node is the setup and execution of the investigated packet processing device."""
LOADGEN_NODE_EXPLANATION = """The task of this node is the setup and execution of the load generator creating the load for the device under test."""
PARAMETER_EXPLANATION = """List of parameters that were used for this instance of the experiment."""
EVALUATION_EXPLANATION = """The evaluation script that plots the results."""
PUBLICATION_EXPLANATION = """The publication script that created this website."""

NAV = """<div style="padding: 10pt 5pt 5pt 5pt; background-color: white"><b>Experiments</b></div>
  <ul class="nav-list">
$liments  </ul>"""

NAV_ELEMENT = """<li {% if page.url == "/web/${page}.html" %}class="current_path current"{% endif %}><a href="{{ site.url }}/web/${page}.html">${name}</a></li>"""

SMALL_TITLE_TEMPLATE = """<h3>${title}</h3>\n"""
SCRIPT_TEMPLATE = """<details><summary>${title}</summary><pre><code>${code}</code></pre></details>\n"""
FIGURE_TEMPLATE = """<figure style="text-align:center;"><img src="../${svgpath}" /><figcaption>${caption}</figcaption></figure>\n"""
P_TEMPLATE = """<p>${content}</p>\n"""


def evaluate(result_path, loadgen_name, experiment_id):
    """Evaluate the measurement before building the website."""
    plot_script = os.path.abspath('plot_scripts/plot_throughput.py')
    prog = ['python3', plot_script, '\'\'', result_path + '/' + loadgen_name,
            '--label', 'T',
            '--name', experiment_id,
            '--throughput-filename', 'throughput_run*.log',
            '--throughput-strip', '2',
            '--metric', 'avg_mpps',
            #'--metric', 'max_mpps',
            '--loop-filename', '*_unknown_run*.loop',
            '--loop-order', 'pkt_sz',
            '--loop-order', 'pkt_rate',
            '--additional-export', 'svg'
           ]
    plot_call = ''
    for string in prog:
        plot_call = plot_call + ' ' + string
    with subprocess.Popen(prog, stdout=subprocess.PIPE) as proc:
        proc.stdout.read()
    return plot_call


# create output folder if necessary
output_folder = Path(OUTPUT_PATH)
#if output_folder.exists():
#    shutil.rmtree(output_folder)
distutils.dir_util.copy_tree('./template', str(output_folder))
#shutil.copytree('./template', output_folder)

def create_nav():
    i = 0
    liments = ""
    for result in RESULT_PATHS:
        stemp = Template(NAV_ELEMENT)
        name = 'Experiment ' + str(i)
        page = result.split('/')[-1]
        element = stemp.substitute(name=name, page=page)
        i += 1
        liments = liments + element + '\n'
    navtemp = Template(NAV)
    nav = navtemp.substitute(liments=liments)

    read_data = ""
    with open(output_folder.joinpath(NAV_PATH)) as fil:
        read_data = fil.read()
    with open(output_folder.joinpath(NAV_PATH), mode='w') as fil:
        output = Template(read_data)
        output = output.substitute(navigation=nav)
        fil.write(output)

create_nav()

def read_script(filename):
    files = glob.glob(EXPERIMENT_PATH + '/**/*.sh', recursive=True)
    matching = [s for s in files if filename in s]
    read_data = ''
    if len(matching) == 1:
        with open(matching[0]) as filil:
            read_data = filil.read()
    else:
        print('Wrong number of main scripts found')
        sys.exit(1)
    return read_data

def read_vars(resultfolder):
    with open(Path(resultfolder).joinpath(ALLOCATIONS_PATH)) as json_file:
        data = json.load(json_file)
        return data['variables']
        #print(json.dumps(data['variables'], indent=4, sort_keys=True))

def read_id(resultfolder):
    with open(Path(resultfolder).joinpath(ALLOCATIONS_PATH)) as json_file:
        data = json.load(json_file)
        return data['id']

def detect_host(resultfolder, setupscript):
    files = glob.glob(resultfolder + '/**/*_unknown.file', recursive=True)
    for fil in files:
        with open(fil) as opn:
            if setupscript == opn.read():
                return fil.split('/')[-2]
    return ''

def create_experiments():
    ex_temp_data = ""
    with open(output_folder.joinpath(EX_PATH)) as fil:
        ex_temp_data = fil.read()
    i = 0
    #liments = ""
    for result in RESULT_PATHS:
        variables = read_vars(result)
        title = 'Experiment ' + str(i)
        name = result.split('/')[-1]
        name = name + '.html'
        with open(output_folder.joinpath(WEB_PATH).joinpath(name), mode='w') as fil:
            output = Template(ex_temp_data)
            content = ''

            loadgen_setup = read_script(LOADGEN_SETUP_FILE)
            loadgen_experiment = read_script(LOADGEN_MEASUREMENT_FILE)
            hostname = detect_host(result, loadgen_setup)
            experiment_id = read_id(result)
            plot_call = evaluate(result, hostname, experiment_id)

            par_template = Template(P_TEMPLATE)

            # svgs
            svgs = glob.glob('figures/' + experiment_id + '*.svg')
            print("The generated plots were written to: " + svgs)
            content += par_template.substitute(content='') # empty paragraph to avoid first-of application to next paragraph
            figure_template = Template(FIGURE_TEMPLATE)
            for svg in svgs:
                content += figure_template.substitute(svgpath=svg, caption=svg.replace('/figures/', '').replace('.svg', ''))

            # git
            content += par_template.substitute(content='') # distance
            small_title_template = Template(SMALL_TITLE_TEMPLATE)
            content += small_title_template.substitute(title='Git Repository')
            content += par_template.substitute(content=REPO_EXPLANATION)
            script_template = Template(SCRIPT_TEMPLATE)
            content += script_template.substitute(title='Git clone', code='git clone ' + args.git_repo + ' /root/pos-artifacts')

            # main script
            content += par_template.substitute(content='') # distance
            content += small_title_template.substitute(title='Experiment Setup')
            content += par_template.substitute(content=EXPERIMENT_EXPLANATION)
            read_data = read_script(EXPERIMENT_FILE)
            content += script_template.substitute(title='Experiment script', code=read_data)

            # parameters
            content += par_template.substitute(content='') # distance
            content += small_title_template.substitute(title='Global and Loop Parameters')
            content += par_template.substitute(content=PARAMETER_EXPLANATION)
            content += script_template.substitute(title='Global parameters', code=json.dumps(variables['global'], indent=4, sort_keys=True))
            content += script_template.substitute(title='Loop parameters', code=json.dumps(variables['loop'], indent=4, sort_keys=True))

            # load generator
            content += par_template.substitute(content='') # distance
            content += small_title_template.substitute(title='Load Generator')
            content += par_template.substitute(content=LOADGEN_NODE_EXPLANATION)
            content += script_template.substitute(title='Local parameters', code=json.dumps(variables[hostname], indent=4, sort_keys=True))
            content += script_template.substitute(title='Setup script', code=loadgen_setup)
            content += script_template.substitute(title='Measurement script', code=loadgen_experiment)

            # device under test
            content += par_template.substitute(content='') # distance
            content += small_title_template.substitute(title='Device under Test')
            content += par_template.substitute(content=DUT_NODE_EXPLANATION)
            dut_setup = read_script(DUT_SETUP_FILE)
            dut_measurement = read_script(DUT_MEASUREMENT_FILE)
            hostname = detect_host(result, dut_setup)
            content += script_template.substitute(title='Local parameters', code=json.dumps(variables[hostname], indent=4, sort_keys=True))
            content += script_template.substitute(title='Setup script', code=loadgen_setup)
            content += script_template.substitute(title='Measurement script', code=dut_measurement)

            # evaluation
            content += par_template.substitute(content='') # distance
            content += small_title_template.substitute(title='Evaluation')
            content += par_template.substitute(content=EVALUATION_EXPLANATION)
            plot_call = 'cd ' + os.getcwd() + '\n' + plot_call
            content += script_template.substitute(title='Evaluation script call', code=plot_call)

            # publication
            content += par_template.substitute(content='') # distance
            content += small_title_template.substitute(title='Publication')
            content += par_template.substitute(content=PUBLICATION_EXPLANATION)
            call = 'cd ' + os.getcwd() + '\n python3 '
            call += ' '.join(sys.argv)
            content += script_template.substitute(title='Publication script call', code=call)


            output = output.substitute(title=title, content=content)
            fil.write(output)

        i += 1

create_experiments()


#print(EXPERIMENT_PATH)
#print(RESULT_PATHS)
#print(OUTPUT_PATH)


# Plotting scripts for measurement data generated in I8 testbeds

## Setup
Best practise is to install everything into a virtualenv

### Virtualenv
```
virtualenv -p python3 .venv3
source .venv3/bin/activate
pip3 install -r requirements
```
### Jupyter Notebooks
```
jupyter-notebook --port <PORT>
```
Access your browser
```
localhost:<PORT>
```
And navigate to your plotting script

### Convert jupyter notebook to regular python script
```
util/nbconvert.sh <.ipynb>
```

## Usage
### jupyter notebooks
* load the notebook
* adapt the last cell with paths to your data
* run all cells
* make changes to graphs, data, ...
### python script
* all notebooks are available as equivalent python scripts
* use with --help to see command-line options

## Scripts
### Latency
* plot_histogram.{ipynb, py} for histogram and (optional) sequence data
* generates commonly used views
  * optional: sequence (distribution over time)
  * histogram
  * Cumulative Distribution Function (CDF)
  * High Dynamic Range (HDR)

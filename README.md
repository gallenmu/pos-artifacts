# Experiment artifacts

The plain orchestrating service (pos) is a test controller that creates reproducible network experiments.
This repo contains all the artifacts for such an experiment.

The artifacts contain:

* experiment scripts
* measurement results
* evaluation scripts
* plots
* website generator

## Content

The experiment and its results are contained in the following folders.
To fully document the actual experiments, all artifacts listed below must be released.

* `./experiment`: Experiment scripts to be executed on the pos management host
* `./results`: Measurement results of the executed experiment
* `./plot_scripts`: Plotting scripts for generating plots
* `./figures`: Generated plots (tex and svg files)
* `./data`: Data used for plotting

The associated website uses the following files:

* `./_includes`, `./web`, `_config.yml` and `index.html`: Content files for the website
* `./template`: Initial website template used by the website generator
* `publish.py`: Website generation script

For the website to work, the content of the `ìnclude` and `web` folder, the `_config.yml` and the `ìndex.html` must be added to a repository.
The `./template` folder and `publish.py` file are only used for website generation; publication of these files is not required for the website to work.
However, publication is recommended to allow others to easily create their own website.

## How to use the tools

We created a [website](https://gallenmu.github.io/pos-artifacts) that explains how to reproduce this experiment.

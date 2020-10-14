#! /bin/bash
if [ $# -eq 1 ]; then
	jupyter nbconvert --to script $1
else
	find . -name "*.ipynb" ! -path "*venv*" ! -path "*ipynb_checkpoints*" \
		| xargs jupyter nbconvert --to script
fi

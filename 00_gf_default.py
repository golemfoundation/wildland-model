#!/usr/bin/python3

from bootstrap_golem import golem_foundation_init
from reporting import dump_state, prep_output_dir

prep_output_dir()
golem_foundation_init()

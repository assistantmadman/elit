#!/usr/bin/python
import os
import sys
import yaml


def ConfGet(f):
    try:
        c_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            f
        )
        with open(c_file, 'r') as yaml_conf:
            conf = yaml.load(yaml_conf)
    except Exception:
        sys.exit(1)
    return conf

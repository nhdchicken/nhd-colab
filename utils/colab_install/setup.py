#!/usr/bin/env python
"""The setup script.

"""
import sys
import os
from setuptools import setup, find_packages

setup_dir = os.path.dirname(__file__)

# ------------------
# Execution
# -----------------------------------------------------------------------------
# This calls the setup. It should not need to be configured.
# -----------------------------------------------------------------------------

setup(
    name='colab-install',
    author="Chicken Chicken",
    author_email='nhdchicken@gmail.com',
    version='1.0',
    description="notebook installer for nhd-colab notebooks ",
    install_requires=['click', 'pyyaml'],
    py_modules=['colab_install'],
    url='https://github.com/nhdchicken/nhd-colab',
    zip_safe=False,
    entry_points=dict(
        console_scripts=[
            'colab=colab_install:cli_main',
        ],
    ),
)

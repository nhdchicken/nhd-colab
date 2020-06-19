#!/usr/bin/env python
"""The setup script.

"""
import sys
import os
from setuptools import setup, find_packages

__src_dir__ = 'src'
sys.path.insert(0, __src_dir__)

# ------------------
# Execution
# -----------------------------------------------------------------------------
# This calls the setup. It should not need to be configured.
# -----------------------------------------------------------------------------

setup(
    name='nhd-colab',
    author="Chicken Chicken",
    author_email='nhdchicken@gmail.com',
    version='1.0',
    description="notebook installer for nhd-colab notebooks ",
    install_requires=['click', 'pyyaml'],
    package_dir={'': __src_dir__},
    packages=find_packages(__src_dir__),
    url='https://github.com/nhdchicken/nhd-colab',
    zip_safe=False,
    entry_points=dict(
        console_scripts=[
            'nhdcolab=nhdcolab.colab_install:cli_main',
        ],
    ),
)

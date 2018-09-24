#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

def read(path, encoding='utf-8'):
    with io.open(path, encoding=encoding) as f:
        content = f.read()
    return content

def get_install_reqs(path):
    content = read(path)
    requirements = [req for req in content.split("\n")
                    if req != '' and not req.startswith('#')]
    return requirements

setup(
    name='pev-photons',
    version='0.1',
    description='The scripts used to produce the IceCube Gamma-Ray Analysis',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/zdgriffith/pev-photons',
    author='Zachary Griffith',
    author_email='griffitzd@gmail.com',
    packages=find_packages(),
    install_requires=get_install_reqs(os.path.join(here, 'requirements.txt')),
)

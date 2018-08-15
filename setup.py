#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def get_install_reqs(path):
    content = read(path)
    requirements = [req for req in content.split("\n")
                    if req != '' and not req.startswith('#')]
    return requirements

setup(
    name='pev-photons',
    version='0.1',
    description='The scripts used to produce the IceCube Gamma-Ray Analysis',
    long_description=open('README.txt').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/zdgriffith/pev-photons',
    author='Zachary Griffith'
    author_email='griffitzd@gmail.com',
    packages=find_packages(),
    install_requires=get_install_reqs(os.path.join(here, 'requirements.txt')),
)

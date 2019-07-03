#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import setuptools

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = []
setup_requirements = []
test_requirements = ['pytest']
extra_requirements = {}

setuptools.setup(
    name='building-detector',
    author='Cor Zuurmond',
    author_email='jczuurmond@protonmail.com',
    description='Detecting buildings',
    url='https://github.com/JCZuurmond/building-detector',
    license='Open source',
    packages=setuptools.find_packages('.', include=['open_data']),
    version='0.1.0',
    install_requires=requirements,
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    extras_require=extra_requirements,
)

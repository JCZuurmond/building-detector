#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import setuptools


with open('README.md') as readme_file:
    readme = readme_file.read()


requirements = [
    'requests>=2.22.0',
    'Pillow>=6.1.0',
    'owslib>=0.19.0',
]
setup_requirements = []
test_requirements = ['pytest']
extra_requirements = {
    'dev': ['jupyter>=1.0.0', 'matplotlib>=3.1.2', 'flake8>=3.7.9'],
}


setuptools.setup(
    name='building_detector',
    author='Cor Zuurmond',
    author_email='jczuurmond@protonmail.com',
    description='Detecting buildings',
    url='https://github.com/JCZuurmond/building-detector',
    license='Open source',
    packages=['building_detector'],
    version='0.1.0',
    install_requires=requirements,
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    extras_require=extra_requirements,
)

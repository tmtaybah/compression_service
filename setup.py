# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

setup(
    name='compression_service',
    version='0.1.0',
    description='A simple command-line compression service using the Huffman coding algorithm',
    long_description=readme,
    author='Tara Taybah',
    author_email='tara.taybah@gmail.com',
    packages=find_packages(exclude=('tests', 'docs'))
)

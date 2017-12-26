# -*- coding: utf-8 -*-
from distutils.core import setup
import setuptools

setup(
    name='metaweb',
    version='1.7.8',
    author='Mengchen LEE',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries',
    ],
    description='A web framework based on other web frameworks.',
    extras_require={
        'test': ['fixtures2'],
    },
    install_requires=[
        'decorated>=1.6.1',
        'inflection',
        'loggingd',
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    url='https://github.com/cooledcoffee/metaweb'
)

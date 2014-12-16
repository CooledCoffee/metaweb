# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='metaweb',
    version='1.4',
    author='Mengchen LEE',
    author_email='CooledCoffee@gmail.com',
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
        'decorated',
        'inflection',
        'loggingd',
    ],
    packages=[
        'metaweb',
        'metaweb.impls'
    ],
    url='https://github.com/CooledCoffee/metaweb/',
)

import os
import sys

from setuptools import setup, find_packages

VERSION = '0.2'

install_reqs = ['crcmod']

if sys.version_info < (3, 0):
    install_reqs.append('pyserial')
else:
    install_reqs.append('pyserial-py3k')

setup(name='plugwiselib', 
    version=VERSION,
    description='A library for communicating with Plugwise smartplugs',
    author='Sven Petai',
    author_email='hadara@bsd.ee',
    url='https://bitbucket.org/hadara/python-plugwise/wiki/Home',
    license='MIT',
    packages=find_packages(),
    py_modules=['plugwise'],
    install_requires=install_reqs,
    scripts=['plugwise_util'],
)


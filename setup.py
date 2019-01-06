import sys
import requests.certs

from setuptools import setup

APP = ['Keywords.py']
OPTIONS = {'iconfile':'img/icon.icns', 'packages': ['boto3'], "includes":[(requests.certs.where(),'cacert.pem')]}
setup(
    app = APP,
    options = {'py2app': OPTIONS},
    setup_requires = ['py2app', 'boto3', 'setuptools', 'pillow', 'pathlib', 'configparser'],
    data_files = [('', ['img']),('etc', ['config.ini'])], install_requires=['clarifai']
)
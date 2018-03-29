#!/usr/bin/env python
from os import path
from setuptools import setup, find_packages
from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

pfile = Project(chdir=True).parsed_pipfile
requirements = convert_deps_to_pip(pfile['packages'], r=False)
test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)


root_path = path.abspath(path.dirname(__file__))
with open(path.join(root_path, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Yatcobot',

    version='1.0.0',

    description='The best bot for searching twitter contests and automatically retweet them',

    long_description=long_description,  # Optional

    url='https://github.com/buluba89/Yatcobot',

    author='John Buluba',

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='twitter bot contest retweet',

    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'utils']),  # Required

    package_data={  # Optional
        'yatcobot': ['config_default.yaml'],
    },

    install_requires=requirements,

    entry_points={  # Optional
        'console_scripts': [
            'yatcobot=yatcobot.cli:main',
        ],
    },

    project_urls={
        'Source': 'https://github.com/buluba89/Yatcobot',
    },
)

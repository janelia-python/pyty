from setuptools import setup, find_packages
from codecs import open
from os import path
from version import get_git_version

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyty',

    version=get_git_version(),

    description='Python wrapper for TyTools collection of tools to manage Teensy boards',
    long_description=long_description,

    url='https://github.com/janelia-pypi/pyty',

    author='Peter Polidoro',
    author_email='peterpolidoro@gmail.com',

    license='BSD',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],

    keywords='',

    packages=find_packages('src',exclude=['contrib', 'docs', 'tests*']),
    package_dir={'':'src'},

    install_requires=['Click',
                      'sre_yield',
    ],

    entry_points={
        'console_scripts': [
            'fu=pyty:cli',
        ],
    },
)

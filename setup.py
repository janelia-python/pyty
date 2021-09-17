import os
import re
import sys
import sysconfig
import platform
import subprocess
import pathlib

from distutils.version import LooseVersion
from setuptools import setup, find_packages
from distutils.command.install_data import install_data

from codecs import open

here = pathlib.Path(__file__).resolve().parent

with open(here.joinpath('DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

class BuildTyToolsAndInstallData(install_data):
    """Custom handler to build TyTools and install data."""

    name = 'tytools'
    source_path_relative = pathlib.Path('src') / name
    debug = False

    def run(self):
        self.build_tytools()
        super().run()

    def build_tytools(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                'CMake must be installed to build the following: {0}'.format(self.name))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)',
                                         out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        cmake_args = ['-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''),
            self.distribution.get_version())
        build_path = pathlib.Path.cwd() / 'build'
        if not pathlib.Path.exists(build_path):
            pathlib.Path.mkdir(build_path)
        source_path = pathlib.Path.cwd() / self.source_path_relative
        subprocess.check_call(['cmake', source_path] + cmake_args,
                              cwd=build_path, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args,
                              cwd=build_path)
        print()  # Add an empty line for cleaner output

setup(
    name='pyty',

    use_scm_version = True,
    setup_requires=['setuptools_scm'],

    description='Tools for managing Teensy boards.',
    long_description=long_description,

    url='https://github.com/janelia-pypi/pyty',

    author='Peter Polidoro',
    author_email='peter@polidoro.io',

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

    zip_safe=True,

    install_requires=['Click',
                      'sre_yield',
    ],

    cmdclass={'install_data': BuildTyToolsAndInstallData},

    data_files=[('tytools', ['build/tycmd',
                             'build/tycommander',
                             'build/tyupdater',
                             'build/enumerate_devices',
                             'build/monitor_devices',
                             'build/serial_dumper',
                             'build/test_libty',
                             ])],

    entry_points={
        'console_scripts': [
            'pytycmd=pyty.cli:pytycmd',
        ],
    },
)

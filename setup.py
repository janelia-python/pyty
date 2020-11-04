import os
import re
import sys
import sysconfig
import platform
import subprocess
import pathlib

from distutils.version import LooseVersion
from setuptools import setup, find_packages
import distutils.cmd

from version import get_git_version
from codecs import open

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

def get_virtualenv_path():
    """Used to work out path to install compiled binaries to."""
    if hasattr(sys, 'real_prefix'):
        return sys.prefix

    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        return sys.prefix

    if 'conda' in sys.prefix:
        return sys.prefix

    return None

class BuildTyToolsCommand(distutils.cmd.Command):
    """A custom command to compile TyTools."""

    description = 'compile TyTools'
    user_options = [
        # The format is (long option, short option, description).
    ]
    name = 'tytools'
    sourcedir = pathlib.Path('src') / name

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.debug = False
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        self.build_and_install()

    def build_and_install(self):
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

        self.build()
        self.install()

    def build(self):
        # extdir = os.path.abspath(
        #     os.path.dirname(self.get_ext_fullpath(ext.name)))
        # cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
        #               '-DPYTHON_EXECUTABLE=' + sys.executable]
        cmake_args = ['-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            # cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(
            #     cfg.upper(),
            #     extdir)]
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
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(['cmake', self.sourcedir] + cmake_args,
                              cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args,
                              cwd=self.build_temp)
        print()  # Add an empty line for cleaner output

    def install(self):
        pass
    #     build_temp = pathlib.Path(self.build_temp).resolve()
    #     dest_path = pathlib.Path(self.get_ext_fullpath(ext.name)).resolve()
    #     source_path = build_temp / self.get_ext_filename(ext.name)
    #     print('source_path = {0}'.format(source_path))
    #     dest_directory = dest_path.parents[0]
    #     print('dest_directory = {0}'.format(dest_directory))
    #     # bin_path = os.path.join(get_virtualenv_path(),'bin')
    #     # cmake_args += ['-DCMAKE_INSTALL_PREFIX=' + bin_path]
    #     # print('cmake_args = {0}'.format(cmake_args))

setup(
    name='pyty',

    use_scm_version = {
        "root": "..",
        "relative_to": __file__,
        "local_scheme": "node-and-timestamp"
    },
    setup_requires=['setuptools_scm'],

    # version=get_git_version(),

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

    cmdclass={'build_tytools': BuildTyToolsCommand},
    zip_safe=True,

    install_requires=['Click',
                      'sre_yield',
    ],

    # data_files=[('bin', ['bm/b1.gif', 'bm/b2.gif'])],

    # scripts=['bin/funniest-joke'],

    # entry_points={
    #     'console_scripts': [
    #         'fu=pyty:cli',
    #     ],
    # },
)

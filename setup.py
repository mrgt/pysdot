#!/usr/bin/env python3

from setuptools import setup, find_packages, Extension
from setuptools.dist import Distribution
import sys

extra_compile_args = []
if 'darwin' in sys.platform:
    extra_compile_args.append("-std=c++14")
    extra_compile_args.append("-stdlib=libc++")
    extra_compile_args.append("-Wno-missing-braces")
    extra_compile_args.append("-march=native")
    extra_compile_args.append("-ffast-math")
if 'linux' in sys.platform:
    extra_compile_args.append("-march=native")
    extra_compile_args.append("-ffast-math")

ext_modules = []
for TF in ["double"]:
    for dim in [2, 3]:
        name = 'pybind_sdot_{}d_{}'.format(dim, TF)
        ext_modules.append(Extension(
            name,
            sources=['pysdot/cpp/pybind_sdot.cpp'],
            include_dirs=['ext'],
            define_macros=[
                ('PD_MODULE_NAME', name),
                ('PD_TYPE', TF),
                ('PD_DIM', str(dim))
            ],
            language='c++',
            extra_compile_args=extra_compile_args,
        ))

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False

setup(
    name='pysdot',
    version='0.1',
    packages=find_packages(exclude=[
        'hugo', 'ext', 'build', 'dist',
        'examples', 'results', 'tests'
    ]),
    include_package_data=True,
    distclass=BinaryDistribution,
    ext_modules=ext_modules,
    install_requires=[
        "numpy",
    ],
)

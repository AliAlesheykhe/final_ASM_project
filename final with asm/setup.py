# setup.py
from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules = cythonize("/media/aa/84423E3E423E34F0/University/computer structure and language/final project/final with asm/ballmotion.pyx"),
    include_dirs=[numpy.get_include()]
)

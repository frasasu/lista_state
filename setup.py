#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup.py pour la compilation Cython
"""

from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
import os
import sys

# Forcer l'encodage UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Trouver tous les fichiers à compiler
extensions = []

# Fichiers core
core_dir = 'app/core'
if os.path.exists(core_dir):
    for root, dirs, files in os.walk(core_dir):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                full_path = os.path.join(root, file)
                module_name = full_path.replace(os.sep, '.').replace('.py', '')
                extensions.append(Extension(module_name, [full_path]))

# Fichiers principaux (assets.py et main.py)
app_dir = 'app'
for file in ['assets.py', 'main.py']:
    full_path = os.path.join(app_dir, file)
    if os.path.exists(full_path):
        module_name = file.replace('.py', '')
        extensions.append(Extension(module_name, [full_path]))

# Options de compilation
compiler_directives = {
    'language_level': 3,
    'boundscheck': False,
    'wraparound': False,
    'cdivision': True,
    'embedsignature': False,
    'binding': False,
}

# Compilation
setup(
    name="ListaStateCore",
    ext_modules=cythonize(
        extensions,
        compiler_directives=compiler_directives,
        force=True,
        verbose=True,
        build_dir='build_temp',
        compile_time_env={'CYTHON_LIMITS': '1000000'},
    ),
)
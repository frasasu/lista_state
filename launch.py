#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher for Lista State - loads compiled main.pyd
"""

import sys
from pathlib import Path

# Ajouter le dossier core_compiled au PYTHONPATH
core_compiled_dir = Path(__file__).parent / "app" / "core_compiled"
sys.path.insert(0, str(core_compiled_dir))

# Importer main.pyd (compilé)
from main import run

if __name__ == "__main__":
    run()
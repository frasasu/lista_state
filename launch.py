#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher for Lista State - loads compiled main.pyd
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier core_compiled au PYTHONPATH
core_compiled_dir = Path(__file__).parent / "app" / "core_compiled"
if core_compiled_dir.exists():
    sys.path.insert(0, str(core_compiled_dir))

# Ajouter le dossier app au PYTHONPATH
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Ajouter le dossier courant pour les dépendances
sys.path.insert(0, str(Path(__file__).parent))

# Importer main.pyd (compilé)
try:
    from main import run
except ImportError as e:
    print(f"Error importing main: {e}")
    print(f"Python path: {sys.path}")
    
    # Essayer de trouver le fichier main.pyd
    main_pyd = core_compiled_dir / "main.pyd"
    if main_pyd.exists():
        print(f"main.pyd found at: {main_pyd}")
    else:
        print(f"main.pyd not found at: {main_pyd}")
    
    sys.exit(1)

if __name__ == "__main__":
    run()
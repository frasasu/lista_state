#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Point d'entree principal pour Lista State
Ce fichier reste non compile pour demarrer l'application
"""

import sys
import os
from pathlib import Path

# Forcer l'encodage UTF-8 pour la sortie
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Ajouter le dossier app au PYTHONPATH
APP_DIR = Path(__file__).parent / "app"
sys.path.insert(0, str(APP_DIR))

# Variable pour suivre si nous utilisons les modules compiles
using_compiled = False

# Importer le loader qui va charger les modules compiles
try:
    from loader import load_compiled_modules
    load_compiled_modules()
    using_compiled = True
    print("[INFO] Using compiled modules")
except ImportError as e:
    print(f"[WARN] Loader not found: {e}")
    print("[INFO] Falling back to source files")

# Importer main (compiled or source)
ListaStateApp = None
run = None

# Essayer d'importer depuis les modules compiles
if using_compiled:
    try:
        from main import ListaStateApp, run
        print("[INFO] Main module loaded from compiled .pyd")
    except ImportError as e:
        print(f"[WARN] Could not import compiled main: {e}")
        using_compiled = False

# Fallback vers les sources
if not using_compiled:
    try:
        # Ajouter le chemin pour les sources
        sys.path.insert(0, str(Path(__file__).parent))
        from app.main import ListaStateApp, run
        print("[INFO] Main module loaded from source files")
    except ImportError as e:
        print(f"[ERROR] Could not import main module: {e}")
        sys.exit(1)

# Lancer l'application
if __name__ == "__main__":
    try:
        print("[INFO] Starting Lista State application...")
        run()
    except KeyboardInterrupt:
        print("\n[INFO] Application stopped by user")
    except Exception as e:
        print(f"[ERROR] Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
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

# Ajouter le dossier core_compiled au PYTHONPATH pour les modules compiles
CORE_COMPILED_DIR = APP_DIR / "core_compiled"
if CORE_COMPILED_DIR.exists():
    sys.path.insert(0, str(CORE_COMPILED_DIR))
    print(f"[INFO] Compiled modules path: {CORE_COMPILED_DIR}")

# Variable pour suivre si nous utilisons les modules compiles
using_compiled = False
ListaStateApp = None
run = None

# Essayer d'importer depuis les modules compiles (main.pyd est dans core_compiled)
try:
    # main.pyd est dans core_compiled, donc on l'importe directement
    from app.main import ListaStateApp, run
    using_compiled = True
    print("[INFO] Main module loaded from compiled .pyd")
except ImportError as e:
    print(f"[WARN] Could not import compiled main: {e}")
    using_compiled = False

# Fallback vers les sources si la compilation a echoue
if not using_compiled:
    try:
        # Supprimer le chemin core_compiled pour eviter les conflits
        if str(CORE_COMPILED_DIR) in sys.path:
            sys.path.remove(str(CORE_COMPILED_DIR))
        
        # Importer depuis les sources
        from app.main import ListaStateApp, run
        print("[INFO] Main module loaded from source files")
    except ImportError as e:
        print(f"[ERROR] Could not import main module: {e}")
        print("[ERROR] Make sure the application structure is correct")
        print(f"[ERROR] Python path: {sys.path}")
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
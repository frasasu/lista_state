#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher avec vérification de l'environnement
"""

import sys
import os
import platform
from pathlib import Path

def check_environment():
    """Vérifie l'environnement d'exécution"""
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Executable: {sys.executable}")
    
    # Vérifier les fichiers requis
    base_dir = Path(__file__).parent
    required_files = [
        base_dir / "app" / "core_compiled" / "main.pyd",
        base_dir / "app" / "core_compiled" / "assets.pyd",
    ]
    
    for file in required_files:
        if file.exists():
            size = file.stat().st_size / 1024
            print(f"  OK: {file.name} ({size:.1f} KB)")
        else:
            print(f"  MISSING: {file}")
            return False
    
    return True

def setup_paths():
    """Configure les chemins d'import"""
    base_dir = Path(__file__).parent
    app_dir = base_dir / "app"
    core_dir = app_dir / "core_compiled"
    
    # Ajouter les chemins
    if str(core_dir) not in sys.path:
        sys.path.insert(0, str(core_dir))
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    
    return core_dir

def main():
    """Point d'entrée principal"""
    print("=" * 50)
    print("Lista State Launcher")
    print("=" * 50)
    
    # Vérifier l'environnement
    if not check_environment():
        print("Erreur: Environnement invalide")
        sys.exit(1)
    
    try:
        # Configurer les chemins
        core_dir = setup_paths()
        print(f"Répertoire core: {core_dir}")
        
        # Importer et exécuter
        from main import run
        run()
        
    except ImportError as e:
        print(f"Erreur d'import: {e}")
        print(f"PYTHONPATH: {sys.path}")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
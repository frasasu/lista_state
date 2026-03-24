#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de compilation Cython pour proteger le code Python
Compile tous les fichiers .py en .pyd, y compris assets.py et main.py
Version corrigee sans emojis pour compatibilite GitHub Actions
"""

import os
import sys
import shutil
from pathlib import Path
from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

# Forcer l'encodage UTF-8 pour la sortie
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
PROJECT_ROOT = Path(__file__).parent
APP_DIR = PROJECT_ROOT / "app"
CORE_DIR = APP_DIR / "core"
OUTPUT_DIR = APP_DIR / "core_compiled"
BUILD_DIR = PROJECT_ROOT / "build_temp"

def find_all_py_files():
    """Trouve tous les fichiers .py a compiler"""
    py_files = []
    
    # Fichiers dans core/
    if CORE_DIR.exists():
        for py_file in CORE_DIR.glob('**/*.py'):
            if py_file.name == '__init__.py':
                continue
            py_files.append(py_file)
    
    # Fichiers principaux dans app/ (assets.py et main.py)
    for py_file in APP_DIR.glob('*.py'):
        if py_file.name not in ['__init__.py', 'loader.py']:
            py_files.append(py_file)
    
    return py_files

def clean_compiled_files():
    """Nettoie les anciens fichiers compiles"""
    patterns = ['*.pyd', '*.so', '*.c', '*.cpp', '*.html']
    for pattern in patterns:
        for f in PROJECT_ROOT.glob(f'**/{pattern}'):
            if 'build' not in str(f) and 'core_compiled' not in str(f):
                try:
                    f.unlink()
                    print(f"   [DEL] {f}")
                except:
                    pass

def create_loader_script():
    """Cree un script de chargement pour les fichiers compiles"""
    loader_content = '''# -*- coding: utf-8 -*-
"""
Script de chargement automatique pour les modules compiles
Genere automatiquement par compile.py
"""

import sys
import os
from pathlib import Path

def load_compiled_modules():
    """Charge les modules compiles"""
    # Ajouter le dossier core_compiled au PYTHONPATH
    app_dir = Path(__file__).parent
    core_compiled_dir = app_dir / "core_compiled"
    
    if core_compiled_dir.exists():
        sys.path.insert(0, str(core_compiled_dir))
    
    # Ajouter app_dir pour les modules principaux
    sys.path.insert(0, str(app_dir))

# Charger automatiquement au demarrage
load_compiled_modules()
'''
    
    loader_file = APP_DIR / "loader.py"
    with open(loader_file, 'w', encoding='utf-8') as f:
        f.write(loader_content)
    print(f"[OK] Script loader.py cree")
    return loader_file

def main():
    print("=" * 60)
    print("COMPILATION CYTHON - Lista State")
    print("=" * 60)
    
    # Nettoyer les anciens fichiers
    print("\n[INFO] Nettoyage des anciens fichiers compiles...")
    clean_compiled_files()
    
    # Créer le dossier de sortie
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"[INFO] Dossier de sortie: {OUTPUT_DIR}")
    
    # Trouver tous les fichiers à compiler
    py_files = find_all_py_files()
    
    if not py_files:
        print("[ERROR] Aucun fichier trouve a compiler!")
        return False
    
    print(f"\n[INFO] Fichiers a compiler: {len(py_files)}")
    for f in py_files:
        print(f"   - {f.relative_to(PROJECT_ROOT)}")
    
    try:
        # Créer les extensions
        extensions = []
        for py_file in py_files:
            # Déterminer le nom du module
            rel_path = py_file.relative_to(APP_DIR)
            module_name = str(rel_path.with_suffix('')).replace(os.sep, '.')
            
            extensions.append(
                Extension(
                    module_name,
                    [str(py_file)],
                )
            )
        
        # Compilation
        print("\n[INFO] Compilation en cours...")
        compiled_ext = cythonize(
            extensions,
            compiler_directives={
                'language_level': 3,
                'boundscheck': False,
                'wraparound': False,
                'cdivision': True,
                'embedsignature': False,
                'binding': False,
            },
            force=True,
            verbose=False,
            build_dir=str(BUILD_DIR),
        )
        
        # Compiler avec setuptools
        setup(
            name="ListaStateCore",
            ext_modules=compiled_ext,
            script_args=['build_ext', '--inplace'],
        )
        
        print("\n[OK] Compilation Cython terminee!")
        
        # Déplacer les fichiers compilés vers core_compiled
        print("\n[INFO] Deplacement des fichiers compiles...")
        compiled_count = 0
        
        # Chercher les fichiers compilés
        for pattern in ['*.pyd', '*.so']:
            for compiled_file in APP_DIR.glob(f'**/{pattern}'):
                # Éviter de déplacer depuis core_compiled
                if 'core_compiled' not in str(compiled_file):
                    # Déterminer le sous-dossier relatif
                    rel_path = compiled_file.relative_to(APP_DIR)
                    target_dir = OUTPUT_DIR / rel_path.parent
                    target_dir.mkdir(parents=True, exist_ok=True)
                    
                    target_file = target_dir / compiled_file.name
                    shutil.move(str(compiled_file), str(target_file))
                    print(f"   [MOV] {compiled_file.name} -> {target_file}")
                    compiled_count += 1
        
        # Créer le script loader.py
        loader_file = create_loader_script()
        
        # Supprimer les fichiers sources originaux
        print("\n[INFO] Suppression des fichiers sources originaux...")
        for py_file in py_files:
            try:
                if py_file.exists():
                    py_file.unlink()
                    print(f"   [DEL] {py_file}")
            except Exception as e:
                print(f"   [WARN] Impossible de supprimer {py_file}: {e}")
        
        # Nettoyer les fichiers .c temporaires
        for c_file in PROJECT_ROOT.glob('**/*.c'):
            if 'core_compiled' not in str(c_file) and 'build' not in str(c_file):
                try:
                    c_file.unlink()
                except:
                    pass
        
        # Nettoyer le dossier de build
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
            print("[INFO] Nettoyage du dossier de build")
        
        print(f"\n[OK] Compilation reussie! {compiled_count} fichiers compiles dans {OUTPUT_DIR}")
        
        # Afficher les fichiers générés
        print("\n[INFO] Fichiers compiles generes:")
        for f in OUTPUT_DIR.glob('**/*.pyd'):
            print(f"   - {f}")
        for f in OUTPUT_DIR.glob('**/*.so'):
            print(f"   - {f}")
        
        print(f"\n[INFO] Script loader: {loader_file}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la compilation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
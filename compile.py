#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de compilation Cython pour proteger le code Python
Compile TOUS les fichiers .py en .pyd (y compris assets.py)
Version corrigee avec creation des dossiers avant copie
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

# Liste des fichiers à exclure
EXCLUDE_FILES = ['__init__.py', 'loader.py']

def find_all_py_files():
    """Trouve tous les fichiers .py a compiler"""
    py_files = []
    
    # Fichiers dans core/
    if CORE_DIR.exists():
        for py_file in CORE_DIR.glob('**/*.py'):
            if py_file.name == '__init__.py':
                continue
            py_files.append(py_file)
    
    # Fichiers principaux dans app/
    for py_file in APP_DIR.glob('*.py'):
        if py_file.name not in EXCLUDE_FILES:
            py_files.append(py_file)
    
    return py_files

def clean_compiled_files():
    """Nettoie les anciens fichiers compiles"""
    patterns = ['*.pyd', '*.so', '*.c', '*.cpp', '*.html']
    for pattern in patterns:
        for f in PROJECT_ROOT.glob(f'**/{pattern}'):
            if 'build' not in str(f) and 'core_compiled' not in str(f):
                if 'app/ui' in str(f):
                    continue
                try:
                    if f.exists():
                        f.unlink()
                        print(f"   [DEL] {f}")
                except:
                    pass

def create_loader_script():
    """Cree un script de chargement"""
    loader_content = '''# -*- coding: utf-8 -*-
"""
Script de chargement automatique pour les modules compiles
"""

import sys
from pathlib import Path

def load_compiled_modules():
    app_dir = Path(__file__).parent
    core_compiled_dir = app_dir / "core_compiled"
    
    if core_compiled_dir.exists():
        if str(core_compiled_dir) not in sys.path:
            sys.path.insert(0, str(core_compiled_dir))
    
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

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
    
    print(f"\n[INFO] Fichiers exclus: {EXCLUDE_FILES}")
    
    # Nettoyer les anciens fichiers
    print("\n[INFO] Nettoyage des anciens fichiers compiles...")
    clean_compiled_files()
    
    # Creer les dossiers necessaires
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Dossier de sortie cree: {OUTPUT_DIR}")
    
    # Creer le dossier core dans OUTPUT_DIR pour les fichiers core
    core_output_dir = OUTPUT_DIR / "core"
    core_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Dossier core cree: {core_output_dir}")
    
    # Creer le dossier core dans le repertoire courant pour la copie
    current_core_dir = PROJECT_ROOT / "core"
    current_core_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Dossier core courant cree: {current_core_dir}")
    
    # Trouver tous les fichiers à compiler
    py_files = find_all_py_files()
    
    if not py_files:
        print("[ERROR] Aucun fichier trouve a compiler!")
        return False
    
    print(f"\n[INFO] Fichiers a compiler: {len(py_files)}")
    for f in py_files:
        print(f"   - {f.relative_to(PROJECT_ROOT)}")
    
    try:
        # Creer les extensions
        extensions = []
        for py_file in py_files:
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
        
        # Deplacer les fichiers compiles vers core_compiled
        print("\n[INFO] Deplacement des fichiers compiles...")
        compiled_count = 0
        
        # Chercher les fichiers compiles dans build/lib
        build_lib_dir = PROJECT_ROOT / "build" / "lib.win-amd64-cpython-311"
        if build_lib_dir.exists():
            print(f"[INFO] Recherche dans {build_lib_dir}")
            for compiled_file in build_lib_dir.glob('**/*.pyd'):
                # Determiner la destination
                rel_path = compiled_file.relative_to(build_lib_dir)
                if 'core' in str(rel_path):
                    target_dir = core_output_dir
                else:
                    target_dir = OUTPUT_DIR
                
                target_dir.mkdir(parents=True, exist_ok=True)
                target_file = target_dir / compiled_file.name
                
                # Supprimer si existe
                if target_file.exists():
                    target_file.unlink()
                
                shutil.move(str(compiled_file), str(target_file))
                print(f"   [MOV] {compiled_file.name} -> {target_file}")
                compiled_count += 1
        
        # Chercher aussi dans le repertoire courant (pour les fichiers dans core/)
        for pattern in ['*.pyd', '*.so']:
            for compiled_file in PROJECT_ROOT.glob(f'**/{pattern}'):
                if 'core_compiled' not in str(compiled_file) and 'build' not in str(compiled_file):
                    # Determiner la destination
                    if compiled_file.parent.name == 'core' or 'core' in str(compiled_file.parent):
                        target_dir = core_output_dir
                    else:
                        target_dir = OUTPUT_DIR
                    
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target_file = target_dir / compiled_file.name
                    
                    # Supprimer si existe
                    if target_file.exists():
                        target_file.unlink()
                    
                    shutil.move(str(compiled_file), str(target_file))
                    print(f"   [MOV] {compiled_file.name} -> {target_file}")
                    compiled_count += 1
        
        # Creer le script loader.py
        loader_file = create_loader_script()
        
        # Supprimer les fichiers sources originaux
        print("\n[INFO] Suppression des fichiers sources originaux...")
        for py_file in py_files:
            try:
                if py_file.exists() and py_file.name not in EXCLUDE_FILES:
                    py_file.unlink()
                    print(f"   [DEL] {py_file}")
            except Exception as e:
                print(f"   [WARN] Impossible de supprimer {py_file}: {e}")
        
        # Nettoyer les fichiers temporaires
        for c_file in PROJECT_ROOT.glob('**/*.c'):
            if 'core_compiled' not in str(c_file) and 'build' not in str(c_file):
                try:
                    if c_file.exists():
                        c_file.unlink()
                except:
                    pass
        
        # Nettoyer le dossier de build
        if BUILD_DIR.exists():
            shutil.rmtree(BUILD_DIR)
            print("[INFO] Nettoyage du dossier build_temp")
        
        # Nettoyer le dossier build de setuptools
        build_dir = PROJECT_ROOT / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print("[INFO] Nettoyage du dossier build")
        
        # Nettoyer le dossier core courant
        if current_core_dir.exists():
            try:
                shutil.rmtree(current_core_dir)
                print("[INFO] Nettoyage du dossier core courant")
            except:
                pass
        
        print(f"\n[OK] Compilation reussie! {compiled_count} fichiers compiles dans {OUTPUT_DIR}")
        
        # Afficher les fichiers generes
        print("\n[INFO] Fichiers compiles generes:")
        for f in OUTPUT_DIR.glob('**/*.pyd'):
            size = f.stat().st_size / 1024
            rel_path = f.relative_to(OUTPUT_DIR)
            print(f"   - {rel_path} ({size:.2f} KB)")
        
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
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer le fichier assets.py à partir du fichier HTML
Version corrigée sans emojis pour compatibilité GitHub Actions
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Forcer l'encodage UTF-8 pour la sortie
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PROJECT_ROOT = Path(__file__).parent
APP_DIR = PROJECT_ROOT / "app"
HTML_FILE = PROJECT_ROOT / "app" / "ui" / "index.html"
ASSETS_FILE = APP_DIR / "assets.py"

def read_html_file():
    """Lit le contenu du fichier HTML"""
    if not HTML_FILE.exists():
        print(f"[ERROR] Fichier HTML non trouve: {HTML_FILE}")
        return None
    
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def generate_assets_py(html_content):
    """Génère le fichier assets.py avec le contenu HTML"""
    
    template = '''# -*- coding: utf-8 -*-
"""
Fichier genere automatiquement par build_assets.py
Ne pas modifier manuellement
Genere le: {timestamp}
"""

INDEX_HTML = \"\"\"{html_content}\"\"\"
'''
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return template.format(
        timestamp=timestamp,
        html_content=html_content
    )

def main():
    print("=" * 60)
    print("GENERATION DE ASSETS.PY")
    print("=" * 60)
    
    # Lire le fichier HTML
    print(f"\n[INFO] Lecture du fichier HTML: {HTML_FILE}")
    html_content = read_html_file()
    
    if html_content is None:
        return False
    
    # Générer le fichier assets.py
    print(f"\n[INFO] Generation de {ASSETS_FILE}")
    assets_content = generate_assets_py(html_content)
    
    # Écrire le fichier
    with open(ASSETS_FILE, 'w', encoding='utf-8') as f:
        f.write(assets_content)
    
    # Vérifier la taille
    size = ASSETS_FILE.stat().st_size / 1024
    print(f"[SUCCESS] Fichier genere avec succes! ({size:.2f} KB)")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
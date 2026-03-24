#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script pour intégrer tous les assets dans un fichier Python
Version sans esbuild - uniquement Python
Adapté pour la structure: app/ui/
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).parent
APP_DIR = PROJECT_ROOT / "app"
UI_DIR = APP_DIR / "ui"
SCRIPTS_DIR = UI_DIR / "scripts"
STYLES_DIR = UI_DIR / "styles"
OUTPUT_DIR = APP_DIR / "assets_compiled"
OUTPUT_FILE = OUTPUT_DIR / "assets.py"

# Ordre de chargement des modules JS (dépendances d'abord)
JS_LOAD_ORDER = [
    "DataCore.js",          # Pas de dépendances
    "SettingsManager.js",   # Dépend de DataCore
    "analysis.js",          # Dépend de DataCore
    "index.js"              # Dépend de DataCore et SettingsManager
]

def ensure_directories():
    """Crée les dossiers nécessaires"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Dossier de sortie: {OUTPUT_DIR}")

def minify_css(css_content):
    """Minifie le CSS"""
    # Supprimer les commentaires
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    # Supprimer les espaces inutiles
    css_content = re.sub(r'\s+', ' ', css_content)
    # Supprimer les espaces autour des caractères spéciaux
    css_content = re.sub(r'\s*([{}:;,])\s*', r'\1', css_content)
    # Supprimer les espaces avant et après
    css_content = css_content.strip()
    return css_content

def minify_html(html_content):
    """Minifie le HTML"""
    # Supprimer les commentaires
    html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    # Supprimer les espaces multiples
    html_content = re.sub(r'\s+', ' ', html_content)
    # Supprimer les espaces entre balises
    html_content = re.sub(r'>\s+<', '><', html_content)
    return html_content.strip()

def parse_js_file(file_path):
    """
    Parse un fichier JS pour extraire les imports/exports
    Retourne: (code_transformé, exports_liste, imports_dict)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire les noms de fichiers importés
    imports = {}
    
    # Imports nommés: import { X, Y } from "./file.js"
    named_imports = re.findall(
        r'import\s+{([^}]+)}\s+from\s+["\']\./([^"\']+)["\']',
        content
    )
    for names, module in named_imports:
        imports[module] = [n.strip() for n in names.split(',')]
        # Supprimer la ligne d'import
        content = re.sub(
            rf'import\s+{{{re.escape(names)}}}\s+from\s+["\']\./{re.escape(module)}["\']\s*;?',
            '',
            content
        )
    
    # Import default: import X from "./file.js"
    default_imports = re.findall(
        r'import\s+(\w+)\s+from\s+["\']\./([^"\']+)["\']',
        content
    )
    for var, module in default_imports:
        imports[module] = ['default']
        # Supprimer la ligne d'import
        content = re.sub(
            rf'import\s+{re.escape(var)}\s+from\s+["\']\./{re.escape(module)}["\']\s*;?',
            '',
            content
        )
    
    # Exports nommés: export { X, Y }
    named_exports = re.findall(r'export\s+{([^}]+)}', content)
    exports = []
    for ex in named_exports:
        exports.extend([e.strip() for e in ex.split(',')])
        # Supprimer la ligne d'export
        content = re.sub(r'export\s+{[^}]+}\s*;?', '', content)
    
    # Export default: export default X
    default_export = re.search(r'export\s+default\s+(\w+)', content)
    if default_export:
        exports.append('default')
        # Remplacer export default par une variable
        var_name = default_export.group(1)
        content = re.sub(
            rf'export\s+default\s+{re.escape(var_name)}',
            f'const __default_export = {var_name}',
            content
        )
    
    # Export const/function/class: export const X = ...
    export_declarations = re.findall(
        r'export\s+(const|let|var|function|class)\s+(\w+)',
        content
    )
    for decl_type, name in export_declarations:
        exports.append(name)
        # Remplacer "export" par rien
        content = re.sub(
            rf'export\s+{re.escape(decl_type)}\s+{re.escape(name)}',
            f'{decl_type} {name}',
            content
        )
    
    return content, imports, exports

def bundle_js():
    """
    Bundle tous les modules JS manuellement
    Gère les imports/exports ES modules
    """
    print("\n📦 Bundling JavaScript modules...")
    
    if not SCRIPTS_DIR.exists():
        print(f"   ❌ Dossier scripts non trouvé: {SCRIPTS_DIR}")
        return None
    
    js_files = list(SCRIPTS_DIR.glob("*.js"))
    if not js_files:
        print("   ⚠️  Aucun fichier JS trouvé")
        return ""
    
    print(f"   Fichiers JS trouvés: {[f.name for f in js_files]}")
    
    # Lire et parser tous les fichiers
    modules = {}
    for js_file in JS_LOAD_ORDER:
        file_path = SCRIPTS_DIR / js_file
        if file_path.exists():
            content, imports, exports = parse_js_file(file_path)
            modules[js_file] = {
                'content': content,
                'imports': imports,
                'exports': exports,
                'name': js_file.replace('.js', '')
            }
            print(f"      - {js_file}: exports {exports}")
    
    # Construire le bundle
    bundle_parts = []
    
    # En-tête du bundle
    bundle_parts.append("""
// ============================================================
// BUNDLE GÉNÉRÉ AUTOMATIQUEMENT - Lista State
// Ne pas modifier manuellement
// ============================================================

(function() {
    // Système de modules
    const __modules__ = {};
    const __exports__ = {};
    
    function __require__(name) {
        if (__modules__[name]) {
            return __modules__[name];
        }
        return null;
    }
    
    function __export__(name, value) {
        __exports__[name] = value;
        return value;
    }
    
    // Rendre disponible globalement
    window.__modules__ = __modules__;
    window.__exports__ = __exports__;
    window.__require__ = __require__;
""")
    
    # Définir chaque module dans une IIFE
    for js_file in JS_LOAD_ORDER:
        if js_file in modules:
            mod = modules[js_file]
            module_name = mod['name']
            
            bundle_parts.append(f"""
    // ========== Module: {js_file} ==========
    (function() {{
        const exports = {{}};
        const module = {{ exports: exports }};
        
        // Imports
        {chr(10).join([f'        const {imp} = __require__("{imp}_module")?.{imp};' for imps in mod['imports'].values() for imp in imps if imp != 'default'])}
        {chr(10).join([f'        const default_import = __require__("{mod}")?.default;' for mod in mod['imports'].keys()])}
        
        // Code du module
        {mod['content']}
        
        // Exports
        {chr(10).join([f'        __export__("{exp}", {exp});' for exp in mod['exports']])}
        {chr(10).join([f'        __export__("{exp}", {exp});' for exp in mod['exports']])}
        
        // Enregistrer le module
        __modules__["{module_name}"] = __exports__;
    }})();
""")
    
    # Ajouter le point d'entrée (index.js)
    if "index.js" in modules:
        bundle_parts.append(f"""
    // ========== Point d'entrée: index.js ==========
    (function() {{
        // Récupérer les exports des dépendances
        const DataCore = __require__("DataCore")?.DataCore;
        const settingsManager = __require__("SettingsManager")?.default || __require__("SettingsManager")?.settingsManager;
        const analysisManager = __require__("analysis")?.analysisManager;
        
        // Code d'initialisation
        {modules['index.js']['content']}
    }})();
""")
    
    # Fermeture de l'IIFE
    bundle_parts.append("""
})();
""")
    
    result = '\n'.join(bundle_parts)
    print(f"   ✅ JS bundlé: {len(result):,} caractères")
    return result

def build_css():
    """Combine et minifie tous les fichiers CSS"""
    print("\n🎨 Building CSS...")
    
    if not STYLES_DIR.exists():
        print(f"   ❌ Dossier styles non trouvé: {STYLES_DIR}")
        return ""
    
    css_files = list(STYLES_DIR.glob("*.css"))
    if not css_files:
        print("   ⚠️  Aucun fichier CSS trouvé")
        return ""
    
    print(f"   Fichiers CSS trouvés: {[f.name for f in css_files]}")
    
    combined_css = []
    for css_file in sorted(css_files):
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
            combined_css.append(f"/* {css_file.name} */\n{content}")
    
    minified_css = minify_css('\n'.join(combined_css))
    print(f"   ✅ CSS combiné: {len(minified_css):,} caractères")
    return minified_css

def build_html(js_content, css_content):
    """Intègre JS et CSS dans le HTML"""
    print("\n📄 Building HTML...")
    
    html_file = UI_DIR / "index.html"
    if not html_file.exists():
        print(f"   ❌ Fichier HTML non trouvé: {html_file}")
        return ""
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"   Fichier HTML: {html_file.name}")
    
    # Supprimer les balises link CSS (styles/)
    html_content = re.sub(
        r'<link[^>]*href=["\']styles/[^"\']*\.css["\'][^>]*>',
        '',
        html_content,
        flags=re.IGNORECASE
    )
    
    # Supprimer les balises script externes (scripts/)
    html_content = re.sub(
        r'<script[^>]*src=["\']scripts/[^"\']*\.js["\'][^>]*>.*?</script>',
        '',
        html_content,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    # Insérer le CSS inline
    if css_content:
        # Chercher une balise style existante
        style_match = re.search(r'<style[^>]*>.*?</style>', html_content, re.DOTALL)
        if style_match:
            html_content = re.sub(
                r'<style[^>]*>.*?</style>',
                f'<style>\n{css_content}\n</style>',
                html_content,
                flags=re.DOTALL
            )
        else:
            # Insérer avant </head>
            html_content = html_content.replace(
                '</head>',
                f'<style>\n{css_content}\n</style>\n</head>'
            )
    
    # Insérer le JS inline
    if js_content:
        # Insérer avant </body>
        html_content = html_content.replace(
            '</body>',
            f'<script>\n{js_content}\n</script>\n</body>'
        )
    
    # Minifier le HTML
    html_content = minify_html(html_content)
    
    print(f"   ✅ HTML construit: {len(html_content):,} caractères")
    return html_content

def generate_assets_py(html_content):
    """Génère le fichier assets.py"""
    print("\n📝 Generating assets.py...")
    
    # Échapper les triples quotes
    html_escaped = html_content.replace('"""', '\\"\\"\\"')
    
    content = f'''# -*- coding: utf-8 -*-
"""
Fichier généré automatiquement par build_assets.py
Ne pas modifier manuellement
Généré le: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

INDEX_HTML = """{html_escaped}"""
'''
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"   ✅ Fichier généré: {OUTPUT_FILE}")
    print(f"   📊 Taille: {len(html_content):,} caractères")

def verify_assets():
    """Vérifie que tous les assets sont présents"""
    print("\n🔍 Vérification des assets...")
    
    missing = []
    
    # Vérifier scripts JS
    if not SCRIPTS_DIR.exists():
        missing.append(f"Dossier scripts manquant: {SCRIPTS_DIR}")
    else:
        js_files = list(SCRIPTS_DIR.glob("*.js"))
        if not js_files:
            missing.append("Aucun fichier JS trouvé")
        else:
            print(f"   ✅ {len(js_files)} fichiers JS:")
            for f in js_files:
                print(f"      - {f.name}")
    
    # Vérifier styles CSS
    if not STYLES_DIR.exists():
        missing.append(f"Dossier styles manquant: {STYLES_DIR}")
    else:
        css_files = list(STYLES_DIR.glob("*.css"))
        if not css_files:
            missing.append("Aucun fichier CSS trouvé")
        else:
            print(f"   ✅ {len(css_files)} fichiers CSS:")
            for f in css_files:
                print(f"      - {f.name}")
    
    # Vérifier HTML
    html_file = UI_DIR / "index.html"
    if not html_file.exists():
        missing.append(f"Fichier HTML manquant: {html_file}")
    else:
        print(f"   ✅ index.html trouvé")
    
    if missing:
        print("   ⚠️  Problèmes détectés:")
        for m in missing:
            print(f"      - {m}")
        return False
    
    return True

def clean():
    """Nettoie les fichiers temporaires"""
    print("\n🧹 Nettoyage...")
    
    temp_files = [
        SCRIPTS_DIR / "bundle.js",
        SCRIPTS_DIR / "bundle.min.js",
    ]
    
    for f in temp_files:
        if f.exists():
            f.unlink()
            print(f"   Supprimé: {f}")
    
    print("   ✅ Nettoyage terminé")

def main():
    """Script principal"""
    print("=" * 60)
    print("🚀 BUILD ASSETS - Lista State (sans esbuild)")
    print("=" * 60)
    print(f"📁 Projet: {PROJECT_ROOT}")
    print(f"📁 UI: {UI_DIR}")
    print(f"📁 Sortie: {OUTPUT_DIR}")
    
    # Créer les dossiers nécessaires
    ensure_directories()
    
    # Vérifier les assets
    if not verify_assets():
        print("\n❌ Build annulé - assets manquants")
        return False
    
    # 1. Bundler JavaScript (version Python pure)
    js_content = bundle_js()
    if js_content is None:
        return False
    
    # 2. Builder CSS
    css_content = build_css()
    
    # 3. Builder HTML avec JS et CSS inline
    html_content = build_html(js_content, css_content)
    
    if not html_content:
        print("❌ Build échoué - contenu HTML vide")
        return False
    
    # 4. Générer assets.py
    generate_assets_py(html_content)
    
    # 5. Nettoyer
    clean()
    
    print("\n" + "=" * 60)
    print("✅ BUILD ASSETS TERMINÉ AVEC SUCCÈS!")
    print(f"📁 Fichier généré: {OUTPUT_FILE}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
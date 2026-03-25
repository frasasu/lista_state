#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Point d'entrée principal de Lista State
"""

import sys
import os
import json
from pathlib import Path
import webview

# Importer les modules compilés
try:
    from core_compiled.executors import Executor
    from core_compiled.lexers import Lexer
    from core_compiled.parsers import Parser
    from core_compiled.simple_dataframe import SimpleDataFrame
    from core_compiled.stats_calculator import StatsCalculator
    from core_compiled.table_importer import TableImporter
    from core_compiled.vis import Visualizer
except ImportError:
    # Fallback pour le développement
    from core.executors import Executor
    from core.lexers import Lexer
    from core.parsers import Parser
    from core.simple_dataframe import SimpleDataFrame
    from core.stats_calculator import StatsCalculator
    from core.table_importer import TableImporter
    from core.vis import Visualizer

from core_compiled.assets import INDEX_HTML

class ListaStateApp:
    def __init__(self):
        self.session_name = ""
        self.datas = {
            "tables": {},
            "analysis": {},
            "settings": {
                "general": {
                    "defaultSession": "new",
                    "autoSave": True,
                    "autoSaveInterval": 30
                },
                "editor": {
                    "theme": "dracula",
                    "fontSize": 14
                },
                "appearance": {
                    "theme": "dark",
                    "accentColor": "#4299e1"
                }
            }
        }
        self.current_table = None
        
    def evaluate_dsl(self, code, datas):
        """Évalue le code DSL"""
        try:
            executor = Executor()
            result = executor.execute(code, datas)
            return result
        except Exception as e:
            return {
                "success": False,
                "messages": [{"type": "error", "content": str(e)}]
            }
    
    def save_as(self, data):
        """Sauvegarde la session"""
        try:
            # Créer le dossier sessions si nécessaire
            sessions_dir = Path("sessions")
            sessions_dir.mkdir(exist_ok=True)
            
            # Sauvegarder le fichier
            filepath = sessions_dir / f"{self.session_name}.lst"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return {"success": True, "message": "Session sauvegardée"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_file_dialog(self):
        """Ouvre une boîte de dialogue pour charger une session"""
        try:
            from tkinter import filedialog, Tk
            root = Tk()
            root.withdraw()
            filepath = filedialog.askopenfilename(
                title="Ouvrir une session",
                filetypes=[("Lista State Session", "*.lst"), ("Tous les fichiers", "*.*")]
            )
            root.destroy()
            
            if filepath:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                name = Path(filepath).stem
                return {"success": True, "name": name, "data": data}
            return {"success": False, "cancelled": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def import_table(self):
        """Importe une table depuis un fichier CSV/Excel"""
        try:
            from tkinter import filedialog, Tk
            root = Tk()
            root.withdraw()
            filepath = filedialog.askopenfilename(
                title="Importer une table",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("Excel files", "*.xlsx *.xls"),
                    ("Tous les fichiers", "*.*")
                ]
            )
            root.destroy()
            
            if filepath:
                importer = TableImporter()
                table_name = Path(filepath).stem
                table_data = importer.import_file(filepath)
                return [table_name, table_data]
            return None
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def choose_folder(self):
        """Ouvre une boîte de dialogue pour choisir un dossier"""
        try:
            from tkinter import filedialog, Tk
            root = Tk()
            root.withdraw()
            folder = filedialog.askdirectory(title="Choisir un dossier")
            root.destroy()
            return folder if folder else None
        except Exception:
            return None
    
    def initial_data(self):
        """Données initiales"""
        return {
            "success": True,
            "name": "Nouvelle session",
            "data": self.datas
        }

def run():
    """Lance l'application"""
    app = ListaStateApp()
    
    # Créer la fenêtre principale
    window = webview.create_window(
        title="Lista State",
        html=INDEX_HTML,
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600),
        js_api=app,
    )
    
    webview.start(debug=False)

if __name__ == "__main__":
    run()
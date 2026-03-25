#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Point d'entrée principal de Lista State
"""
import webview
import os
import sys
import zipfile
from pathlib import PurePosixPath
import json
from typing import Dict, Any, Optional, Tuple
from core_compiled.executors import evaluate_dsl_code
import traceback
from datetime import datetime
from core_compiled.table_importer import TableImporter
from core_compiled.assets import INDEX_HTML


def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))


class ManagerApp:
    def __init__(self):
        self.current_file = sys.argv[1] if len(sys.argv) > 1 else None
        self.base_path = get_base_path()
        self.importer = TableImporter(webview)

    def get_ui_path(self):
        """Retourne le chemin vers l'interface HTML"""
        return os.path.join(self.base_path, 'ui', 'index.html')

    def initial_data(self):
        """Charge les données d'une session existante"""
        if not self.current_file or not os.path.exists(self.current_file):
            return {"error": "Aucun fichier charge."}
        if not zipfile.is_zipfile(self.current_file):
            return {"error": "Erreur du fichier .lst"}

        try:
            data = {"tables": {}, "analysis": {}, "settings": {}}
            with zipfile.ZipFile(self.current_file, "r") as z:
                for info in z.infolist():
                    if info.is_dir():
                        continue

                    path = PurePosixPath(info.filename)
                    folder = path.parts[0]
                    filename = path.name
                    filename = filename.split(".")[0]

                    with z.open(info) as f:
                        content = f.read()
                        if folder == "tables":
                            data["tables"][filename] = json.loads(content)
                        elif folder == "analysis":
                            data["analysis"][filename] = content.decode("utf-8")
                        elif folder == "settings" and filename == "config":
                            data["settings"] = json.loads(content)

            return {
                "success": True,
                "name": os.path.basename(self.current_file),
                "data": data
            }
        except Exception as e:
            return {"error": str(e)}

    def save_as(self, data: Dict[str, Any]):
        """Sauvegarde une session"""
        if not self.current_file:
            return {"error": "Aucune session"}

        try:
            with zipfile.ZipFile(self.current_file, "w", compression=zipfile.ZIP_DEFLATED) as z:

                for name_table, content_table in data.get("tables", {}).items():
                    z.writestr(f"tables/{name_table}.json", json.dumps(content_table))


                for name_analysis, content_analysis in data.get("analysis", {}).items():
                    z.writestr(f"analysis/{name_analysis}.txt", content_analysis)


                if "settings" in data:
                    z.writestr("settings/config.json", json.dumps(data["settings"]))

            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    def ChoosePathNewSession(self, name: str) -> Dict[str, Any]:
        """
        Crée une nouvelle session.
        Retourne un dictionnaire pour une meilleure compatibilité avec JavaScript.
        """
        try:
            if not name or not name.strip():
                return {"error": "Nom de session invalide"}

            window = webview.active_window()
            if not window:
                return {"error": "Fenêtre non disponible"}


            file_path = window.create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=f"{name.strip()}.lst"
            )

            if not file_path:
                return {"cancelled": True}

            if isinstance(file_path, Tuple):
                file_path = file_path[0]

            if not file_path.endswith(".lst"):
                file_path += ".lst"

            self.current_file = file_path

            datas = {
                "tables": {
                    "demo": {
                        "first_variable": [1, 2, 3, 4, 5],
                        "second_variable": [10, 20, 30, 40, 50]
                    }
                },
                "analysis": {
                    "demo": "# Analyse demo\nLoad demo as data\nAnalyze data [total = COUNT(*)] with show=true"
                },
                "settings": {
                    "general": {
                        "defaultSession": "new",
                        "autoSave": True,
                        "autoSaveInterval": 30
                    }
                }
            }


            save_result = self.save_as(datas)
            if "error" in save_result:
                return {"error": save_result["error"]}


            return {
                "success": True,
                "name": os.path.basename(file_path),
                "data": datas
            }

        except Exception as e:
            print(f"Erreur dans ChoosePathNewSession: {e}")
            traceback.print_exc()
            return {"error": str(e)}

    def open_file_dialog(self):
        """Ouvre une session existante"""
        try:
            window = webview.active_window()
            file_types = ('Lista State files (*.lst)',)
            file_paths = window.create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=file_types
            )

            if not file_paths:
                return {"cancelled": True}

            self.current_file = file_paths[0]
            result = self.initial_data()

            if "error" in result:
                return result

            return {
                "success": True,
                "name": result["name"],
                "data": result["data"]
            }

        except Exception as e:
            return {"error": str(e)}

    def import_table(self):
        """Importe un fichier CSV ou Excel"""
        try:
            return self.importer.import_table()
        except Exception as e:
            print(f"Erreur import_table: {e}")
            return {"error": str(e)}

    def evaluate_dsl(self, code: str, datas: dict) -> dict:
        """Évalue du code DSL et retourne les résultats"""
        try:
            result = evaluate_dsl_code(code, datas)
            return result
        except Exception as e:
            error_msg = f"Erreur lors de l'évaluation: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return {
                "success": False,
                "errors": [error_msg],
                "messages": [{
                    "type": "error",
                    "content": {
                        "message": error_msg,
                        "traceback": traceback.format_exc()
                    },
                    "line": 0,
                    "timestamp": datetime.now().isoformat()
                }],
                "datas": datas
            }



api = ManagerApp()

def run():
    window = webview.create_window(
    "Lista State - Statistical Data Analysis",
    html=INDEX_HTML,
    js_api=api,
    width=1200,
    height=1000,
    min_size=(1000, 800),
    resizable=True,
    fullscreen=False,
    confirm_close=True,
    text_select=True,
)


if __name__ == '__main__':
    run()

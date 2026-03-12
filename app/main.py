import webview
import os
import sys
import zipfile
import pandas as pd
from pathlib import PurePosixPath
import json
from typing import Dict,Any
from core.executors import evaluate_dsl_code
import json
import traceback
from datetime import datetime

def get_base_path():
    if getattr(sys, 'frozen', False):

        return sys._MEIPASS
    else:

        return os.path.dirname(os.path.abspath(__file__))


class ManagerApp:
    def __init__(self):
        self.current_file = sys.argv[1] if len(sys.argv) > 1 else None
        self.base_path = get_base_path()

    def get_ui_path(self):
        """Retourne le chemin vers l'interface HTML"""
        return os.path.join(self.base_path, 'ui', 'index.html')

    def initial_data(self):
        if not self.current_file or not os.path.exists(self.current_file):
            return {"error":"Aucun fichier charge."}
        if not zipfile.is_zipfile(self.current_file):
            return {"error":"Erreur du fichier .lst"}

        try:
            data = {"tables":{},"analysis":{},"settings": {}}
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
                            data["tables"][filename]=json.loads(content)
                         elif folder == "analysis":
                            data["analysis"][filename]=content.decode("utf-8")
                         elif folder == "settings" and filename == "config":
                            data["settings"] = json.loads(content)


            return os.path.basename(self.current_file), data
        except Exception as e:
            return {"error":str(e)}


    def save_as(self, data:Dict[str,Any]):
        if not self.current_file:
            return {"error":"Aucune session"}

        if self.current_file:

            try:
                with zipfile.ZipFile(self.current_file, "w", compression=zipfile.ZIP_DEFLATED) as z:

                    for name_table, content_table in data["tables"].items():
                        z.writestr(f"tables/{name_table}.json", json.dumps(content_table))

                    for name_analysis, content_analysis in data["analysis"].items():
                        z.writestr(f"analysis/{name_analysis}.txt", content_analysis)

                    if "settings" in data:
                        z.writestr("settings/config.json", json.dumps(data["settings"]))
                return {"success":True}
            except Exception as e:
                return {"error":str(e)}




    def ChoosePathNewSession(self, name):
        if name:
            window = webview.active_window()
            file_path = window.create_file_dialog(webview.SAVE_DIALOG, save_filename=f"{name}.lst")
            if not file_path or not file_path.endswith(".lst"):
                return None,None
            self.current_file = file_path
            datas = {
                "tables":{
                    "demo":{
                        "first_variable":[1,1,1],
                        "second_variable":[1,1,1]
                    }
                },
                "analysis":{
                    "demo":"#Analysis"
                }
            }
            result =self.save_as(datas)
            return os.path.basename(self.current_file), datas
        return None,None

    def open_file_dialog(self):
        window = webview.active_window()
        file_types = ('Lista State files (*.lst)', )
        file_paths = window.create_file_dialog(
        webview.OPEN_DIALOG,
        allow_multiple=False,
        file_types=file_types
       )
        if file_paths:
            self.current_file = file_paths[0]
            return os.path.basename(self.current_file), self.initial_data()[1]
        return None,

    def import_table(self):
        window = webview.active_window()
        file_types=('Fichier csv(*.csv)','Fichier xlsx(*.xlsx)','Fichier xls(*.xls)')
        file_paths = window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types
        )

        if file_paths:
            file_table = file_paths[0]

            if file_table.endswith(".csv"):
                df = pd.read_csv(file_table)
            elif file_table.endswith('.xlsx') or file_table.endswith('.xls'):
                df = pd.read_excel(file_table, sheet_name=0)

            resultat = df.to_dict(orient='list')
            file_table = os.path.basename(file_table)

            return file_table.split(".")[0], resultat

    def evaluate_dsl(self, code: str, datas: dict) -> dict:
        """
        Évalue du code DSL et retourne les résultats.
        Appelée depuis JavaScript via pywebview.

        Args:
            code: Code DSL à exécuter
            datas: Données actuelles au format {"tables": {...}, "analysis": {...}}

        Returns:
            Dict avec les résultats et messages
        """
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

window = webview.create_window(
    "Lista State - Statistical Data Analysis",
    api.get_ui_path(),
    js_api=api,
    width=1200,
    height=1000,
    min_size=(1000, 800),
    resizable=True,
    fullscreen=False,
    confirm_close=True,
    text_select=True,
)

webview.start()

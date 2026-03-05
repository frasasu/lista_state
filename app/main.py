import webview
import os
import pickle
import sys
import zipfile
from pathlib import PurePosixPath
import json
from typing import Dict,Any
from core.data import DataManager

dataView = DataManager()

class ManagerApp:
    def __init__(self):
        self.current_file = sys.argv[1] if len(sys.argv) > 1 else None

    def initial_data(self):
        if not self.current_file or not os.path.exists(self.current_file):
            return {"error":"Aucun fichier charge."}
        if not zipfile.is_zipfile(self.current_file):
            return {"error":"Erreur du fichier .lst"}

        try:
            data = {"tables":{},"analysis":{}}
            with zipfile.ZipFile(self.current_file, "r") as z:
                for info in z.infolist():

                    if info.is_dir():
                        continue

                    path = PurePosixPath(info.filename)
                    folder = path.parts[0]

                    filename = path.name

                    with z.open(info) as f:
                         content = f.read()
                         if folder == "tables":
                            data["tables"][filename]=json.loads(content)
                         elif folder == "analysis":
                            data["analysis"][filename]=content.decode("utf-8")

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
                        z.writestr(f"tables/{name_table}", json.dumps(content_table))

                    for name_analysis, content_analysis in data["analysis"].items():
                        z.writestr(f"analysis/{name_analysis}", content_analysis)
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
                    "demo.json":{
                        "first variable":[1,1,1],
                        "second variable":[1,1,1]
                    }
                },
                "analysis":{}
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
        return None,None


api = ManagerApp()

webview.create_window(
    "Lista State",
    "ui/index.html",
    js_api=api,
    width=1200,
    height=1000,
    min_size=(1000, 800)
)

webview.start()

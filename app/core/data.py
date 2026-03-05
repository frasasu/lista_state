import json
from typing import List, Tuple, Any, Dict

class DataManager:
    def __init__(self):
        self.name_session = "New session"
        self.tables = [{
            "type": "table",
            "name": "First table",
            "columns": ["First variable", "second variable", "third variable"],
            "rows": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        }]

    def create_new_session(self, name):
        if name:
            self.tables = []
            self.name_session = name
            self.tables.append({
                "type": "table",
                "name": "New table",
                "columns": ["First variable" for i in range(15)],
                "rows": [[0 for i in range(15)] for i in range(50)]
            })

    def upload_session(self, name, tables):
        if name:
            self.tables = []
            self.name_session = name
            for table in tables:
                if table.get("type", "") == "table":
                    if "name" in table and "columns" in table and "rows" in table:
                        if table["rows"] and len(table["columns"]) == len(table["rows"][0]):
                            self.tables.append(table)

    def write_data(self):
        return {
            "type": "Data_global",
            "name": self.name_session,
            "tables": self.tables
        }

    def list_tables(self):
        all_names = []
        for table in self.tables:
            if table.get("type", "") == "table":
                table_name = table.get("name", "")
                if table_name not in all_names:
                    all_names.append(table_name)
        return all_names

    def add_table(self, name, columns, rows=None):
        if name in self.list_tables():
            return f"The table - {name} already created!"

        if name and columns:
            if rows is not None and len(columns) == len(rows[0]):
                self.tables.append({
                    "type": "table",
                    "name": name,
                    "columns": columns,
                    "rows": rows
                })
            else:
                self.tables.append({
                    "type": "table",
                    "name": name,
                    "columns": columns,
                    "rows": [[0 for i in range(len(columns))] for i in range(5)]
                })
        return "Table added successfully"

data = {
    "colonne 1":[],
    "colonne 2":[]
}
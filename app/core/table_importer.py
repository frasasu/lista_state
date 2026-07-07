
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


class TableImporter:
    """Importateur de fichiers CSV et Excel, basé sur pandas."""

    def __init__(self, webview_instance):
        self.webview = webview_instance

    def import_table(self) -> Tuple[Optional[str], Optional[Dict[str, List]]]:
        """Importe un fichier CSV ou Excel via boîte de dialogue."""
        window = self.webview.active_window()
        file_types = ("Fichier csv(*.csv)", "Fichier xlsx(*.xlsx)", "Fichier xls(*.xls)")

        file_paths = window.create_file_dialog(
            self.webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types,
        )

        if not file_paths:
            return None, None

        file_path = file_paths[0]

        try:
            data = self._import_file(file_path)
            if data is None:
                return None, None

            filename = os.path.basename(file_path)
            name_without_ext = os.path.splitext(filename)[0]
            return name_without_ext, data

        except Exception as e:
            print(f"Erreur lors de l'import: {e}")
            return None, None

    # ------------------------------------------------------------------
    def _import_file(self, file_path: str) -> Optional[Dict[str, List]]:
        if file_path.endswith(".csv"):
            return self._import_csv(file_path)
        elif file_path.endswith((".xlsx", ".xls")):
            return self._import_excel(file_path)
        return None

    def _import_csv(self, file_path: str) -> Dict[str, List]:
        """Lit un CSV avec `pandas.read_csv` (sniffing automatique du séparateur)."""
        try:
            df = pd.read_csv(file_path, sep=None, engine="python", encoding="utf-8-sig")
        except Exception:
            # Repli robuste si le sniffing échoue (fichier atypique)
            df = pd.read_csv(file_path, encoding="utf-8-sig")
        return self._frame_to_dict(df)

    def _import_excel(self, file_path: str) -> Dict[str, List]:
        """Lit un classeur Excel avec `pandas.read_excel` (moteur openpyxl)."""
        df = pd.read_excel(file_path, engine="openpyxl" if file_path.endswith(".xlsx") else None)
        return self._frame_to_dict(df)

    # ------------------------------------------------------------------
    @staticmethod
    def _frame_to_dict(df: pd.DataFrame) -> Dict[str, List]:
        """Convertit un DataFrame pandas en {colonne: [valeurs]} avec None
        pour les valeurs manquantes (NaN/NaT), et types Python natifs."""
        df = df.convert_dtypes()  # types "pythoniques" cohérents (Int64, boolean, string...)
        result: Dict[str, List] = {}
        for col in df.columns:
            series = df[col].where(pd.notnull(df[col]), None)
            result[str(col)] = [v.item() if hasattr(v, "item") else v for v in series.tolist()]
        return result

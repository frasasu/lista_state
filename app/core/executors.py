
import pandas as pd
import numpy as np
import math
from typing import Dict, Any, List, Optional
from datetime import datetime
import traceback


def convert_to_json_serializable(obj):
    """Convertit les types numpy/pandas en types Python standards pour JSON"""
    if obj is None:
        return None
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif pd.isna(obj):
        return None
    return obj


class Evaluator:
    """
    Évaluateur d'AST pour le DSL Data Science.
    Utilise la structure de données: {"tables": {nom: {col: [valeurs]}}, "analysis": {}}
    """

    def __init__(self, initial_datas: Dict[str, Any] = None):
        self.datas = initial_datas or {"tables": {}, "analysis": {}}
        self.current_tables = {}
        self.analysis_results: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        self.output_messages: List[Dict[str, Any]] = []
        self.current_line = 0

        self._refresh_pandas_tables()

    def _convert_dict_to_json_serializable(self, d: Any) -> Any:
        """Convertit récursivement un dictionnaire pour le rendre JSON serializable"""
        if isinstance(d, dict):
            result = {}
            for key, value in d.items():
                if isinstance(value, dict):
                    result[key] = self._convert_dict_to_json_serializable(value)
                elif isinstance(value, list):
                    result[key] = [
                        self._convert_dict_to_json_serializable(item) if isinstance(item, dict)
                        else convert_to_json_serializable(item)
                        for item in value
                    ]
                else:
                    result[key] = convert_to_json_serializable(value)
            return result
        elif isinstance(d, list):
            return [
                self._convert_dict_to_json_serializable(item) if isinstance(item, dict)
                else convert_to_json_serializable(item)
                for item in d
            ]
        else:
            return convert_to_json_serializable(d)

    def _convert_to_numeric(self, series: pd.Series) -> pd.Series:
        """Convertit une série en numérique si possible"""
        if series.dtype == 'object':
            try:

                converted = pd.to_numeric(series, errors='coerce')

                if not converted.isna().all():
                    return converted
            except:
                pass
        return series

    def _convert_dataframe_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convertit automatiquement les colonnes d'un DataFrame en types numériques si possible"""
        new_df = df.copy()
        for col in new_df.columns:
            new_df[col] = self._convert_to_numeric(new_df[col])
        return new_df

    def _refresh_pandas_tables(self):
        """Convertit les tables du dictionnaire en DataFrames pandas avec conversion automatique"""
        for table_name, table_data in self.datas["tables"].items():
            df = pd.DataFrame(table_data)

            df = self._convert_dataframe_columns(df)
            self.current_tables[table_name] = df

    def _update_dict_tables(self):
        """Met à jour le dictionnaire original à partir des DataFrames"""
        for table_name, df in self.current_tables.items():

            dict_data = df.replace({np.nan: None}).to_dict(orient='list')

            dict_data = self._convert_dict_to_json_serializable(dict_data)
            self.datas["tables"][table_name] = dict_data

    def add_output(self, message_type: str, content: Any, line: int = 0):
        """Ajoute un message de sortie pour l'interface avec conversion JSON"""

        if isinstance(content, dict):
            content = self._convert_dict_to_json_serializable(content)
        elif isinstance(content, list):
            content = [self._convert_dict_to_json_serializable(item) if isinstance(item, dict) else convert_to_json_serializable(item) for item in content]
        else:
            content = convert_to_json_serializable(content)

        self.output_messages.append({
            "type": message_type,
            "content": content,
            "line": line or self.current_line,
            "timestamp": datetime.now().isoformat()
        })

    def evaluate(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Point d'entrée principal : évalue un programme complet
        Retourne la liste des messages de sortie
        """
        self.output_messages = []

        try:
            if ast.get("type") != "dsl_program":
                self.add_output("error", "AST invalide: type de programme manquant")
                return self.output_messages

            for command in ast.get("commands", []):
                self.current_line = command.get("line", 0)
                self.evaluate_command(command)

            self._update_dict_tables()

            converted_analysis = {}
            for key, value in self.analysis_results.items():
                converted_analysis[key] = self._convert_dict_to_json_serializable(value)
            self.datas["analysis"].update(converted_analysis)

        except Exception as e:
            self.add_output("error", {
                "message": str(e),
                "traceback": traceback.format_exc()
            })

        return self.output_messages

    def evaluate_command(self, command: Dict[str, Any]):
        """Évalue une commande individuelle"""
        cmd_type = command.get("type")

        if cmd_type == "load":
            self.evaluate_load(command)
        elif cmd_type == "transform":
            self.evaluate_transform(command)
        elif cmd_type == "analyze":
            self.evaluate_analyze(command)
        elif cmd_type == "if":
            self.evaluate_if(command)
        elif cmd_type == "for":
            self.evaluate_for(command)
        else:
            self.add_output("error", f"Type de commande inconnu: {cmd_type}", self.current_line)

    def evaluate_load(self, command: Dict[str, Any]):
        """Évalue une commande LOAD - charge une table depuis le dictionnaire"""
        props = command.get("properties", {})
        name = props.get("name")
        alias = props.get("alias", name)

        self.add_output("info", f"Chargement de la table '{name}' -> '{alias}'", self.current_line)

        if name in self.datas["tables"]:

            table_data = self.datas["tables"][name]
            df = pd.DataFrame(table_data)

            df = self._convert_dataframe_columns(df)
            self.current_tables[alias] = df

            preview = df.head(10).replace({np.nan: None}).to_dict(orient='records')
            preview = self._convert_dict_to_json_serializable(preview)

            self.add_output("table", {
                "name": alias,
                "source": name,
                "columns": list(df.columns),
                "types": [str(df[col].dtype) for col in df.columns],
                "preview": preview,
                "shape": list(df.shape),
                "row_count": len(df),
                "col_count": len(df.columns)
            })

            self.add_output("success", f"Table '{alias}' chargée avec succès ({len(df)} lignes)", self.current_line)
        else:
            self.add_output("error", f"Table '{name}' introuvable dans les données", self.current_line)

    def evaluate_transform(self, command: Dict[str, Any]):
        """Évalue une commande TRANSFORM"""
        props = command.get("properties", {})
        source_name = props.get("name")
        alias = props.get("alias", f"{source_name}_transformed")
        contents = command.get("contents", [])

        self.add_output("info", f"Transformation de '{source_name}' -> '{alias}'", self.current_line)

        if source_name not in self.current_tables:
            self.add_output("error", f"Table source '{source_name}' introuvable", self.current_line)
            return

        df = self.current_tables[source_name].copy()
        operations_applied = []

        for operation in contents:
            op_type = operation.get("type")
            operations_applied.append(op_type)

            if op_type == "select":
                df = self.apply_select(df, operation)
            elif op_type == "drop":
                df = self.apply_drop(df, operation)
            elif op_type == "filter":
                df = self.apply_filter(df, operation)
            elif op_type == "create_feature":
                df = self.apply_create_feature(df, operation)
            elif op_type == "group_by":
                df = self.apply_group_by(df, operation)
            elif op_type == "agg":
                df = self.apply_agg(df, operation)
            elif op_type == "join":
                df = self.apply_join(df, operation)
            elif op_type == "having":
                df = self.apply_having(df, operation)

        self.current_tables[alias] = df

        preview = df.head(10).replace({np.nan: None}).to_dict(orient='records')
        preview = self._convert_dict_to_json_serializable(preview)

        self.add_output("table", {
            "name": alias,
            "source": source_name,
            "columns": list(df.columns),
            "types": [str(df[col].dtype) for col in df.columns],
            "preview": preview,
            "shape": list(df.shape),
            "row_count": len(df),
            "col_count": len(df.columns),
            "operations": operations_applied
        })

        self.add_output("success", f"Table '{alias}' créée avec succès ({len(df)} lignes)", self.current_line)

    def apply_select(self, df: pd.DataFrame, operation: Dict[str, Any]) -> pd.DataFrame:
        """Applique une opération SELECT"""
        args = operation.get("args", [])
        selected_cols = []
        new_df = df.copy()

        for arg in args:
            if "name" in arg:
                col_name = arg["name"]
                alias = arg.get("alias", col_name)
                if col_name in new_df.columns:
                    if alias != col_name:
                        new_df = new_df.rename(columns={col_name: alias})
                        selected_cols.append(alias)
                    else:
                        selected_cols.append(col_name)
                else:
                    self.add_output("error", f"Colonne '{col_name}' introuvable", self.current_line)
            elif "expression" in arg:

                expr_result = self.evaluate_expression(arg["expression"], new_df)
                alias = arg.get("alias", f"col_{len(selected_cols)}")
                new_df[alias] = expr_result
                selected_cols.append(alias)

        if selected_cols:
            return new_df[selected_cols]
        return new_df

    def apply_drop(self, df: pd.DataFrame, operation: Dict[str, Any]) -> pd.DataFrame:
        """Applique une opération DROP"""
        args = operation.get("args", [])
        cols_to_drop = [col for col in args if col in df.columns]
        if cols_to_drop:
            return df.drop(columns=cols_to_drop)
        return df

    def apply_filter(self, df: pd.DataFrame, operation: Dict[str, Any]) -> pd.DataFrame:
        """Applique une opération FILTER"""
        condition = operation.get("condition")
        mask = self.evaluate_filter_condition(condition, df)
        return df[mask]

    def apply_create_feature(self, df: pd.DataFrame, operation: Dict[str, Any]) -> pd.DataFrame:
        """Applique une opération CREATE_FEATURE"""
        features = operation.get("features", [])
        new_df = df.copy()

        for feature in features:
            name = feature.get("name")
            expr = feature.get("expression")

            result = self.evaluate_expression(expr, new_df)
            new_df[name] = result

            self.add_output("info", f"Feature créée: {name}", self.current_line)

        return new_df

    def apply_group_by(self, df: pd.DataFrame, operation: Dict[str, Any]) -> pd.DataFrame:
        """Applique une opération GROUP BY (prépare pour AGG)"""
        columns = operation.get("columns", [])

        df.attrs['group_by_columns'] = columns
        return df

    def apply_agg(self, df: pd.DataFrame, operation: Dict[str, Any]) -> pd.DataFrame:
        """Applique une opération AGG (agrégation)"""
        aggregations = operation.get("aggregations", [])
        group_by_cols = df.attrs.get('group_by_columns', [])

        if not group_by_cols:

            result_dict = {}
            for agg_item in aggregations:
                name = agg_item.get("name")
                func_call = agg_item.get("function", {})
                func_name = func_call.get("name")
                args = func_call.get("arguments", [])

                if args and len(args) > 0:
                    col_name = self.extract_column_name(args[0])
                    if col_name and col_name in df.columns:
                        col_data = self._convert_to_numeric(df[col_name])
                        if func_name == "SUM":
                            result_dict[name] = col_data.sum(skipna=True)
                        elif func_name == "AVG" or func_name == "MEAN":
                            result_dict[name] = col_data.mean(skipna=True)
                        elif func_name == "COUNT":
                            result_dict[name] = len(df)
                        elif func_name == "MIN":
                            result_dict[name] = col_data.min(skipna=True)
                        elif func_name == "MAX":
                            result_dict[name] = col_data.max(skipna=True)

            return pd.DataFrame([result_dict])

        agg_dict = {}
        for agg_item in aggregations:
            name = agg_item.get("name")
            func_call = agg_item.get("function", {})
            func_name = func_call.get("name")
            args = func_call.get("arguments", [])

            if args and len(args) > 0:
                col_name = self.extract_column_name(args[0])
                if col_name and col_name in df.columns:
                    agg_dict[name] = pd.NamedAgg(column=col_name, aggfunc=func_name.lower())

        if agg_dict and group_by_cols:
            result = df.groupby(group_by_cols).agg(**agg_dict).reset_index()
            return result

        return df

    def apply_join(self, df: pd.DataFrame, operation: Dict[str, Any]) -> pd.DataFrame:
        """Applique une opération JOIN"""
        table_name = operation.get("table")
        on_condition = operation.get("on")
        join_type = operation.get("type", "inner")
        suffix = operation.get("suffix", "_right")

        if table_name not in self.current_tables:
            self.add_output("error", f"Table à joindre '{table_name}' introuvable", self.current_line)
            return df

        right_df = self.current_tables[table_name]

        left_col, right_col = self.parse_join_condition(on_condition)

        if left_col and right_col:
            try:
                result = pd.merge(
                    df, right_df,
                    left_on=left_col, right_on=right_col,
                    how=join_type,
                    suffixes=('', suffix)
                )
                return result
            except Exception as e:
                self.add_output("error", f"Erreur lors du JOIN: {str(e)}", self.current_line)

        return df

    def apply_having(self, df: pd.DataFrame, operation: Dict[str, Any]) -> pd.DataFrame:
        """Applique une opération HAVING (filtre après groupement)"""
        condition = operation.get("condition")
        mask = self.evaluate_filter_condition(condition, df)
        return df[mask]

    def evaluate_analyze(self, command: Dict[str, Any]):
        """Évalue une commande ANALYZE"""
        target = command.get("target")
        operations = command.get("operations", [])
        options = command.get("options", {})

        self.add_output("info", f"Analyse de '{target}'...", self.current_line)

        if target not in self.current_tables:
            self.add_output("error", f"Table cible '{target}' introuvable", self.current_line)
            return

        df = self.current_tables[target]
        results = {}

        for op in operations:
            if isinstance(op, dict) and "name" in op:
                op_name = op.get("name")
                op_args = op.get("arguments", [])
                variable = op.get("variable")

                result = self.evaluate_stat_function(op_name, op_args, df)

                if variable:
                    results[variable] = result
                    self.variables[variable] = result
                else:
                    results[op_name] = result

        analysis_name = f"analysis_{len(self.analysis_results)}"
        self.analysis_results[analysis_name] = results

        self.add_output("analysis", {
            "name": analysis_name,
            "target": target,
            "results": results,
            "options": options
        })

        self.add_output("success", f"Analyse '{analysis_name}' terminée", self.current_line)

    def evaluate_if(self, command: Dict[str, Any]):
        """Évalue une commande IF/ELIF/ELSE"""
        branches = command.get("branches", [])
        else_branch = command.get("else", [])

        for branch in branches:
            condition = branch.get("condition")
            body = branch.get("body", [])

            if self.evaluate_boolean_condition(condition):
                self.add_output("info", "Condition IF vraie, exécution du bloc", self.current_line)
                for cmd in body:
                    self.evaluate_command(cmd)
                return

        if else_branch:
            self.add_output("info", "Exécution du bloc ELSE", self.current_line)
            for cmd in else_branch:
                self.evaluate_command(cmd)

    def evaluate_for(self, command: Dict[str, Any]):
        """Évalue une commande FOR"""
        variable = command.get("variable")
        collection_name = command.get("collection")
        body = command.get("commands", [])

        if collection_name in self.current_tables:
            collection = self.current_tables[collection_name]

            for idx, (_, row) in enumerate(collection.iterrows()):

                row_dict = row.replace({np.nan: None}).to_dict()
                row_dict = self._convert_dict_to_json_serializable(row_dict)
                self.variables[variable] = row_dict
                self.add_output("info", f"Itération {idx+1}: {variable} = {self.variables[variable]}", self.current_line)

                for cmd in body:
                    self.evaluate_command(cmd)

        elif collection_name in self.variables:
            collection = self.variables[collection_name]
            if isinstance(collection, list):
                for idx, item in enumerate(collection):
                    self.variables[variable] = item
                    self.add_output("info", f"Itération {idx+1}: {variable} = {item}", self.current_line)
                    for cmd in body:
                        self.evaluate_command(cmd)

    def evaluate_filter_condition(self, condition: Any, df: pd.DataFrame) -> pd.Series:
        """Évalue une condition de filtre et retourne un masque booléen"""
        if condition is None:
            return pd.Series([True] * len(df))

        if isinstance(condition, dict):
            cond_type = condition.get("type")

            if cond_type == "binary_operation":
                left = self.evaluate_filter_condition(condition.get("left"), df)
                right = self.evaluate_filter_condition(condition.get("right"), df)
                operator = condition.get("operator")

                if operator in ["AND", "&&"]:
                    return left & right
                elif operator in ["OR", "||"]:
                    return left | right

            elif cond_type == "comparison":
                left = self.evaluate_expression(condition.get("left"), df)
                right = self.evaluate_expression(condition.get("right"), df)
                operator = condition.get("operator")

                if isinstance(left, pd.Series) and left.dtype == 'object':
                    left = self._convert_to_numeric(left)
                if isinstance(right, pd.Series) and right.dtype == 'object':
                    right = self._convert_to_numeric(right)

                try:
                    if operator == ">":
                        return left > right
                    elif operator == "<":
                        return left < right
                    elif operator == ">=":
                        return left >= right
                    elif operator == "<=":
                        return left <= right
                    elif operator == "==":
                        return left == right
                    elif operator == "!=":
                        return left != right
                except Exception as e:
                    self.add_output("error", f"Erreur de comparaison: {e}", self.current_line)
                    return pd.Series([False] * len(df))

            elif cond_type == "between":
                left = self.evaluate_expression(condition.get("left"), df)
                lower = self.evaluate_expression(condition.get("lower"), df)
                upper = self.evaluate_expression(condition.get("upper"), df)

                left = self._convert_to_numeric(left) if isinstance(left, pd.Series) else left
                lower = self._convert_to_numeric(lower) if isinstance(lower, pd.Series) else lower
                upper = self._convert_to_numeric(upper) if isinstance(upper, pd.Series) else upper

                return (left >= lower) & (left <= upper)

            elif cond_type == "in":
                left = self.evaluate_expression(condition.get("left"), df)
                values = condition.get("values", [])
                evaluated_values = [self.evaluate_expression(v, df) for v in values]

                if isinstance(left, pd.Series):
                    return left.isin(evaluated_values)
                else:
                    return pd.Series([left in evaluated_values] * len(df))

            elif cond_type == "not":
                expr = self.evaluate_filter_condition(condition.get("expression"), df)
                return ~expr

            elif cond_type == "column":
                col_name = condition.get("value")
                if col_name in df.columns:
                    col = df[col_name]
                    if col.dtype == 'object':
                        col = self._convert_to_numeric(col)
                    return col.astype(bool)

            elif cond_type == "boolean":
                return pd.Series([condition.get("value", True)] * len(df))

        return pd.Series([True] * len(df))

    def evaluate_expression(self, expr: Any, df: pd.DataFrame = None) -> Any:
        """Évalue une expression mathématique avec conversion automatique des types"""
        if expr is None:
            return None

        if isinstance(expr, dict):
            expr_type = expr.get("type")

            if expr_type == "column":
                col_name = expr.get("value")
                if df is not None and col_name in df.columns:
                    col = df[col_name]

                    return self._convert_to_numeric(col)
                return col_name

            elif expr_type == "number":
                return expr.get("value", 0)

            elif expr_type == "float":
                return float(expr.get("value", 0.0))

            elif expr_type == "string":
                val = expr.get("value", "")

                try:
                    if val.replace('.', '').replace('-', '').replace('e', '').replace('E', '').isdigit():
                        if '.' in val or 'e' in val or 'E' in val:
                            return float(val)
                        else:
                            return int(val)
                except:
                    pass
                return val

            elif expr_type == "boolean":
                return expr.get("value", False)

            elif expr_type == "null":
                return None

            elif expr_type == "binary_operation":
                left = self.evaluate_expression(expr.get("left"), df)
                right = self.evaluate_expression(expr.get("right"), df)
                operator = expr.get("operator")

                if isinstance(left, str) and not isinstance(right, str):
                    try:
                        left = float(left) if '.' in left else int(left)
                    except:
                        pass
                if isinstance(right, str) and not isinstance(left, str):
                    try:
                        right = float(right) if '.' in right else int(right)
                    except:
                        pass

                try:
                    if operator == "+":
                        return left + right
                    elif operator == "-":
                        return left - right
                    elif operator == "*":
                        return left * right
                    elif operator == "/":

                        if isinstance(right, pd.Series):
                            return left / right.replace(0, np.nan)
                        elif isinstance(left, pd.Series):
                            return left / right if right != 0 else float('inf')
                        else:
                            return left / right if right != 0 else float('inf')
                    elif operator == "**":
                        return left ** right
                    elif operator == "%":
                        return left % right
                except Exception as e:
                    self.add_output("error", f"Erreur dans l'expression: {e}", self.current_line)
                    return None

            elif expr_type == "function_call":
                return self.evaluate_function(expr, df)

            elif expr_type == "case":
                return self.evaluate_case(expr, df)

        return expr

    def evaluate_function(self, func_call: Dict[str, Any], df: pd.DataFrame = None) -> Any:
        """Évalue un appel de fonction avec conversion automatique"""
        name = func_call.get("name")
        args = func_call.get("arguments", [])
        over = func_call.get("over")

        evaluated_args = []
        for arg in args:
            val = self.evaluate_expression(arg, df)

            if isinstance(val, pd.Series) and val.dtype == 'object':
                val = self._convert_to_numeric(val)
            evaluated_args.append(val)

        if name == "SUM":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, pd.Series):
                    return col.sum(skipna=True)
                elif isinstance(col, (list, np.ndarray)):
                    return np.nansum(col) if hasattr(np, 'nansum') else sum(col)
                return col
        elif name == "AVG" or name == "MEAN":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, pd.Series):
                    return col.mean(skipna=True)
                elif isinstance(col, (list, np.ndarray)):
                    return np.nanmean(col) if hasattr(np, 'nanmean') else np.mean(col)
                return col
        elif name == "MEDIAN":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, pd.Series):
                    return col.median(skipna=True)
                elif isinstance(col, (list, np.ndarray)):
                    return np.nanmedian(col) if hasattr(np, 'nanmedian') else np.median(col)
                return col
        elif name == "COUNT":
            if len(evaluated_args) > 0:
                if isinstance(evaluated_args[0], dict) and evaluated_args[0].get("type") == "star":
                    return len(df) if df is not None else 0
                col = evaluated_args[0]
                if isinstance(col, pd.Series):
                    return col.count()
                elif isinstance(col, (list, np.ndarray)):
                    return len(col)
                return 1
        elif name == "MIN":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, pd.Series):
                    return col.min(skipna=True)
                elif isinstance(col, (list, np.ndarray)):
                    return np.nanmin(col) if hasattr(np, 'nanmin') else min(col)
                return col
        elif name == "MAX":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, pd.Series):
                    return col.max(skipna=True)
                elif isinstance(col, (list, np.ndarray)):
                    return np.nanmax(col) if hasattr(np, 'nanmax') else max(col)
                return col
        elif name == "STD":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, pd.Series):
                    return col.std(skipna=True)
                elif isinstance(col, (list, np.ndarray)):
                    return np.nanstd(col) if hasattr(np, 'nanstd') else np.std(col)
                return 0
        elif name == "VAR":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, pd.Series):
                    return col.var(skipna=True)
                elif isinstance(col, (list, np.ndarray)):
                    return np.nanvar(col) if hasattr(np, 'nanvar') else np.var(col)
                return 0
        elif name == "CORR":
            if len(evaluated_args) >= 2:
                col1 = evaluated_args[0]
                col2 = evaluated_args[1]
                if isinstance(col1, pd.Series) and isinstance(col2, pd.Series):
                    return col1.corr(col2)
                return np.corrcoef(col1, col2)[0, 1] if len(col1) > 1 and len(col2) > 1 else 0

        elif name == "LOG":
            if len(evaluated_args) > 0:
                val = evaluated_args[0]
                if isinstance(val, pd.Series):
                    return np.log(val.clip(lower=1e-10))
                elif hasattr(val, '__iter__') and not isinstance(val, str):
                    return np.log(np.maximum(val, 1e-10))
                return math.log(val) if val > 0 else float('-inf')
        elif name == "EXP":
            if len(evaluated_args) > 0:
                val = evaluated_args[0]
                if isinstance(val, pd.Series):
                    return np.exp(val)
                elif hasattr(val, '__iter__') and not isinstance(val, str):
                    return np.exp(val)
                return math.exp(val)
        elif name == "SQRT":
            if len(evaluated_args) > 0:
                val = evaluated_args[0]
                if isinstance(val, pd.Series):
                    return np.sqrt(val.clip(lower=0))
                elif hasattr(val, '__iter__') and not isinstance(val, str):
                    return np.sqrt(np.maximum(val, 0))
                return math.sqrt(val) if val >= 0 else float('nan')
        elif name == "ABS":
            if len(evaluated_args) > 0:
                val = evaluated_args[0]
                if isinstance(val, pd.Series):
                    return np.abs(val)
                elif hasattr(val, '__iter__') and not isinstance(val, str):
                    return np.abs(val)
                return abs(val)
        elif name == "ROUND":
            if len(evaluated_args) >= 1:
                val = evaluated_args[0]
                decimals = evaluated_args[1] if len(evaluated_args) > 1 else 0
                if isinstance(val, pd.Series):
                    return np.round(val, decimals)
                elif hasattr(val, '__iter__') and not isinstance(val, str):
                    return np.round(val, decimals)
                return round(val, decimals)

        if over:
            return self.evaluate_window_function(name, evaluated_args, over, df)

        return evaluated_args[0] if evaluated_args else None

    def evaluate_window_function(self, name: str, args: List, over: Dict, df: pd.DataFrame) -> Any:
        """Évalue une fonction de fenêtrage avec OVER (version simplifiée)"""
        if df is None or len(df) == 0:
            return None

        partition_by = over.get("partition_by", [])

        if name == "RANK":
            result = pd.Series(1, index=df.index)
            if partition_by and all(col in df.columns for col in partition_by):
                for _, group in df.groupby(partition_by):
                    result.loc[group.index] = range(1, len(group) + 1)
            return result
        elif name == "ROW_NUMBER":
            result = pd.Series(range(1, len(df) + 1), index=df.index)
            if partition_by and all(col in df.columns for col in partition_by):
                for _, group in df.groupby(partition_by):
                    result.loc[group.index] = range(1, len(group) + 1)
            return result

        return pd.Series([None] * len(df), index=df.index)

    def evaluate_case(self, case_expr: Dict[str, Any], df: pd.DataFrame = None) -> Any:
        """Évalue une expression CASE WHEN"""
        when_then = case_expr.get("when_then", [])
        else_val = case_expr.get("else")

        if df is not None:

            result = pd.Series([None] * len(df), index=df.index)

            for wt in when_then:
                condition = self.evaluate_filter_condition(wt.get("when"), df)
                then_val = self.evaluate_expression(wt.get("then"), df)

                if isinstance(then_val, pd.Series):
                    result[condition] = then_val[condition]
                else:
                    result[condition] = then_val

            if else_val is not None:
                else_result = self.evaluate_expression(else_val, df)
                if isinstance(else_result, pd.Series):
                    result[result.isna()] = else_result[result.isna()]
                else:
                    result[result.isna()] = else_result

            return result
        else:

            for wt in when_then:
                condition = self.evaluate_boolean_condition(wt.get("when"))
                if condition:
                    return self.evaluate_expression(wt.get("then"))
            return self.evaluate_expression(else_val) if else_val else None

    def evaluate_boolean_condition(self, condition: Any) -> bool:
        """Évalue une condition booléenne simple"""
        if condition is None:
            return True

        if isinstance(condition, dict):
            if condition.get("type") == "comparison":
                left_val = condition.get("left")
                right_val = condition.get("right")
                op = condition.get("operator")

                left = left_val.get("value") if isinstance(left_val, dict) else left_val
                right = right_val.get("value") if isinstance(right_val, dict) else right_val

                if isinstance(left, str):
                    try:
                        left = float(left) if '.' in left else int(left)
                    except:
                        pass
                if isinstance(right, str):
                    try:
                        right = float(right) if '.' in right else int(right)
                    except:
                        pass

                try:
                    if op == ">":
                        return left > right
                    elif op == "<":
                        return left < right
                    elif op == ">=":
                        return left >= right
                    elif op == "<=":
                        return left <= right
                    elif op == "==":
                        return left == right
                    elif op == "!=":
                        return left != right
                except:
                    return False

            elif condition.get("type") == "binary_operation":
                left = self.evaluate_boolean_condition(condition.get("left"))
                right = self.evaluate_boolean_condition(condition.get("right"))
                op = condition.get("operator")

                if op in ["AND", "&&"]:
                    return left and right
                elif op in ["OR", "||"]:
                    return left or right

            elif condition.get("type") == "not":
                return not self.evaluate_boolean_condition(condition.get("expression"))

            elif condition.get("type") == "boolean":
                return condition.get("value", False)

        return bool(condition)

    def evaluate_stat_function(self, name: str, args: List, df: pd.DataFrame) -> Any:
        """Évalue une fonction statistique pour ANALYZE avec conversion automatique"""
        evaluated_args = []
        for arg in args:
            val = self.evaluate_expression(arg, df)

            if isinstance(val, pd.Series) and val.dtype == 'object':
                val = self._convert_to_numeric(val)
            evaluated_args.append(val)

        if name == "COUNT":
            return len(df)
        elif name == "SUM":
            col = evaluated_args[0] if evaluated_args else None
            if col is not None:
                if isinstance(col, pd.Series):
                    return col.sum(skipna=True)
                elif isinstance(col, (list, np.ndarray)):
                    return np.nansum(col) if hasattr(np, 'nansum') else sum(col)
                return col
        elif name == "AVG" or name == "MEAN":
            col = evaluated_args[0] if evaluated_args else None
            if col is not None:
                if isinstance(col, pd.Series):
                    return col.mean(skipna=True)
                elif isinstance(col, (list, np.ndarray)):
                    return np.nanmean(col) if hasattr(np, 'nanmean') else np.mean(col)
                return col
        elif name == "MIN":
            col = evaluated_args[0] if evaluated_args else None
            if col is not None:
                if isinstance(col, pd.Series):
                    return col.min(skipna=True)
                elif isinstance(col, (list, np.ndarray)):
                    return np.nanmin(col) if hasattr(np, 'nanmin') else min(col)
                return col
        elif name == "MAX":
            col = evaluated_args[0] if evaluated_args else None
            if col is not None:
                if isinstance(col, pd.Series):
                    return col.max(skipna=True)
                elif isinstance(col, (list, np.ndarray)):
                    return np.nanmax(col) if hasattr(np, 'nanmax') else max(col)
                return col
        elif name == "CORR":
            if len(evaluated_args) >= 2:
                col1 = evaluated_args[0]
                col2 = evaluated_args[1]
                if isinstance(col1, pd.Series) and isinstance(col2, pd.Series):
                    return col1.corr(col2)
                return None

        return None

    def extract_column_name(self, arg: Any) -> Optional[str]:
        """Extrait le nom de colonne d'un argument"""
        if isinstance(arg, dict):
            if arg.get("type") == "column":
                return arg.get("value")
            elif arg.get("type") == "string":
                return arg.get("value")
        elif isinstance(arg, str):
            return arg
        return None

    def parse_join_condition(self, condition: Any) -> tuple:
        """Parse une condition ON pour JOIN"""
        if isinstance(condition, dict) and condition.get("type") == "comparison":
            left = condition.get("left")
            right = condition.get("right")

            left_col = self.extract_column_name(left)
            right_col = self.extract_column_name(right)

            return left_col, right_col

        if isinstance(condition, str):
            return condition, condition

        return None, None

    def get_table(self, name: str) -> Optional[Dict[str, List]]:
        """Retourne une table au format {colonne: [valeurs]}"""
        if name in self.datas["tables"]:
            return self.datas["tables"][name]
        return None

    def get_table_names(self) -> List[str]:
        """Retourne la liste des noms de tables disponibles"""
        return list(self.datas["tables"].keys())

    def get_analysis_names(self) -> List[str]:
        """Retourne la liste des noms d'analyses disponibles"""
        return list(self.datas["analysis"].keys())

    def export_results(self) -> Dict[str, Any]:
        """Exporte tous les résultats pour sauvegarde"""
        self._update_dict_tables()

        return self._convert_dict_to_json_serializable(self.datas)

    def clear(self):
        """Réinitialise l'évaluateur"""
        self.datas = {"tables": {}, "analysis": {}}
        self.current_tables.clear()
        self.analysis_results.clear()
        self.variables.clear()
        self.output_messages.clear()



def evaluate_dsl_code(code: str, datas: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fonction d'entrée pour évaluer du code DSL depuis l'interface webview.

    Args:
        code: Code DSL à exécuter
        datas: Dictionnaire des données au format {"tables": {...}, "analysis": {...}}

    Returns:
        Dictionnaire contenant les résultats et les messages
    """
    from core import Lexer
    from core import Parser

    try:

        lexer = Lexer(code)
        tokens = lexer.tokenise()

        parser = Parser(tokens)
        ast, errors = parser.parse()

        if errors:
            return {
                "success": False,
                "errors": errors,
                "messages": [{"type": "error", "content": e} for e in errors]
            }

        evaluator = Evaluator(datas)
        messages = evaluator.evaluate(ast)

        converted_messages = []
        for msg in messages:
            if isinstance(msg.get('content'), dict):
                msg['content'] = evaluator._convert_dict_to_json_serializable(msg['content'])
            converted_messages.append(msg)

        return {
            "success": True,
            "messages": converted_messages,
            "datas": evaluator.export_results()
        }

    except Exception as e:
        return {
            "success": False,
            "errors": [str(e)],
            "messages": [{
                "type": "error",
                "content": {
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
            }]
        }

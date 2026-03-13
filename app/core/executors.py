# executors.py
import math
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from .simple_dataframe import SimpleDataFrame, to_numeric, is_numeric, ensure_list_length


def convert_to_json_serializable(obj):
    """Convertit les types spéciaux en types Python standards pour JSON"""
    if obj is None:
        return None
    if isinstance(obj, (int, float, bool, str)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    if isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, SimpleDataFrame):
        return obj.to_dict(orient='list')
    return str(obj)


class Evaluator:
    """
    Évaluateur d'AST pour le DSL Data Science.
    Utilise SimpleDataFrame au lieu de pandas.
    """

    def __init__(self, initial_datas: Dict[str, Any] = None):
        self.datas = initial_datas or {"tables": {}, "analysis": {}}
        self.current_tables: Dict[str, SimpleDataFrame] = {}
        self.transformed_tables: Dict[str, SimpleDataFrame] = {}
        self.analysis_results: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        self.output_messages: List[Dict[str, Any]] = []
        self.current_line = 0

        self._refresh_tables()

    def _convert_dict_to_json_serializable(self, d: Any) -> Any:
        """Convertit récursivement pour JSON"""
        return convert_to_json_serializable(d)

    def _convert_to_numeric_series(self, values: List) -> List:
        """Convertit une liste en valeurs numériques si possible"""
        result = []
        for v in values:
            if isinstance(v, (int, float)):
                result.append(v)
            elif isinstance(v, str):
                try:
                    v_stripped = v.strip()
                    if v_stripped and (v_stripped.replace('.', '').replace('-', '').isdigit() or
                                     'e' in v_stripped.lower()):
                        if '.' in v_stripped or 'e' in v_stripped.lower():
                            result.append(float(v_stripped))
                        else:
                            result.append(int(v_stripped))
                    else:
                        result.append(v_stripped)
                except:
                    result.append(v)
            else:
                result.append(v)
        return result

    def _convert_dataframe_columns(self, df: SimpleDataFrame) -> SimpleDataFrame:
        """Convertit les colonnes en types numériques si possible"""
        new_df = df.copy()
        for col in new_df.columns:
            new_df[col] = self._convert_to_numeric_series(new_df[col])
        return new_df

    def _refresh_tables(self):
        """Convertit les tables du dictionnaire en SimpleDataFrame"""
        for table_name, table_data in self.datas["tables"].items():
            df = SimpleDataFrame(table_data)
            df = self._convert_dataframe_columns(df)
            self.current_tables[table_name] = df
            self.transformed_tables[table_name] = df.copy()

    def _update_dict_tables(self):
        """Met à jour le dictionnaire original à partir des SimpleDataFrame"""
        all_tables = {**self.current_tables, **self.transformed_tables}
        for table_name, df in all_tables.items():
            dict_data = df.to_dict(orient='list')
            dict_data = self._convert_dict_to_json_serializable(dict_data)
            self.datas["tables"][table_name] = dict_data

    def add_output(self, message_type: str, content: Any, line: int = 0):
        """Ajoute un message de sortie pour l'interface"""
        content = convert_to_json_serializable(content)
        self.output_messages.append({
            "type": message_type,
            "content": content,
            "line": line or self.current_line,
            "timestamp": datetime.now().isoformat()
        })

    def evaluate(self, ast: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Point d'entrée principal : évalue un programme complet"""
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
        """Évalue une commande LOAD"""
        props = command.get("properties", {})
        name = props.get("name")
        alias = props.get("alias", name)

        self.add_output("info", f"Chargement de la table '{name}' -> '{alias}'", self.current_line)

        if name in self.datas["tables"]:
            table_data = self.datas["tables"][name]
            df = SimpleDataFrame(table_data)
            df = self._convert_dataframe_columns(df)
            self.current_tables[alias] = df
            self.transformed_tables[alias] = df.copy()

            preview = df.head(10).to_dict(orient='records')
            preview = self._convert_dict_to_json_serializable(preview)

            self.add_output("table", {
                "name": alias,
                "source": name,
                "columns": df.columns,
                "types": [str(type(df[col][0]).__name__) if df[col] and len(df[col]) > 0 else 'unknown' 
                         for col in df.columns],
                "preview": preview,
                "shape": list(df.shape),
                "row_count": df.shape[0],
                "col_count": df.shape[1]
            })

            self.add_output("success", f"Table '{alias}' chargée avec succès ({df.shape[0]} lignes)", 
                          self.current_line)
        else:
            self.add_output("error", f"Table '{name}' introuvable dans les données", self.current_line)

    def evaluate_transform(self, command: Dict[str, Any]):
        """Évalue une commande TRANSFORM"""
        props = command.get("properties", {})
        source_name = props.get("name")
        alias = props.get("alias", f"{source_name}_transformed")
        contents = command.get("contents", [])

        self.add_output("info", f"Transformation de '{source_name}' -> '{alias}'", self.current_line)

        source_df = None
        if source_name in self.transformed_tables:
            source_df = self.transformed_tables[source_name]
        elif source_name in self.current_tables:
            source_df = self.current_tables[source_name]
        else:
            self.add_output("error", f"Table source '{source_name}' introuvable", self.current_line)
            return

        df = source_df.copy()
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

        self.transformed_tables[alias] = df.copy()
        self.current_tables[alias] = df.copy()

        preview = df.head(10).to_dict(orient='records')
        preview = self._convert_dict_to_json_serializable(preview)

        self.add_output("table", {
            "name": alias,
            "source": source_name,
            "columns": df.columns,
            "types": [str(type(df[col][0]).__name__) if df[col] and len(df[col]) > 0 else 'unknown' 
                     for col in df.columns],
            "preview": preview,
            "shape": list(df.shape),
            "row_count": df.shape[0],
            "col_count": df.shape[1],
            "operations": operations_applied
        })

        self.add_output("success", f"Table '{alias}' créée avec succès ({df.shape[0]} lignes)", 
                      self.current_line)

    def apply_select(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
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
                        new_df = new_df.rename({col_name: alias})
                        selected_cols.append(alias)
                    else:
                        selected_cols.append(col_name)
                else:
                    self.add_output("error", f"Colonne '{col_name}' introuvable", self.current_line)
            elif "expression" in arg:
                expr_result = self.evaluate_expression(arg["expression"], new_df)
                alias = arg.get("alias", f"col_{len(selected_cols)}")

                expr_result = ensure_list_length(expr_result, len(new_df))
                new_df[alias] = expr_result
                selected_cols.append(alias)

        if selected_cols:
            return new_df.select(selected_cols)
        return new_df

    def apply_drop(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique une opération DROP"""
        args = operation.get("args", [])
        return df.drop(args)

    def apply_filter(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique une opération FILTER"""
        condition = operation.get("condition")
        mask = self.evaluate_filter_condition(condition, df)
        return df.filter(mask)

    def apply_create_feature(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique une opération CREATE_FEATURE"""
        features = operation.get("features", [])
        new_df = df.copy()
        current_len = len(new_df)

        for feature in features:
            name = feature.get("name")
            expr = feature.get("expression")

            result = self.evaluate_expression(expr, new_df)

            result = ensure_list_length(result, current_len)
            new_df[name] = result

            self.add_output("info", f"Feature créée: {name}", self.current_line)

        return new_df

    def apply_group_by(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique une opération GROUP BY"""
        columns = operation.get("columns", [])
        df._attrs['group_by_columns'] = columns
        return df

    def apply_agg(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique une opération AGG"""
        aggregations = operation.get("aggregations", [])
        group_by_cols = df._attrs.get('group_by_columns', [])

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
                        col_data = df[col_name]
                        numeric_data = [to_numeric(x) for x in col_data if x is not None]
                        valid_data = [x for x in numeric_data if isinstance(x, (int, float))]

                        if func_name == "SUM":
                            result_dict[name] = sum(valid_data) if valid_data else 0
                        elif func_name == "AVG" or func_name == "MEAN":
                            result_dict[name] = sum(valid_data) / len(valid_data) if valid_data else None
                        elif func_name == "COUNT":
                            result_dict[name] = len(df)
                        elif func_name == "MIN":
                            result_dict[name] = min(valid_data) if valid_data else None
                        elif func_name == "MAX":
                            result_dict[name] = max(valid_data) if valid_data else None

            return SimpleDataFrame({k: [v] for k, v in result_dict.items()})


        groups = {}

        for i in range(len(df)):
            key_parts = []
            for col in group_by_cols:
                val = df[col][i]
                key_parts.append(str(val) if val is not None else "None")
            key = tuple(key_parts)

            if key not in groups:
                groups[key] = []
            groups[key].append(i)


        result = {col: [] for col in group_by_cols}

        for agg_item in aggregations:
            name = agg_item.get("name")
            result[name] = []


        for key, indices in groups.items():

            for i, col in enumerate(group_by_cols):

                val = key[i]
                if val == "None":
                    result[col].append(None)
                else:
                    num_val = to_numeric(val)
                    if num_val is not None and not isinstance(num_val, str):
                        result[col].append(num_val)
                    else:
                        result[col].append(val)


            for agg_item in aggregations:
                name = agg_item.get("name")
                func_call = agg_item.get("function", {})
                func_name = func_call.get("name")
                args = func_call.get("arguments", [])

                if args and len(args) > 0:
                    col_name = self.extract_column_name(args[0])
                    if col_name and col_name in df.columns:

                        values = [df[col_name][i] for i in indices]

                        numeric_values = []
                        for v in values:
                            if v is not None:
                                if isinstance(v, (int, float)):
                                    numeric_values.append(v)
                                else:
                                    num_v = to_numeric(v)
                                    if isinstance(num_v, (int, float)):
                                        numeric_values.append(num_v)

                        if func_name == "SUM":
                            result[name].append(sum(numeric_values) if numeric_values else 0)
                        elif func_name == "AVG" or func_name == "MEAN":
                            result[name].append(sum(numeric_values) / len(numeric_values) if numeric_values else None)
                        elif func_name == "COUNT":
                            result[name].append(len(values))
                        elif func_name == "MIN":
                            result[name].append(min(numeric_values) if numeric_values else None)
                        elif func_name == "MAX":
                            result[name].append(max(numeric_values) if numeric_values else None)
                        else:
                            result[name].append(None)
                    else:
                        result[name].append(None)

        return SimpleDataFrame(result)

    def apply_join(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique une opération JOIN"""
        table_name = operation.get("table")
        on_condition = operation.get("on")
        join_type = operation.get("type", "inner")
        suffix = operation.get("suffix", "_right")

        right_df = None
        if table_name in self.transformed_tables:
            right_df = self.transformed_tables[table_name]
        elif table_name in self.current_tables:
            right_df = self.current_tables[table_name]
        else:
            self.add_output("error", f"Table à joindre '{table_name}' introuvable", self.current_line)
            return df

        left_col, right_col = self.parse_join_condition(on_condition)

        if left_col and right_col:
            try:
                return df.merge(right_df, left_on=left_col, right_on=right_col, how=join_type)
            except Exception as e:
                self.add_output("error", f"Erreur lors du JOIN: {str(e)}", self.current_line)

        return df

    def apply_having(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique une opération HAVING"""
        condition = operation.get("condition")
        mask = self.evaluate_filter_condition(condition, df)
        return df.filter(mask)

    def evaluate_analyze(self, command: Dict[str, Any]):
        """Évalue une commande ANALYZE"""
        target = command.get("target")
        operations = command.get("operations", [])
        options = command.get("options", {})

        self.add_output("info", f"Analyse de '{target}'...", self.current_line)

        df = None
        if target in self.transformed_tables:
            df = self.transformed_tables[target]
        elif target in self.current_tables:
            df = self.current_tables[target]
        else:
            self.add_output("error", f"Table cible '{target}' introuvable", self.current_line)
            return

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

        collection = None
        if collection_name in self.transformed_tables:
            collection = self.transformed_tables[collection_name]
        elif collection_name in self.current_tables:
            collection = self.current_tables[collection_name]
        elif collection_name in self.variables:
            collection = self.variables[collection_name]

        if collection is not None and isinstance(collection, SimpleDataFrame):
            for idx in range(len(collection)):
                row_dict = collection[idx]
                row_dict = self._convert_dict_to_json_serializable(row_dict)
                self.variables[variable] = row_dict
                self.add_output("info", f"Itération {idx+1}: {variable} = {row_dict}", self.current_line)

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

    def evaluate_filter_condition(self, condition: Any, df: SimpleDataFrame) -> List[bool]:
        """Évalue une condition de filtre et retourne un masque booléen"""
        if condition is None:
            return [True] * len(df)

        if isinstance(condition, dict):
            cond_type = condition.get("type")

            if cond_type == "binary_operation":
                left = self.evaluate_filter_condition(condition.get("left"), df)
                right = self.evaluate_filter_condition(condition.get("right"), df)
                operator = condition.get("operator")

                if operator in ["AND", "&&"]:
                    return [l and r for l, r in zip(left, right)]
                elif operator in ["OR", "||"]:
                    return [l or r for l, r in zip(left, right)]

            elif cond_type == "comparison":
                left = self.evaluate_expression(condition.get("left"), df)
                right = self.evaluate_expression(condition.get("right"), df)
                operator = condition.get("operator")

                if not isinstance(left, list):
                    left = [left] * len(df)
                if not isinstance(right, list):
                    right = [right] * len(df)

                left_num = []
                right_num = []
                for l in left:
                    if isinstance(l, str):
                        l_num = to_numeric(l)
                        left_num.append(l_num if l_num is not None else l)
                    else:
                        left_num.append(l)

                for r in right:
                    if isinstance(r, str):
                        r_num = to_numeric(r)
                        right_num.append(r_num if r_num is not None else r)
                    else:
                        right_num.append(r)

                try:
                    result = []
                    for l, r in zip(left_num, right_num):
                        if l is None or r is None:
                            result.append(False)
                        elif operator == ">":
                            result.append(l > r)
                        elif operator == "<":
                            result.append(l < r)
                        elif operator == ">=":
                            result.append(l >= r)
                        elif operator == "<=":
                            result.append(l <= r)
                        elif operator == "==":
                            result.append(l == r)
                        elif operator == "!=":
                            result.append(l != r)
                        else:
                            result.append(False)
                    return result
                except Exception as e:
                    self.add_output("error", f"Erreur de comparaison: {e}", self.current_line)
                    return [False] * len(df)

            elif cond_type == "between":
                left = self.evaluate_expression(condition.get("left"), df)
                lower = self.evaluate_expression(condition.get("lower"), df)
                upper = self.evaluate_expression(condition.get("upper"), df)

                if not isinstance(left, list):
                    left = [left] * len(df)

                lower_val = lower[0] if isinstance(lower, list) and len(lower) > 0 else lower
                upper_val = upper[0] if isinstance(upper, list) and len(upper) > 0 else upper

                result = []
                for l in left:
                    l_num = to_numeric(l) if isinstance(l, str) else l
                    lower_num = to_numeric(lower_val) if isinstance(lower_val, str) else lower_val
                    upper_num = to_numeric(upper_val) if isinstance(upper_val, str) else upper_val

                    if l_num is None or lower_num is None or upper_num is None:
                        result.append(False)
                    else:
                        result.append(lower_num <= l_num <= upper_num)
                return result

            elif cond_type == "in":
                left = self.evaluate_expression(condition.get("left"), df)
                values = condition.get("values", [])
                evaluated_values = [self.evaluate_expression(v, df) for v in values]

                flat_values = []
                for val in evaluated_values:
                    if isinstance(val, list):
                        flat_values.extend(val)
                    else:
                        flat_values.append(val)

                if isinstance(left, list):
                    return [l in flat_values for l in left]
                else:
                    return [left in flat_values] * len(df)

            elif cond_type == "not":
                expr = self.evaluate_filter_condition(condition.get("expression"), df)
                return [not e for e in expr]

            elif cond_type == "column":
                col_name = condition.get("value")
                if col_name in df.columns:
                    return [bool(x) for x in df[col_name]]
                return [True] * len(df)

            elif cond_type == "boolean":
                val = condition.get("value", True)
                return [val] * len(df)

        return [True] * len(df)

    def evaluate_expression(self, expr: Any, df: SimpleDataFrame = None) -> Any:
        """Évalue une expression mathématique"""
        if expr is None:
            return None

        if isinstance(expr, dict):
            expr_type = expr.get("type")

            if expr_type == "column":
                col_name = expr.get("value")
                if df is not None and col_name in df.columns:
                    return df[col_name]
                return col_name

            elif expr_type == "number":
                return expr.get("value", 0)

            elif expr_type == "float":
                return float(expr.get("value", 0.0))

            elif expr_type == "string":
                val = expr.get("value", "")
                try:
                    val_stripped = val.strip()
                    if val_stripped and (val_stripped.replace('.', '').replace('-', '').replace('e', '').replace('E', '').isdigit()):
                        if '.' in val_stripped or 'e' in val_stripped or 'E' in val_stripped:
                            return float(val_stripped)
                        else:
                            return int(val_stripped)
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

                if df is not None:
                    if not isinstance(left, list):
                        left = [left] * len(df)
                    if not isinstance(right, list):
                        right = [right] * len(df)

                try:
                    result = []
                    for l, r in zip(left, right):
                        l_num = to_numeric(l) if isinstance(l, str) else l
                        r_num = to_numeric(r) if isinstance(r, str) else r

                        if l_num is None or r_num is None:
                            result.append(None)
                        elif operator == "+":
                            result.append(l_num + r_num)
                        elif operator == "-":
                            result.append(l_num - r_num)
                        elif operator == "*":
                            result.append(l_num * r_num)
                        elif operator == "/":
                            result.append(l_num / r_num if r_num != 0 else float('inf'))
                        elif operator == "**":
                            result.append(l_num ** r_num)
                        elif operator == "%":
                            result.append(l_num % r_num if r_num != 0 else None)
                        else:
                            result.append(None)
                    return result
                except Exception as e:
                    self.add_output("error", f"Erreur dans l'expression: {e}", self.current_line)
                    return [None] * len(df)

            elif expr_type == "function_call":
                return self.evaluate_function(expr, df)

            elif expr_type == "case":
                return self.evaluate_case(expr, df)

        return expr

    def evaluate_function(self, func_call: Dict[str, Any], df: SimpleDataFrame = None) -> Any:
        """Évalue un appel de fonction"""
        name = func_call.get("name")
        args = func_call.get("arguments", [])
        over = func_call.get("over")

        evaluated_args = [self.evaluate_expression(arg, df) for arg in args]

        if name == "SUM":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [to_numeric(x) for x in col if to_numeric(x) is not None and isinstance(to_numeric(x), (int, float))]
                    return sum(valid) if valid else 0
                return col
        elif name == "AVG" or name == "MEAN":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [to_numeric(x) for x in col if isinstance(to_numeric(x), (int, float))]
                    return sum(valid) / len(valid) if valid else None
                return col
        elif name == "MEDIAN":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [to_numeric(x) for x in col if isinstance(to_numeric(x), (int, float))]
                    if valid:
                        sorted_vals = sorted(valid)
                        n = len(sorted_vals)
                        mid = n // 2
                        if n % 2 == 0:
                            return (sorted_vals[mid-1] + sorted_vals[mid]) / 2
                        else:
                            return sorted_vals[mid]
                return None
        elif name == "COUNT":
            if len(evaluated_args) > 0:
                if isinstance(evaluated_args[0], dict) and evaluated_args[0].get("type") == "star":
                    return len(df) if df is not None else 0
                col = evaluated_args[0]
                if isinstance(col, list):
                    return len([x for x in col if x is not None])
                return 1 if col is not None else 0
        elif name == "MIN":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [to_numeric(x) for x in col if isinstance(to_numeric(x), (int, float))]
                    return min(valid) if valid else None
                return col
        elif name == "MAX":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [to_numeric(x) for x in col if isinstance(to_numeric(x), (int, float))]
                    return max(valid) if valid else None
                return col
        elif name == "STD":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [to_numeric(x) for x in col if isinstance(to_numeric(x), (int, float))]
                    if len(valid) > 1:
                        mean = sum(valid) / len(valid)
                        variance = sum((x - mean) ** 2 for x in valid) / (len(valid) - 1)
                        return math.sqrt(variance)
                return 0
        elif name == "VAR":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [to_numeric(x) for x in col if isinstance(to_numeric(x), (int, float))]
                    if len(valid) > 1:
                        mean = sum(valid) / len(valid)
                        return sum((x - mean) ** 2 for x in valid) / (len(valid) - 1)
                return 0
        elif name == "CORR":
            if len(evaluated_args) >= 2:
                col1 = evaluated_args[0]
                col2 = evaluated_args[1]
                if isinstance(col1, list) and isinstance(col2, list):
                    pairs = []
                    for x, y in zip(col1, col2):
                        x_num = to_numeric(x)
                        y_num = to_numeric(y)
                        if isinstance(x_num, (int, float)) and isinstance(y_num, (int, float)):
                            pairs.append((x_num, y_num))

                    if len(pairs) > 1:
                        xs = [p[0] for p in pairs]
                        ys = [p[1] for p in pairs]
                        mean_x = sum(xs) / len(xs)
                        mean_y = sum(ys) / len(ys)

                        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
                        den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
                        den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))

                        if den_x * den_y != 0:
                            return num / (den_x * den_y)
                return 0

        elif name == "LOG":
            if len(evaluated_args) > 0:
                val = evaluated_args[0]
                if isinstance(val, list):
                    return [math.log(v) if v > 0 else float('-inf') for v in val]
                return math.log(val) if val > 0 else float('-inf')
        elif name == "EXP":
            if len(evaluated_args) > 0:
                val = evaluated_args[0]
                if isinstance(val, list):
                    return [math.exp(v) for v in val]
                return math.exp(val)
        elif name == "SQRT":
            if len(evaluated_args) > 0:
                val = evaluated_args[0]
                if isinstance(val, list):
                    return [math.sqrt(v) if v >= 0 else float('nan') for v in val]
                return math.sqrt(val) if val >= 0 else float('nan')
        elif name == "ABS":
            if len(evaluated_args) > 0:
                val = evaluated_args[0]
                if isinstance(val, list):
                    return [abs(v) for v in val]
                return abs(val)
        elif name == "ROUND":
            if len(evaluated_args) >= 1:
                val = evaluated_args[0]
                decimals = evaluated_args[1] if len(evaluated_args) > 1 else 0
                if isinstance(val, list):
                    return [round(v, decimals) for v in val]
                return round(val, decimals)

        if over:
            return self.evaluate_window_function(name, evaluated_args, over, df)

        return evaluated_args[0] if evaluated_args else None

    def evaluate_window_function(self, name: str, args: List, over: Dict, df: SimpleDataFrame) -> Any:
        """Évalue une fonction de fenêtrage"""
        if df is None or len(df) == 0:
            return None

        partition_by = over.get("partition_by", [])

        if name == "RANK":
            result = [1] * len(df)
            if partition_by and all(col in df.columns for col in partition_by):
                pass
            return result
        elif name == "ROW_NUMBER":
            return list(range(1, len(df) + 1))

        return [None] * len(df)

    def evaluate_case(self, case_expr: Dict[str, Any], df: SimpleDataFrame = None) -> Any:
        """Évalue une expression CASE WHEN"""
        when_then = case_expr.get("when_then", [])
        else_val = case_expr.get("else")

        if df is not None:
            result = [None] * len(df)

            for wt in when_then:
                condition = self.evaluate_filter_condition(wt.get("when"), df)
                then_val = self.evaluate_expression(wt.get("then"), df)

                then_val = ensure_list_length(then_val, len(df))

                for i, cond in enumerate(condition):
                    if cond and result[i] is None:
                        result[i] = then_val[i]

            if else_val is not None:
                else_result = self.evaluate_expression(else_val, df)

                else_result = ensure_list_length(else_result, len(df))
                for i in range(len(result)):
                    if result[i] is None:
                        result[i] = else_result[i]

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

    def evaluate_stat_function(self, name: str, args: List, df: SimpleDataFrame) -> Any:
        """Évalue une fonction statistique pour ANALYZE"""
        evaluated_args = [self.evaluate_expression(arg, df) for arg in args]

        if name == "COUNT":
            return len(df)
        elif name == "SUM":
            col = evaluated_args[0] if evaluated_args else None
            if col and isinstance(col, list):
                valid = [to_numeric(x) for x in col if isinstance(to_numeric(x), (int, float))]
                return sum(valid) if valid else None
        elif name == "AVG" or name == "MEAN":
            col = evaluated_args[0] if evaluated_args else None
            if col and isinstance(col, list):
                valid = [to_numeric(x) for x in col if isinstance(to_numeric(x), (int, float))]
                return sum(valid) / len(valid) if valid else None
        elif name == "MIN":
            col = evaluated_args[0] if evaluated_args else None
            if col and isinstance(col, list):
                valid = [to_numeric(x) for x in col if isinstance(to_numeric(x), (int, float))]
                return min(valid) if valid else None
        elif name == "MAX":
            col = evaluated_args[0] if evaluated_args else None
            if col and isinstance(col, list):
                valid = [to_numeric(x) for x in col if isinstance(to_numeric(x), (int, float))]
                return max(valid) if valid else None
        elif name == "CORR":
            if len(evaluated_args) >= 2:
                col1 = evaluated_args[0]
                col2 = evaluated_args[1]
                if isinstance(col1, list) and isinstance(col2, list):
                    pairs = []
                    for x, y in zip(col1, col2):
                        x_num = to_numeric(x)
                        y_num = to_numeric(y)
                        if isinstance(x_num, (int, float)) and isinstance(y_num, (int, float)):
                            pairs.append((x_num, y_num))

                    if len(pairs) > 1:
                        xs = [p[0] for p in pairs]
                        ys = [p[1] for p in pairs]
                        mean_x = sum(xs) / len(xs)
                        mean_y = sum(ys) / len(ys)

                        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
                        den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
                        den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))

                        if den_x * den_y != 0:
                            return num / (den_x * den_y)
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
        return list(self.datas["tables"].keys())

    def get_analysis_names(self) -> List[str]:
        return list(self.datas["analysis"].keys())

    def get_transformed_table(self, name: str) -> Optional[SimpleDataFrame]:
        """Retourne une table transformée par son nom"""
        return self.transformed_tables.get(name)

    def list_transformed_tables(self) -> List[str]:
        """Liste toutes les tables transformées"""
        return list(self.transformed_tables.keys())

    def export_results(self) -> Dict[str, Any]:
        """Exporte tous les résultats pour sauvegarde"""
        self._update_dict_tables()
        return self._convert_dict_to_json_serializable(self.datas)

    def clear(self):
        """Réinitialise l'évaluateur"""
        self.datas = {"tables": {}, "analysis": {}}
        self.current_tables.clear()
        self.transformed_tables.clear()
        self.analysis_results.clear()
        self.variables.clear()
        self.output_messages.clear()


def evaluate_dsl_code(code: str, datas: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fonction d'entrée pour évaluer du code DSL.
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

        result_datas = evaluator.export_results()
        result_datas['transformed_tables'] = evaluator.list_transformed_tables()

        return {
            "success": True,
            "messages": converted_messages,
            "datas": result_datas
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
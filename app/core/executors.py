# executors.py
import math
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from .simple_dataframe import SimpleDataFrame, to_numeric, is_numeric, ensure_list_length
from .stats_calculator import StatsCalculator
from .vis import Visualizer


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
    Utilise SimpleDataFrame, StatsCalculator et Visualizer.
    """

    def __init__(self, initial_datas: Dict[str, Any] = None):
        self.datas = initial_datas or {"tables": {}, "analysis": {}}
        self.current_tables: Dict[str, SimpleDataFrame] = {}
        self.transformed_tables: Dict[str, SimpleDataFrame] = {}
        self.analysis_results: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}
        self.output_messages: List[Dict[str, Any]] = []
        self.current_line = 0

        # Initialiser les nouveaux modules
        self.stats = StatsCalculator()
        self.viz = Visualizer()

        self._refresh_tables()

    def _convert_dict_to_json_serializable(self, d: Any) -> Any:
        """Convertit récursivement pour JSON"""
        return convert_to_json_serializable(d)

    def _convert_to_numeric_series(self, values: List) -> List:
        """
        Convertit une liste en valeurs numériques si possible.
        Préserve None pour les valeurs manquantes.
        """
        result = []
        for v in values:
            if v is None:
                result.append(None)  # Préserver None pour valeurs manquantes
            elif isinstance(v, (int, float)):
                result.append(v)
            elif isinstance(v, str):
                v_stripped = v.strip()
                if v_stripped in ["", '.']:
                    result.append(None)  # Chaîne vide intentionnelle
                else:
                    try:
                        # Essayer de convertir en nombre
                        if v_stripped.replace('.', '').replace('-', '').replace('e', '').replace('E', '').isdigit():
                            if '.' in v_stripped or 'e' in v_stripped.lower() or 'E' in v_stripped:
                                result.append(float(v_stripped))
                            else:
                                result.append(int(v_stripped))
                        else:
                            result.append(v_stripped)  # Garder comme chaîne
                    except (ValueError, TypeError):
                        result.append(v_stripped)  # Garder comme chaîne
            else:
                result.append(v)  # Autres types (bool, etc.)
        return result

    def _convert_dataframe_columns(self, df: SimpleDataFrame) -> SimpleDataFrame:
        """Convertit les colonnes en types numériques si possible, préserve None"""
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
        elif cmd_type == "stats":
            self.evaluate_stats(command)
        elif cmd_type == "visualize":
            self.evaluate_visualize(command)
        elif cmd_type == "if":
            self.evaluate_if(command)
        elif cmd_type == "for":
            self.evaluate_for(command)
        elif cmd_type == "describe":
            self.evaluate_describe(command)
        elif cmd_type == "describe_all":
            self.evaluate_describe_all(command)
        elif cmd_type == "summary":
            self.evaluate_summary(command)
        elif cmd_type == "clean":
            self.evaluate_clean(command)
        else:
            self.add_output("error", f"Type de commande inconnu: {cmd_type}", self.current_line)

    # ========== COMMANDE LOAD ==========

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
                "types": [str(type(df[col][0]).__name__) if df[col] and len(df[col]) > 0 and df[col][0] is not None else 'None' 
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

    # ========== COMMANDE TRANSFORM ==========

    def evaluate_transform(self, command: Dict[str, Any]):
        """Évalue une commande TRANSFORM"""
        props = command.get("properties", {})
        source_name = props.get("name")
        alias = props.get("alias", f"{source_name}_transformed")
        contents = command.get("contents", [])

        self.add_output("info", f"Transformation de '{source_name}' -> '{alias}'", self.current_line)

        source_df = None
        var_df = None
        if source_name in self.transformed_tables:
            source_df = self.transformed_tables[source_name]
        elif source_name in self.current_tables:
            source_df = self.current_tables[source_name]
        elif source_name in self.variables:
            var_df = self.variables[source_name]
        else:
            self.add_output("error", f"Table source '{source_name}' introuvable", self.current_line)
            return

        if source_df:
            df = source_df.copy()
        elif var_df:
            df = var_df.copy()

        operations_applied = []

        for operation in contents:
            op_type = operation.get("type")
            operations_applied.append(op_type)

            # Opérations existantes
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

            # Opérations de nettoyage
            elif op_type == "drop_na":
                df = self.apply_drop_na(df, operation)
            elif op_type == "fill_na":
                df = self.apply_fill_na(df, operation)
            elif op_type == "replace":
                df = self.apply_replace(df, operation)
            elif op_type == "clip":
                df = self.apply_clip(df, operation)
            elif op_type == "remove_outliers":
                df = self.apply_remove_outliers(df, operation)
            elif op_type == "standardize":
                df = self.apply_standardize(df, operation)
            elif op_type == "min_max_scale":
                df = self.apply_min_max_scale(df, operation)
            elif op_type == "one_hot_encode":
                df = self.apply_one_hot_encode(df, operation)
            elif op_type == "label_encode":
                df = self.apply_label_encode(df, operation)

        if source_df:
            self.transformed_tables[alias] = df.copy()
            self.current_tables[alias] = df.copy()
        elif var_df:
            self.variables[alias] = df.copy()

        preview = df.head(10).to_dict(orient='records')
        preview = self._convert_dict_to_json_serializable(preview)

        self.add_output("table", {
            "name": alias,
            "source": source_name,
            "columns": df.columns,
            "types": [str(type(df[col][0]).__name__) if df[col] and len(df[col]) > 0 and df[col][0] is not None else 'None' 
                     for col in df.columns],
            "preview": preview,
            "shape": list(df.shape),
            "row_count": df.shape[0],
            "col_count": df.shape[1],
            "operations": operations_applied
        })

        self.add_output("success", f"Table '{alias}' créée avec succès ({df.shape[0]} lignes)", 
                      self.current_line)

    # ========== OPÉRATIONS DE TRANSFORMATION ==========

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
            # Agrégation globale
            result_dict = {}
            for agg_item in aggregations:
                name = agg_item.get("name")

                if "expression" in agg_item:
                    expression = agg_item["expression"]
                    new_df = df.copy()
                    value = self.evaluate_expression(expression, new_df)
                    if isinstance(value, (tuple, list)):
                        value = value[0] if value else None
                    result_dict[name] = value

            return SimpleDataFrame({k: [v] for k, v in result_dict.items()})

        # Agrégation par groupe
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
            # Ajouter les clés
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

            # Calculer les agrégations
            for agg_item in aggregations:
                name = agg_item.get("name")

                if "expression" in agg_item:
                    expression = agg_item.get("expression")
                    new_df = {}
                    for col_name in df.columns:
                        numeric_values = self.do_values(df, col_name, indices, keep_none=True)
                        new_df[col_name] = numeric_values
                    new_df = SimpleDataFrame(new_df)
                    value = self.evaluate_expression(expr=expression, df=new_df)
                    if isinstance(value, (tuple, list)):
                        value = value[0] if value else None
                    result[name].append(value)

        return SimpleDataFrame(result)

    def apply_join(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique une opération JOIN"""
        table_name = operation.get("table")
        on_condition = operation.get("on")
        join_type = operation.get("how", "inner")

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

    # ========== OPÉRATIONS DE NETTOYAGE ==========

    def apply_drop_na(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique drop_na() - Supprime les lignes avec valeurs manquantes"""
        params = operation.get("params", {})
        columns = params.get("columns")
        how = params.get("how", 'any')
        thresh = params.get("thresh")

        return df.drop_na(columns=columns, how=how, thresh=thresh)

    def apply_fill_na(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique fill_na() - Remplit les valeurs manquantes"""
        params = operation.get("params", {})
        value = params.get("value")
        method = params.get("method")
        columns = params.get("columns")

        # Convertir la méthode en minuscules si c'est une chaîne
        if method and isinstance(method, str):
            method = method.lower()

        return df.fill_na(value=value, method=method, columns=columns)

    def apply_replace(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique replace() - Remplace des valeurs"""
        params = operation.get("params", {})
        to_replace = params.get("to_replace")
        value = params.get("value")
        columns = params.get("columns")

        return df.replace(to_replace=to_replace, value=value, columns=columns)

    def apply_clip(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique clip() - Limite les valeurs à un intervalle"""
        params = operation.get("params", {})
        lower = params.get("lower")
        upper = params.get("upper")
        columns = params.get("columns")

        return df.clip(lower=lower, upper=upper, columns=columns)

    def apply_remove_outliers(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique remove_outliers() - Supprime les outliers"""
        params = operation.get("params", {})
        column = params.get("column")
        factor = params.get("factor", 1.5)

        return df.remove_outliers_iqr(column=column, factor=factor)

    def apply_standardize(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique standardize() - Standardisation (moyenne=0, écart-type=1)"""
        params = operation.get("params", {})
        columns = params.get("columns")

        return df.standardize(columns=columns)

    def apply_min_max_scale(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique min_max_scale() - Normalisation min-max"""
        params = operation.get("params", {})
        columns = params.get("columns")
        feature_range = params.get("feature_range", (0, 1))

        return df.min_max_scale(columns=columns, feature_range=feature_range)

    def apply_one_hot_encode(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique one_hot_encode() - Encodage one-hot"""
        params = operation.get("params", {})
        column = params.get("column")
        prefix = params.get("prefix", column)
        drop_first = params.get("drop_first", False)

        return df.one_hot_encode(column=column, prefix=prefix, drop_first=drop_first)

    def apply_label_encode(self, df: SimpleDataFrame, operation: Dict[str, Any]) -> SimpleDataFrame:
        """Applique label_encode() - Encodage par étiquettes"""
        params = operation.get("params", {})
        column = params.get("column")
        prefix = params.get("prefix", f"{column}_encoded")

        return df.label_encode(column=column, prefix=prefix)

    # ========== COMMANDE CLEAN ==========

    def evaluate_clean(self, command: Dict[str, Any]):
        """
        Évalue une commande CLEAN - Applique plusieurs opérations de nettoyage
        """
        target = command.get("target")
        operations = command.get("operations", [])

        self.add_output("info", f"Nettoyage de la table '{target}'...", self.current_line)

        df = None
        if target in self.transformed_tables:
            df = self.transformed_tables[target]
        elif target in self.current_tables:
            df = self.current_tables[target]
        elif target in self.variables:
            df = self.variables[target]
        else:
            self.add_output("error", f"Table cible '{target}' introuvable", self.current_line)
            return

        result_df = df.copy()
        operations_applied = []

        for operation in operations:
            op_type = operation.get("type")
            operations_applied.append(op_type)

            if op_type == "drop_na":
                result_df = self.apply_drop_na(result_df, operation)
            elif op_type == "fill_na":
                result_df = self.apply_fill_na(result_df, operation)
            elif op_type == "replace":
                result_df = self.apply_replace(result_df, operation)
            elif op_type == "clip":
                result_df = self.apply_clip(result_df, operation)
            elif op_type == "remove_outliers":
                result_df = self.apply_remove_outliers(result_df, operation)
            elif op_type == "standardize":
                result_df = self.apply_standardize(result_df, operation)
            elif op_type == "min_max_scale":
                result_df = self.apply_min_max_scale(result_df, operation)
            elif op_type == "one_hot_encode":
                result_df = self.apply_one_hot_encode(result_df, operation)
            elif op_type == "label_encode":
                result_df = self.apply_label_encode(result_df, operation)

        # Sauvegarder le résultat
        alias = f"{target}_cleaned"
        self.transformed_tables[alias] = result_df.copy()
        self.current_tables[alias] = result_df.copy()

        preview = result_df.head(10).to_dict(orient='records')
        preview = self._convert_dict_to_json_serializable(preview)

        self.add_output("table", {
            "name": alias,
            "source": target,
            "columns": result_df.columns,
            "types": [str(type(result_df[col][0]).__name__) if result_df[col] and len(result_df[col]) > 0 and result_df[col][0] is not None else 'None' 
                     for col in result_df.columns],
            "preview": preview,
            "shape": list(result_df.shape),
            "row_count": result_df.shape[0],
            "col_count": result_df.shape[1],
            "operations": operations_applied
        })

        self.add_output("success", f"Table '{alias}' nettoyée avec succès ({result_df.shape[0]} lignes)", 
                      self.current_line)

    # ========== COMMANDE STATS ==========

    def evaluate_stats(self, command: Dict[str, Any]):
        """Évalue une commande STATS pour les statistiques avancées"""
        target = command.get("target")
        operations = command.get("operations", [])

        self.add_output("info", f"Calcul des statistiques avancées sur '{target}'...", self.current_line)

        df = None
        if target in self.transformed_tables:
            df = self.transformed_tables[target]
        elif target in self.current_tables:
            df = self.current_tables[target]
        elif target in self.variables:
            df = self.variables[target]
        else:
            self.add_output("error", f"Table cible '{target}' introuvable", self.current_line)
            return

        self.stats.set_dataframe(df)
        results = {}

        for op in operations:
            if isinstance(op, dict):
                expression = op.get("expression")
                variable = op.get("variable")

                result = self.evaluate_stats_expression(expression, df)

                if variable:
                    results[variable] = result
                    self.variables[variable] = result
                else:
                    name = f"stat_{len(results)}"
                    results[name] = result

        analysis_name = f"stats_{len(self.analysis_results)}"
        self.analysis_results[analysis_name] = results

        self.add_output("analysis", {
            "name": analysis_name,
            "target": target,
            "results": results,
            "type": "stats"
        })

        self.add_output("success", f"Statistiques avancées '{analysis_name}' terminées", self.current_line)

    def evaluate_stats_expression(self, expr: Any, df: SimpleDataFrame) -> Any:
        """Évalue une expression statistique avancée"""
        if isinstance(expr, dict) and expr.get("type") == "function_call":
            name = expr.get("name")
            args = expr.get("arguments", [])

            data_args = []
            for arg in args:
                if isinstance(arg, dict) and arg.get("type") == "column":
                    col_name = arg.get("value")
                    if col_name in df.columns:
                        # Filtrer les None pour les calculs statistiques
                        col_data = [x for x in df[col_name] if x is not None]
                        data_args.append(col_data)
                    else:
                        data_args.append([])
                else:
                    data_args.append(self.evaluate_expression(arg, df))

            if name == "MEAN" or name == "AVG":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.mean(data_args[0])
            elif name == "GEOMETRIC_MEAN":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.geometric_mean(data_args[0])
            elif name == "HARMONIC_MEAN":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.harmonic_mean(data_args[0])
            elif name == "QUADRATIC_MEAN":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.quadratic_mean(data_args[0])
            elif name == "WEIGHTED_MEAN":
                if len(data_args) >= 2:
                    return self.stats.weighted_mean(data_args[0], data_args[1])
            elif name == "TRIMMED_MEAN":
                if len(data_args) >= 1:
                    prop = data_args[1] if len(data_args) > 1 else 0
                    return self.stats.trimmed_mean(data_args[0], prop)
            elif name == "MIDRANG":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.midrange(data_args[0])
            elif name == "MEDIAN":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.median(data_args[0])
            elif name == "MODE":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.mode(data_args[0])
            elif name == "VAR":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.variance(data_args[0])
            elif name == "STD":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.std(data_args[0])
            elif name == "SKEWNESS":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.skewness(data_args[0])
            elif name == "KURTOSIS":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.kurtosis(data_args[0])
            elif name == "MOMENT":
                if len(data_args) >= 2:
                    return self.stats.moment(data_args[0], data_args[1])
            elif name == "GINI":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.gini(data_args[0])
            elif name == "ENTROPY":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.entropy(data_args[0])

            elif name == "CORR":
                if len(data_args) >= 2:
                    return self.stats.correlation(data_args[0], data_args[1])
            elif name == "COVARIANCE":
                if len(data_args) >= 2:
                    return self.stats.covariance(data_args[0], data_args[1])
            elif name == "SPEARMAN":
                if len(data_args) >= 2:
                    return self.stats.spearman_correlation(data_args[0], data_args[1])
            elif name == "KENDALL":
                if len(data_args) >= 2:
                    return self.stats.kendall_tau(data_args[0], data_args[1])

            elif name == "T_TEST":
                if len(data_args) >= 1:
                    mu = data_args[1] if len(data_args) > 1 else 0
                    return self.stats.t_test_onesample(data_args[0], mu)
            elif name == "F_TEST":
                if len(data_args) >= 2:
                    return self.stats.f_test(data_args[0], data_args[1])
            elif name == "CHI2":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.chi2_test(data_args[0])
            elif name == "SHAPIRO":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.shapiro_wilk(data_args[0])
            elif name == "ANDERSON":
                if data_args and isinstance(data_args[0], list):
                    return self.stats.anderson_darling(data_args[0])

            elif name == "ACF":
                if data_args and isinstance(data_args[0], list):
                    nlags = data_args[1] if len(data_args) > 1 else 10
                    return self.stats.acf(data_args[0], nlags)
            elif name == "LAG":
                if len(data_args) >= 2:
                    return self.stats.lag(data_args[0], data_args[1])
            elif name == "DIFF":
                if len(data_args) >= 2:
                    return self.stats.diff(data_args[0], data_args[1])
            elif name == "PCT_CHANGE":
                if len(data_args) >= 2:
                    return self.stats.pct_change(data_args[0], data_args[1])
            elif name == "MOVING_AVG":
                if len(data_args) >= 2:
                    return self.stats.moving_average(data_args[0], data_args[1])

            elif name == "EUCLIDEAN":
                if len(data_args) >= 2:
                    return self.stats.euclidean_distance(data_args[0], data_args[1])
            elif name == "MANHATTAN":
                if len(data_args) >= 2:
                    return self.stats.manhattan_distance(data_args[0], data_args[1])
            elif name == "COSINE":
                if len(data_args) >= 2:
                    return self.stats.cosine_similarity(data_args[0], data_args[1])

        return None

    # ========== COMMANDES DESCRIBE, DESCRIBE_ALL, SUMMARY ==========

    def evaluate_describe(self, command: Dict[str, Any]):
        """
        Évalue une commande DESCRIBE - Statistiques descriptives
        """
        target = command.get("target")
        columns = command.get("columns")
        options = command.get("options", {})

        self.add_output("info", f"Calcul des statistiques descriptives sur '{target}'...", self.current_line)

        df = None
        if target in self.transformed_tables:
            df = self.transformed_tables[target]
        elif target in self.current_tables:
            df = self.current_tables[target]
        elif target in self.variables:
            df = self.variables[target]
        else:
            self.add_output("error", f"Table cible '{target}' introuvable", self.current_line)
            return

        self.stats.set_dataframe(df)

        # Si columns est spécifié, on ne décrit que ces colonnes
        cols_to_describe = columns if columns else None

        try:
            result = self.stats.describe(cols_to_describe)

            # Ajouter le format d'affichage
            display_format = options.get("FORMAT", "table")
            if isinstance(display_format, dict):
                display_format = display_format.get("value", "table")

            self.add_output("analysis", {
                "type": "describe",
                "target": target,
                "results": result,
                "format": display_format,
                "columns_described": list(result.keys())
            }, self.current_line)

            self.add_output("success", f"Statistiques descriptives calculées pour '{target}'", self.current_line)

        except Exception as e:
            self.add_output("error", f"Erreur lors du calcul des statistiques: {str(e)}", self.current_line)

    def evaluate_describe_all(self, command: Dict[str, Any]):
        """
        Évalue une commande DESCRIBE_ALL - Statistiques complètes
        """
        target = command.get("target")
        options = command.get("options", {})

        self.add_output("info", f"Calcul des statistiques complètes sur '{target}'...", self.current_line)

        df = None
        if target in self.transformed_tables:
            df = self.transformed_tables[target]
        elif target in self.current_tables:
            df = self.current_tables[target]
        elif target in self.variables:
            df = self.variables[target]
        else:
            self.add_output("error", f"Table cible '{target}' introuvable", self.current_line)
            return

        self.stats.set_dataframe(df)

        try:
            result = self.stats.describe_all()

            # Ajouter le format d'affichage
            display_format = options.get("FORMAT", "detailed")
            if isinstance(display_format, dict):
                display_format = display_format.get("value", "detailed")

            self.add_output("analysis", {
                "type": "describe_all",
                "target": target,
                "results": result,
                "format": display_format,
                "shape": df.shape
            }, self.current_line)

            self.add_output("success", f"Statistiques complètes calculées pour '{target}'", self.current_line)

        except Exception as e:
            self.add_output("error", f"Erreur lors du calcul des statistiques: {str(e)}", self.current_line)

    def evaluate_summary(self, command: Dict[str, Any]):
        """
        Évalue une commande SUMMARY - Résumé du DataFrame
        """
        target = command.get("target")

        self.add_output("info", f"Calcul du résumé de '{target}'...", self.current_line)

        df = None
        if target in self.transformed_tables:
            df = self.transformed_tables[target]
        elif target in self.current_tables:
            df = self.current_tables[target]
        elif target in self.variables:
            df = self.variables[target]
        else:
            self.add_output("error", f"Table cible '{target}' introuvable", self.current_line)
            return

        self.stats.set_dataframe(df)

        try:
            result = self.stats.summary()

            self.add_output("analysis", {
                "type": "summary",
                "target": target,
                "results": result
            }, self.current_line)

            self.add_output("success", f"Résumé calculé pour '{target}'", self.current_line)

        except Exception as e:
            self.add_output("error", f"Erreur lors du calcul du résumé: {str(e)}", self.current_line)

    # ========== COMMANDE VISUALIZE ==========

    def _get_param(self, params: Dict, keys: List[str], default=None):
        """Récupère un paramètre en essayant différentes clés (majuscules/minuscules)"""
        for key in keys:
            if key in params:
                return params[key]

            lower_key = key.lower()
            if lower_key in params:
                return params[lower_key]

            upper_key = key.upper()
            if upper_key in params:
                return params[upper_key]
        return default

    def _convert_to_int(self, value, default):
        """Convertit une valeur en entier si possible"""
        if value is None:
            return default
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

    def _convert_to_float(self, value, default):
        """Convertit une valeur en float si possible"""
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        return default

    def _convert_to_bool(self, value, default):
        """Convertit une valeur en booléen"""
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'on']
        return bool(value)

    def evaluate_visualize(self, command: Dict[str, Any]):
        """Évalue une commande VISUALIZE pour générer des graphiques"""
        chart_type = command.get("chart_type")
        target = command.get("target")
        params = command.get("params", {})
        options = command.get("options", {})

        self.add_output("info", f"Génération du graphique {chart_type} à partir de '{target}'...", self.current_line)

        # Récupérer le DataFrame
        df = None
        if target in self.transformed_tables:
            df = self.transformed_tables[target]
        elif target in self.current_tables:
            df = self.current_tables[target]
        elif target in self.variables:
            df = self.variables[target]
        else:
            self.add_output("error", f"Table cible '{target}' introuvable", self.current_line)
            return

        if df is None or len(df) == 0:
            self.add_output("error", f"La table '{target}' est vide", self.current_line)
            return

        svg_content = ""

        # ===== HISTOGRAMME =====
        if chart_type == "histogram":
            # Récupérer la colonne
            column = self._get_param(params, ["COLUMN", "column", "X", "x"])
            if not column:
                self.add_output("error", "Paramètre 'column' requis pour HISTOGRAM", self.current_line)
                return

            if column not in df.columns:
                self.add_output("error", f"Colonne '{column}' non trouvée. Colonnes disponibles: {list(df.columns)}", self.current_line)
                return

            # Récupérer les paramètres
            data = [x for x in df[column] if x is not None]  # Filtrer None pour l'histogramme
            bins = self._convert_to_int(self._get_param(params, ["BINS", "bins"]), 10)
            title = self._get_param(params, ["TITLE", "title"], f"Histogramme de {column}")
            xlabel = self._get_param(params, ["XLABEL", "xlabel"], column)
            ylabel = self._get_param(params, ["YLABEL", "ylabel"], "Fréquence")
            color = self._get_param(params, ["COLOR", "color"], "#4ECDC4")
            density = self._convert_to_bool(self._get_param(params, ["DENSITY", "density"]), False)

            # Générer le SVG
            svg_content = self.viz.histogram(
                data,
                bins=bins,
                title=title,
                x_label=xlabel,
                y_label=ylabel,
                color=color,
                density=density
            )

        # ===== SCATTER PLOT =====
        elif chart_type == "scatter":
            x_col = self._get_param(params, ["X", "x"])
            y_col = self._get_param(params, ["Y", "y"])

            if not x_col or not y_col:
                self.add_output("error", "Paramètres 'x' et 'y' requis pour SCATTER", self.current_line)
                return

            if x_col not in df.columns:
                self.add_output("error", f"Colonne X '{x_col}' non trouvée", self.current_line)
                return
            if y_col not in df.columns:
                self.add_output("error", f"Colonne Y '{y_col}' non trouvée", self.current_line)
                return

            # Filtrer les paires où une des valeurs est None
            x_data = df[x_col]
            y_data = df[y_col]
            pairs = [(x, y) for x, y in zip(x_data, y_data) if x is not None and y is not None]
            if not pairs:
                self.add_output("error", "Pas de paires de valeurs valides pour SCATTER", self.current_line)
                return

            x_filtered, y_filtered = zip(*pairs) if pairs else ([], [])

            title = self._get_param(params, ["TITLE", "title"], f"{y_col} vs {x_col}")
            xlabel = self._get_param(params, ["XLABEL", "xlabel"], x_col)
            ylabel = self._get_param(params, ["YLABEL", "ylabel"], y_col)
            color = self._get_param(params, ["COLOR", "color"], "#FF6B6B")
            size = self._convert_to_int(self._get_param(params, ["SIZE", "size"]), 4)
            alpha = self._convert_to_float(self._get_param(params, ["ALPHA", "alpha"]), 1.0)

            svg_content = self.viz.scatter(
                list(x_filtered), list(y_filtered),
                title=title,
                x_label=xlabel,
                y_label=ylabel,
                color=color,
                size=size,
                alpha=alpha
            )

        # ===== LINE CHART =====
        elif chart_type == "line_chart":
            x_col = self._get_param(params, ["X", "x"])
            y_cols = self._get_param(params, ["Y", "y"])

            if not x_col or not y_cols:
                self.add_output("error", "Paramètres 'x' et 'y' requis pour LINE_CHART", self.current_line)
                return

            if x_col not in df.columns:
                self.add_output("error", f"Colonne X '{x_col}' non trouvée", self.current_line)
                return

            # Convertir y_cols en liste si c'est une chaîne
            if isinstance(y_cols, str):
                y_cols = [y_cols]

            y_data = {}
            x_vals = df[x_col]

            for y_col in y_cols:
                if y_col in df.columns:
                    # Filtrer les paires où x ou y est None
                    y_vals = df[y_col]
                    pairs = [(x, y) for x, y in zip(x_vals, y_vals) if x is not None and y is not None]
                    if pairs:
                        x_filtered, y_filtered = zip(*pairs)
                        y_data[y_col] = list(y_filtered)
                    else:
                        self.add_output("warning", f"Pas de valeurs valides pour {y_col}", self.current_line)
                else:
                    self.add_output("warning", f"Colonne Y '{y_col}' ignorée (non trouvée)", self.current_line)

            if not y_data:
                self.add_output("error", "Aucune colonne Y valide trouvée", self.current_line)
                return

            # Utiliser les x filtrés du premier y_col (ils devraient être cohérents)
            first_y = list(y_data.keys())[0]
            x_filtered = [x for x, y in zip(x_vals, df[first_y]) if x is not None and y is not None]

            title = self._get_param(params, ["TITLE", "title"], "Graphique en lignes")
            xlabel = self._get_param(params, ["XLABEL", "xlabel"], x_col)
            ylabel = self._get_param(params, ["YLABEL", "ylabel"], "Valeurs")
            colors = self._get_param(params, ["COLORS", "colors"])
            markers = self._convert_to_bool(self._get_param(params, ["MARKERS", "markers"]), True)

            svg_content = self.viz.line_chart(
                x_filtered, y_data,
                title=title,
                x_label=xlabel,
                y_label=ylabel,
                colors=colors,
                markers=markers
            )

        # ===== BOX PLOT =====
        elif chart_type == "box_plot":
            # Récupérer les colonnes
            columns = self._get_param(params, ["COLUMNS", "columns"])
            if not columns:
                column = self._get_param(params, ["COLUMN", "column"])
                if column:
                    columns = [column]
                else:
                    # Par défaut, prendre les 3 premières colonnes numériques
                    columns = df.columns[:3]

            # Filtrer les colonnes qui existent
            valid_columns = [col for col in columns if col in df.columns]
            if not valid_columns:
                self.add_output("error", "Aucune colonne valide trouvée pour BOX_PLOT", self.current_line)
                return

            data_dict = {}
            for col in valid_columns:
                # Filtrer les None pour le box plot
                data_dict[col] = [x for x in df[col] if x is not None]

            title = self._get_param(params, ["TITLE", "title"], "Boîte à moustaches")
            xlabel = self._get_param(params, ["XLABEL", "xlabel"], "")
            ylabel = self._get_param(params, ["YLABEL", "ylabel"], "Valeurs")

            svg_content = self.viz.boxplot(
                data_dict,
                title=title,
                x_label=xlabel,
                y_label=ylabel
            )

        # ===== BAR CHART =====
        elif chart_type == "bar_chart":
            x_col = self._get_param(params, ["X", "x"])
            y_col = self._get_param(params, ["Y", "y"])

            if not x_col or not y_col:
                self.add_output("error", "Paramètres 'x' et 'y' requis pour BAR_CHART", self.current_line)
                return

            if x_col not in df.columns:
                self.add_output("error", f"Colonne X '{x_col}' non trouvée", self.current_line)
                return
            if y_col not in df.columns:
                self.add_output("error", f"Colonne Y '{y_col}' non trouvée", self.current_line)
                return

            # Agrégation par catégorie (ignorer les None)
            categories = {}
            for x_val, y_val in zip(df[x_col], df[y_col]):
                if x_val is not None and y_val is not None:
                    if x_val not in categories:
                        categories[x_val] = []
                    categories[x_val].append(y_val)

            if not categories:
                self.add_output("error", "Pas de données valides pour BAR_CHART", self.current_line)
                return

            cat_list = list(categories.keys())
            values = [sum(vals)/len(vals) for vals in categories.values()]  # Moyenne par catégorie

            title = self._get_param(params, ["TITLE", "title"], f"{y_col} par {x_col}")
            xlabel = self._get_param(params, ["XLABEL", "xlabel"], x_col)
            ylabel = self._get_param(params, ["YLABEL", "ylabel"], y_col)
            colors = self._get_param(params, ["COLORS", "colors"])
            stacked = self._convert_to_bool(self._get_param(params, ["STACKED", "stacked"]), False)

            svg_content = self.viz.bar_chart(
                cat_list, values,
                title=title,
                x_label=xlabel,
                y_label=ylabel,
                colors=colors,
                stacked=stacked
            )

        # ===== HEATMAP =====
        elif chart_type == "heatmap":
            columns = self._get_param(params, ["COLUMNS", "columns"])
            if not columns:
                # Par défaut, toutes les colonnes numériques
                columns = [col for col in df.columns if any(isinstance(val, (int, float)) for val in df[col] if val is not None)]

            if len(columns) < 2:
                self.add_output("error", "Au moins 2 colonnes nécessaires pour HEATMAP", self.current_line)
                return

            # Créer une matrice de corrélation
            valid_columns = [col for col in columns if col in df.columns]

            corr_matrix = []
            for col1 in valid_columns:
                row = []
                for col2 in valid_columns:
                    # Pour la corrélation, on a besoin de paires
                    pairs = [(x, y) for x, y in zip(df[col1], df[col2]) if x is not None and y is not None]
                    if len(pairs) > 1:
                        x_vals, y_vals = zip(*pairs)
                        corr = self.stats.correlation(list(x_vals), list(y_vals))
                        row.append(corr if not math.isnan(corr) else 0)
                    else:
                        row.append(0)
                corr_matrix.append(row)

            title = self._get_param(params, ["TITLE", "title"], "Matrice de corrélation")
            xlabel = self._get_param(params, ["XLABEL", "xlabel"], "")
            ylabel = self._get_param(params, ["YLABEL", "ylabel"], "")
            cmap = self._get_param(params, ["CMAP", "cmap"], "viridis")

            svg_content = self.viz.heatmap(
                corr_matrix,
                row_labels=valid_columns,
                col_labels=valid_columns,
                title=title,
                x_label=xlabel,
                y_label=ylabel,
                cmap=cmap
            )

        # ===== QQ PLOT =====
        elif chart_type == "qq_plot":
            column = self._get_param(params, ["COLUMN", "column"])
            if not column:
                self.add_output("error", "Paramètre 'column' requis pour QQ_PLOT", self.current_line)
                return

            if column not in df.columns:
                self.add_output("error", f"Colonne '{column}' non trouvée", self.current_line)
                return

            # Filtrer les None
            data = [x for x in df[column] if x is not None]
            if not data:
                self.add_output("error", f"Pas de données valides dans la colonne '{column}'", self.current_line)
                return

            title = self._get_param(params, ["TITLE", "title"], f"Q-Q Plot de {column}")
            xlabel = self._get_param(params, ["XLABEL", "xlabel"], "Quantiles théoriques")
            ylabel = self._get_param(params, ["YLABEL", "ylabel"], "Quantiles observés")
            dist = self._get_param(params, ["DIST", "dist"], "normal")

            svg_content = self.viz.qq_plot(
                data,
                dist=dist,
                title=title,
                x_label=xlabel,
                y_label=ylabel
            )

        # ===== ACF PLOT =====
        elif chart_type == "acf_plot":
            column = self._get_param(params, ["COLUMN", "column"])
            if not column:
                self.add_output("error", "Paramètre 'column' requis pour ACF_PLOT", self.current_line)
                return

            if column not in df.columns:
                self.add_output("error", f"Colonne '{column}' non trouvée", self.current_line)
                return

            # Filtrer les None
            data = [x for x in df[column] if x is not None]
            if len(data) < 2:
                self.add_output("error", f"Pas assez de données pour ACF (minimum 2 points)", self.current_line)
                return

            nlags = self._convert_to_int(self._get_param(params, ["NLAGS", "nlags"]), min(20, len(data)-1))
            title = self._get_param(params, ["TITLE", "title"], "Autocorrélation")
            xlabel = self._get_param(params, ["XLABEL", "xlabel"], "Décalage")
            ylabel = self._get_param(params, ["YLABEL", "ylabel"], "Autocorrélation")

            svg_content = self.viz.acf_plot(
                data,
                nlags=nlags,
                title=title,
                x_label=xlabel,
                y_label=ylabel
            )

        # ===== PIE CHART =====
        elif chart_type == "pie_chart":
            values_col = self._get_param(params, ["VALUES", "values"])
            labels_col = self._get_param(params, ["LABELS", "labels"])

            if not values_col or not labels_col:
                self.add_output("error", "Paramètres 'values' et 'labels' requis pour PIE_CHART", self.current_line)
                return

            if values_col not in df.columns:
                self.add_output("error", f"Colonne values '{values_col}' non trouvée", self.current_line)
                return
            if labels_col not in df.columns:
                self.add_output("error", f"Colonne labels '{labels_col}' non trouvée", self.current_line)
                return

            # Agrégation par label (ignorer les None)
            label_values = {}
            for label, val in zip(df[labels_col], df[values_col]):
                if label is not None and val is not None:
                    if label not in label_values:
                        label_values[label] = []
                    label_values[label].append(val)

            if not label_values:
                self.add_output("error", "Pas de données valides pour PIE_CHART", self.current_line)
                return

            labels = list(label_values.keys())
            values = [sum(vals)/len(vals) for vals in label_values.values()]  # Moyenne par label

            title = self._get_param(params, ["TITLE", "title"], "Diagramme circulaire")

            svg_content = self.viz.pie_chart(
                labels=labels,
                values=values,
                title=title
            )

        else:
            self.add_output("error", f"Type de graphique non supporté: {chart_type}", self.current_line)
            return

        # Ajouter le SVG aux résultats si généré
        if svg_content:
            # Sauvegarder si demandé
            save_path = self._get_param(options, ["SAVE", "save"])
            if save_path:
                try:
                    with open(save_path, 'w', encoding='utf-8') as f:
                        f.write(svg_content)
                    self.add_output("success", f"Graphique sauvegardé dans {save_path}", self.current_line)
                except Exception as e:
                    self.add_output("error", f"Erreur lors de la sauvegarde: {e}", self.current_line)

            # Ajouter le message SVG
            self.add_output("svg", {
                "content": svg_content,
                "title": title,
                "width": self._convert_to_int(self._get_param(params, ["WIDTH", "width"]), 800),
                "height": self._convert_to_int(self._get_param(params, ["HEIGHT", "height"]), 600)
            })

            self.add_output("success", f"Graphique {chart_type} généré avec succès", self.current_line)
        else:
            self.add_output("error", f"Échec de la génération du graphique {chart_type}", self.current_line)

    # ========== COMMANDES ANALYZE, IF, FOR ==========

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
        elif target in self.variables:
            df = self.variables[target]
        else:
            self.add_output("error", f"Table cible '{target}' introuvable", self.current_line)
            return

        results = {}

        for op in operations:
            if isinstance(op, dict):
                expression = op.get("expression")
                variable = op.get("variable")
                new_df = df.copy()

                result = self.evaluate_expression(expression, new_df)
                if isinstance(result, (tuple, list)):
                    result = result[0] if result else None

                if variable:
                    results[variable] = result
                    self.variables[variable] = result
                else:
                    name = f"Result_{len(results)}"
                    results[name] = result

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
                row_dict = SimpleDataFrame.from_records([row_dict])
                self.variables[variable] = row_dict
                self.add_output("info", f"Itération {idx+1} sur {collection_name}", self.current_line)

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

    # ========== ÉVALUATION D'EXPRESSIONS ==========

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

                lower_val = lower[0] if isinstance(lower, list) and lower else lower
                upper_val = upper[0] if isinstance(upper, list) and upper else upper

                result = []
                for l in left:
                    if l is None or lower_val is None or upper_val is None:
                        result.append(False)
                    else:
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
                    return [bool(x) if x is not None else False for x in df[col_name]]
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
                except (ValueError, TypeError):
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
                        if l is None or r is None:
                            result.append(None)
                        else:
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

        # Fonctions d'agrégation existantes
        if name == "SUM":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [x for x in col if x is not None and isinstance(to_numeric(x), (int, float))]
                    valid_num = [to_numeric(x) for x in valid]
                    return sum(valid_num) if valid_num else 0
                return col
        elif name == "AVG" or name == "MEAN":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [x for x in col if x is not None and isinstance(to_numeric(x), (int, float))]
                    valid_num = [to_numeric(x) for x in valid]
                    return sum(valid_num) / len(valid_num) if valid_num else None
                return col
        elif name == "MEDIAN":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [x for x in col if x is not None and isinstance(to_numeric(x), (int, float))]
                    valid_num = [to_numeric(x) for x in valid]
                    if valid_num:
                        sorted_vals = sorted(valid_num)
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
                    valid = [x for x in col if x is not None and isinstance(to_numeric(x), (int, float))]
                    valid_num = [to_numeric(x) for x in valid]
                    return min(valid_num) if valid_num else None
                return col
        elif name == "MAX":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [x for x in col if x is not None and isinstance(to_numeric(x), (int, float))]
                    valid_num = [to_numeric(x) for x in valid]
                    return max(valid_num) if valid_num else None
                return col
        elif name == "STD":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [x for x in col if x is not None and isinstance(to_numeric(x), (int, float))]
                    valid_num = [to_numeric(x) for x in valid]
                    if len(valid_num) > 1:
                        mean = sum(valid_num) / len(valid_num)
                        variance = sum((x - mean) ** 2 for x in valid_num) / (len(valid_num) - 1)
                        return math.sqrt(variance)
                return 0
        elif name == "VAR":
            if len(evaluated_args) > 0:
                col = evaluated_args[0]
                if isinstance(col, list):
                    valid = [x for x in col if x is not None and isinstance(to_numeric(x), (int, float))]
                    valid_num = [to_numeric(x) for x in valid]
                    if len(valid_num) > 1:
                        mean = sum(valid_num) / len(valid_num)
                        return sum((x - mean) ** 2 for x in valid_num) / (len(valid_num) - 1)
                return 0
        elif name == "CORR":
            if len(evaluated_args) >= 2:
                col1 = evaluated_args[0]
                col2 = evaluated_args[1]
                if isinstance(col1, list) and isinstance(col2, list):
                    pairs = []
                    for x, y in zip(col1, col2):
                        if x is not None and y is not None:
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
                    return [math.log(v) if v is not None and v > 0 else float('-inf') for v in val]
                return math.log(val) if val is not None and val > 0 else float('-inf')
        elif name == "EXP":
            if len(evaluated_args) > 0:
                val = evaluated_args[0]
                if isinstance(val, list):
                    return [math.exp(v) if v is not None else float('nan') for v in val]
                return math.exp(val) if val is not None else float('nan')
        elif name == "SQRT":
            if len(evaluated_args) > 0:
                val = evaluated_args[0]
                if isinstance(val, list):
                    return [math.sqrt(v) if v is not None and v >= 0 else float('nan') for v in val]
                return math.sqrt(val) if val is not None and val >= 0 else float('nan')
        elif name == "ABS":
            if len(evaluated_args) > 0:
                val = evaluated_args[0]
                if isinstance(val, list):
                    return [abs(v) if v is not None else None for v in val]
                return abs(val) if val is not None else None
        elif name == "ROUND":
            if len(evaluated_args) >= 1:
                val = evaluated_args[0]
                decimals = evaluated_args[1] if len(evaluated_args) > 1 else 0
                if isinstance(val, list):
                    return [round(v, decimals) if v is not None else None for v in val]
                return round(val, decimals) if val is not None else None

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
                        if left in self.variables:
                            left = self.variables[left]
                        left = float(left) if '.' in left else int(left)
                    except (ValueError, TypeError):
                        pass
                if isinstance(right, str):
                    try:
                        if right in self.variables:
                            right = self.variables[right]
                        right = float(right) if '.' in right else int(right)
                    except (ValueError, TypeError):
                        pass

                try:
                    if left is None or right is None:
                        return False
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
                except (TypeError, ValueError):
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
                valid = [x for x in col if x is not None and isinstance(to_numeric(x), (int, float))]
                valid_num = [to_numeric(x) for x in valid]
                return sum(valid_num) if valid_num else None
        elif name == "AVG" or name == "MEAN":
            col = evaluated_args[0] if evaluated_args else None
            if col and isinstance(col, list):
                valid = [x for x in col if x is not None and isinstance(to_numeric(x), (int, float))]
                valid_num = [to_numeric(x) for x in valid]
                return sum(valid_num) / len(valid_num) if valid_num else None
        elif name == "MIN":
            col = evaluated_args[0] if evaluated_args else None
            if col and isinstance(col, list):
                valid = [x for x in col if x is not None and isinstance(to_numeric(x), (int, float))]
                valid_num = [to_numeric(x) for x in valid]
                return min(valid_num) if valid_num else None
        elif name == "MAX":
            col = evaluated_args[0] if evaluated_args else None
            if col and isinstance(col, list):
                valid = [x for x in col if x is not None and isinstance(to_numeric(x), (int, float))]
                valid_num = [to_numeric(x) for x in valid]
                return max(valid_num) if valid_num else None
        elif name == "CORR":
            if len(evaluated_args) >= 2:
                col1 = evaluated_args[0]
                col2 = evaluated_args[1]
                if isinstance(col1, list) and isinstance(col2, list):
                    pairs = []
                    for x, y in zip(col1, col2):
                        if x is not None and y is not None:
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

    # ========== FONCTIONS UTILITAIRES ==========

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
        if isinstance(condition, dict):
            left_col = condition.get("left_on")
            right_col = condition.get("right_on")
            return left_col, right_col
        return None, None

    def do_values(self, df, col_name, indices, keep_none=False):
        """Récupère les valeurs d'une colonne pour des indices donnés

        Args:
            df: DataFrame source
            col_name: Nom de la colonne
            indices: Liste des indices à récupérer
            keep_none: Si True, garde les None, sinon les remplace par 0 pour les calculs
        """
        values = [df[col_name][i] for i in indices]

        if keep_none:
            return values

        numeric_values = []
        for v in values:
            if v is not None:
                if isinstance(v, (int, float)):
                    numeric_values.append(v)
                else:
                    num_v = to_numeric(v)
                    if isinstance(num_v, (int, float)):
                        numeric_values.append(num_v)
                    else:
                        numeric_values.append(0)  # Valeur non-numérique → 0
            else:
                numeric_values.append(0)  # None → 0 pour les calculs
        return numeric_values

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
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

        # Types de fonctions existants
        self.function_types = [
            'SUM', 'AVG', 'MEAN', 'MEDIAN', 'MODE', 'COUNT', 'MIN', 'MAX',
            'STD', 'VAR', 'SKEW', 'KURT', 'QUANTILE', 'PERCENTILE', 'CORR',
            'COV', 'CROSSTAB', 'FREQ', 'TOP', 'ENTROPY', 'RANK', 'ROW_NUMBER',
            
            'LOG', 'EXP', 'SQRT', 'ABS', 'ROUND', 'FLOOR', 'CEIL',
            'SIN', 'COS', 'TAN', 'ASIN', 'ACOS', 'ATAN', 'POWER', 'MOD',
            
            'WORD_COUNT', 'SENTENCE_COUNT', 'TOP_WORDS', 'TOP_PHRASES',
            'SENTIMENT', 'SUBJECTIVITY', 'LDA', 'KEYPHRASES', 'NER',
            'COSINE_SIMILARITY',
            
            'T_TEST', 'ANOVA', 'CHI2', 'MANN_WHITNEY', 'KRUSKAL',
            'KS_TEST', 'ADF_TEST', 'KPSS_TEST', 'ACF', 'PACF',
            'DECOMPOSE', 'CUSUM', 'SEASONAL_STRENGTH', 'TREND', 'EXPONENTIAL_SMOOTHING',
            
            # NOUVELLES FONCTIONS STATISTIQUES
            'MOMENT', 'GINI', 'SKEWNESS', 'KURTOSIS', 'COVARIANCE',
            'F_TEST', 'SHAPIRO', 'ANDERSON',
            
            # FONCTIONS DE DISTANCE
            'EUCLIDEAN', 'MANHATTAN', 'COSINE', 'JACCARD',
            
            # FONCTIONS DE SÉRIES TEMPORELLES
            'LAG', 'DIFF', 'PCT_CHANGE', 'MOVING_AVG', 'EWMA', 'AUTOCORR'
        ]

    def peek(self, offset=0):
        if 0 <= self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def consume(self, token_type=None):
        token = self.peek()
        if not token:
            self.error(f"Expected {token_type} but found end of file", None)
        if token_type and token["type"] != token_type:
            self.error(f"Expected {token_type} but found {token['type']} ({token['value']})", token)
        self.pos += 1
        return token

    def consume_any(self, token_types=None):
        token = self.peek()
        if not token:
            self.error(f"Expected one of {token_types} but found end of file", None)
        if token_types and token["type"] not in token_types:
            self.error(f"Expected one of {token_types} but found {token['type']} ({token['value']})", token)
        self.pos += 1
        return token

    def error(self, msg, token=None):
        if token is None:
            token = self.peek(-1) if self.pos > 1 else (self.peek() or {'line': 'EOF', 'col': 'EOF'})

        line = token.get('line', '?')
        col = token.get('col', '?')
        error_msg = f"Parsing error at line:{line}, col:{col}, msg:{msg}"
        self.errors.append(error_msg)
        raise Exception(error_msg)

    def parse(self):
        ast = {"type": "dsl_program", "commands": []}

        while self.pos < len(self.tokens):
            token = self.peek()
            if not token:
                break

            if token["type"] == "LOAD":
                ast["commands"].append(self.parse_load())
            elif token["type"] == "TRANSFORM":
                ast["commands"].append(self.parse_transform())
            elif token["type"] in ["ANALYZE", "ANALYSE"]:
                ast["commands"].append(self.parse_analyze())
            elif token["type"] in ['VIZ','VISUALIZE']:
                ast["commands"].append(self.parse_visualize())
            elif token["type"] == "CLEAN":
                ast["commands"].append(self.parse_clean())
            elif token["type"] == "STATS":
                ast["commands"].append(self.parse_stats())
            elif token["type"] == "DESCRIBE":
                ast["commands"].append(self.parse_describe())
            elif token["type"] == "DESCRIBE_ALL":
                ast["commands"].append(self.parse_describe_all())
            elif token["type"] == "SUMMARY":
                ast["commands"].append(self.parse_summary())
            elif token["type"] == "IF":
                ast["commands"].append(self.parse_if())
            elif token["type"] == "FOR":
                ast["commands"].append(self.parse_for())
            elif token["type"] == "NEWLINE":
                self.consume("NEWLINE")
                continue
            else:
                self.error(f"Expected top-level command but found {token['type']}({token['value']})", token)

        return ast, self.errors

    # ========== COMMANDES EXISTANTES ==========

    def parse_load(self):
        node = {"type": "load", "properties": {}}
        self.consume("LOAD")

        if self.peek() and self.peek()["type"] == "LPAREN":
            self.consume("LPAREN")
            node["properties"]["name"] = self.consume("IDENTIFIER")["value"]
            self.consume("RPAREN")
        else:
            node["properties"]["name"] = self.consume("IDENTIFIER")["value"]

        if self.peek() and self.peek()["type"] == "FROM":
            self.consume("FROM")
            node["properties"]["source"] = self.parse_string_or_identifier()

        if self.peek() and self.peek()["type"] == "WITH":
            node["properties"]["options"] = self.parse_with_options()

        if self.peek() and self.peek()["type"] in ["AS", "SHIFT_RIGHT"]:
            self.consume(self.peek()["type"])
            node["properties"]["alias"] = self.consume("IDENTIFIER")["value"]

        return node

    def parse_string_or_identifier(self):
        token = self.peek()
        if token["type"] == "STRING":
            return self.strip_quotes(self.consume("STRING")["value"])
        else:
            return self.consume("IDENTIFIER")["value"]

    def parse_transform(self):
        node = {"type": "transform", "properties": {}, "contents": []}
        self.consume("TRANSFORM")
        node["properties"]["name"] = self.consume("IDENTIFIER")["value"]

        block = False
        if self.peek() and self.peek()["type"] == "LBRACKET":
            block = True
            self.consume("LBRACKET")

        node["contents"] = self.parse_transform_content(block)

        if block:
            self.consume("RBRACKET")

        if self.peek() and self.peek()["type"] in ["AS", "SHIFT_RIGHT"]:
            self.consume(self.peek()["type"])
            node["properties"]["alias"] = self.consume("IDENTIFIER")["value"]

        return node

    def parse_transform_content(self, block):
        contents = []

        if not block:
            token_type = self.peek()["type"]
            if token_type == "SELECT":
                contents.append(self.parse_select())
            elif token_type == "DROP":
                contents.append(self.parse_drop())
            elif token_type == "FILTER":
                contents.append(self.parse_filter())
            elif token_type == "CREATE_FEATURE":
                contents.append(self.parse_create_feature())
            elif token_type == "GROUP_BY":
                contents.append(self.parse_group_by())
            elif token_type == "AGG":
                contents.append(self.parse_agg())
            elif token_type == "JOIN":
                contents.append(self.parse_join())
            elif token_type == "HAVING":
                contents.append(self.parse_having())
            # NOUVELLES OPÉRATIONS DE NETTOYAGE
            elif token_type == "DROP_NA":
                contents.append(self.parse_drop_na())
            elif token_type == "FILL_NA":
                contents.append(self.parse_fill_na())
            elif token_type == "REPLACE":
                contents.append(self.parse_replace())
            elif token_type == "CLIP":
                contents.append(self.parse_clip())
            elif token_type == "REMOVE_OUTLIERS":
                contents.append(self.parse_remove_outliers())
            elif token_type == "STANDARDIZE":
                contents.append(self.parse_standardize())
            elif token_type == "MIN_MAX_SCALE":
                contents.append(self.parse_min_max_scale())
            elif token_type == "ONE_HOT_ENCODE":
                contents.append(self.parse_one_hot_encode())
            elif token_type == "LABEL_ENCODE":
                contents.append(self.parse_label_encode())
            return contents

        if self.peek() and self.peek()["type"] in ["SELECT", "DROP", "FILTER", "CREATE_FEATURE",
                                                    "GROUP_BY", "AGG", "JOIN", "HAVING",
                                                    "DROP_NA", "FILL_NA", "REPLACE", "CLIP",
                                                    "REMOVE_OUTLIERS", "STANDARDIZE", "MIN_MAX_SCALE",
                                                    "ONE_HOT_ENCODE", "LABEL_ENCODE"]:
            contents.append(self.parse_current_operation())

        while self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            if self.peek() and self.peek()["type"] in ["SELECT", "DROP", "FILTER", "CREATE_FEATURE",
                                                        "GROUP_BY", "AGG", "JOIN", "HAVING",
                                                        "DROP_NA", "FILL_NA", "REPLACE", "CLIP",
                                                        "REMOVE_OUTLIERS", "STANDARDIZE", "MIN_MAX_SCALE",
                                                        "ONE_HOT_ENCODE", "LABEL_ENCODE"]:
                contents.append(self.parse_current_operation())

        return contents

    def parse_current_operation(self):
        token_type = self.peek()["type"]
        if token_type == "SELECT":
            return self.parse_select()
        elif token_type == "DROP":
            return self.parse_drop()
        elif token_type == "FILTER":
            return self.parse_filter()
        elif token_type == "CREATE_FEATURE":
            return self.parse_create_feature()
        elif token_type == "GROUP_BY":
            return self.parse_group_by()
        elif token_type == "AGG":
            return self.parse_agg()
        elif token_type == "JOIN":
            return self.parse_join()
        elif token_type == "HAVING":
            return self.parse_having()
        # NOUVELLES OPÉRATIONS
        elif token_type == "DROP_NA":
            return self.parse_drop_na()
        elif token_type == "FILL_NA":
            return self.parse_fill_na()
        elif token_type == "REPLACE":
            return self.parse_replace()
        elif token_type == "CLIP":
            return self.parse_clip()
        elif token_type == "REMOVE_OUTLIERS":
            return self.parse_remove_outliers()
        elif token_type == "STANDARDIZE":
            return self.parse_standardize()
        elif token_type == "MIN_MAX_SCALE":
            return self.parse_min_max_scale()
        elif token_type == "ONE_HOT_ENCODE":
            return self.parse_one_hot_encode()
        elif token_type == "LABEL_ENCODE":
            return self.parse_label_encode()
        else:
            self.error(f"Unexpected operation: {token_type}", self.peek())

    # ========== COMMANDES DE NETTOYAGE ==========

    def parse_drop_na(self):
        """Parse drop_na(columns=['col1','col2'], how='any', thresh=5)"""
        node = {"type": "drop_na", "params": {}}
        self.consume("DROP_NA")
        self.consume("LPAREN")

        param_names = ['COLUMNS','HOW','THRESH','SUBSET']

        while self.peek() and self.peek()["type"] != "RPAREN":
            param_name = self.consume_any(param_names)["value"]
            self.consume("ASSIGN")

            if param_name == "columns":
                node["params"]["columns"] = self.parse_list()
            elif param_name == "how":
                node["params"]["how"] = self.consume_any(["ANY", "ALL"])["value"]
            elif param_name == "thresh":
                node["params"]["thresh"] = int(self.consume("NUMBER")["value"])
            elif param_name == "subset":
                node["params"]["columns"] = self.parse_list()

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        self.consume("RPAREN")
        return node

    def parse_fill_na(self):
        """Parse fill_na(value=0, method='ffill', columns=['col1'])"""
        node = {"type": "fill_na", "params": {}}
        self.consume("FILL_NA")
        self.consume("LPAREN")

        param_names = ['VALUE','METHOD','COLUMNS']

        has_value = False
        has_method = False

        while self.peek() and self.peek()["type"] != "RPAREN":
            param_name = self.consume_any(param_names)["value"]
            self.consume("ASSIGN")

            if param_name == "value":
                has_value = True
                node["params"]["value"] = self.parse_literal()["value"]
            elif param_name == "method":
                has_method = True
                node["params"]["method"] = self.consume_any(["FFILL", "BFILL"])["value"]
            elif param_name == "columns":
                node["params"]["columns"] = self.parse_list()

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        if has_value and has_method:
           self.error("Cannot specify both 'value' and 'method' in fill_na", self.peek(-1))


        self.consume("RPAREN")
        return node

    def parse_replace(self):
        """Parse replace(to_replace=0, value=1, columns=['col1'])"""
        node = {"type": "replace", "params": {}}
        self.consume("REPLACE")
        self.consume("LPAREN")

        para_names = ['TO_REPLACE','VALUE','COLUMNS']

        while self.peek() and self.peek()["type"] != "RPAREN":
            param_name = self.consume_any(para_names)["value"]
            self.consume("ASSIGN")

            if param_name == "to_replace":
                node["params"]["to_replace"] = self.parse_literal()["value"]
            elif param_name == "value":
                node["params"]["value"] = self.parse_literal()["value"]
            elif param_name == "columns":
                node["params"]["columns"] = self.parse_list()

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        self.consume("RPAREN")
        return node

    def parse_clip(self):
        """Parse clip(lower=0, upper=100, columns=['col1'])"""
        node = {"type": "clip", "params": {}}
        self.consume("CLIP")
        self.consume("LPAREN")

        param_names = ['LOWER','UPPER','COLUMNS']

        while self.peek() and self.peek()["type"] != "RPAREN":
            param_name = self.consume_any(param_names)["value"]
            self.consume("ASSIGN")

            if param_name == "lower":
                node["params"]["lower"] = float(self.consume("NUMBER")["value"])
            elif param_name == "upper":
                node["params"]["upper"] = float(self.consume("NUMBER")["value"])
            elif param_name == "columns":
                node["params"]["columns"] = self.parse_list()

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        self.consume("RPAREN")
        return node

    def parse_remove_outliers(self):
        """Parse remove_outliers(column='col1', factor=1.5)"""
        node = {"type": "remove_outliers", "params": {}}
        self.consume("REMOVE_OUTLIERS")
        self.consume("LPAREN")

        param_names = ['COLUMN','FACTOR']

        while self.peek() and self.peek()["type"] != "RPAREN":
            param_name = self.consume_any(param_names)["value"]
            self.consume("ASSIGN")

            if param_name == "column":
                node["params"]["column"] = self.consume("IDENTIFIER")["value"]
            elif param_name == "factor":
                node["params"]["factor"] = float(self.consume("NUMBER")["value"])

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        self.consume("RPAREN")
        return node

    def parse_standardize(self):
        """Parse standardize(columns=['col1','col2'])"""
        node = {"type": "standardize", "params": {}}
        self.consume("STANDARDIZE")
        self.consume("LPAREN")

        while self.peek() and self.peek()["type"] != "RPAREN":
            param_name = self.consume('COLUMNS')["value"]
            self.consume("ASSIGN")

            if param_name == "columns":
                node["params"]["columns"] = self.parse_list()

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        self.consume("RPAREN")
        return node

    def parse_min_max_scale(self):
        """Parse min_max_scale(columns=['col1','col2'], feature_range=(0,1))"""
        node = {"type": "min_max_scale", "params": {}}
        self.consume("MIN_MAX_SCALE")
        self.consume("LPAREN")

        param_names = ['COLUMNS','FEATURE_RANGE']

        while self.peek() and self.peek()["type"] != "RPAREN":
            param_name = self.consume_any(param_names)["value"]
            self.consume("ASSIGN")

            if param_name == "columns":
                node["params"]["columns"] = self.parse_list()
            elif param_name == "feature_range":
                self.consume("LPAREN")
                min_val = float(self.consume("NUMBER")["value"])
                self.consume("COMMA")
                max_val = float(self.consume("NUMBER")["value"])
                self.consume("RPAREN")
                node["params"]["feature_range"] = (min_val, max_val)

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        self.consume("RPAREN")
        return node

    def parse_one_hot_encode(self):
        """Parse one_hot_encode(column='col1', prefix='cat', drop_first=False)"""
        node = {"type": "one_hot_encode", "params": {}}
        self.consume("ONE_HOT_ENCODE")
        self.consume("LPAREN")

        param_names = ['COLUMN','PREFIX','DROP_FIRST']

        while self.peek() and self.peek()["type"] != "RPAREN":
            param_name = self.consume_any(param_names)["value"]
            self.consume("ASSIGN")

            if param_name == "column":
                node["params"]["column"] = self.consume("IDENTIFIER")["value"]
            elif param_name == "prefix":
                node["params"]["prefix"] = self.parse_string_or_identifier()
            elif param_name == "drop_first":
                node["params"]["drop_first"] = self.consume("TRUE")["value"] == "TRUE" if self.peek()["type"] == "TRUE" else False

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        self.consume("RPAREN")
        return node

    def parse_label_encode(self):
        """Parse label_encode(column='col1', prefix='enc')"""
        node = {"type": "label_encode", "params": {}}
        self.consume("LABEL_ENCODE")
        self.consume("LPAREN")

        param_names = ['COLUMN','PREFIX']
        while self.peek() and self.peek()["type"] != "RPAREN":
            param_name = self.consume_any(param_names)["value"]
            self.consume("ASSIGN")

            if param_name == "column":
                node["params"]["column"] = self.consume("IDENTIFIER")["value"]
            elif param_name == "prefix":
                node["params"]["prefix"] = self.parse_string_or_identifier()

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        self.consume("RPAREN")
        return node

    # ========== NOUVELLE COMMANDE CLEAN ==========

    def parse_clean(self):
        """
        Parse CLEAN command for data cleaning operations.
        Clean est une commande top-level qui applique plusieurs opérations de nettoyage.
        Syntax: CLEAN target [ operations ]
        """
        node = {"type": "clean", "target": None, "operations": []}
        self.consume("CLEAN")

        # Cible (table)
        node["target"] = self.consume("IDENTIFIER")["value"]

        # Opérations de nettoyage
        if self.peek() and self.peek()["type"] == "LBRACKET":
            self.consume("LBRACKET")
            node["operations"] = self.parse_clean_operations()
            self.consume("RBRACKET")

        return node

    def parse_clean_operations(self):
        """Parse les opérations à l'intérieur d'une commande CLEAN"""
        operations = []

        while self.peek() and self.peek()["type"] != "RBRACKET":
            token = self.peek()

            if token["type"] == "DROP_NA":
                operations.append(self.parse_drop_na())
            elif token["type"] == "FILL_NA":
                operations.append(self.parse_fill_na())
            elif token["type"] == "REPLACE":
                operations.append(self.parse_replace())
            elif token["type"] == "CLIP":
                operations.append(self.parse_clip())
            elif token["type"] == "REMOVE_OUTLIERS":
                operations.append(self.parse_remove_outliers())
            elif token["type"] == "STANDARDIZE":
                operations.append(self.parse_standardize())
            elif token["type"] == "MIN_MAX_SCALE":
                operations.append(self.parse_min_max_scale())
            elif token["type"] == "ONE_HOT_ENCODE":
                operations.append(self.parse_one_hot_encode())
            elif token["type"] == "LABEL_ENCODE":
                operations.append(self.parse_label_encode())
            else:
                self.error(f"Unexpected operation in CLEAN: {token['type']}", token)

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        return operations

    # ========== NOUVELLE COMMANDE STATS ==========

    def parse_stats(self):
        """Parse STATS command for advanced statistics"""
        node = {"type": "stats", "target": None, "operations": []}
        self.consume("STATS")
        node["target"] = self.consume("IDENTIFIER")["value"]

        if self.peek() and self.peek()["type"] == "LBRACKET":
            self.consume("LBRACKET")
            node["operations"] = self.parse_stats_operations()
            self.consume("RBRACKET")

        return node

    def parse_stats_operations(self):
        """Parse operations inside STATS command"""
        operations = []

        while self.peek() and self.peek()["type"] != "RBRACKET":
            token = self.peek()

            op = {}

            # Avec assignation (result = FUNCTION(...))
            if token["type"] == "IDENTIFIER" and self.peek(1) and self.peek(1)["type"] == "ASSIGN":
                op["variable"] = self.consume("IDENTIFIER")["value"]
                self.consume("ASSIGN")
                op["expression"] = self.parse_expression()
            else:
                op["expression"] = self.parse_expression()

            operations.append(op)

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        return operations

    # ========== NOUVELLE COMMANDE VISUALIZE ==========

    def parse_visualize(self):
        """Parse VISUALIZE command for generating charts"""
        node = {"type": "visualize", "chart_type": None, "target": None, "params": {}}
        self.consume_any(['VIZ','VISUALIZE'])

        # Type de graphique
        chart_types = ["HISTOGRAM", "BAR_CHART", "SCATTER", "LINE_CHART", "BOX_PLOT", 
                       "VIOLIN_PLOT", "HEATMAP", "QQ_PLOT", "ACF_PLOT", "PIE_CHART"]
        node["chart_type"] = self.consume_any(chart_types)["value"]

        # Cible (table)
        node["target"] = self.consume("IDENTIFIER")["value"]

        # Paramètres optionnels
        if self.peek() and self.peek()["type"] == "LPAREN":
            self.consume("LPAREN")
            node["params"] = self.parse_viz_params()
            self.consume("RPAREN")

        # Options WITH
        if self.peek() and self.peek()["type"] == "WITH":
            node["options"] = self.parse_with_options()

        return node

    def parse_viz_params(self):
        """Parse visualization parameters"""
        params = {}

        viz_params_tokens = ["BINS","WIDTH", "HEIGHT","SIZE","ALPHA","FACTOR","TITLE",
                             "XLABEL","YLABEL","COLOR","CMAP","COLORS","STACKED","MARKERS",
                             "DENSITY","GRID",  "LEGEND","COLUMNS", "COLUMN","X","Y","DIST","LABELS","VALUES",'SHOW_PERCENT']

        while self.peek() and self.peek()["type"] != "RPAREN":
            param_name = self.consume_any(viz_params_tokens)["value"]
            self.consume("ASSIGN")

            if param_name in ["bins", "width", "height", "size"]:
                params[param_name] = int(self.consume("NUMBER")["value"])
            elif param_name in ["alpha", "factor"]:
                params[param_name] = float(self.consume("FLOAT")["value"])
            elif param_name in ["title", "xlabel", "ylabel", "color", "cmap"]:
                params[param_name] = self.parse_string_or_identifier()
            elif param_name in ["colors"]:
                params[param_name] = self.parse_list()
            elif param_name in ["stacked", "markers", "density", "grid", "legend"]:
                token = self.peek()
                if token["type"] == "TRUE":
                    params[param_name] = True
                    self.consume("TRUE")
                elif token["type"] == "FALSE":
                    params[param_name] = False
                    self.consume("FALSE")
                else:
                    params[param_name] = self.consume("IDENTIFIER")["value"] == "true"
            elif param_name == "x" or param_name == "y":
                params[param_name] = self.consume("IDENTIFIER")["value"]
            elif param_name in ['values','labels','show_percent']:
                params[param_name] = self.consume("IDENTIFIER")["value"]
            elif param_name == 'columns':
                params[param_name] = self.parse_list()
            elif param_name == "column":
                params[param_name] = self.consume("IDENTIFIER")["value"]

            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        return params

    # ========== NOUVELLES COMMANDES DESCRIBE, DESCRIBE_ALL, SUMMARY ==========

    def parse_describe(self):
        """
        Parse DESCRIBE command for descriptive statistics.
        Syntax: DESCRIBE target [ columns ] [ with options ]
        """
        node = {"type": "describe", "target": None, "columns": None, "options": {}}
        self.consume("DESCRIBE")
        
        # Cible (table)
        node["target"] = self.consume("IDENTIFIER")["value"]
        
        # Colonnes optionnelles entre crochets
        if self.peek() and self.peek()["type"] == "LBRACKET":
            self.consume("LBRACKET")
            node["columns"] = self.parse_describe_columns()
            self.consume("RBRACKET")
        
        # Options WITH
        if self.peek() and self.peek()["type"] == "WITH":
            node["options"] = self.parse_with_options()
        
        return node

    def parse_describe_columns(self):
        """Parse la liste des colonnes pour DESCRIBE"""
        columns = []
        
        # Première colonne
        token = self.peek()
        if token["type"] == "IDENTIFIER":
            columns.append(self.consume("IDENTIFIER")["value"])
        elif token["type"] == "STRING":
            columns.append(self.strip_quotes(self.consume("STRING")["value"]))
        else:
            self.error("Expected column name", token)
        
        # Colonnes supplémentaires séparées par des virgules
        while self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            token = self.peek()
            if token["type"] == "IDENTIFIER":
                columns.append(self.consume("IDENTIFIER")["value"])
            elif token["type"] == "STRING":
                columns.append(self.strip_quotes(self.consume("STRING")["value"]))
            else:
                self.error("Expected column name", token)
        
        return columns

    def parse_describe_all(self):
        """
        Parse DESCRIBE_ALL command for complete statistics.
        Syntax: DESCRIBE_ALL target [ with options ]
        """
        node = {"type": "describe_all", "target": None, "options": {}}
        self.consume("DESCRIBE_ALL")
        
        # Cible (table)
        node["target"] = self.consume("IDENTIFIER")["value"]
        
        # Options WITH
        if self.peek() and self.peek()["type"] == "WITH":
            node["options"] = self.parse_with_options()
        
        return node

    def parse_summary(self):
        """
        Parse SUMMARY command for DataFrame summary.
        Syntax: SUMMARY target
        """
        node = {"type": "summary", "target": None}
        self.consume("SUMMARY")
        
        # Cible (table)
        node["target"] = self.consume("IDENTIFIER")["value"]
        
        return node

    # ========== FONCTIONS EXISTANTES ==========

    def parse_select(self):
        node = {"type": "select", "args": []}
        self.consume("SELECT")
        self.consume("LPAREN")

        arg = self.parse_select_arg()
        node["args"].append(arg)

        while self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            arg = self.parse_select_arg()
            node["args"].append(arg)

        self.consume("RPAREN")
        return node

    def parse_select_arg(self):
        arg = {}

        if self.peek()["type"] in self.function_types:
            arg["expression"] = self.parse_function_call()
        elif self.peek()["type"] == "IDENTIFIER":
            arg["name"] = self.consume("IDENTIFIER")["value"]
        else:
            arg["expression"] = self.parse_expression()

        if self.peek() and self.peek()['type'] in ["AS", "SHIFT_RIGHT"]:
            self.consume(self.peek()["type"])
            arg["alias"] = self.consume("IDENTIFIER")['value']

        return arg

    def parse_drop(self):
        node = {"type": "drop", "args": []}
        self.consume("DROP")
        self.consume("LPAREN")

        node["args"].append(self.consume("IDENTIFIER")["value"])

        while self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            node["args"].append(self.consume("IDENTIFIER")["value"])

        self.consume("RPAREN")
        return node

    def parse_filter(self):
        node = {"type": "filter", "condition": None}
        self.consume("FILTER")
        self.consume("LPAREN")
        node["condition"] = self.parse_filter_expression()
        self.consume("RPAREN")
        return node

    def parse_filter_expression(self):
        """Parse une expression de filtre avec opérateurs logiques (AND/OR)"""
        left = self.parse_filter_term()

        while self.peek() and self.peek()["type"] in ["AND", "OR", "AND_OP", "OR_OP"]:
            operator = self.consume(self.peek()["type"])["value"]
            right = self.parse_filter_term()
            left = {
                "type": "binary_operation",
                "operator": operator,
                "left": left,
                "right": right
            }

        return left

    def parse_filter_term(self):
        """Parse un terme de filtre (condition simple ou parenthésée)"""
        if self.peek() and self.peek()["type"] == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_filter_expression()
            self.consume("RPAREN")
            return expr

        if self.peek() and self.peek()["type"] == "NOT":
            self.consume("NOT")
            return {
                "type": "not",
                "expression": self.parse_filter_term()
            }

        return self.parse_filter_condition()

    def parse_filter_condition(self):
        """Parse une condition de comparaison simple"""
        left = self.parse_filter_value()

        if not self.peek() or self.peek()["type"] not in ["GT", "LT", "GE", "LE", "EQ", "NE", "BETWEEN", "IN", "LIKE"]:
            self.error("Expected comparison operator", self.peek())

        op_token = self.peek()

        if op_token["type"] == "BETWEEN":
            self.consume("BETWEEN")
            lower = self.parse_filter_value()
            self.consume("AND")
            upper = self.parse_filter_value()
            return {
                "type": "between",
                "left": left,
                "lower": lower,
                "upper": upper
            }

        if op_token["type"] == "IN":
            self.consume("IN")
            self.consume("LPAREN")
            values = [self.parse_filter_value()]
            while self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")
                values.append(self.parse_filter_value())
            self.consume("RPAREN")
            return {
                "type": "in",
                "left": left,
                "values": values
            }

        if op_token["type"] == "LIKE":
            operator = self.consume("LIKE")["value"]
            right = self.parse_filter_value()
            return {
                "type": "like",
                "operator": operator,
                "left": left,
                "right": right
            }

        operator = self.consume(op_token["type"])["value"]
        right = self.parse_filter_value()

        return {
            "type": "comparison",
            "operator": operator,
            "left": left,
            "right": right
        }

    def parse_filter_value(self):
        """Parse une valeur dans une condition de filtre"""
        token = self.peek()
        if not token:
            self.error("Expected value in filter condition", None)

        if token["type"] in self.function_types:
            return self.parse_function_call()

        if token["type"] == "IDENTIFIER":
            return {
                "type": "column",
                "value": self.consume("IDENTIFIER")["value"]
            }

        return self.parse_literal()

    def parse_literal(self):
        """Parse un littéral (nombre, chaîne, booléen, null)"""
        token = self.peek()
        if not token:
            self.error("Expected literal", None)

        if token["type"] == "NUMBER":
            return {
                "type": "number",
                "value": int(self.consume("NUMBER")["value"])
            }
        elif token["type"] == "FLOAT":
            return {
                "type": "float",
                "value": float(self.consume("FLOAT")["value"])
            }
        elif token["type"] == "STRING":
            return {
                "type": "string",
                "value": self.strip_quotes(self.consume("STRING")["value"])
            }
        elif token["type"] == "TRUE":
            self.consume("TRUE")
            return {"type": "boolean", "value": True}
        elif token["type"] == "FALSE":
            self.consume("FALSE")
            return {"type": "boolean", "value": False}
        elif token["type"] == "NULL":
            self.consume("NULL")
            return {"type": "null", "value": None}
        else:
            self.error(f"Expected literal, got {token['type']}", token)

    def parse_function_call(self):
        """Parse un appel de fonction où le nom est un type de token spécifique"""
        token = self.peek()
        if not token or token["type"] not in self.function_types:
            self.error(f"Expected function name, got {token['type'] if token else 'None'}", token)

        name = self.consume(token["type"])["value"]

        self.consume("LPAREN")
        args = self.parse_function_arguments(name)
        self.consume("RPAREN")
        over = None
        if self.peek() and self.peek()["type"] == "OVER":
            over = self.parse_over_clause()

        result = {
            "type": "function_call",
            "name": name,
            "arguments": args
        }

        if over:
            result["over"] = over

        return result

    def parse_function_arguments(self, function_name):
        """Parse les arguments d'une fonction selon son nom"""
        args = []

        if self.peek() and self.peek()["type"] == "RPAREN":
            return args

        if function_name == "COUNT":
            if self.peek() and self.peek()["type"] == "MULT":
                self.consume("MULT")
                args.append({"type": "star"})
                return args

            if self.peek() and self.peek()["type"] == "DISTINCT":
                self.consume("DISTINCT")
                col = self.consume("IDENTIFIER")["value"]
                args.append({"type": "distinct", "column": col})
                return args

        args.append(self.parse_expression())

        while self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            args.append(self.parse_expression())

        return args

    def parse_over_clause(self):
        """Parse OVER (PARTITION BY ... ORDER BY ...)"""
        self.consume("OVER")
        self.consume("LPAREN")

        over = {}

        if self.peek() and self.peek()["type"] == "PARTITION":
            self.consume("PARTITION")
            self.consume("BY")
            over["partition_by"] = [self.consume("IDENTIFIER")["value"]]
            while self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")
                over["partition_by"].append(self.consume("IDENTIFIER")["value"])

        if self.peek() and self.peek()["type"] == "ORDER":
            self.consume("ORDER")
            self.consume("BY")
            over["order_by"] = [self.parse_order_by_item()]
            while self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")
                over["order_by"].append(self.parse_order_by_item())

        if self.peek() and self.peek()["type"] == "ROWS":
            self.consume("ROWS")
            self.consume("BETWEEN")

            over["rows"] = {
                "start": self.parse_frame_bound(),
                "end": self.parse_frame_bound()
            }

        self.consume("RPAREN")
        return over

    def parse_order_by_item(self):
        """Parse un élément ORDER BY (col ASC/DESC)"""
        item = {"column": self.consume("IDENTIFIER")["value"]}
        if self.peek() and self.peek()["type"] in ["ASC", "DESC"]:
            item["direction"] = self.consume(self.peek()["type"])["value"]
        return item

    def parse_frame_bound(self):
        """Parse UNBOUNDED PRECEDING, CURRENT ROW, etc."""
        if self.peek() and self.peek()["type"] == "UNBOUNDED":
            self.consume("UNBOUNDED")
            bound = {"type": "unbounded"}
        elif self.peek() and self.peek()["type"] == "CURRENT":
            self.consume("CURRENT")
            self.consume("ROW")
            bound = {"type": "current_row"}
        else:
            value = int(self.consume("NUMBER")["value"])
            direction = self.consume_any(["PRECEDING", "FOLLOWING"])["value"]
            bound = {"type": "value", "value": value, "direction": direction}

        return bound

    def parse_create_feature(self):
        """Parse create_feature(assignations)"""
        node = {"type": "create_feature", "features": []}
        self.consume("CREATE_FEATURE")
        self.consume("LPAREN")

        node["features"].append(self.parse_feature_assignment())

        while self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            node["features"].append(self.parse_feature_assignment())

        self.consume("RPAREN")
        return node

    def parse_feature_assignment(self):
        """Parse nom_feature = expression"""
        feature = {
            "name": self.consume("IDENTIFIER")["value"]
        }
        self.consume("ASSIGN")

        if self.peek() and self.peek()["type"] == "CASE":
            feature["expression"] = self.parse_case_when()
        else:
            feature["expression"] = self.parse_expression()

        return feature

    def parse_case_when(self):
        """Parse CASE WHEN condition THEN value ELSE value END"""
        self.consume("CASE")
        case_node = {"type": "case", "when_then": []}

        while self.peek() and self.peek()["type"] == "WHEN":
            self.consume("WHEN")
            condition = self.parse_filter_expression()
            self.consume("THEN")
            then_value = self.parse_expression()
            case_node["when_then"].append({
                "when": condition,
                "then": then_value
            })

        if self.peek() and self.peek()["type"] == "ELSE":
            self.consume("ELSE")
            case_node["else"] = self.parse_expression()

        self.consume("END")
        return case_node

    def parse_expression(self, precedence=0):
        """Parse une expression avec précédence des opérateurs"""
        left = self.parse_primary()

        operators = {
            'OR': 1, 'AND': 2,
            'EQ': 3, 'NE': 3, 'GT': 3, 'LT': 3, 'GE': 3, 'LE': 3,
            'PLUS': 4, 'MINUS': 4,
            'MULT': 5, 'DIV': 5, 'MOD': 5,
            'POW': 6
        }

        while self.peek() and self.peek()["type"] in operators and operators[self.peek()["type"]] > precedence:
            op_token = self.peek()
            op_type = op_token["type"]
            op_value = op_token["value"]
            self.consume(op_type)
            next_prec = operators[op_type]
            right = self.parse_expression(next_prec)
            left = {
                "type": "binary_operation",
                "operator": op_value,
                "left": left,
                "right": right
            }

        return left

    def parse_primary(self):
        """Parse un élément primaire dans une expression"""
        token = self.peek()
        if not token:
            self.error("Expected expression", None)

        if token["type"] == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr

        if token["type"] in self.function_types:
            return self.parse_function_call()

        if token["type"] == "CASE":
            return self.parse_case_when()

        if token["type"] == "IDENTIFIER":
            return {
                "type": "column",
                "value": self.consume("IDENTIFIER")["value"]
            }

        return self.parse_literal()

    def parse_group_by(self):
        """Parse group_by(col1, col2, ...)"""
        node = {"type": "group_by", "columns": []}
        self.consume("GROUP_BY")
        self.consume("LPAREN")

        node["columns"].append(self.consume("IDENTIFIER")["value"])

        while self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            node["columns"].append(self.consume("IDENTIFIER")["value"])

        self.consume("RPAREN")
        return node

    def parse_agg(self):
        """Parse agg(agg1 = SUM(col), agg2 = AVG(col), ...)"""
        node = {"type": "agg", "aggregations": []}
        self.consume("AGG")
        self.consume("LPAREN")

        node["aggregations"].append(self.parse_agg_item())

        while self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            node["aggregations"].append(self.parse_agg_item())

        self.consume("RPAREN")
        return node

    def parse_agg_item(self):
        """Parse nom = FUNCTION(col)"""
        item = {}

        item["name"] = self.consume("IDENTIFIER")["value"]
        self.consume("ASSIGN")

        if self.peek():
            expr = self.parse_expression()
            item["expression"] = expr

        return item

    def parse_join(self):
        """Parse join(table, on=condition, type='inner')"""
        node = {"type": "join"}
        self.consume("JOIN")
        self.consume("LPAREN")

        node["table"] = self.consume("IDENTIFIER")["value"]

        self.consume("COMMA")
        self.consume("ON")
        self.consume("ASSIGN")
        node["on"] = {}
        left = node["on"]["left_on"] = self.strip_quotes(self.consume_any(["STRING","IDENTIFIER"])["value"])
        lone = True
        if self.peek() and self.peek()["type"] == "COLON":
            lone = False
            self.consume("COLON")
            node["on"]["right_on"] = self.strip_quotes(self.consume_any(["STRING","IDENTIFIER"])["value"])

        if lone == True:
            node['on']["right_on"] = left

        if self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            self.consume("TYPE")
            self.consume("ASSIGN")
            node["how"] = self.consume_any(["INNER","LEFT","RIGHT","OUTER"])["value"]

        self.consume("RPAREN")
        return node

    def parse_having(self):
        """Parse having(condition)"""
        node = {"type": "having", "condition": None}
        self.consume("HAVING")
        self.consume("LPAREN")
        node["condition"] = self.parse_filter_expression()
        self.consume("RPAREN")
        return node

    def parse_list(self):
        """Parse [item1, item2, ...]"""
        items = []
        self.consume("LBRACKET")

        if not self.peek() or self.peek()["type"] != "RBRACKET":
            items.append(self.parse_list_item())
            while self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")
                items.append(self.parse_list_item())

        self.consume("RBRACKET")
        return items

    def parse_list_item(self):
        """Parse un élément de liste"""
        token = self.peek()
        if token["type"] == "STRING":
            return self.strip_quotes(self.consume("STRING")["value"])
        elif token["type"] == "NUMBER":
            return int(self.consume("NUMBER")["value"])
        elif token["type"] == "FLOAT":
            return float(self.consume("FLOAT")["value"])
        elif token["type"] in ["TRUE", "FALSE"]:
            return self.consume(token["type"])["value"] == "TRUE"
        else:
            return self.consume("IDENTIFIER")["value"]

    def parse_if(self):
        """Parse IF condition [ commands ] ELIF ... ELSE [ commands ]"""
        node = {"type": "if", "branches": []}
        self.consume("IF")

        branch = {
            "condition": self.parse_filter_expression(),
            "body": []
        }

        self.consume("LBRACKET")
        branch["body"] = self.parse_block()
        self.consume("RBRACKET")
        node["branches"].append(branch)


        while self.peek() and self.peek()["type"] == "ELIF":
            self.consume("ELIF")
            branch = {
                "condition": self.parse_filter_expression(),
                "body": []
            }
            self.consume("LBRACKET")
            branch["body"] = self.parse_block()
            self.consume("RBRACKET")
            node["branches"].append(branch)


        if self.peek() and self.peek()["type"] == "ELSE":
            self.consume("ELSE")
            self.consume("LBRACKET")
            node["else"] = self.parse_block()
            self.consume("RBRACKET")

        return node

    def parse_for(self):
        """Parse FOR var IN collection [ commands ]"""
        node = {"type": "for", "variable": None, "collection": None, "commands": []}
        self.consume("FOR")

        node["variable"] = self.consume("IDENTIFIER")["value"]
        self.consume("IN")
        node["collection"] = self.consume("IDENTIFIER")["value"]

        self.consume("LBRACKET")
        node["commands"] = self.parse_block()
        self.consume("RBRACKET")

        return node

    def parse_analyze(self):
        """Parse ANALYZE target [ operations ] with options"""
        node = {"type": "analyze", "target": None, "operations": [], "options": {}}
        self.consume_any(["ANALYZE", "ANALYSE"])

        node["target"] = self.consume("IDENTIFIER")["value"]

        if self.peek() and self.peek()["type"] == "LBRACKET":
            self.consume("LBRACKET")
            node["operations"] = self.parse_analyze_operations()
            self.consume("RBRACKET")

        if self.peek() and self.peek()["type"] == "WITH":
            node["options"] = self.parse_with_options()

        return node

    def parse_analyze_operations(self):
        """Parse les opérations d'analyse"""
        operations = []

        while self.peek() and self.peek()["type"] != "RBRACKET":
            token = self.peek()

            op = {}

            if token["type"] == "IDENTIFIER":

                if self.peek(1) and self.peek(1)["type"] == "ASSIGN":

                    var_name = self.consume("IDENTIFIER")["value"]
                    self.consume("ASSIGN")
                    expr = self.parse_expression()
                    op["variable"] = var_name
                    op["expression"] = expr
                    operations.append(op)
            else:
                expr = self.parse_expression()
                op["expression"] = expr
                operations.append(op)


            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        return operations

    def parse_with_options(self):
        """Parse WITH option1=value1, option2=value2"""
        options = {}
        self.consume("WITH")

        opt_names = ["SHOW", "FORMAT", "TITLE", "WIDTH", "HEIGHT", "SAVE", "DETAILED"]
        
        opt_name = self.consume_any(opt_names)["value"]
        self.consume("ASSIGN")
        opt_value = self.parse_literal()["value"]
        options[opt_name] = opt_value

        while self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            opt_name = self.consume_any(opt_names)["value"]
            self.consume("ASSIGN")
            opt_value = self.parse_literal()["value"]
            options[opt_name] = opt_value

        return options

    def parse_block(self):
        """Parse un bloc de commandes entre crochets"""
        commands = []

        while self.peek() and self.peek()["type"] != "RBRACKET":
            token = self.peek()

            if token["type"] == "TRANSFORM":
                commands.append(self.parse_transform())
            elif token["type"] == "LOAD":
                commands.append(self.parse_load())
            elif token["type"] in ["ANALYZE", "ANALYSE"]:
                commands.append(self.parse_analyze())
            elif token["type"] == "VIZ":
                commands.append(self.parse_visualize())
            elif token["type"] == "STATS":
                commands.append(self.parse_stats())
            elif token["type"] == "DESCRIBE":
                commands.append(self.parse_describe())
            elif token["type"] == "DESCRIBE_ALL":
                commands.append(self.parse_describe_all())
            elif token["type"] == "SUMMARY":
                commands.append(self.parse_summary())
            elif token["type"] == "CLEAN":
                commands.append(self.parse_clean())
            elif token["type"] == "IF":
                commands.append(self.parse_if())
            elif token["type"] == "FOR":
                commands.append(self.parse_for())
            else:
                self.error(f"Unexpected command in block: {token['type']}", token)

        return commands

    def strip_quotes(self, s):
        if s.startswith('"') and s.endswith('"'):
            return s[1:-1]
        elif s.startswith("'") and s.endswith("'"):
            return s[1:-1]
        return s
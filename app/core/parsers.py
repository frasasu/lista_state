from core import Lexer
import re

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

        self.function_types = [

            'SUM', 'AVG', 'MEAN', 'MEDIAN', 'MODE', 'COUNT', 'MIN', 'MAX',
            'STD', 'VAR', 'SKEW', 'KURT', 'QUANTILE', 'PERCENTILE', 'CORR',
            'COV', 'CROSSTAB', 'FREQ', 'TOP', 'ENTROPY','RANK','ROW_NUMBER',

            'LOG', 'EXP', 'SQRT', 'ABS', 'ROUND', 'FLOOR', 'CEIL',
            'SIN', 'COS', 'TAN', 'ASIN', 'ACOS', 'ATAN', 'POWER', 'MOD',

            'WORD_COUNT', 'SENTENCE_COUNT', 'TOP_WORDS', 'TOP_PHRASES',
            'SENTIMENT', 'SUBJECTIVITY', 'LDA', 'KEYPHRASES', 'NER',
            'COSINE_SIMILARITY',

            'T_TEST', 'ANOVA', 'CHI2', 'MANN_WHITNEY', 'KRUSKAL',
            'KS_TEST', 'ADF_TEST', 'KPSS_TEST', 'ACF', 'PACF',
            'DECOMPOSE', 'CUSUM', 'SEASONAL_STRENGTH', 'TREND', 'EXPONENTIAL_SMOOTHING'
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
            return contents

        if self.peek() and self.peek()["type"] in ["SELECT", "DROP", "FILTER", "CREATE_FEATURE",
                                                    "GROUP_BY", "AGG", "JOIN", "HAVING"]:
            contents.append(self.parse_current_operation())

        while self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            if self.peek() and self.peek()["type"] in ["SELECT", "DROP", "FILTER", "CREATE_FEATURE",
                                                        "GROUP_BY", "AGG", "JOIN", "HAVING"]:
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
        else:
            self.error(f"Unexpected operation: {token_type}", self.peek())

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

        func = self.parse_function_call()
        item["function"] = func

        return item

    def parse_join(self):
        """Parse join(table, on=condition, type='inner')"""
        node = {"type": "join"}
        self.consume("JOIN")
        self.consume("LPAREN")

        node["table"] = self.consume("IDENTIFIER")["value"]

        while self.peek() and self.peek()["type"] != "RPAREN":
            if self.peek()["type"] == "COMMA":
                self.consume("COMMA")

            param_name = self.consume("IDENTIFIER")["value"]
            self.consume("ASSIGN")

            if param_name == "on":
                node["on"] = self.parse_filter_expression()
            elif param_name == "type":
                node["type"] = self.parse_string_or_identifier()
            elif param_name == "suffix":
                node["suffix"] = self.parse_string_or_identifier()
            elif param_name == "columns":
                node["columns"] = self.parse_list()

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

            if token["type"] == "IDENTIFIER":

                if self.peek(1) and self.peek(1)["type"] == "ASSIGN":

                    var_name = self.consume("IDENTIFIER")["value"]
                    self.consume("ASSIGN")
                    func = self.parse_function_call()
                    func["variable"] = var_name
                    operations.append(func)
            elif token["type"] in self.function_types:

                operations.append(self.parse_function_call())
            else:
                self.error(f"Expected function call in analyze operations, got {token['type']}", token)


            if self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")

        return operations

    def parse_with_options(self):
        """Parse WITH option1=value1, option2=value2"""
        options = {}
        self.consume("WITH")

        opt_name = self.consume_any(["SHOW"])["value"]
        self.consume("ASSIGN")
        opt_value = self.parse_literal()["value"]
        options[opt_name] = opt_value

        while self.peek() and self.peek()["type"] == "COMMA":
            self.consume("COMMA")
            opt_name = self.consume_any(['FORMAT'])["value"]
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

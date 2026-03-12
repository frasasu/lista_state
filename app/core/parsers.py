code = """
# Test 1: LOAD avec différentes syntaxes
Load employes as emp
Load clients >> cli
Load produits as prod

# Test 2: TRANSFORM simple (sans bloc)
Transform employes drop(age, taille) as emp_clean
Transform employes select(nom, prenom, salaire) as emp_basic
Transform employes select(nom as name, prenom as firstname) as emp_rename
Transform employes select(age >> years, salaire >> salary) as emp_shift
Transform employes filter(age > 18) as adultes
Transform employes filter(salaire >= 30000) as hauts_salaires

# Test 3: TRANSFORM avec bloc simple
Transform employes [
    drop(age, taille)
] as emp_sans_age

# Test 4: TRANSFORM avec bloc multiple
Transform employes [
    drop(age, taille),
    select(nom, prenom, salaire)
] as emp_transform1

# Test 5: TRANSFORM avec SELECT complexe dans bloc
Transform employes [
    select(nom as name, prenom as firstname, salaire),
    select(age >> years, taille >> height),
    drop(departement, manager)
] as emp_complex

# Test 6: TRANSFORM avec FILTER
Transform employes filter(age > 25 AND salaire > 30000) as jeunes_riches
Transform employes filter(departement == "IT" OR departement == "R&D") as tech_team

# Test 7: TRANSFORM avec FILTER dans bloc
Transform employes [
    filter(age BETWEEN 30 AND 45),
    select(nom, prenom, salaire),
    drop(adresse, telephone)
] as middle_aged

# Test 8: Test de tous les types de filtres
Transform tests [
    # Comparaisons simples
    filter(age > 18),
    filter(age < 65),
    filter(age >= 30),
    filter(age <= 60),
    filter(departement == "IT"),
    filter(statut != "inactif"),

    # Opérateurs logiques
    filter(age > 25 AND salaire > 40000),
    filter(departement == "IT" OR departement == "Marketing"),

    # BETWEEN
    filter(age BETWEEN 25 AND 50),
    filter(salaire BETWEEN 30000 AND 80000),

    # IN
    filter(departement IN ("IT", "RH", "Finance")),
    filter(statut IN ("actif", "vacances")),

    # Expressions avec parenthèses
    filter((age > 30 OR experience > 5) AND salaire > 50000),
] as tous_les_filtres

# Test 9: TRANSFORM avec CREATE_FEATURE
Transform employes [
    create_feature(
        age_mois = age * 12,
        salaire_k = salaire / 1000,
        experience_carre = experience ** 2
    )
] as features

# Test 10: CREATE_FEATURE avec expressions complexes
Transform employes [
    create_feature(
        bonus = salaire * 0.1,
        age_plus_experience = age + experience,
        ratio = salaire / experience
    )
] as features2

# Test 11: CREATE_FEATURE avec appels de fonction
Transform employes [
    create_feature(
        log_salaire = LOG(salaire),
        age_moyen = AVG(age),
        somme_salaire = SUM(salaire)
    )
] as features3

# Test 12: IF simple
IF age_moyen > 40 [
    Transform employes filter(age > 40) as seniors
]

# Test 13: IF avec ELSE
IF nombre_employes > 100 [
    Transform employes [] as echantillon
] ELSE [
    Transform employes as tous
]

# Test 14: IF dans un bloc
Transform employes [
    filter(age > 18),
    select(nom, age)
] as emp_temp

IF compteur > 0 [
    Transform emp_temp drop(age) as sans_age
]

# Test 15: ANALYZE avec opérations
Analyze employes [
    count_total = COUNT(*),
    age_moyen = AVG(age),
    salaire_max = MAX(salaire),
    CORR(age, salaire)
] with show=true, format="json"

# Test 16: GROUP BY et AGG
Transform ventes [
    group_by(region, produit),
    agg(
        total_ventes = SUM(montant),
        moyenne_ventes = AVG(montant),
        nombre_transactions = COUNT(*)
    )
] as ventes_par_region

# Test 17: HAVING clause
Transform ventes [
    group_by(region),
    having(COUNT(*) > 100 AND AVG(montant) > 1000),
    agg(
        total = SUM(montant)
    )
] as regions_importantes

# Test 18: JOIN
Transform commandes [
    join(clients, on=client_id == id, type="inner"),
    join(produits, on=produit_id == id, type="left", suffix="_prod")
] as commandes_enrichies

# Test 19: FOR simple
FOR emp IN employes [
    Transform emp select(nom) as nom_seul
]

# Test 20: Combinaison complexe
Load commandes as cmd
Transform cmd [
    filter(montant > 1000),
    select(client, montant, date),
    drop(adresse_livraison)
] as grosses_commandes

Analyze grosses_commandes [
    total = SUM(montant),
    moyenne = AVG(montant),
    nombre = COUNT(*)
] with show=true

IF total_commandes > 1000 [
    Transform grosses_commandes [] as echantillon_commandes
] ELSE [
    Transform grosses_commandes as toutes_commandes
]

FOR cmd IN grosses_commandes [
    Transform cmd select(client, montant) as details_cmd
]

# Test 21: Test des chaînes avec quotes
Load fichier as data
Transform data filter(nom == "Jean Dupont") as jean
Transform data filter(ville == 'Paris') as parisiens

# Test 22: Test des nombres et flottants
Transform data [
    filter(age == 25),
    filter(taille == 1.75),
    filter(poids >= 70.5)
] as numerics

# Test 23: Test des opérateurs SHIFT_RIGHT (>>) comme alias
Transform source >> destination
Transform source select(col1 >> alias1, col2 >> alias2) as result

# Test 24: Blocs vides et commandes simples
Transform vide [] as rien
Load test as t
Transform t select(col) as simple

# Test 25: Test des booléens et null
Transform data [
    filter(actif == true),
    filter(inactif == false),
    filter(valeur == null)
] as booleens

# Test 26: Chaînage de transformations
Transform source as s1
Transform s1 as s2
Transform s2 as s3
Transform s3 as final

# Test 27: Mélange de tous les concepts
Transform donnees [
    filter(age > 18 AND actif == true),
    create_feature(
        age_carre = age ** 2,
        log_revenu = LOG(revenu),
        age_plus_10 = age + 10,
        ratio = revenu / age
    ),
    select(nom, age, revenu, age_carre, log_revenu),
    drop(id_interne, date_creation)
] as preparation

IF compteur > 0 [
    Analyze preparation [
        age_moyen = AVG(age),
        revenu_total = SUM(revenu)
    ] with show=true
    
    FOR row IN preparation [
        Transform row select(nom) as noms
    ]
] ELSE [
    Load backup as secours
    Transform secours as preparation
]

# Test 28: CASE WHEN dans create_feature
Transform employes [
    create_feature(
        categorie_age = CASE 
            WHEN age < 25 THEN "junior"
            WHEN age < 40 THEN "mid"
            ELSE "senior" 
        END,
        bonus = CASE 
            WHEN salaire > 50000 THEN salaire * 0.2
            ELSE salaire * 0.1
        END
    )
] as employes_avec_categorie

# Test 29: Window functions avec OVER
Transform ventes [
    create_feature(
        rang = RANK() OVER (PARTITION BY region ORDER BY montant DESC),
        moyenne_mobile = AVG(montant) OVER (
            PARTITION BY region 
            ORDER BY date 
            ROWS BETWEEN 2 PRECEDING  CURRENT ROW
        )
    )
] as ventes_avec_rang

# Test 30: Opérations mathématiques complexes
Transform calculs [
    create_feature(
        resultat1 = (salaire + age * 2 - age / 5 ) / 1000,
        resultat2 = (revenu - depenses) ** 2,
        resultat3 = LOG(salaire + 1) * 100,
        resultat4 = ABS(age - moyenne_age),
        resultat5 = ROUND(salaire / 1000, 2)
    )
] as calculs_complexes
"""
from core import Lexer
import json


import re
import json

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        
        # Liste de tous les types de tokens qui sont des fonctions
        self.function_types = [
            # Agrégations
            'SUM', 'AVG', 'MEAN', 'MEDIAN', 'MODE', 'COUNT', 'MIN', 'MAX',
            'STD', 'VAR', 'SKEW', 'KURT', 'QUANTILE', 'PERCENTILE', 'CORR',
            'COV', 'CROSSTAB', 'FREQ', 'TOP', 'ENTROPY','RANK','ROW_NUMBER',
            
            # Mathématiques
            'LOG', 'EXP', 'SQRT', 'ABS', 'ROUND', 'FLOOR', 'CEIL',
            'SIN', 'COS', 'TAN', 'ASIN', 'ACOS', 'ATAN', 'POWER', 'MOD',
            
            # NLP
            'WORD_COUNT', 'SENTENCE_COUNT', 'TOP_WORDS', 'TOP_PHRASES',
            'SENTIMENT', 'SUBJECTIVITY', 'LDA', 'KEYPHRASES', 'NER',
            'COSINE_SIMILARITY',
            
            # Tests statistiques
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
        
        # Option: parenthèses autour du nom
        if self.peek() and self.peek()["type"] == "LPAREN":
            self.consume("LPAREN")
            node["properties"]["name"] = self.consume("IDENTIFIER")["value"]
            self.consume("RPAREN")
        else:
            node["properties"]["name"] = self.consume("IDENTIFIER")["value"]
        
        # Option: FROM
        if self.peek() and self.peek()["type"] == "FROM":
            self.consume("FROM")
            node["properties"]["source"] = self.parse_string_or_identifier()
        
        # Options WITH
        if self.peek() and self.peek()["type"] == "WITH":
            node["properties"]["options"] = self.parse_with_options()
        
        # Alias
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

        # Mode bloc
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

        # Premier argument
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
        
        # Peut être une expression ou un identifiant
        if self.peek()["type"] in self.function_types:
            arg["expression"] = self.parse_function_call()
        elif self.peek()["type"] == "IDENTIFIER":
            arg["name"] = self.consume("IDENTIFIER")["value"]
        else:
            arg["expression"] = self.parse_expression()
        
        # Alias optionnel
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
        
        # NOT operator
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

        # BETWEEN
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

        # IN
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

        # LIKE
        if op_token["type"] == "LIKE":
            operator = self.consume("LIKE")["value"]
            right = self.parse_filter_value()
            return {
                "type": "like",
                "operator": operator,
                "left": left,
                "right": right
            }

        # Opérateurs de comparaison normaux
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

        # Appel de fonction (le nom est un type de fonction)
        if token["type"] in self.function_types:
            return self.parse_function_call()

        # Colonne
        if token["type"] == "IDENTIFIER":
            return {
                "type": "column",
                "value": self.consume("IDENTIFIER")["value"]
            }

        # Valeur littérale
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
        
        # Consommer le token de fonction (qui a un type spécifique)
        name = self.consume(token["type"])["value"]
        
        # Parenthèse ouvrante
        self.consume("LPAREN")
        
        # Arguments
        args = self.parse_function_arguments(name)
        
        # Parenthèse fermante
        self.consume("RPAREN")
        
        # Clause OVER optionnelle
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
        
        # Si pas d'arguments (parenthèse fermante directe)
        if self.peek() and self.peek()["type"] == "RPAREN":
            return args
        
        # Cas spéciaux pour COUNT
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
        
        # Cas général: expressions
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
        
        # PARTITION BY
        if self.peek() and self.peek()["type"] == "PARTITION":
            self.consume("PARTITION")
            self.consume("BY")
            over["partition_by"] = [self.consume("IDENTIFIER")["value"]]
            while self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")
                over["partition_by"].append(self.consume("IDENTIFIER")["value"])
        
        # ORDER BY
        if self.peek() and self.peek()["type"] == "ORDER":
            self.consume("ORDER")
            self.consume("BY")
            over["order_by"] = [self.parse_order_by_item()]
            while self.peek() and self.peek()["type"] == "COMMA":
                self.consume("COMMA")
                over["order_by"].append(self.parse_order_by_item())
        
        # ROWS BETWEEN
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
        
        # CASE WHEN expression
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

        # Parenthèses
        if token["type"] == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr

        # Appel de fonction (le nom est un type de fonction)
        if token["type"] in self.function_types:
            return self.parse_function_call()

        # CASE WHEN
        if token["type"] == "CASE":
            return self.parse_case_when()

        # Colonne
        if token["type"] == "IDENTIFIER":
            return {
                "type": "column",
                "value": self.consume("IDENTIFIER")["value"]
            }

        # Littéral
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
        
        # Nom de l'agrégation
        item["name"] = self.consume("IDENTIFIER")["value"]
        self.consume("ASSIGN")
        
        # Appel de fonction d'agrégation
        func = self.parse_function_call()
        item["function"] = func
        
        return item

    def parse_join(self):
        """Parse join(table, on=condition, type='inner')"""
        node = {"type": "join"}
        self.consume("JOIN")
        self.consume("LPAREN")

        # Table à joindre
        node["table"] = self.consume("IDENTIFIER")["value"]

        while self.peek() and self.peek()["type"] != "RPAREN":
            if self.peek()["type"] == "COMMA":
                self.consume("COMMA")
            
            # Paramètres nommés
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






lexer = Lexer(code)
tokens = lexer.tokenise()

parser = Parser(tokens)
errors, ast = parser.parse()
print(json.dumps(errors, indent=4))
import re

class Lexer:

    tokens_types = [

    ('SKIP_COMMENT', r'^//[^\n]*|^#[^\n]*',),
    ('SKIP_BLOCK_COMMENT', r'^/\*.*?\*/',),


    ('STRING', r'^"[^"\\]*(\\.[^"\\]*)*"',),
    ('STRING', r"^'[^'\\]*(\\.[^'\\]*)*'",),


    ('LOAD', r'^Load\b',),
    ('TRANSFORM', r'^Transform\b',),
    ('ANALYSE', r'^Analyse\b',),
    ('ANALYZE', r'^Analyze\b',),
    ('VISUALIZE', r'^Visualize\b',),
    ('TRAIN', r'^Train\b',),
    ('EVALUATE', r'^Evaluate\b',),
    ('EXPORT', r'^Export\b',),
    ('IMPORT', r'^Import\b',),
    ('CONFIG', r'^CONFIG\b',),
    ('CONNECTION', r'^CONNECTION\b',),
    ('DASHBOARD', r'^DASHBOARD\b',),
    ('SECTION', r'^SECTION\b',),
    ('METRIC', r'^METRIC\b',),
    ('PLOT', r'^PLOT\b'),
    ('TABLE', r'^TABLE\b',),
    ('FILTERS', r'^FILTERS\b',),
    ('ML', r'^ML\b',),
    ('PIPELINE', r'^Pipeline\b',),
    ('OPTIMIZE', r'^Optimize\b',),
    ('IF', r'^IF\b',),
    ('ELSE', r'^ELSE\b',),
    ('ELIF', r'^ELIF\b',),
    ('FOR', r'^FOR\b',),
    ('WHILE', r'^WHILE\b',),


    ('IN', r'^IN\b'),
    ('AS', r'^as\b'),
    ('FROM', r'^from\b'),
    ('TO', r'^to\b'),
    ('WITH', r'^with\b',),
    ('SHOW', r'^show\b',),
    ('FORMAT', r'^format\b',),
    ('TRUE', r'^true\b',),
    ('FALSE', r'^false\b',),
    ('NULL', r'^null\b',),
    ('AND', r'^AND\b',),
    ('OR', r'^OR\b',),
    ('NOT', r'^NOT\b',),
    ('BETWEEN', r'^BETWEEN\b',),
    ('CASE', r'^CASE\b',),
    ('WHEN', r'^WHEN\b',),
    ('THEN', r'^THEN\b',),
    ('END', r'^END\b',),
    ('GROUP_BY', r'^group_by\b',),
    ('AGG', r'^agg\b',),
    ('HAVING', r'^having\b',),
    ("JOIN", r'^join\b',),

    # KEYWORDS - Fonctions d'agrégation
    ('SUM', r'^SUM\b',),
    ('AVG', r'^AVG\b',),
    ('MEAN', r'^MEAN\b',),
    ('MEDIAN', r'^MEDIAN\b',),
    ('MODE', r'^MODE\b',),
    ('COUNT', r'^COUNT\b',),
    ('MIN', r'^MIN\b',),
    ('MAX', r'^MAX\b',),
    ('STD', r'^STD\b',),
    ('VAR', r'^VAR\b',),
    ('SKEW', r'^SKEW\b',),
    ('KURT', r'^KURT\b',),
    ('QUANTILE', r'^QUANTILE\b',),
    ('PERCENTILE', r'^PERCENTILE\b',),
    ('CORR', r'^CORR\b',),
    ('COV', r'^COV\b',),
    ('CROSSTAB', r'^CROSSTAB\b',),
    ('FREQ', r'^FREQ\b',),
    ('TOP', r'^TOP\b',),
    ('ENTROPY', r'^ENTROPY\b',),
    ('ROW_NUMBER', r'^ROW_NUMBER\b',),

    ('SELECT', r'^select\b',),
    ('DROP', r'^drop\b',),
    ('FILTER', r'^filter\b',),
    ("CREATE_FEATURE", r'^create_feature\b',),

    ('T_TEST', r'^t_test\b',),
    ('ANOVA', r'^anova\b',),
    ('CHI2', r'^chi2_test\b',),
    ('MANN_WHITNEY', r'^mann_whitney\b',),
    ('KRUSKAL', r'^kruskal_wallis\b',),
    ('KS_TEST', r'^ks_test\b',),
    ('ADF_TEST', r'^ADF_TEST\b',),
    ('KPSS_TEST', r'^KPSS_TEST\b',),
    ('ACF', r'^ACF\b',),
    ('PACF', r'^PACF\b',),
    ('DECOMPOSE', r'^DECOMPOSE\b',),
    ('CUSUM', r'^CUSUM\b',),
    ('SEASONAL', r'^SEASONAL_STRENGTH\b',),
    ('TREND', r'^TREND\b',),
    ('EXPONENTIAL', r'^EXPONENTIAL_SMOOTHING\b',),
    ('LOG', r'^LOG\b',),

    ('WORD_COUNT', r'^WORD_COUNT\b',),
    ('SENTENCE_COUNT', r'^SENTENCE_COUNT\b',),
    ('TOP_WORDS', r'^TOP_WORDS\b',),
    ('TOP_PHRASES', r'^TOP_PHRASES\b',),
    ('SENTIMENT', r'^SENTIMENT\b',),
    ('SUBJECTIVITY', r'^SUBJECTIVITY\b',),
    ('LDA', r'^LDA\b',),
    ('KEYPHRASES', r'^KEYPHRASES\b',),
    ('NER', r'^NER\b',),
    ('COSINE_SIMILARITY', r'^COSINE_SIMILARITY\b',),

    ('HISTOGRAM', r'^histogram\b',),
    ('BAR_CHART', r'^bar_chart\b',),
    ('SCATTER', r'^scatter\b',),
    ('BOX_PLOT', r'^box_plot\b',),
    ('VIOLIN_PLOT', r'^violin_plot\b',),
    ('LINE_CHART', r'^line_chart\b',),
    ('AREA_CHART', r'^area_chart\b',),
    ('HEATMAP', r'^heatmap\b',),
    ('PAIR_PLOT', r'^pair_plot\b',),
    ('CHOROPLETH', r'^choropleth\b',),
    ('POINT_MAP', r'^point_map\b',),
    ('WORDCLOUD', r'^wordcloud\b',),
    ('DENDROGRAM', r'^dendrogram\b',),
    ('CONFUSION_MATRIX', r'^confusion_matrix\b',),
    ('ROC_CURVES', r'^roc_curves\b',),
    ('RANK', r'^RANK\b',),
    ('OVER',r'^OVER\b',),
    ('PARTITION', r'^PARTITION\b',),
    ('BY', r'^BY\b',),
    ('ORDER', r'^ORDER\b',),
    ('DESC', r'^DESC\b',),
    ('ASC', r'^ASC\b',),
    ('ROWS', r'^ROWS\b',),
    ('PRECEDING', r'^PRECEDING\b',),
    ('FOLLOWING', r'^FOLLOWING\b',),
    ('CURRENT', r'^CURRENT\b',),
    ('ROW', r'^ROW\b',),
    ('ABS',r'^ABS\b',),
    ('ROUND',r'^ROUND\b',),
    ('UNBOUNDED', r'^UNBOUNDED\b',),

    ('REGRESSION', r'^regression\b',),
    ('CLASSIFICATION', r'^classification\b',),
    ('CLUSTER', r'^cluster\b',),
    ('RANDOM_FOREST', r'^random_forest\b',),
    ('GRADIENT_BOOSTING', r'^gradient_boosting\b',),
    ('XGBOOST', r'^xgboost\b',),
    ('SVM', r'^svm\b',),
    ('SVR', r'^svr\b',),
    ('NEURAL_NETWORK', r'^neural_network\b',),
    ('LOGISTIC', r'^logistic_regression\b',),
    ('RIDGE', r'^ridge\b'),
    ('LASSO', r'^lasso\b'),
    ('ELASTIC_NET', r'^elastic_net\b',),
    ('KMEANS', r'^kmeans\b',),
    ('PCA', r'^pca\b',),
    ('SMOTE', r'^smote\b',),
    ('GRID_SEARCH', r'^grid_search\b',),
    ('RANDOM_SEARCH', r'^random_search\b',),
    ('BAYESIAN', r'^bayesian_optimization\b',),
    ('CROSS_VALIDATION', r'^cross_validation\b',),

    ('POW', r'^\*\*',),
    ('GE', r'^>=',),
    ('LE', r'^<=',),
    ('EQ', r'^==',),
    ('NE', r'^!=',),
    ('SHIFT_LEFT', r'^<<',),
    ('SHIFT_RIGHT', r'^>>',),
    ('PLUS_ASSIGN', r'^\+=',),
    ('MINUS_ASSIGN', r'^-=',),
    ('MULT_ASSIGN', r'^\*=',),
    ('DIV_ASSIGN', r'^/=',),
    ('AND_OP', r'^&&',),
    ('OR_OP', r'^\|\|',),
    ('ARROW', r'^->',),
    ('ELLIPSIS', r'^\.\.\.',),

    ('GT', r'^>',),
    ('LT', r'^<',),
    ('PLUS', r'^\+',),
    ('MINUS', r'^-',),
    ('MULT', r'^\*',),
    ('DIV', r'^/',),
    ('MOD', r'^%',),
    ('ASSIGN', r'^=',),
    ('BIT_AND', r'^&',),
    ('BIT_OR', r'^\|',),
    ('BIT_XOR', r'^\^',),
    ('BIT_NOT', r'^~',),
    ('NOT_OP', r'^!',),
    ('TERNARY', r'^\?',),

    ('FLOAT', r'^\d+\.\d+',),
    ('NUMBER', r'^\d+',),

    ('IDENTIFIER', r'^[a-zA-Z_][a-zA-Z0-9_]*',),

    ('LPAREN', r'^\(',),
    ('RPAREN', r'^\)',),
    ('LBRACE', r'^\{',),
    ('RBRACE', r'^\}',),
    ('LBRACKET', r'^\[',),
    ('RBRACKET', r'^\]',),
    ('SEMICOLON', r'^;',),
    ('COLON', r'^:',),
    ('COMMA', r'^,',),
    ('DOT', r'^\.',),
    ('INTERPOLATION', r'^\$\{',),

    ('NEWLINE', r'^\n',),
    ('WHITESPACE', r'^[ \t]+',)
]

    def __init__(self, input_text):
        self.input = input_text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []

    def tokenise(self):
        while self.pos < len(self.input):
            matched = False
            for token_type, pattern in self.tokens_types:
                flags = re.DOTALL if token_type == 'SKIP_BLOCK_COMMENT' else 0
                match = re.match(pattern, self.input[self.pos:], flags)

                if match:
                    value = match.group(0)


                    if token_type in ["NEWLINE", "WHITESPACE", "SKIP_COMMENT", "SKIP_BLOCK_COMMENT"]:

                        self._update_position(value)
                        matched = True
                        break
                    else:

                        self.tokens.append({
                            "type": token_type,
                            "value": value,
                            "line": self.line,
                            "col": self.col
                        })
                        self._update_position(value)
                        matched = True
                        break
            if not matched:
                raise Exception(
                    f"Lexing error at line:{self.line}, col:{self.col} "
                    f"unexpected character: '{self.input[self.pos]}'"
                )
        return self.tokens

    def _update_position(self, value):

        lines = value.count('\n')
        if lines > 0:
            self.line += lines
            self.col = len(value) - value.rfind('\n') - 1
        else:
            self.col += len(value)
        self.pos += len(value)

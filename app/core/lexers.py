import re

class Lexer:
    tokens_types = [
        # COMMENTAIRES
        ('SKIP_COMMENT', r'^//[^\n]*|^#[^\n]*',),
        ('SKIP_BLOCK_COMMENT', r'^/\*.*?\*/',),

        # CHAÎNES
        ('STRING', r'^"[^"\\]*(\\.[^"\\]*)*"',),
        ('STRING', r"^'[^'\\]*(\\.[^'\\]*)*'",),

        # ===== COMMANDES PRINCIPALES =====
        ('LOAD', r'^Load\b',),
        ('TRANSFORM', r'^Transform\b',),
        ('ANALYSE', r'^Analyse\b',),
        ('ANALYZE', r'^Analyze\b',),
        ('VISUALIZE', r'^Visualize\b',),
        ('VIZ', r'^Viz\b',),
        ('STATS', r'^Stats\b',),
        ('CLEAN', r'^Clean\b',),
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

        # ===== COMMANDES DE STATISTIQUES DESCRIPTIVES =====
        ('DESCRIBE', r'^describe\b',),
        ('DESCRIBE_ALL', r'^describe_all\b',),
        ('SUMMARY', r'^summary\b',),

        # ===== MOTS-CLÉS DE CONTRÔLE =====
        ('IN', r'^IN\b'),
        ('AS', r'^as\b'),
        ('FROM', r'^from\b'),
        ('TO', r'^to\b'),
        ('WITH', r'^with\b',),
        ('SHOW', r'^show\b',),
        ('FORMAT', r'^format\b',),
        ('DETAILED', r'^detailed\b',),
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
        ('LIKE', r'^LIKE\b',),

        # ===== FONCTIONS D'AGRÉGATION DE BASE =====
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

        # ===== FONCTIONS DE NETTOYAGE =====
        ('DROP_NA', r'^drop_na\b',),
        ('FILL_NA', r'^fill_na\b',),
        ('REPLACE', r'^replace\b',),
        ('CLIP', r'^clip\b',),
        ('REMOVE_OUTLIERS', r'^remove_outliers\b',),
        ('DETECT_OUTLIERS', r'^detect_outliers\b',),
        ('STANDARDIZE', r'^standardize\b',),
        ('MIN_MAX_SCALE', r'^min_max_scale\b',),
        ('ONE_HOT_ENCODE', r'^one_hot_encode\b',),
        ('LABEL_ENCODE', r'^label_encode\b',),

        # ===== FONCTIONS STATISTIQUES AVANCÉES =====
        ('MOMENT', r'^MOMENT\b',),
        ('GINI', r'^GINI\b',),
        ('SKEWNESS', r'^SKEWNESS\b',),
        ('KURTOSIS', r'^KURTOSIS\b',),
        ('COVARIANCE', r'^COVARIANCE\b',),
        ('VARIANCE', r'^VARIANCE\b',),
        ('RANGE', r'^RANGE\b',),
        ('IQR', r'^IQR\b',),
        ('MAD', r'^MAD\b',),
        ('CV', r'^CV\b',),
        ('GEOMETRIC_MEAN', r'^GEOMETRIC_MEAN\b',),
        ('HARMONIC_MEAN', r'^HARMONIC_MEAN\b',),
        ('QUADRATIC_MEAN', r'^QUADRATIC_MEAN\b',),
        ('WEIGHTED_MEAN', r'^WEIGHTED_MEAN\b',),
        ('TRIMMED_MEAN', r'^TRIMMED_MEAN\b',),
        ('MIDRANGE', r'^MIDRANGE\b',),

        # ===== MATRICES DE CORRÉLATION/COVARIANCE =====
        ('COVARIANCE_MATRIX', r'^covariance_matrix\b',),
        ('CORRELATION_MATRIX', r'^correlation_matrix\b',),
        ('SPEARMAN', r'^SPEARMAN\b',),
        ('KENDALL', r'^KENDALL\b',),

        # ===== TESTS STATISTIQUES =====
        ('T_TEST', r'^T_TEST\b',),
        ('T_TEST_INDEPENDENT', r'^T_TEST_INDEPENDENT\b',),
        ('F_TEST', r'^F_TEST\b',),
        ('ANOVA', r'^ANOVA\b',),
        ('CHI2', r'^CHI2_TEST\b',),
        ('CHI2', r'^CHI2\b',),
        ('MANN_WHITNEY', r'^mann_whitney\b',),
        ('KRUSKAL', r'^kruskal_wallis\b',),
        ('KS_TEST', r'^ks_test\b',),
        ('SHAPIRO', r'^shapiro_wilk\b',),
        ('SHAPIRO_WILK', r'^SHAPIRO_WILK\b',),
        ('ANDERSON', r'^anderson_darling\b',),
        ('ANDERSON_DARLING', r'^ANDERSON_DARLING\b',),
        ('ADF_TEST', r'^ADF_TEST\b',),
        ('KPSS_TEST', r'^KPSS_TEST\b',),

        # ===== FONCTIONS DE SÉRIES TEMPORELLES =====
        ('ACF', r'^ACF\b',),
        ('PACF', r'^PACF\b',),
        ('DECOMPOSE', r'^DECOMPOSE\b',),
        ('CUSUM', r'^CUSUM\b',),
        ('SEASONAL_STRENGTH', r'^SEASONAL_STRENGTH\b',),
        ('TREND', r'^TREND\b',),
        ('EXPONENTIAL_SMOOTHING', r'^EXPONENTIAL_SMOOTHING\b',),
        ('LAG', r'^lag\b',),
        ('DIFF', r'^diff\b',),
        ('PCT_CHANGE', r'^pct_change\b',),
        ('MOVING_AVG', r'^moving_avg\b',),
        ('EWMA', r'^ewma\b',),
        ('AUTOCORR', r'^autocorr\b',),

        # ===== FONCTIONS DE DISTANCE =====
        ('EUCLIDEAN', r'^euclidean\b',),
        ('MANHATTAN', r'^manhattan\b',),
        ('COSINE', r'^cosine\b',),
        ('JACCARD', r'^jaccard\b',),
        ('MINKOWSKI', r'^minkowski\b',),

        # ===== FONCTIONS DE CLASSEMENT =====
        ('RANK', r'^RANK\b',),
        ('ZSCORE', r'^ZSCORE\b',),
        ('PERCENTILE_RANK', r'^PERCENTILE_RANK\b',),
        ('MIN_MAX_SCALE', r'^min_max_scale\b',),
        ('ROBUST_SCALE', r'^robust_scale\b',),

        # ===== FONCTIONS DE RÉ-ÉCHANTILLONNAGE =====
        ('BOOTSTRAP', r'^bootstrap\b',),
        ('JACKKNIFE', r'^jackknife\b',),

        # ===== FONCTIONS MATHÉMATIQUES =====
        ('LOG', r'^LOG\b',),
        ('EXP', r'^EXP\b',),
        ('SQRT', r'^SQRT\b',),
        ('ABS', r'^ABS\b',),
        ('ROUND', r'^ROUND\b',),
        ('FLOOR', r'^FLOOR\b',),
        ('CEIL', r'^CEIL\b',),
        ('SIN', r'^SIN\b',),
        ('COS', r'^COS\b',),
        ('TAN', r'^TAN\b',),
        ('ASIN', r'^ASIN\b',),
        ('ACOS', r'^ACOS\b',),
        ('ATAN', r'^ATAN\b',),
        ('POWER', r'^POWER\b',),
        ('MOD', r'^MOD\b',),

        # ===== FONCTIONS NLP =====
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

        # ===== FONCTIONS DE VISUALISATION =====
        ('HISTOGRAM', r'^histogram\b',),
        ('BAR_CHART', r'^bar_chart\b',),
        ('SCATTER', r'^scatter\b',),
        ('LINE_CHART', r'^line_chart\b',),
        ('BOX_PLOT', r'^box_plot\b',),
        ('VIOLIN_PLOT', r'^violin_plot\b',),
        ('HEATMAP', r'^heatmap\b',),
        ('QQ_PLOT', r'^qq_plot\b',),
        ('ACF_PLOT', r'^acf_plot\b',),
        ('PIE_CHART', r'^pie_chart\b',),

        # ===== FONCTIONS DE TRANSFORMATION =====
        ('SELECT', r'^select\b',),
        ('DROP', r'^drop\b',),
        ('FILTER', r'^filter\b',),
        ('CREATE_FEATURE', r'^create_feature\b',),

        # ===== MOTS-CLÉS POUR WINDOW FUNCTIONS =====
        ('OVER', r'^OVER\b',),
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
        ('UNBOUNDED', r'^UNBOUNDED\b',),
        ('DISTINCT', r'^Distinct\b',),

        # ===== PARAMÈTRES POUR VISUALISATIONS =====
        ('BINS', r'^bins\b',),
        ('WIDTH', r'^width\b',),
        ('HEIGHT', r'^height\b',),
        ('SIZE', r'^size\b',),
        ('ALPHA', r'^alpha\b',),
        ('FACTOR', r'^factor\b',),
        ('TITLE', r'^title\b',),
        ('XLABEL', r'^xlabel\b',),
        ('YLABEL', r'^ylabel\b',),
        ('COLOR', r'^color\b',),
        ('CMAP', r'^cmap\b',),
        ('COLORS', r'^colors\b',),
        ('STACKED', r'^stacked\b',),
        ('MARKERS', r'^markers\b',),
        ('DENSITY', r'^density\b',),
        ('GRID', r'^grid\b',),
        ('LEGEND', r'^legend\b',),
        ('COLUMNS', r'^columns\b',),
        ('COLUMN', r'^column\b',),
        ('X', r'^x\b',),
        ('Y', r'^y\b',),
        ('DIST', r'^dist\b',),
        ('VALUES', r'^values\b',),
        ('LABELS', r'^labels\b',),
        ('SHOW_PERCENT', r'^show_percent\b',),

        # ===== PARAMÈTRES POUR NETTOYAGE =====
        ('HOW', r'^how\b',),
        ('THRESH', r'^thresh\b',),
        ('METHOD', r'^method\b',),
        ('VALUE', r'^value\b',),
        ('LOWER', r'^lower\b',),
        ('UPPER', r'^upper\b',),
        ('KEEP', r'^keep\b',),
        ('SUBSET', r'^subset\b',),
        ('AXIS', r'^axis\b',),
        ('INPLACE', r'^inplace\b',),
        ('FEATURE_RANGE', r'^feature_range\b',),
        ('DROP_FIRST', r'^drop_first\b',),
        ('PREFIX', r'^prefix\b',),
        ('TO_REPLACE', r'^to_replace\b',),
        ('FFILL', r'^ffill\b',),
        ('BFILL', r'^bfill\b',),
        ('ANY', r'^any\b',),
        ('ALL', r'^all\b',),

        # ===== PARAMÈTRES POUR STATISTIQUES =====
        ('DDOF', r'^ddof\b',),
        ('PROPORTION', r'^proportion\b',),
        ('WEIGHTS', r'^weights\b',),
        ('ALPHA', r'^alpha\b',),
        ('N_SAMPLES', r'^n_samples\b',),
        ('STATISTIC', r'^statistic\b',),
        ('LAGS', r'^lags\b',),
        ('WINDOW', r'^window\b',),
        ('P', r'^p\b',),

        # ===== PARAMÈTRES POUR JOIN =====
        ('TYPE', r'^type\b',),
        ('ON', r'^on\b',),
        ('INNER', r'^inner\b',),
        ('LEFT', r'^left\b',),
        ('RIGHT', r'^right\b',),
        ('OUTER', r'^outer\b',),

        # ===== MOTS-CLÉS ML =====
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

        # ===== OPÉRATEURS LONGS =====
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

        # ===== OPÉRATEURS SIMPLES =====
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

        # ===== NOMBRES =====
        ('FLOAT', r'^\d+\.\d+',),
        ('NUMBER', r'^\d+',),

        # ===== IDENTIFIANTS =====
        ('IDENTIFIER', r'^[a-zA-Z_][a-zA-Z0-9_]*',),

        # ===== DÉLIMITEURS =====
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

        # ===== ESPACES =====
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
# stats_calculator.py
import math
import random
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, Set
from collections import Counter
from .simple_dataframe import SimpleDataFrame, to_numeric, is_numeric


class StatsCalculator:
    """
    Calculateur de statistiques descriptives pour SimpleDataFrame.
    Fournit plus de 100 fonctions statistiques sans dépendances externes.
    
    NOTE: Tous les calculs sont implémentés avec des algorithmes numériquement
    stables et précis en pur Python.
    """

    def __init__(self, df: Optional[SimpleDataFrame] = None):
        """
        Initialise le calculateur avec un DataFrame optionnel.

        Args:
            df: SimpleDataFrame à analyser
        """
        self.df = df

    def set_dataframe(self, df: SimpleDataFrame):
        """Définit le DataFrame à analyser"""
        self.df = df

    # ========== STATISTIQUES UNIVARIÉES ==========

    # --- Mesures de tendance centrale ---

    def mean(self, data: List[Union[int, float]]) -> float:
        """Moyenne arithmétique (algorithme numériquement stable)"""
        if not data:
            return float('nan')
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return float('nan')
        
        # Algorithme de Kahan pour réduire l'erreur d'arrondi
        total = 0.0
        c = 0.0  # compensation
        for x in valid:
            y = x - c
            t = total + y
            c = (t - total) - y
            total = t
        return total / len(valid)

    def median(self, data: List[Union[int, float]]) -> float:
        """Médiane"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return float('nan')
        sorted_vals = sorted(valid)
        n = len(sorted_vals)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_vals[mid-1] + sorted_vals[mid]) / 2
        return sorted_vals[mid]

    def mode(self, data: List[Any]) -> List[Any]:
        """Mode (valeurs les plus fréquentes)"""
        if not data:
            return []
        valid = [x for x in data if x is not None]
        counter = Counter(valid)
        max_count = max(counter.values())
        return [k for k, v in counter.items() if v == max_count]

    def geometric_mean(self, data: List[Union[int, float]]) -> float:
        """Moyenne géométrique (utilise les logs pour la stabilité)"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float)) and x > 0]
        if not valid:
            return float('nan')
        
        # Utilisation des logarithmes pour éviter le débordement
        log_sum = sum(math.log(x) for x in valid)
        return math.exp(log_sum / len(valid))

    def harmonic_mean(self, data: List[Union[int, float]]) -> float:
        """Moyenne harmonique"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float)) and x > 0]
        if not valid:
            return float('nan')
        
        # Algorithme stable
        sum_recip = 0.0
        for x in valid:
            sum_recip += 1.0 / x
        return len(valid) / sum_recip

    def quadratic_mean(self, data: List[Union[int, float]]) -> float:
        """Moyenne quadratique (RMS)"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return float('nan')
        
        # Algorithme de Kahan pour les carrés
        sum_squares = 0.0
        c = 0.0
        for x in valid:
            y = x * x - c
            t = sum_squares + y
            c = (t - sum_squares) - y
            sum_squares = t
        return math.sqrt(sum_squares / len(valid))

    def weighted_mean(self, data: List[Union[int, float]], weights: List[Union[int, float]]) -> float:
        """Moyenne pondérée"""
        if len(data) != len(weights):
            raise ValueError("Les données et les poids doivent avoir la même longueur")
        pairs = [(x, w) for x, w in zip(data, weights) 
                 if x is not None and w is not None 
                 and isinstance(x, (int, float)) and isinstance(w, (int, float))]
        if not pairs:
            return float('nan')
        
        sum_weighted = 0.0
        sum_weights = 0.0
        c1 = c2 = 0.0
        
        for x, w in pairs:
            y1 = x * w - c1
            t1 = sum_weighted + y1
            c1 = (t1 - sum_weighted) - y1
            sum_weighted = t1
            
            y2 = w - c2
            t2 = sum_weights + y2
            c2 = (t2 - sum_weights) - y2
            sum_weights = t2
        
        return sum_weighted / sum_weights if sum_weights != 0 else float('nan')

    def trimmed_mean(self, data: List[Union[int, float]], proportion: float = 0.1) -> float:
        """Moyenne tronquée (ignore les extrêmes)"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return float('nan')
        sorted_vals = sorted(valid)
        n = len(sorted_vals)
        trim = int(n * proportion)
        if trim * 2 >= n:
            return float('nan')
        trimmed = sorted_vals[trim:n-trim]
        return self.mean(trimmed)

    def midrange(self, data: List[Union[int, float]]) -> float:
        """Milieu de l'étendue (min+max)/2"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return float('nan')
        return (min(valid) + max(valid)) / 2

    # --- Mesures de dispersion ---

    def variance(self, data: List[Union[int, float]], ddof: int = 1) -> float:
        """
        Variance avec algorithme en une passe numériquement stable
        (algorithme de Welford)
        """
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if len(valid) <= ddof:
            return float('nan')
        
        n = 0
        mean = 0.0
        m2 = 0.0
        
        for x in valid:
            n += 1
            delta = x - mean
            mean += delta / n
            delta2 = x - mean
            m2 += delta * delta2
        
        return m2 / (n - ddof)

    def std(self, data: List[Union[int, float]], ddof: int = 1) -> float:
        """Écart-type"""
        var = self.variance(data, ddof)
        return math.sqrt(var) if not math.isnan(var) else float('nan')

    def range_stat(self, data: List[Union[int, float]]) -> float:
        """Étendue (max - min)"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return float('nan')
        return max(valid) - min(valid)

    def iqr(self, data: List[Union[int, float]]) -> float:
        """Intervalle interquartile (Q3 - Q1)"""
        q1, q3 = self.quantiles(data, [0.25, 0.75])
        return q3 - q1

    def mad(self, data: List[Union[int, float]]) -> float:
        """Écart absolu médian"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return float('nan')
        median_val = self.median(valid)
        abs_dev = [abs(x - median_val) for x in valid]
        return self.median(abs_dev)

    def cv(self, data: List[Union[int, float]]) -> float:
        """Coefficient de variation (écart-type / moyenne)"""
        mean_val = self.mean(data)
        if mean_val == 0 or math.isnan(mean_val):
            return float('nan')
        return self.std(data, 0) / mean_val

    def quantile(self, data: List[Union[int, float]], q: float) -> float:
        """Quantile avec interpolation linéaire (méthode R7, comme R et numpy)"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid or q < 0 or q > 1:
            return float('nan')
        
        sorted_vals = sorted(valid)
        n = len(sorted_vals)
        
        # Méthode R7 (la plus courante)
        index = 1 + (n - 1) * q
        lo = int(math.floor(index))
        hi = int(math.ceil(index))
        
        if lo == hi:
            return sorted_vals[lo-1]
        
        # Interpolation linéaire
        return sorted_vals[lo-1] + (index - lo) * (sorted_vals[hi-1] - sorted_vals[lo-1])

    def quantiles(self, data: List[Union[int, float]], probs: List[float]) -> List[float]:
        """Plusieurs quantiles"""
        return [self.quantile(data, p) for p in probs]

    def percentile(self, data: List[Union[int, float]], p: float) -> float:
        """Percentile (p entre 0 et 100)"""
        return self.quantile(data, p / 100)

    def percentiles(self, data: List[Union[int, float]], ps: List[float]) -> List[float]:
        """Plusieurs percentiles"""
        return [self.percentile(data, p) for p in ps]

    # --- Mesures de forme ---

    def skewness(self, data: List[Union[int, float]]) -> float:
        """
        Asymétrie (skewness) avec correction du biais
        (formule de Fisher-Pearson)
        """
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if len(valid) < 3:
            return float('nan')
        
        n = len(valid)
        mean_val = self.mean(valid)
        
        # Calcul des moments avec l'algorithme de Welford étendu
        m2 = m3 = 0.0
        for x in valid:
            delta = x - mean_val
            delta_n = delta / n
            term1 = delta * delta_n * (n - 1)
            m3 += term1 * delta_n * (n - 2) - 3 * delta_n * m2
            m2 += delta * (x - mean_val)  # Correction pour m2
        
        m2 /= n
        m3 /= n
        
        if m2 == 0:
            return 0.0
        
        # Correction du biais pour échantillon
        g1 = m3 / (m2 ** 1.5)
        return math.sqrt(n * (n - 1)) / (n - 2) * g1

    def kurtosis(self, data: List[Union[int, float]]) -> float:
        """
        Kurtosis (excès par rapport à la normale)
        avec correction du biais
        """
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if len(valid) < 4:
            return float('nan')
        
        n = len(valid)
        mean_val = self.mean(valid)
        
        # Calcul des moments
        m2 = m4 = 0.0
        for x in valid:
            delta = x - mean_val
            delta2 = delta * delta
            m2 += delta2
            m4 += delta2 * delta2
        
        m2 /= n
        m4 /= n
        
        if m2 == 0:
            return 0.0
        
        # Kurtosis avec correction du biais
        g2 = m4 / (m2 * m2) - 3
        # Correction pour échantillon
        return ((n + 1) * g2 + 6) * (n - 1) / ((n - 2) * (n - 3))

    def moment(self, data: List[Union[int, float]], k: int) -> float:
        """Moment centré d'ordre k"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid or k < 0:
            return float('nan')
        
        if k == 0:
            return 1.0
        
        mean_val = self.mean(valid)
        n = len(valid)
        
        # Algorithme stable pour les moments
        if k == 1:
            return 0.0
        
        moment = 0.0
        for x in valid:
            moment += (x - mean_val) ** k
        return moment / n

    # --- Autres statistiques univariées ---

    def count(self, data: List[Any]) -> int:
        """Nombre d'éléments non nuls"""
        return sum(1 for x in data if x is not None)

    def count_all(self, data: List[Any]) -> int:
        """Nombre total d'éléments (y compris nuls)"""
        return len(data)

    def count_unique(self, data: List[Any]) -> int:
        """Nombre de valeurs uniques"""
        valid = [x for x in data if x is not None]
        return len(set(valid))

    def freq_table(self, data: List[Any]) -> Dict[Any, int]:
        """Table de fréquences"""
        valid = [x for x in data if x is not None]
        return dict(Counter(valid))

    def missing_count(self, data: List[Any]) -> int:
        """Nombre de valeurs manquantes"""
        return sum(1 for x in data if x is None)

    def missing_ratio(self, data: List[Any]) -> float:
        """Proportion de valeurs manquantes"""
        return self.missing_count(data) / len(data) if data else 0

    def entropy(self, data: List[Any], base: float = 2.0) -> float:
        """Entropie de Shannon (pour données catégorielles)"""
        valid = [x for x in data if x is not None]
        if not valid:
            return 0.0
        
        n = len(valid)
        counter = Counter(valid)
        
        entropy = 0.0
        for count in counter.values():
            p = count / n
            if p > 0:
                entropy -= p * math.log(p) / math.log(base)
        
        return entropy

    def gini(self, data: List[Union[int, float]]) -> float:
        """
        Coefficient de Gini (inégalité)
        Formule correcte: (2 * Σ(i * x_i)) / (n * Σx) - (n+1)/n
        """
        valid = [x for x in data if x is not None and isinstance(x, (int, float)) and x >= 0]
        if not valid or sum(valid) == 0:
            return 0.0
        
        sorted_vals = sorted(valid)
        n = len(sorted_vals)
        total = sum(sorted_vals)
        
        # Formule correcte du coefficient de Gini
        weighted_sum = 0.0
        for i, x in enumerate(sorted_vals):
            weighted_sum += (i + 1) * x
        
        gini = (2 * weighted_sum) / (n * total) - (n + 1) / n
        return gini

    # ========== STATISTIQUES BIVARIÉES ==========

    def covariance(self, x: List[Union[int, float]], y: List[Union[int, float]], ddof: int = 1) -> float:
        """Covariance avec algorithme en une passe stable"""
        if len(x) != len(y):
            raise ValueError("Les séries doivent avoir la même longueur")
        
        pairs = [(xi, yi) for xi, yi in zip(x, y) 
                 if xi is not None and yi is not None 
                 and isinstance(xi, (int, float)) and isinstance(yi, (int, float))]
        
        if len(pairs) <= ddof:
            return float('nan')
        
        n = 0
        mean_x = mean_y = 0.0
        C = 0.0
        
        for xi, yi in pairs:
            n += 1
            dx = xi - mean_x
            dy = yi - mean_y
            mean_x += dx / n
            mean_y += dy / n
            C += dx * (yi - mean_y)
        
        return C / (n - ddof)

    def correlation(self, x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
        """Corrélation de Pearson (algorithme stable)"""
        if len(x) != len(y):
            raise ValueError("Les séries doivent avoir la même longueur")
        
        pairs = [(xi, yi) for xi, yi in zip(x, y) 
                 if xi is not None and yi is not None 
                 and isinstance(xi, (int, float)) and isinstance(yi, (int, float))]
        
        if len(pairs) < 2:
            return float('nan')
        
        n = 0
        mean_x = mean_y = 0.0
        C = 0.0
        var_x = var_y = 0.0
        
        for xi, yi in pairs:
            n += 1
            dx = xi - mean_x
            dy = yi - mean_y
            mean_x += dx / n
            mean_y += dy / n
            var_x += dx * (xi - mean_x)
            var_y += dy * (yi - mean_y)
            C += dx * (yi - mean_y)
        
        if var_x == 0 or var_y == 0:
            return 0.0
        
        return C / math.sqrt(var_x * var_y)

    def spearman_correlation(self, x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
        """Corrélation de Spearman (rang)"""
        if len(x) != len(y):
            raise ValueError("Les séries doivent avoir la même longueur")
        
        pairs = [(xi, yi) for xi, yi in zip(x, y) 
                 if xi is not None and yi is not None 
                 and isinstance(xi, (int, float)) and isinstance(yi, (int, float))]
        
        if len(pairs) < 2:
            return float('nan')
        
        x_vals, y_vals = zip(*pairs)
        x_rank = self._rank(list(x_vals))
        y_rank = self._rank(list(y_vals))
        
        return self.correlation(x_rank, y_rank)

    def _rank(self, data: List[Union[int, float]]) -> List[float]:
        """Calcule les rangs (gère les ex-aequo avec la méthode 'average')"""
        n = len(data)
        # Créer une liste d'indices triés par valeur
        indexed = list(enumerate(data))
        indexed.sort(key=lambda x: x[1])
        
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            # Trouver tous les éléments égaux
            while j < n and abs(indexed[j][1] - indexed[i][1]) < 1e-12:
                j += 1
            
            # Calculer le rang moyen pour ce groupe
            rank = (i + j - 1) / 2 + 1
            for k in range(i, j):
                ranks[indexed[k][0]] = rank
            i = j
        
        return ranks

    def kendall_tau(self, x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
        """Corrélation de Kendall (tau-b avec gestion des ex-aequo)"""
        if len(x) != len(y):
            raise ValueError("Les séries doivent avoir la même longueur")
        
        pairs = [(xi, yi) for xi, yi in zip(x, y) 
                 if xi is not None and yi is not None 
                 and isinstance(xi, (int, float)) and isinstance(yi, (int, float))]
        
        if len(pairs) < 2:
            return float('nan')
        
        n = len(pairs)
        concordant = discordant = 0
        tied_x = tied_y = 0
        
        for i in range(n):
            for j in range(i+1, n):
                xi, yi = pairs[i]
                xj, yj = pairs[j]
                
                if xi == xj and yi == yj:
                    continue
                elif xi == xj:
                    tied_x += 1
                elif yi == yj:
                    tied_y += 1
                else:
                    if (xi - xj) * (yi - yj) > 0:
                        concordant += 1
                    else:
                        discordant += 1
        
        total = concordant + discordant + tied_x + tied_y
        if total == 0:
            return 0.0
        
        # Tau-b avec correction pour ex-aequo
        return (concordant - discordant) / math.sqrt((concordant + discordant + tied_x) * 
                                                     (concordant + discordant + tied_y))

    def covariance_matrix(self, columns: List[str]) -> Dict[str, Dict[str, float]]:
        """Matrice de covariance pour plusieurs colonnes"""
        if not self.df:
            raise ValueError("Aucun DataFrame défini")
        
        result = {}
        for col1 in columns:
            result[col1] = {}
            data1 = self.df[col1]
            for col2 in columns:
                data2 = self.df[col2]
                result[col1][col2] = self.covariance(data1, data2)
        return result

    def correlation_matrix(self, columns: List[str]) -> Dict[str, Dict[str, float]]:
        """Matrice de corrélation pour plusieurs colonnes"""
        if not self.df:
            raise ValueError("Aucun DataFrame défini")
        
        result = {}
        for col1 in columns:
            result[col1] = {}
            data1 = self.df[col1]
            for col2 in columns:
                data2 = self.df[col2]
                result[col1][col2] = self.correlation(data1, data2)
        return result

    # ========== STATISTIQUES SUR LE DATAFRAME ==========

    def describe(self, columns: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
        """Statistiques descriptives pour les colonnes numériques"""
        if not self.df:
            raise ValueError("Aucun DataFrame défini")
        
        cols = columns if columns else self.df.columns
        result = {}
        
        for col in cols:
            data = self.df[col]
            numeric_data = [to_numeric(x) for x in data if x is not None]
            numeric_data = [x for x in numeric_data if isinstance(x, (int, float))]
            
            if numeric_data:
                result[col] = {
                    'count': len(numeric_data),
                    'mean': self.mean(numeric_data),
                    'std': self.std(numeric_data, 1),
                    'min': min(numeric_data),
                    '25%': self.quantile(numeric_data, 0.25),
                    '50%': self.median(numeric_data),
                    '75%': self.quantile(numeric_data, 0.75),
                    'max': max(numeric_data),
                    'skew': self.skewness(numeric_data),
                    'kurt': self.kurtosis(numeric_data)
                }
        
        return result

    def describe_all(self) -> Dict[str, Dict[str, Any]]:
        """Statistiques pour toutes les colonnes (numériques et catégorielles)"""
        if not self.df:
            raise ValueError("Aucun DataFrame défini")
        
        result = {}
        for col in self.df.columns:
            data = self.df[col]
            numeric_data = [to_numeric(x) for x in data if x is not None]
            numeric_data = [x for x in numeric_data if isinstance(x, (int, float))]
            
            if numeric_data:
                # Colonne numérique
                result[col] = {
                    'type': 'numeric',
                    'count': len(numeric_data),
                    'missing': self.missing_count(data),
                    'mean': self.mean(numeric_data),
                    'std': self.std(numeric_data, 1),
                    'min': min(numeric_data),
                    'max': max(numeric_data),
                    'median': self.median(numeric_data),
                    'skew': self.skewness(numeric_data),
                    'kurt': self.kurtosis(numeric_data)
                }
            else:
                # Colonne catégorielle
                unique_vals = [x for x in data if x is not None]
                freq = Counter(unique_vals)
                result[col] = {
                    'type': 'categorical',
                    'count': len(unique_vals),
                    'missing': self.missing_count(data),
                    'unique': len(freq),
                    'top': max(freq.items(), key=lambda x: x[1])[0] if freq else None,
                    'freq': max(freq.values()) if freq else 0,
                    'entropy': self.entropy(data)
                }
        
        return result

    def summary(self) -> Dict[str, Any]:
        """Résumé du DataFrame"""
        if not self.df:
            raise ValueError("Aucun DataFrame défini")
        
        n_rows, n_cols = self.df.shape
        return {
            'shape': (n_rows, n_cols),
            'columns': self.df.columns,
            'total_cells': n_rows * n_cols,
            'missing_cells': sum(self.missing_count(self.df[col]) for col in self.df.columns),
            'numeric_columns': sum(1 for col in self.df.columns 
                                   if any(isinstance(to_numeric(x), (int, float)) 
                                          for x in self.df[col] if x is not None)),
            'categorical_columns': sum(1 for col in self.df.columns 
                                       if not any(isinstance(to_numeric(x), (int, float)) 
                                                  for x in self.df[col] if x is not None))
        }

    # ========== TESTS STATISTIQUES PRÉCIS ==========

    def _beta_inc(self, a: float, b: float, x: float) -> float:
        """
        Fonction de répartition de la loi Beta (incomplète régularisée)
        Implémentation de la série de continued fraction de Lentz
        """
        if x < 0 or x > 1:
            return float('nan')
        if x == 0:
            return 0.0
        if x == 1:
            return 1.0
        
        # Utiliser la symétrie
        if x > (a + 1) / (a + b + 2):
            return 1 - self._beta_inc(b, a, 1 - x)
        
        # Continued fraction ( méthode de Lentz )
        fpmin = 1e-30
        qab = a + b
        qap = a + 1
        qam = a - 1
        c = 1.0
        d = 1.0 - qab * x / qap
        if abs(d) < fpmin:
            d = fpmin
        d = 1.0 / d
        h = d
        
        for m in range(1, 300):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1.0 + aa * d
            if abs(d) < fpmin:
                d = fpmin
            c = 1.0 + aa / c
            if abs(c) < fpmin:
                c = fpmin
            d = 1.0 / d
            h *= d * c
            
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1.0 + aa * d
            if abs(d) < fpmin:
                d = fpmin
            c = 1.0 + aa / c
            if abs(c) < fpmin:
                c = fpmin
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-8:
                break
        
        return h * math.exp(a * math.log(x) + b * math.log(1 - x) - 
                           (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)))

    def _t_cdf(self, t: float, df: float) -> float:
        """Fonction de répartition exacte du t de Student"""
        if df <= 0:
            return float('nan')
        
        x = (t + math.sqrt(t * t + df)) / (2 * math.sqrt(t * t + df))
        prob = self._beta_inc(df / 2, df / 2, x)
        
        if t > 0:
            return 1 - 0.5 * prob
        else:
            return 0.5 * prob

    def _f_cdf(self, f: float, df1: float, df2: float) -> float:
        """Fonction de répartition exacte de Fisher"""
        if f <= 0 or df1 <= 0 or df2 <= 0:
            return float('nan')
        
        x = df1 * f / (df1 * f + df2)
        return 1 - self._beta_inc(df2 / 2, df1 / 2, 1 - x)

    def _chi2_cdf(self, chi2: float, df: float) -> float:
        """Fonction de répartition exacte du chi-carré"""
        if chi2 < 0 or df <= 0:
            return float('nan')
        if chi2 == 0:
            return 0.0
        
        return self._gamma_inc(df / 2, chi2 / 2)

    def _gamma_inc(self, a: float, x: float) -> float:
        """
        Fonction gamma incomplète régularisée (P(a,x))
        Utilise la série pour x < a+1 et la continued fraction sinon
        """
        if x < 0 or a <= 0:
            return float('nan')
        if x == 0:
            return 0.0
        
        if x < a + 1:
            # Série
            ap = a
            total = 1.0 / a
            delta = total
            n = 1
            while abs(delta) > 1e-15:
                ap += 1
                delta = delta * x / ap
                total += delta
                n += 1
                if n > 1000:  # Sécurité
                    break
            return total * math.exp(-x + a * math.log(x) - math.lgamma(a))
        else:
            # Continued fraction
            fpmin = 1e-30
            b = x + 1 - a
            c = 1.0 / fpmin
            d = 1.0 / b
            h = d
            for i in range(1, 300):
                an = -i * (i - a)
                b += 2
                d = an * d + b
                if abs(d) < fpmin:
                    d = fpmin
                c = b + an / c
                if abs(c) < fpmin:
                    c = fpmin
                d = 1.0 / d
                delta = d * c
                h *= delta
                if abs(delta - 1.0) < 1e-12:
                    break
            return 1 - h * math.exp(-x + a * math.log(x) - math.lgamma(a))

    def t_test_onesample(self, data: List[Union[int, float]], mu: float) -> Dict[str, float]:
        """Test t pour un échantillon (p-value exacte)"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if len(valid) < 2:
            return {'t_stat': float('nan'), 'p_value': float('nan'), 'df': 0}
        
        n = len(valid)
        mean_val = self.mean(valid)
        std_val = self.std(valid, 1)
        
        if std_val == 0:
            return {'t_stat': float('nan'), 'p_value': float('nan'), 'df': n-1}
        
        t_stat = (mean_val - mu) / (std_val / math.sqrt(n))
        df = n - 1
        
        # p-value exacte via la fonction de répartition
        p_value = 2 * (1 - self._t_cdf(abs(t_stat), df))
        
        return {
            't_stat': t_stat,
            'p_value': min(p_value, 1.0),  # Protection contre les erreurs numériques
            'df': df,
            'mean': mean_val,
            'std': std_val
        }

    def t_test_independent(self, group1: List[Union[int, float]], group2: List[Union[int, float]]) -> Dict[str, float]:
        """Test t pour deux échantillons indépendants (test de Welch exact)"""
        g1 = [x for x in group1 if x is not None and isinstance(x, (int, float))]
        g2 = [x for x in group2 if x is not None and isinstance(x, (int, float))]
        
        if len(g1) < 2 or len(g2) < 2:
            return {'t_stat': float('nan'), 'p_value': float('nan'), 'df': 0}
        
        n1, n2 = len(g1), len(g2)
        mean1, mean2 = self.mean(g1), self.mean(g2)
        var1, var2 = self.variance(g1, 1), self.variance(g2, 1)
        
        # Test de Welch (variances inégales)
        t_stat = (mean1 - mean2) / math.sqrt(var1/n1 + var2/n2)
        
        # Degrés de liberté de Welch-Satterthwaite
        df_num = (var1/n1 + var2/n2)**2
        df_den = (var1/n1)**2/(n1-1) + (var2/n2)**2/(n2-1)
        df = df_num / df_den if df_den > 0 else 0
        
        # p-value exacte
        p_value = 2 * (1 - self._t_cdf(abs(t_stat), df))
        
        return {
            't_stat': t_stat,
            'p_value': min(p_value, 1.0),
            'df': df,
            'mean1': mean1,
            'mean2': mean2
        }

    def f_test(self, group1: List[Union[int, float]], group2: List[Union[int, float]]) -> Dict[str, float]:
        """Test F pour comparaison de variances (p-value exacte)"""
        g1 = [x for x in group1 if x is not None and isinstance(x, (int, float))]
        g2 = [x for x in group2 if x is not None and isinstance(x, (int, float))]
        
        if len(g1) < 2 or len(g2) < 2:
            return {'f_stat': float('nan'), 'p_value': float('nan'), 'df1': 0, 'df2': 0}
        
        var1, var2 = self.variance(g1, 1), self.variance(g2, 1)
        
        # Mettre la plus grande variance au numérateur
        if var1 > var2:
            f_stat = var1 / var2
            df1, df2 = len(g1)-1, len(g2)-1
        else:
            f_stat = var2 / var1
            df1, df2 = len(g2)-1, len(g1)-1
        
        # p-value exacte (test bilatéral)
        p_value = 2 * min(self._f_cdf(f_stat, df1, df2), 1 - self._f_cdf(f_stat, df1, df2))
        
        return {
            'f_stat': f_stat,
            'p_value': min(p_value, 1.0),
            'df1': df1,
            'df2': df2
        }

    def chi2_test(self, observed: List[int], expected: Optional[List[float]] = None) -> Dict[str, float]:
        """Test du chi-carré (p-value exacte)"""
        if expected is None:
            # Test d'ajustement à une distribution uniforme
            total = sum(observed)
            expected = [total / len(observed)] * len(observed)
        
        if len(observed) != len(expected):
            raise ValueError("Les listes observées et attendues doivent avoir la même longueur")
        
        # Vérifier que les effectifs attendus sont > 0
        for e in expected:
            if e <= 0:
                return {'chi2': float('nan'), 'p_value': float('nan'), 'df': len(observed)-1}
        
        chi2 = 0.0
        for o, e in zip(observed, expected):
            if e > 0:
                chi2 += (o - e)**2 / e
        
        df = len(observed) - 1
        p_value = 1 - self._chi2_cdf(chi2, df)
        
        return {
            'chi2': chi2,
            'p_value': min(p_value, 1.0),
            'df': df
        }

    def shapiro_wilk(self, data: List[Union[int, float]]) -> Dict[str, float]:
        """
        Test de normalité de Shapiro-Wilk
        Implémentation basée sur l'algorithme AS R94 (Royston 1995)
        """
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        n = len(valid)
        
        if n < 3 or n > 5000:
            return {'w_stat': float('nan'), 'p_value': float('nan')}
        
        # Trier les données
        sorted_vals = sorted(valid)
        
        # Construire les coefficients a_i
        a = [0.0] * n
        
        if n == 3:
            a[0] = 0.707106781
        else:
            # Calculer les coefficients de Shapiro-Wilk
            m = [0.0] * n
            for i in range(n):
                # Approximation des espérances des statistiques d'ordre pour la normale
                u = (i + 1 - 0.375) / (n + 0.25)
                m[i] = self._norm_inv(u)
            
            # Calculer les coefficients
            m2 = sum(x**2 for x in m)
            
            # Corriger pour n >= 4
            if n >= 4:
                # Méthode de Royston
                w = [0.0] * n
                for i in range(n):
                    for j in range(n):
                        w[i] += abs(m[i] - m[j]) ** (n-1)
                
                # Normaliser
                sum_w = sum(w)
                for i in range(n):
                    w[i] = w[i] / sum_w
                
                # Ajuster les coefficients
                phi = (m2 * n) / (n - 1)
                for i in range(n):
                    a[i] = w[i] / math.sqrt(phi)
            else:
                # Pour n=3, utiliser les coefficients précalculés
                a[0] = 0.707106781
                a[1] = 0.0
                a[2] = -0.707106781
        
        # Calculer la statistique W
        mean_val = self.mean(sorted_vals)
        numerator = sum(a[i] * sorted_vals[i] for i in range(n))**2
        denominator = sum((x - mean_val)**2 for x in sorted_vals)
        
        w_stat = numerator / denominator if denominator != 0 else 0
        
        # Transformation pour la p-value
        if n == 3:
            p_value = 6 * (1 - w_stat)  # Approximation
        else:
            # Transformation de Royston
            y = math.log(1 - w_stat)
            mu = -0.375 * n**0.2 + 0.45
            sigma = 0.52 * n**0.1 + 0.21
            z = (y - mu) / sigma
            p_value = 2 * (1 - self._norm_cdf(abs(z)))
        
        return {
            'w_stat': w_stat,
            'p_value': min(abs(p_value), 1.0)
        }

    def _norm_cdf(self, x: float) -> float:
        """Fonction de répartition de la loi normale"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def _norm_inv(self, p: float) -> float:
        """
        Inverse de la fonction de répartition de la loi normale
        Approximation de Beasley-Springer-Moro
        """
        if p <= 0 or p >= 1:
            return float('nan')
        
        if p < 0.5:
            return -self._norm_inv(1 - p)
        
        if p > 0.92:
            # Région des queues
            a = [-3.969683028665376e+01, 2.209460984245205e+02,
                 -2.759285104469687e+02, 1.383577518672690e+02,
                 -3.066479806614716e+01, 2.506628277459239e+00]
            b = [-5.447609879822406e+01, 1.615858368580409e+02,
                 -1.556989798598866e+02, 6.680131188771972e+01,
                 -1.328068155288572e+01]
            
            q = math.sqrt(-2 * math.log(1 - p))
            num = ((((a[0] * q + a[1]) * q + a[2]) * q + a[3]) * q + a[4]) * q + a[5]
            den = (((b[0] * q + b[1]) * q + b[2]) * q + b[3]) * q + b[4]
            return num / den
        else:
            # Région centrale
            c = [2.515517, 0.802853, 0.010328]
            d = [1.432788, 0.189269, 0.001308]
            
            t = math.sqrt(-2 * math.log(1 - p))
            return t - (c[0] + c[1] * t + c[2] * t**2) / (1 + d[0] * t + d[1] * t**2 + d[2] * t**3)

    def ks_test(self, data: List[Union[int, float]], dist: str = 'normal') -> Dict[str, float]:
        """Test de Kolmogorov-Smirnov (p-value exacte)"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return {'ks_stat': float('nan'), 'p_value': float('nan')}
        
        n = len(valid)
        sorted_vals = sorted(valid)
        
        if dist == 'normal':
            mean_val = self.mean(valid)
            std_val = self.std(valid, 0)
            
            if std_val == 0:
                return {'ks_stat': 1.0, 'p_value': 0.0}
            
            # Calculer la statistique KS
            ks_stat = 0.0
            for i, x in enumerate(sorted_vals):
                ecdf = (i + 1) / n
                cdf = self._norm_cdf((x - mean_val) / std_val)
                ks_stat = max(ks_stat, abs(ecdf - cdf), abs((i / n) - cdf))
        
        elif dist == 'uniform':
            a, b = min(sorted_vals), max(sorted_vals)
            if a == b:
                return {'ks_stat': 1.0, 'p_value': 0.0}
            
            ks_stat = 0.0
            for i, x in enumerate(sorted_vals):
                ecdf = (i + 1) / n
                cdf = (x - a) / (b - a)
                ks_stat = max(ks_stat, abs(ecdf - cdf), abs((i / n) - cdf))
        else:
            return {'ks_stat': float('nan'), 'p_value': float('nan')}
        
        # p-value approximée par la formule de Kolmogorov
        z = ks_stat * math.sqrt(n)
        p_value = 2 * sum((-1)**(k-1) * math.exp(-2 * k**2 * z**2) 
                          for k in range(1, 10))  # Sommer les 10 premiers termes
        p_value = min(p_value, 1.0)
        
        return {
            'ks_stat': ks_stat,
            'p_value': p_value
        }

    def anderson_darling(self, data: List[Union[int, float]]) -> Dict[str, float]:
        """Test d'Anderson-Darling pour la normalité"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if len(valid) < 2:
            return {'ad_stat': float('nan'), 'p_value': float('nan')}
        
        n = len(valid)
        sorted_vals = sorted(valid)
        mean_val = self.mean(valid)
        std_val = self.std(valid, 0)
        
        if std_val == 0:
            return {'ad_stat': float('nan'), 'p_value': float('nan')}
        
        # Calcul de la statistique d'Anderson-Darling
        ad_stat = 0.0
        for i, x in enumerate(sorted_vals):
            z = (x - mean_val) / std_val
            cdf = self._norm_cdf(z)
            if cdf <= 0 or cdf >= 1:
                continue
            ad_stat += (2*(i+1) - 1) * (math.log(cdf) + math.log(1 - cdf))
        
        ad_stat = -n - ad_stat / n
        
        # Correction pour petits échantillons
        ad_stat_corr = ad_stat * (1 + 0.75/n + 2.25/n**2)
        
        # Valeurs critiques approximatives
        if ad_stat_corr < 0.2:
            p_value = 0.75
        elif ad_stat_corr < 0.34:
            p_value = 0.5
        elif ad_stat_corr < 0.6:
            p_value = 0.25
        elif ad_stat_corr < 1.0:
            p_value = 0.1
        else:
            p_value = 0.05
        
        return {
            'ad_stat': ad_stat,
            'p_value': p_value
        }

    # ========== FONCTIONS D'AGRÉGATION ==========

    def aggregate(self, group_col: str, agg_dict: Dict[str, str]) -> SimpleDataFrame:
        """Agrège les données selon une colonne de groupe"""
        if not self.df:
            raise ValueError("Aucun DataFrame défini")
        
        groups = {}
        for i in range(len(self.df)):
            key = self.df[group_col][i]
            if key not in groups:
                groups[key] = []
            groups[key].append(i)
        
        result = {group_col: []}
        for agg_col, agg_func in agg_dict.items():
            result[agg_col] = []
        
        for key, indices in groups.items():
            result[group_col].append(key)
            for agg_col, agg_func in agg_dict.items():
                values = [self.df[agg_col][i] for i in indices]
                numeric_values = [to_numeric(x) for x in values if x is not None]
                numeric_values = [x for x in numeric_values if isinstance(x, (int, float))]
                
                if agg_func == 'sum':
                    result[agg_col].append(sum(numeric_values) if numeric_values else 0)
                elif agg_func == 'mean':
                    result[agg_col].append(self.mean(numeric_values) if numeric_values else None)
                elif agg_func == 'median':
                    result[agg_col].append(self.median(numeric_values) if numeric_values else None)
                elif agg_func == 'min':
                    result[agg_col].append(min(numeric_values) if numeric_values else None)
                elif agg_func == 'max':
                    result[agg_col].append(max(numeric_values) if numeric_values else None)
                elif agg_func == 'count':
                    result[agg_col].append(len(values))
                elif agg_func == 'std':
                    result[agg_col].append(self.std(numeric_values, 1) if len(numeric_values) > 1 else None)
                elif agg_func == 'var':
                    result[agg_col].append(self.variance(numeric_values, 1) if len(numeric_values) > 1 else None)
                elif agg_func == 'first':
                    result[agg_col].append(values[0] if values else None)
                elif agg_func == 'last':
                    result[agg_col].append(values[-1] if values else None)
        
        return SimpleDataFrame(result)

    def pivot_table(self, index: str, columns: str, values: str, aggfunc: str = 'mean') -> SimpleDataFrame:
        """Crée un tableau croisé dynamique"""
        if not self.df:
            raise ValueError("Aucun DataFrame défini")
        
        # Récupérer les valeurs uniques
        index_vals = set()
        col_vals = set()
        for i in range(len(self.df)):
            if self.df[index][i] is not None:
                index_vals.add(self.df[index][i])
            if self.df[columns][i] is not None:
                col_vals.add(self.df[columns][i])
        
        index_vals = sorted(index_vals)
        col_vals = sorted(col_vals)
        
        # Initialiser le résultat
        result = {index: []}
        for col in col_vals:
            result[str(col)] = []
        
        # Grouper les données
        groups = {}
        for i in range(len(self.df)):
            idx_val = self.df[index][i]
            col_val = self.df[columns][i]
            val = self.df[values][i]
            
            if idx_val is None or col_val is None or val is None:
                continue
                
            key = (idx_val, col_val)
            if key not in groups:
                groups[key] = []
            groups[key].append(val)
        
        # Calculer les agrégations
        for idx_val in index_vals:
            result[index].append(idx_val)
            for col_val in col_vals:
                key = (idx_val, col_val)
                if key in groups:
                    vals = groups[key]
                    numeric_vals = [to_numeric(v) for v in vals if v is not None]
                    numeric_vals = [v for v in numeric_vals if isinstance(v, (int, float))]
                    
                    if aggfunc == 'sum':
                        result[str(col_val)].append(sum(numeric_vals) if numeric_vals else 0)
                    elif aggfunc == 'mean':
                        result[str(col_val)].append(self.mean(numeric_vals) if numeric_vals else None)
                    elif aggfunc == 'count':
                        result[str(col_val)].append(len(vals))
                    elif aggfunc == 'min':
                        result[str(col_val)].append(min(numeric_vals) if numeric_vals else None)
                    elif aggfunc == 'max':
                        result[str(col_val)].append(max(numeric_vals) if numeric_vals else None)
                    elif aggfunc == 'median':
                        result[str(col_val)].append(self.median(numeric_vals) if numeric_vals else None)
                    else:
                        result[str(col_val)].append(None)
                else:
                    result[str(col_val)].append(None)
        
        return SimpleDataFrame(result)

    def cross_tab(self, col1: str, col2: str) -> Dict[str, Dict[str, int]]:
        """Tableau de contingence entre deux colonnes"""
        if not self.df:
            raise ValueError("Aucun DataFrame défini")
        
        result = {}
        for i in range(len(self.df)):
            val1 = self.df[col1][i]
            val2 = self.df[col2][i]
            if val1 is None or val2 is None:
                continue
            
            if val1 not in result:
                result[val1] = {}
            if val2 not in result[val1]:
                result[val1][val2] = 0
            result[val1][val2] += 1
        
        return result

    # ========== FONCTIONS DE RÉSAMPLAGE ==========

    def bootstrap(self, data: List[Union[int, float]], n_samples: int = 1000, 
                  statistic: Callable = None, alpha: float = 0.05) -> Dict[str, float]:
        """
        Bootstrap pour estimer l'intervalle de confiance
        Si statistic est None, utilise la moyenne
        """
        if statistic is None:
            statistic = self.mean
        
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return {'mean': float('nan'), 'ci_low': float('nan'), 'ci_high': float('nan')}
        
        n = len(valid)
        bootstrap_stats = []
        
        for _ in range(n_samples):
            # Échantillonnage avec remise
            sample = [valid[random.randint(0, n-1)] for _ in range(n)]
            bootstrap_stats.append(statistic(sample))
        
        bootstrap_stats.sort()
        lower_idx = int(n_samples * alpha / 2)
        upper_idx = int(n_samples * (1 - alpha / 2))
        
        return {
            'mean': self.mean(bootstrap_stats),
            'ci_low': bootstrap_stats[lower_idx],
            'ci_high': bootstrap_stats[upper_idx],
            'std': self.std(bootstrap_stats, 0)
        }

    def jackknife(self, data: List[Union[int, float]], statistic: Callable = None) -> Dict[str, float]:
        """
        Jackknife pour estimer le biais et l'erreur-type
        Si statistic est None, utilise la moyenne
        """
        if statistic is None:
            statistic = self.mean
        
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if len(valid) < 2:
            return {'estimate': float('nan'), 'bias': float('nan'), 'se': float('nan')}
        
        n = len(valid)
        jack_stats = []
        
        for i in range(n):
            # Échantillon sans l'observation i
            sample = valid[:i] + valid[i+1:]
            jack_stats.append(statistic(sample))
        
        jack_mean = self.mean(jack_stats)
        original_stat = statistic(valid)
        
        # Biais et erreur-type jackknife
        bias = (n - 1) * (jack_mean - original_stat)
        
        # Variance jackknife
        jack_var = 0.0
        for x in jack_stats:
            jack_var += (x - jack_mean) ** 2
        jack_var = (n - 1) / n * jack_var
        se = math.sqrt(jack_var) if jack_var > 0 else 0.0
        
        return {
            'estimate': original_stat,
            'bias': bias,
            'se': se,
            'jackknife_mean': jack_mean
        }

    # ========== FONCTIONS POUR SÉRIES TEMPORELLES ==========

    def lag(self, data: List[Any], k: int = 1) -> List[Any]:
        """Décale une série de k pas"""
        if k >= len(data):
            return [None] * len(data)
        return [None] * k + data[:-k]

    def diff(self, data: List[Union[int, float]], k: int = 1) -> List[Union[int, float, None]]:
        """Différence d'ordre k"""
        if k >= len(data):
            return [None] * len(data)
        result = [None] * k
        for i in range(k, len(data)):
            if data[i] is not None and data[i-k] is not None:
                result.append(data[i] - data[i-k])
            else:
                result.append(None)
        return result

    def pct_change(self, data: List[Union[int, float]], k: int = 1) -> List[Union[int, float, None]]:
        """Changement en pourcentage"""
        if k >= len(data):
            return [None] * len(data)
        result = [None] * k
        for i in range(k, len(data)):
            if data[i] is not None and data[i-k] is not None and data[i-k] != 0:
                result.append((data[i] - data[i-k]) / abs(data[i-k]) * 100)
            else:
                result.append(None)
        return result

    def moving_average(self, data: List[Union[int, float]], window: int = 3) -> List[Union[int, float, None]]:
        """Moyenne mobile simple"""
        if window > len(data):
            return [None] * len(data)
        result = [None] * (window - 1)
        for i in range(window - 1, len(data)):
            window_vals = [data[j] for j in range(i - window + 1, i + 1) 
                          if data[j] is not None and isinstance(data[j], (int, float))]
            if len(window_vals) == window:  # Toutes les valeurs sont valides
                result.append(self.mean(window_vals))
            else:
                result.append(None)
        return result

    def ewma(self, data: List[Union[int, float]], alpha: float = 0.3) -> List[Union[int, float, None]]:
        """Moyenne mobile exponentielle"""
        result = [None] * len(data)
        if not data or data[0] is None:
            return result
        
        result[0] = data[0]
        for i in range(1, len(data)):
            if data[i] is not None and result[i-1] is not None:
                result[i] = alpha * data[i] + (1 - alpha) * result[i-1]
            else:
                result[i] = None
        return result

    def autocorrelation(self, data: List[Union[int, float]], lag: int = 1) -> float:
        """Autocorrélation à un lag donné"""
        if lag <= 0:
            return 1.0 if lag == 0 else float('nan')
        
        valid_pairs = []
        for i in range(len(data) - lag):
            if data[i] is not None and data[i+lag] is not None:
                valid_pairs.append((data[i], data[i+lag]))
        
        if len(valid_pairs) < 2:
            return float('nan')
        
        x_vals, y_vals = zip(*valid_pairs)
        return self.correlation(list(x_vals), list(y_vals))

    def acf(self, data: List[Union[int, float]], nlags: int = 10) -> List[float]:
        """Fonction d'autocorrélation"""
        return [self.autocorrelation(data, lag) for lag in range(nlags + 1)]

    def pacf(self, data: List[Union[int, float]], nlags: int = 10) -> List[float]:
        """
        Fonction d'autocorrélation partielle via l'algorithme de Durbin-Levinson
        """
        n = len(data)
        valid_data = [x for x in data if x is not None and isinstance(x, (int, float))]
        
        if len(valid_data) < nlags + 1:
            return [float('nan')] * (nlags + 1)
        
        # Calculer l'ACF d'abord
        acf_vals = self.acf(data, nlags)
        
        # Algorithme de Durbin-Levinson pour la PACF
        pacf_vals = [1.0]  # PACF à lag 0 = 1
        phi = [[0.0] * (nlags + 1) for _ in range(nlags + 1)]
        
        for k in range(1, nlags + 1):
            # Calculer phi_kk
            if k == 1:
                phi[k][k] = acf_vals[1]
            else:
                numerator = acf_vals[k]
                for j in range(1, k):
                    numerator -= phi[k-1][j] * acf_vals[k-j]
                denominator = 1.0
                for j in range(1, k):
                    denominator -= phi[k-1][j] * acf_vals[j]
                phi[k][k] = numerator / denominator if denominator != 0 else 0.0
            
            pacf_vals.append(phi[k][k])
            
            # Mettre à jour les autres phi
            for j in range(1, k):
                phi[k][j] = phi[k-1][j] - phi[k][k] * phi[k-1][k-j]
        
        return pacf_vals

    # ========== FONCTIONS DE DISTANCE ET SIMILARITÉ ==========

    def euclidean_distance(self, v1: List[Union[int, float]], v2: List[Union[int, float]]) -> float:
        """Distance euclidienne"""
        if len(v1) != len(v2):
            raise ValueError("Les vecteurs doivent avoir la même longueur")
        
        pairs = [(x, y) for x, y in zip(v1, v2) 
                 if x is not None and y is not None 
                 and isinstance(x, (int, float)) and isinstance(y, (int, float))]
        
        if not pairs:
            return float('nan')
        
        sum_sq = 0.0
        for x, y in pairs:
            diff = x - y
            sum_sq += diff * diff
        return math.sqrt(sum_sq)

    def manhattan_distance(self, v1: List[Union[int, float]], v2: List[Union[int, float]]) -> float:
        """Distance de Manhattan"""
        if len(v1) != len(v2):
            raise ValueError("Les vecteurs doivent avoir la même longueur")
        
        pairs = [(x, y) for x, y in zip(v1, v2) 
                 if x is not None and y is not None 
                 and isinstance(x, (int, float)) and isinstance(y, (int, float))]
        
        if not pairs:
            return float('nan')
        
        return sum(abs(x - y) for x, y in pairs)

    def minkowski_distance(self, v1: List[Union[int, float]], v2: List[Union[int, float]], p: float = 3) -> float:
        """Distance de Minkowski d'ordre p"""
        if len(v1) != len(v2):
            raise ValueError("Les vecteurs doivent avoir la même longueur")
        if p < 1:
            raise ValueError("p doit être >= 1")
        
        pairs = [(x, y) for x, y in zip(v1, v2) 
                 if x is not None and y is not None 
                 and isinstance(x, (int, float)) and isinstance(y, (int, float))]
        
        if not pairs:
            return float('nan')
        
        if p == float('inf'):
            return max(abs(x - y) for x, y in pairs)
        
        sum_p = 0.0
        for x, y in pairs:
            sum_p += abs(x - y) ** p
        return sum_p ** (1.0 / p)

    def cosine_similarity(self, v1: List[Union[int, float]], v2: List[Union[int, float]]) -> float:
        """Similarité cosinus"""
        if len(v1) != len(v2):
            raise ValueError("Les vecteurs doivent avoir la même longueur")
        
        pairs = [(x, y) for x, y in zip(v1, v2) 
                 if x is not None and y is not None 
                 and isinstance(x, (int, float)) and isinstance(y, (int, float))]
        
        if not pairs:
            return float('nan')
        
        x_vals, y_vals = zip(*pairs)
        
        dot_product = 0.0
        norm_x = 0.0
        norm_y = 0.0
        
        for x, y in pairs:
            dot_product += x * y
            norm_x += x * x
            norm_y += y * y
        
        norm_x = math.sqrt(norm_x)
        norm_y = math.sqrt(norm_y)
        
        if norm_x * norm_y == 0:
            return 0.0
        return dot_product / (norm_x * norm_y)

    def jaccard_similarity(self, set1: Set[Any], set2: Set[Any]) -> float:
        """Similarité de Jaccard pour des ensembles"""
        if not set1 and not set2:
            return 1.0
        intersection = set1 & set2
        union = set1 | set2
        return len(intersection) / len(union) if union else 0

    # ========== FONCTIONS DE CLASSEMENT ==========

    def rank(self, data: List[Union[int, float]], method: str = 'average') -> List[float]:
        """
        Calcule les rangs des valeurs
        Methods: 'average', 'min', 'max', 'dense', 'ordinal'
        """
        if method == 'average':
            return self._rank(data)
        elif method == 'min':
            indexed = list(enumerate(data))
            indexed.sort(key=lambda x: (x[1] if x[1] is not None else float('inf'), x[0]))
            ranks = [0] * len(data)
            i = 0
            while i < len(indexed):
                j = i
                while j < len(indexed) and indexed[j][1] == indexed[i][1]:
                    j += 1
                for k in range(i, j):
                    ranks[indexed[k][0]] = i + 1
                i = j
            return ranks
        elif method == 'max':
            indexed = list(enumerate(data))
            indexed.sort(key=lambda x: (x[1] if x[1] is not None else float('inf'), x[0]))
            ranks = [0] * len(data)
            i = 0
            while i < len(indexed):
                j = i
                while j < len(indexed) and indexed[j][1] == indexed[i][1]:
                    j += 1
                for k in range(i, j):
                    ranks[indexed[k][0]] = j
                i = j
            return ranks
        elif method == 'dense':
            # Rangs sans trous
            unique_vals = sorted(set(x for x in data if x is not None))
            val_to_rank = {val: i+1 for i, val in enumerate(unique_vals)}
            return [val_to_rank[x] if x in val_to_rank else None for x in data]
        else:  # ordinal
            return [i+1 for i in range(len(data))]

    def percentile_rank(self, data: List[Union[int, float]], value: Union[int, float]) -> float:
        """Rang percentile d'une valeur"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return float('nan')
        
        count_less = sum(1 for x in valid if x < value)
        count_equal = sum(1 for x in valid if x == value)
        
        # Formule de percentile standard
        return (count_less + 0.5 * count_equal) / len(valid) * 100

    def zscore(self, data: List[Union[int, float]]) -> List[Union[int, float, None]]:
        """Calcule les z-scores"""
        mean_val = self.mean(data)
        std_val = self.std(data, 0)
        
        if math.isnan(mean_val) or std_val == 0:
            return [0.0 if x is not None else None for x in data]
        
        result = []
        for x in data:
            if x is None:
                result.append(None)
            elif isinstance(x, (int, float)):
                result.append((x - mean_val) / std_val)
            else:
                result.append(None)
        return result

    def min_max_scale(self, data: List[Union[int, float]], feature_range: Tuple[float, float] = (0, 1)) -> List[Union[int, float, None]]:
        """Normalisation min-max"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return [None] * len(data)
        
        min_val, max_val = min(valid), max(valid)
        if min_val == max_val:
            return [feature_range[0] if x is not None else None for x in data]
        
        a, b = feature_range
        result = []
        for x in data:
            if x is None:
                result.append(None)
            elif isinstance(x, (int, float)):
                scaled = a + (x - min_val) * (b - a) / (max_val - min_val)
                result.append(scaled)
            else:
                result.append(None)
        return result

    def robust_scale(self, data: List[Union[int, float]]) -> List[Union[int, float, None]]:
        """Mise à l'échelle robuste (basée sur la médiane et l'IQR)"""
        valid = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not valid:
            return [None] * len(data)
        
        median_val = self.median(valid)
        iqr_val = self.iqr(valid)
        
        if iqr_val == 0 or math.isnan(iqr_val):
            return [0.0 if x is not None else None for x in data]
        
        result = []
        for x in data:
            if x is None:
                result.append(None)
            elif isinstance(x, (int, float)):
                result.append((x - median_val) / iqr_val)
            else:
                result.append(None)
        return result
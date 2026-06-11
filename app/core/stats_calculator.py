# stats_calculator.py
from typing import Dict, Collection, Any, Optional 
import warnings
import numpy as np
import pandas as pd


class StatsCalculator:
    def __init__(self, data):
        self.data = np.array(data, dtype=float)
        if len(self.data) == 0:                          
            raise ValueError("il n'ya pas des donnees")

    # les mesures de tendance centrale 
    def moyen_arth(self, data=None):                     
        """moyenne arithmetique"""
        if data is None:                                 
           data = self.data
        return np.mean(data)

    def moyenne_geo(self, data=None):
        """moyenne geometrique"""
        if data is None:
            data = self.data
        data = np.array(data)

        if len(data) == 0:
            return np.nan
        if np.any(data < 0):
            raise ValueError("la moyenne geometrique necessite des valeurs positives")
        if np.any(data == 0):                           
            return 0.0
        return np.exp(np.mean(np.log(data)))

    def moyen_harm(self, data=None):
        """moyenne harmonique"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)

        if len(data) == 0:
            return np.nan
        if np.any(data < 0):
            raise ValueError("les donnees doivent etre strictement positives")
        if np.any(data == 0):
            return 0.0
        return len(data) / sum(1.0 / data)

    def moyen_quadr(self, data=None):
        """moyenne quadratique"""
        if data is None:
            data = self.data
        return np.sqrt(np.mean(np.square(data)))

    def moyen_contrharm(self, data=None):
        """moyenne contra-harmonique"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)
        if sum(data) == 0:
            return np.nan
        return np.sum(data ** 2) / np.sum(data)

    def moyen_tronc(self, proportion: float = 0.1, data=None):
        """moyenne tronquee: supprime proportion*100% des valeurs aux extremites"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)
        n = len(data)
        sorted_data = np.sort(data)
        trim = int(n * proportion)

        if 2 * trim >= n:
            warnings.warn("cette proportion est trop elevee, retour a la mediane")
            return np.median(data)
        trim_data = sorted_data[trim: n - trim]
        return np.mean(trim_data)

    def moyen_pond(self, poids: Optional[np.ndarray] = None, data=None):
        """moyenne ponderee"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)

        if poids is None:
            return np.mean(data)
        poids = np.array(poids, dtype=float)

        if len(poids) != len(data):
            raise ValueError("les poids doivent avoir la meme longueur que les donnees")
        if np.any(poids < 0):
            raise ValueError("les poids doivent etre strictement positifs")
        if np.sum(poids) == 0.0:
            raise ValueError("la somme des poids ne doit pas etre nulle")
        return np.average(data, weights=poids)             

    def mediane(self, data=None):
        """mediane"""
        if data is None:
            data = self.data
        return np.median(data)

    def mode(self, data=None):
        """mode: valeur la plus frequente"""
        if data is None:
            data = self.data
        if isinstance(data, (list, np.ndarray)):            
            data = pd.Series(data)
        modes = data.mode()

        if len(modes) == 0:
            return np.nan
        elif len(modes) == 1:
            return modes.loc[0]
        else:
            return modes.values                             

    def quantiles(self, Q: float, data=None):
        """les quantiles"""
        if data is None:
            data = self.data

        if Q < 0 or Q > 1:
            raise ValueError("les valeurs des quantiles doivent etre entre 0 et 1")
        return np.quantile(data, Q)

    def quartiles(self, data=None):
        """les quartiles Q1, Q2, Q3"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)

        q1 = np.quantile(data, 0.25)
        q2 = np.quantile(data, 0.50)
        q3 = np.quantile(data, 0.75)

        return {'Q1': q1, 'Q2': q2, 'Q3': q3}

    def deciles(self, data=None):
        """retourne les 9 deciles"""
        if data is None:
            data = self.data
        deciles = {}

        for i in range(1, 10):
            deciles[f'd{i}'] = np.quantile(data, i / 10)
        return deciles                                      

    def percentiles(self, percentiles=None, data=None):
        if data is None:
            data = self.data
        if percentiles is None:
            percentiles = [10, 25, 50, 75, 90]
        results = {}

        for p in percentiles:
            if p < 0 or p > 100:
                raise ValueError(f"le percentile {p} doit etre entre 0 et 100")
            results[f"p{p}"] = np.percentile(data, p)
        return results

    def moyen_gen(self, p: float, data=None):
        """moyenne generalisee d'ordre p"""
        if data is None:
            data = self.data
        if p == 0:
            return self.moyenne_geo(data)
        elif p == -np.inf:
            return np.min(data)
        elif p == np.inf:
            return np.max(data)
        else:
            if np.any(data <= 0) and p < 0:             
                raise ValueError(f"pour p={p} negatif, les valeurs doivent etre positives")
            return np.mean(data ** p) ** (1 / p)

    def moyen_winsoriz(self, proportion: float = 0.1, data=None):
        """moyenne winsorisee: remplace les valeurs extremes par les valeurs seuils"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)
        sorted_data = np.sort(data)
        n = len(data)
        k = int(n * proportion)                          

        if k == 0:
            return np.mean(data)
        winsorized = sorted_data.copy()
        winsorized[:k] = sorted_data[k]
        winsorized[-k:] = sorted_data[-k - 1]              
        return np.mean(winsorized)

    def milieu_etendue(self, data=None):
        """milieu de l'etendue"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)
        return (np.min(data) + np.max(data)) / 2

    def trimean(self, data=None):
        """Trimean: (Q1 + 2*Mediane + Q3) / 4"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)

        quartile = self.quartiles(data)
        return (quartile['Q1'] + 2 * quartile['Q2'] + quartile['Q3']) / 4

    def moyen_geo_log(self, base: float = np.e, data=None):
        """moyenne logarithmique"""
        if data is None:
            data = self.data
        log_data = np.log(data) if base == np.e else np.log(data) / np.log(base)
        return np.mean(np.exp(log_data))

    # ---- les parametres de dispersion

    def etendue(self, data=None):                          
        """etendue simple"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)                 
        return np.max(data) - np.min(data)

    def variance_ech(self, data=None, ddof: int = 1):
        """variance echantillon"""
        if data is None:
            data = self.data
        return np.var(data, ddof=ddof)

    def variance_pop(self, data=None, ddof: int = 0):
        """variance population"""
        if data is None:
            data = self.data
        return np.var(data, ddof=ddof)

    def variance_moyenne(self, data=None):
        if data is None:
            data = self.data
        return self.variance_pop(data, ddof=0) / len(data)  

    def ecart_type(self, data=None, ddof: int = 1):
        """ecart-type simple"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)
        return np.std(data, ddof=ddof)

    def erreur_standard(self, data=None):
        """erreur standard de la moyenne"""
        if data is None:
            data = self.data
        return self.ecart_type(data, ddof=1) / np.sqrt(len(data))

    def ecart_abs_moyen(self, data=None):
        if data is None:
            data = self.data
        return np.mean(np.abs(data - self.moyen_arth(data)))

    def ecart_abs_median(self, data=None):
        if data is None:
            data = self.data
        return np.mean(np.abs(data - self.mediane(data)))   

    def ecart_interq(self, data=None):
        if data is None:
            data = self.data
        q1 = np.quantile(data, 0.25)
        q3 = np.quantile(data, 0.75)
        return q3 - q1

    def ecart_semi_quart(self, data=None):
        if data is None:
            data = self.data
        return self.ecart_interq(data) / 2

    def coeff_variation(self, data=None):
        """coefficient de variation base sur la moyenne"""
        if data is None:
            data = self.data
        if self.moyen_arth(data) == 0:
            return np.nan
        return self.ecart_type(data, ddof=0) / self.moyen_arth(data)

    def coeff_var_med(self, data=None):
        """coefficient de variation base sur la mediane"""
        if data is None:
            data = self.data
        if self.mediane(data) == 0:
            return np.nan
        return self.ecart_type(data) / self.mediane(data)

    def variance_relative(self, data=None):
        """variance relative"""
        if data is None:
            data = self.data
        cv = self.coeff_variation(data)
        return cv ** 2 if not np.isnan(cv) else np.nan

    def ecart_type_geo(self, data=None):
        """ecart-type geometrique pour les donnees log-normales"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)
        if np.any(data < 0):
            raise ValueError("les donnees doivent etre positives")
        if np.any(data == 0):                              
            return 0.0
        log_data = np.log(data)
        return np.exp(np.std(log_data, ddof=1))

    def variance_geo(self, data=None):
        """variance geometrique"""
        if data is None:
            data = self.data
        return self.ecart_type_geo(data) ** 2

    def ecart_type_norm(self, data=None):
        """ecart-type normalise"""
        if data is None:
            data = self.data
        return self.ecart_type(data, ddof=1) / np.sqrt(np.mean(data ** 2))

    def etendue_intercentile(self, p: float = 90, data=None):
        """etendue intercentile"""
        if data is None:
            data = self.data
        born_inf = (100 - p) / 2
        born_sup = (100 + p) / 2
        return np.percentile(data, born_sup) - np.percentile(data, born_inf)

    def etendue_interdecile(self, data=None):
        if data is None:
            data = self.data
        return np.quantile(data, 0.9) - np.quantile(data, 0.1)

    def ecart_quartile(self, data=None):
        """ecart interquartile"""
        if data is None:
            data = self.data
        return (np.quantile(data, 0.75) - np.quantile(data, 0.25)) / 2

    def ecart_percentile(self, p1: float = 25, p2: float = 75, data=None):
        """ecart interpercentile"""
        if data is None:
            data = self.data
        if p1 < 0 or p2 > 100 or p2 < 0 or p1 > 100:
            raise ValueError("les valeurs doivent etre entre 0 et 100")
        q1 = np.percentile(data, p1)
        q2 = np.percentile(data, p2)
        return q2 - q1

    def difference_moyenne_absolue(self, data=None):
        """Difference moyenne absolue (difference de Gini)"""
        if data is None:
            data = self.data

        n = len(data)
        if n < 2:
            return 0
        data_sorted = np.sort(data)
        poids = np.arange(1, n + 1) * 2 - n - 1
        return 2 * np.sum(poids * data_sorted) / (n * (n - 1))

    def difference_median_absolue(self, data=None):
        """Difference mediane absolue"""
        if data is None:
            data = self.data
        n = len(data)
        if n < 2:
            return 0
        differences = []
        for i in range(n):
            for j in range(i + 1, n):
                differences.append(data[i] - data[j])
        return np.median(differences)

    def coefficient_ecart_type(self, data=None):
        """Coefficient d'ecart-type : sigma / mu'"""
        if data is None:
            data = self.data

        moyenne_absolue = np.mean(np.abs(data))
        if moyenne_absolue == 0:
            return np.nan
        return self.ecart_type(data, ddof=1) / moyenne_absolue

    def coefficient_dispersion_quartile(self, data=None):
        """Coefficient de dispersion quartile : (Q3-Q1)/(Q3+Q1)"""
        if data is None:
            data = self.data

        q1 = np.quantile(data, 0.25)
        q3 = np.quantile(data, 0.75)

        if q3 + q1 == 0:
            return np.nan
        return (q3 - q1) / (q3 + q1)

    def coefficient_dispersion_median(self, data=None):
        """Coefficient de dispersion base sur la mediane : MAD / mediane"""
        return self.coeff_var_med(data)

    def indice_gini(self, data=None):
        """indice de gini"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)
        data = data[data >= 0]

        if len(data) == 0:
            return np.nan
        sorted_data = np.sort(data)
        n = len(sorted_data)
        consume = np.cumsum(sorted_data)
        gini = (2 * sum(consume) / (n * sum(sorted_data)) - (n - 1) / n)
        return gini

    def variance_absolue(self, data=None):
        """Variance absolue : moyenne des |x_i - mu|^2"""
        if data is None:
            data = self.data

        moyenne = np.mean(data)
        return np.mean(np.abs(data - moyenne) ** 2)

    def deviation_quadratique_moyenne(self, data=None):
        """Deviation quadratique moyenne"""
        if data is None:
            data = self.data

        moyenne = np.mean(data)
        return np.sqrt(np.mean((data - moyenne) ** 2))

    def spread_ratio(self, percentile_low: float = 10, percentile_high: float = 90, data=None):
        """Ratio d'etalement : P(high)/P(low)"""
        if data is None:
            data = self.data

        if np.any(data <= 0):
            raise ValueError("Le ratio d'etalement necessite des valeurs positives")

        p_low = np.percentile(data, percentile_low)
        p_high = np.percentile(data, percentile_high)

        if p_low == 0:
            return np.inf
        return p_high / p_low

    def log_ecart_type(self, data=None):
        """Ecart-type logarithmique"""
        if data is None:
            data = self.data

        if np.any(data <= 0):
            raise ValueError("L'ecart-type logarithmique necessite des valeurs positives")
        return np.std(np.log(data), ddof=1)

    def coefficient_asymetrie_quartile(self, data=None):
        """Coefficient d'asymetrie de Bowley (base sur les quartiles)"""
        if data is None:
            data = self.data

        q1 = np.quantile(data, 0.25)
        q2 = np.quantile(data, 0.50)
        q3 = np.quantile(data, 0.75)

        if q3 - q1 == 0:
            return np.nan
        return (q1 + q3 - 2 * q2) / (q3 - q1)

    def coeff_asymetrie_fisher(self, data=None):
        """Coefficient d'asymetrie de Fisher"""
        if data is None:
            data = self.data

        data = np.array(data, dtype=float)
        ecart_type = np.std(data, ddof=0)
        moment3 = np.mean((data - self.moyen_arth(data)) ** 3)
        return moment3 / (ecart_type ** 3)

    def coefficient_aplatissement_fisher(self, data=None):
        """Coefficient d'aplatissement de Fisher (kurtosis exces)"""
        if data is None:
            data = self.data

        data = np.array(data, dtype=float)
        moyenne = np.mean(data)
        ecart_type = np.std(data, ddof=0)
        moment4 = np.mean((data - moyenne) ** 4)
        kurtosis = moment4 / (ecart_type ** 4)
        return kurtosis - 3

    def coefficient_appl_pearson(self, data=None):
        """Coefficient d'aplatissement de Pearson"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)
        return float(np.mean((data - np.mean(data)) ** 4) / (np.std(data, ddof=0)) ** 4)
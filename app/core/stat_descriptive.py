from typing import Dict, Any, Optional, List, Tuple, Union
import warnings
import numpy as np
import pandas as pd
from scipy import stats,integrate
from scipy.stats import skew, kurtosis, pearsonr, spearmanr, kendalltau

class stat_fonctions:
    def __init__(self, data):
        self.data = np.array(data, dtype=float)
        if len(self.data) == 0:                          
            raise ValueError("il n'y a pas des donnees")

    # ==== MESURES DE TENDANCE CENTRALES ====
    
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
        return len(data) / np.sum(1.0 / data)

    def moyen_quadr(self, data=None):
        """moyenne quadratique"""
        if data is None:
            data = self.data
        return np.sqrt(np.mean(np.square(data)))

    def moyen_cubique(self, data=None):
        """moyenne cubique"""
        if data is None:
            data = self.data
        return np.mean(np.abs(data)**3)**(1/3)

    def moyen_contrharm(self, data=None):
        """moyenne contra-harmonique"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)
        if np.sum(data) == 0:
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

    def quintiles(self, data=None):
        """retourne les 4 quintiles"""
        if data is None:
            data = self.data
        quintiles = {}
        for i in range(1, 5):
            quintiles[f'q{i}'] = np.quantile(data, i / 5)
        return quintiles

    def septiles(self, data=None):
        """retourne les 6 septiles"""
        if data is None:
            data = self.data
        septiles = {}
        for i in range(1, 7):
            septiles[f's{i}'] = np.quantile(data, i / 7)
        return septiles

    def octiles(self, data=None):
        """retourne les 7 octiles"""
        if data is None:
            data = self.data
        octiles = {}
        for i in range(1, 8):
            octiles[f'o{i}'] = np.quantile(data, i / 8)
        return octiles

    def deciles(self, data=None):
        """retourne les 9 deciles"""
        if data is None:
            data = self.data
        deciles = {}
        for i in range(1, 10):
            deciles[f'd{i}'] = np.quantile(data, i / 10)
        return deciles

    def percentiles(self, percentiles=None, data=None):
        """retourne les percentiles demandes"""
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
        quartile = self.quartiles(data)
        return (quartile['Q1'] + 2 * quartile['Q2'] + quartile['Q3']) / 4

    def moyenne_ponderee_harm(self, poids: np.ndarray, data=None):
        """moyenne harmonique ponderee"""
        if data is None:
            data = self.data
        if np.any(data <= 0):
            raise ValueError("les donnees doivent etre positives")
        return np.sum(poids) / np.sum(poids / data)

    def moyenne_ponderee_geo(self, poids: np.ndarray, data=None):
        """moyenne geometrique ponderee"""
        if data is None:
            data = self.data
        if np.any(data <= 0):
            raise ValueError("les donnees doivent etre positives")
        return np.exp(np.sum(poids * np.log(data)) / np.sum(poids))

    def moyenne_ponderee_quad(self, poids: np.ndarray, data=None):
        """moyenne quadratique ponderee"""
        if data is None:
            data = self.data
        return np.sqrt(np.sum(poids * data**2) / np.sum(poids))

    def moyenne_lehmer(self, p: float, data=None):
        """moyenne de Lehmer d'ordre p"""
        if data is None:
            data = self.data
        if np.sum(data**(p-1)) == 0:
            return np.nan
        return np.sum(data**p) / np.sum(data**(p-1))

    def moyenne_puissance(self, r: float, data=None):
        """moyenne de puissance d'ordre r"""
        return self.moyen_gen(r, data)

    # ====PARAMETRES DE DISPERSION =====

    def etendue(self, data=None):
        """etendue simple"""
        if data is None:
            data = self.data
        return np.max(data) - np.min(data)

    def variance_ech(self, data=None, ddof: int = 1):
        """variance echantillon"""
        if data is None:
            data = self.data
        return np.var(data, ddof=ddof)

    def variance_pop(self, data=None):
        """variance population"""
        if data is None:
            data = self.data
        return np.var(data, ddof=0)

    def ecart_type(self, data=None, ddof: int = 1):
        """ecart-type simple"""
        if data is None:
            data = self.data
        return np.std(data, ddof=ddof)

    def erreur_standard(self, data=None):
        """erreur standard de la moyenne"""
        if data is None:
            data = self.data
        return self.ecart_type(data, ddof=1) / np.sqrt(len(data))

    def ecart_abs_moyen(self, data=None):
        """ecart absolu moyen par rapport a la moyenne"""
        if data is None:
            data = self.data
        return np.mean(np.abs(data - self.moyen_arth(data)))

    def ecart_abs_median(self, data=None):
        """ecart absolu median par rapport a la mediane"""
        if data is None:
            data = self.data
        return np.mean(np.abs(data - self.mediane(data)))

    def ecart_interq(self, data=None):
        """ecart interquartile (Q3-Q1)"""
        if data is None:
            data = self.data
        q1 = np.quantile(data, 0.25)
        q3 = np.quantile(data, 0.75)
        return q3 - q1

    def ecart_semi_quart(self, data=None):
        """ecart semi-interquartile"""
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

    def ecart_type_geo(self, data=None):
        """ecart-type geometrique pour les donnees log-normales"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)
        if np.any(data < 0):
            raise ValueError("les donnees doivent etre positives")
        log_data = np.log(data[data > 0])
        if len(log_data) == 0:
            return 0.0
        return np.exp(np.std(log_data, ddof=1))

    def variance_geo(self, data=None):
        """variance geometrique"""
        if data is None:
            data = self.data
        return self.ecart_type_geo(data) ** 2

    def etendue_intercentile(self, p: float = 90, data=None):
        """etendue intercentile (difference entre deux percentiles symetriques)"""
        if data is None:
            data = self.data
        born_inf = (100 - p) / 2
        born_sup = (100 + p) / 2
        return np.percentile(data, born_sup) - np.percentile(data, born_inf)

    def etendue_interdecile(self, data=None):
        """etendue interdecile (difference entre 9eme et 1er decile)"""
        if data is None:
            data = self.data
        return np.quantile(data, 0.9) - np.quantile(data, 0.1)

    def etendue_interquintile(self, data=None):
        """etendue interquintile (difference entre 4eme et 1er quintile)"""
        if data is None:
            data = self.data
        return np.quantile(data, 0.8) - np.quantile(data, 0.2)

    def etendue_semi_interq(self, data=None):
        """etendue semi-interquartile"""
        return self.ecart_semi_quart(data)

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
        """Difference mediane absolue entre toutes les paires"""
        if data is None:
            data = self.data
        n = len(data)
        if n < 2:
            return 0
        differences = []
        for i in range(n):
            for j in range(i+1, n):
                differences.append(abs(data[i] - data[j]))
        return np.median(differences)

    def indice_gini(self, data=None):
        """indice de Gini (mesure d'inegalite)"""
        if data is None:
            data = self.data
        data = np.array(data, dtype=float)
        data = data[data >= 0]
        if len(data) == 0:
            return np.nan
        sorted_data = np.sort(data)
        n = len(sorted_data)
        cumsum = np.cumsum(sorted_data)
        return (2 * np.sum(cumsum) / (n * np.sum(sorted_data)) - (n + 1) / n)

    def mad(self, data=None):
        """Median Absolute Deviation (ecart absolu median robuste)"""
        if data is None:
            data = self.data
        median = self.mediane(data)
        return np.median(np.abs(data - median))

    def variance_ponderee(self, poids: np.ndarray, data=None):
        """variance ponderee"""
        if data is None:
            data = self.data
        moyenne_pond = self.moyen_pond(poids, data)
        return np.sum(poids * (data - moyenne_pond)**2) / np.sum(poids)

    def ecart_type_pond(self, poids: np.ndarray, data=None):
        """ecart-type pondere"""
        return np.sqrt(self.variance_ponderee(poids, data))

    def ecart_interpercentile(self, p_low=25, p_high=75, data=None):
        """ecart interpercentile generique"""
        if data is None:
            data = self.data
        return np.percentile(data, p_high) - np.percentile(data, p_low)

    def spread_ratio(self, p_low=10, p_high=90, data=None):
        """ratio d'etalement (P(high)/P(low))"""
        if data is None:
            data = self.data
        if np.any(data <= 0):
            raise ValueError("Le ratio d'etalement necessite des valeurs positives")
        q_low = np.percentile(data, p_low)
        q_high = np.percentile(data, p_high)
        return q_high / q_low if q_low != 0 else np.inf

    def variance_absolue(self, data=None):
        """variance absolue: moyenne des ecarts absolus au carre"""
        if data is None:
            data = self.data
        moyenne = self.moyen_arth(data)
        return np.mean(np.abs(data - moyenne) ** 2)

    def deviation_quadratique_moyenne(self, data=None):
        """deviation quadratique moyenne (racine de la variance absolue)"""
        if data is None:
            data = self.data
        return np.sqrt(np.mean((data - np.mean(data)) ** 2))

    def coefficient_dispersion_quartile(self, data=None):
        """coefficient de dispersion quartile: (Q3-Q1)/(Q3+Q1)"""
        if data is None:
            data = self.data
        q1, q3 = np.quantile(data, 0.25), np.quantile(data, 0.75)
        return (q3 - q1) / (q3 + q1) if (q3 + q1) != 0 else np.nan

    def ecart_type_log(self, data=None):
        """ecart-type logarithmique"""
        if data is None:
            data = self.data
        if np.any(data <= 0):
            raise ValueError("Les donnees doivent etre positives")
        return np.std(np.log(data), ddof=1)

    def variance_log(self, data=None):
        """variance logarithmique"""
        if data is None:
            data = self.data
        return self.ecart_type_log(data) ** 2

    def ecart_moyen_relative(self, data=None):
        """ecart moyen relatif (ecart moyen / moyenne)"""
        return self.ecart_abs_moyen(data) / self.moyen_arth(data) if self.moyen_arth(data) != 0 else np.nan

    def ecart_median_relative(self, data=None):
        """ecart median relatif"""
        return self.ecart_abs_median(data) / self.mediane(data) if self.mediane(data) != 0 else np.nan

    def indice_dispersion(self, data=None):
        """indice de dispersion pour donnees de comptage (variance/moyenne)"""
        return self.variance_pop(data) / self.moyen_arth(data) if self.moyen_arth(data) != 0 else np.nan

    def coefficient_dispersion_decile(self, data=None):
        """coefficient de dispersion base sur les deciles (D9-D1)/(D9+D1)"""
        d1 = np.quantile(data, 0.1)
        d9 = np.quantile(data, 0.9)
        return (d9 - d1) / (d9 + d1) if (d9 + d1) != 0 else np.nan

    def coefficient_dispersion_quartile_ajuste(self, data=None):
        """coefficient de dispersion quartile ajuste"""
        q1, q3 = np.quantile(data, 0.25), np.quantile(data, 0.75)
        return (q3 - q1) / (q3 + q1 - 2*self.mediane(data)) if (q3 + q1 - 2*self.mediane(data)) != 0 else np.nan

    def variance_relative(self, data=None):
        """variance relative (coeff_variation^2)"""
        cv = self.coeff_variation(data)
        return cv**2 if not np.isnan(cv) else np.nan

    def ecart_type_normalise(self, data=None):
        """ecart-type normalise par la moyenne quadratique"""
        rms = self.moyen_quadr(data)
        return self.ecart_type(data, ddof=0) / rms if rms != 0 else np.nan

    def etendue_normalisee(self, data=None):
        """etendue normalisee par l'ecart-type"""
        return self.etendue(data) / self.ecart_type(data, ddof=0) if self.ecart_type(data, ddof=0) != 0 else np.nan

    # === PARAMETRES DE FORME  ===

    def coeff_asymetrie_fisher(self, data=None):
        """coefficient d'asymetrie de Fisher (skewness)"""
        if data is None:
            data = self.data
        return skew(data, bias=False)

    def coefficient_aplatissement_fisher(self, data=None):
        """coefficient d'aplatissement de Fisher (kurtosis exces)"""
        if data is None:
            data = self.data
        return kurtosis(data, bias=False, fisher=True)

    def skewness_pearson1(self, data=None):
        """coefficient d'asymetrie de Pearson (1ere formule: moyenne-mode)"""
        if data is None:
            data = self.data
        mean, mode_val, std = self.moyen_arth(data), self.mode(data), self.ecart_type(data, ddof=0)
        if isinstance(mode_val, np.ndarray):
            mode_val = mode_val[0] if len(mode_val) > 0 else np.nan
        return (mean - mode_val) / std if std != 0 and not np.isnan(mode_val) else np.nan

    def skewness_pearson2(self, data=None):
        """coefficient d'asymetrie de Pearson (2eme formule: moyenne-mediane)"""
        if data is None:
            data = self.data
        mean, median, std = self.moyen_arth(data), self.mediane(data), self.ecart_type(data, ddof=0)
        return 3 * (mean - median) / std if std != 0 else np.nan

    def coefficient_asymetrie_quartile(self, data=None):
        """coefficient d'asymetrie de Bowley (base sur les quartiles)"""
        if data is None:
            data = self.data
        q1, q2, q3 = np.quantile(data, 0.25), np.quantile(data, 0.50), np.quantile(data, 0.75)
        return (q1 + q3 - 2*q2) / (q3 - q1) if (q3 - q1) != 0 else np.nan

    def skewness_quantile(self, data=None):
        """asymetrie basee sur les quantiles"""
        if data is None:
            data = self.data
        q1, q2, q3 = np.quantile(data, 0.25), np.quantile(data, 0.50), np.quantile(data, 0.75)
        return ((q3 - q2) - (q2 - q1)) / (q3 - q1) if (q3 - q1) != 0 else np.nan

    def coefficient_galtons(self, data=None):
        """coefficient de Galton (asymetrie basee sur les quartiles)"""
        if data is None:
            data = self.data
        q1, q2, q3 = np.quantile(data, 0.25), np.quantile(data, 0.50), np.quantile(data, 0.75)
        return (q2 - q1 - (q3 - q2)) / (q3 - q1) if (q3 - q1) != 0 else np.nan

    def coefficient_yule(self, data=None):
        """coefficient de Yule (asymetrie basee sur les quartiles)"""
        if data is None:
            data = self.data
        q1, q2, q3 = np.quantile(data, 0.25), np.quantile(data, 0.50), np.quantile(data, 0.75)
        num = (q3 - q2) - (q2 - q1)
        denom = (q3 - q2) + (q2 - q1)
        return num / denom if denom != 0 else np.nan

    def skewness_moments(self, data=None):
        """asymetrie basee sur les moments (identique a Fisher)"""
        return self.coeff_asymetrie_fisher(data)

    def skewness_ajuste(self, data=None):
        """asymetrie ajustee pour petits echantillons"""
        n = len(data) if data is None else len(self.data)
        g1 = self.coeff_asymetrie_fisher(data)
        return g1 * np.sqrt(n*(n-1)) / (n-2) if n > 2 else g1

    def kurtosis_moments(self, data=None):
        """kurtosis basee sur les moments (exces de Fisher)"""
        return self.coefficient_aplatissement_fisher(data)

    def kurtosis_ajuste(self, data=None):
        """kurtosis ajuste pour petits echantillons"""
        n = len(data) if data is None else len(self.data)
        g2 = self.coefficient_aplatissement_fisher(data)
        return ((n-1)*((n+1)*g2 + 6)) / ((n-2)*(n-3)) if n > 3 else g2

    def kurtosis_pearson(self, data=None):
        """kurtosis de Pearson (non centre)"""
        if data is None:
            data = self.data
        m2, m4 = self.moment_central(2, data), self.moment_central(4, data)
        return m4 / (m2**2) if m2 != 0 else np.nan

    def moment_central(self, ordre: int, data=None):
        """moment central d'ordre r"""
        if data is None:
            data = self.data
        return np.mean((data - np.mean(data)) ** ordre)

    def moment_non_central(self, ordre: int, data=None):
        """moment non-central d'ordre r"""
        if data is None:
            data = self.data
        return np.mean(data ** ordre)

    def moment_standardise(self, ordre: int, data=None):
        """moment standardise d'ordre r"""
        if data is None:
            data = self.data
        std = self.ecart_type(data, ddof=0)
        return self.moment_central(ordre, data) / (std ** ordre) if std != 0 else np.nan

    def moment_absolu(self, ordre: int, data=None):
        """moment absolu d'ordre r"""
        if data is None:
            data = self.data
        return np.mean(np.abs(data) ** ordre)

    def moment_central_absolu(self, ordre: int, data=None):
        """moment central absolu d'ordre r"""
        if data is None:
            data = self.data
        return np.mean(np.abs(data - np.mean(data)) ** ordre)

    def cumulant_ordre1(self, data=None):
        """cumulant d'ordre 1 (moyenne)"""
        return self.moyen_arth(data)

    def cumulant_ordre2(self, data=None):
        """cumulant d'ordre 2 (variance)"""
        return self.variance_pop(data)

    def cumulant_ordre3(self, data=None):
        """cumulant d'ordre 3 (asymetrie)"""
        if data is None:
            data = self.data
        return self.moment_central(3, data)

    def cumulant_ordre4(self, data=None):
        """cumulant d'ordre 4 (kurtosis)"""
        if data is None:
            data = self.data
        m2, m4 = self.moment_central(2, data), self.moment_central(4, data)
        return m4 - 3 * m2**2

    def index_multimodalite(self, data=None):
        """index de multimodalite (mesure la presence de plusieurs modes)"""
        if data is None:
            data = self.data
        modes = self.mode(data)
        if isinstance(modes, np.ndarray) and len(modes) > 1:
            return np.std(modes) / self.ecart_type(data, ddof=0)
        return 0.0

    def index_antimodalite(self, data=None):
        """index d'antimodalite (mesure l'absence de mode)"""
        if data is None:
            data = self.data
        hist, _ = np.histogram(data, bins='auto')
        hist = hist[hist > 0]
        return np.min(hist) / np.max(hist) if len(hist) > 0 else 1.0

    def index_platykurtique(self, data=None):
        """classification de la kurtosis"""
        kurt = self.coefficient_aplatissement_fisher(data)
        return "Platykurtique" if kurt < 0 else "Leptokurtique" if kurt > 0 else "Mesokurtique"

    def index_asymetrique(self, data=None):
        """classification de l'asymetrie"""
        skew_val = self.coeff_asymetrie_fisher(data)
        if abs(skew_val) < 0.1: return "Symetrique"
        return "Asymetrique positive" if skew_val > 0 else "Asymetrique negative"

    def coefficient_aplatissement_quartile(self, data=None):
        """coefficient d'aplatissement base sur les quartiles"""
        q1, q3 = np.quantile(data, 0.25), np.quantile(data, 0.75)
        p01, p99 = np.percentile(data, 1), np.percentile(data, 99)
        return (q3 - q1) / (p99 - p01) if (p99 - p01) != 0 else np.nan

    def coefficient_asymetrie_decile(self, data=None):
        """coefficient d'asymetrie base sur les deciles"""
        d1, d5, d9 = np.quantile(data, 0.1), np.quantile(data, 0.5), np.quantile(data, 0.9)
        return (d1 + d9 - 2*d5) / (d9 - d1) if (d9 - d1) != 0 else np.nan

    def coefficient_asymetrie_percentile(self, p_low=10, p_high=90, data=None):
        """coefficient d'asymetrie base sur deux percentiles"""
        p1 = np.percentile(data, p_low)
        p2 = np.percentile(data, 50)
        p3 = np.percentile(data, p_high)
        return (p1 + p3 - 2*p2) / (p3 - p1) if (p3 - p1) != 0 else np.nan

    # === PARAMETRES DE CONCENTRATION ===

    def concentration_herfindahl(self, data=None):
        """indice de Herfindahl (concentration)"""
        if data is None:
            data = self.data
        total = np.sum(data)
        if total == 0:
            return np.nan
        parts = data / total
        return np.sum(parts**2)
    def concentration_theil(self, data=None):
       """indice de Theil (inegalite)"""
       if data is None:
          data=self.data
       data = np.array(data)
       data = data[data > 0] 
       if len(data) == 0:
           return np.nan
       mean = np.mean(data)
       return np.mean((data/mean) * np.log(data/mean))

    def concentration_atkinson(self, epsilon=0.5, data=None):
        """indice d'Atkinson (inegalite avec aversion au risque)"""
        if data is None:
            data = self.data[data > 0]
        if len(data) == 0:
            return np.nan
        mean = np.mean(data)
        if epsilon == 1:
            return 1 - np.exp(np.mean(np.log(data))) / mean
        return 1 - (np.mean(data**(1-epsilon)))**(1/(1-epsilon)) / mean

    def concentration_hoover(self, data=None):
        """indice de Hoover (indice de dissimilarite)"""
        if data is None:
            data = self.data
        mean = np.mean(data)
        return np.sum(np.abs(data - mean)) / (2 * np.sum(data)) if np.sum(data) != 0 else np.nan

    def concentration_rosenbluth(self, data=None):
        """indice de Rosenbluth (concentration)"""
        if data is None:
            data = self.data
        total = np.sum(data)
        if total == 0:
            return np.nan
        parts = np.sort(data / total)[::-1]
        n = len(parts)
        return 1 / (2 * np.sum(parts * np.arange(1, n+1)) - 1)

    def concentration_entropy(self, data=None):
        """entropie de Shannon (concentration)"""
        if data is None:
            data = self.data
        total = np.sum(data)
        if total == 0:
            return np.nan
        parts = data[data > 0] / total
        return -np.sum(parts * np.log(parts))

    def concentration_simpson(self, data=None):
        """indice de Simpson (identique a Herfindahl)"""
        return self.concentration_herfindahl(data)

    def concentration_berger_parker(self, data=None):
        """indice de Berger-Parker (concentration de la plus grande part)"""
        if data is None:
            data = self.data
        total = np.sum(data)
        return np.max(data) / total if total != 0 else np.nan

    def ratio_concentration(self, p=0.5, data=None):
        """ratio de concentration (part des p plus grandes valeurs)"""
        if data is None:
            data = self.data
        total = np.sum(data)
        if total == 0:
            return np.nan
        k = max(1, int(len(data) * p))
        return np.sum(np.sort(data)[::-1][:k]) / total

    def indice_polarisation(self, data=None):
        """indice de polarisation de Wolfson"""
        if data is None:
            data = self.data
        gini = self.indice_gini(data)
        mean, median = self.moyen_arth(data), self.mediane(data)
        return 2 * (2*median - mean) * gini / mean if mean != 0 else np.nan

    def indice_diversite(self, data=None):
        """indice de diversite (exponentielle de l'entropie)"""
        return np.exp(self.concentration_entropy(data))

    def indice_dominance(self, data=None):
        """indice de dominance (1 - entropie normalisee)"""
        if data is None:
            data = self.data
        return 1 - self.concentration_entropy(data) / np.log(len(data)) if len(data) > 1 else 1

    def coefficient_monopole(self, data=None):
        """coefficient de monopole (mesure de concentration)"""
        if data is None:
            data = self.data
        total, n = np.sum(data), len(data)
        if total == 0:
            return np.nan
        max_part = np.max(data) / total
        return (max_part - 1/n) / (1 - 1/n) if n > 1 else max_part

    def indice_egalite(self, data=None):
        """indice d'egalite (1 - Gini)"""
        return 1 - self.indice_gini(data)

    def indice_inegalite_1(self, data=None):
        """indice d'inegalite (Gini)"""
        return self.indice_gini(data)

    def indice_inegalite_2(self, data=None):
        """indice d'inegalite de Coulter"""
        return self.coeff_variation(data) / 2

    def indice_inegalite_3(self, data=None):
        """indice d'inegalite de Schutz"""
        return self.concentration_hoover(data)

    def courbe_lorenz(self, data=None):
        """courbe de Lorenz (x: proportion de population, y: proportion de richesse)"""
        if data is None:
            data = self.data
        data_sorted = np.sort(data)
        total = np.sum(data_sorted)
        if total == 0:
            return np.linspace(0, 1, len(data_sorted)), np.zeros(len(data_sorted))
        cumsum = np.cumsum(data_sorted) / total
        return np.linspace(0, 1, len(data_sorted)), cumsum

    def aire_inegalite_lorenz(self, data=None):
        """aire d'inegalite de Lorenz (entre courbe et diagonale)"""
        if data is None:
            data = self.data
        x, y = self.courbe_lorenz(data)
        return integrate.trapezoid(x - y, x)

    def concentration_fraction(self, fraction=0.5, data=None):
        """fraction de la population possedant une fraction donnee de la richesse"""
        if data is None:
            data = self.data
        total = np.sum(data)
        if total == 0:
            return np.nan
        cumsum = np.cumsum(np.sort(data)[::-1])
        return np.searchsorted(cumsum, fraction * total) / len(data)

    def indice_concentration_10_20(self, data=None):
        """indice de concentration 10/20"""
        return self.ratio_concentration(0.1, data) / self.ratio_concentration(0.2, data)

    def indice_concentration_20_40(self, data=None):
        """indice de concentration 20/40"""
        return self.ratio_concentration(0.2, data) / self.ratio_concentration(0.4, data)
    def rapport_interdecile(self,data=None):
        if data is None:
            data=self.data
        data=np.array(data)
        if len(data)==0:
            print("Attention: données vides")
            return np.nan
        if np.all(np.isnan(data)):
            print("Attention: toutes les données sont NaN")
            return np.nan
        if np.any(np.isnan(data)):
            print("Attention: des données sont NaN")
            data = data[~np.isnan(data)]
        d1=np.quantile(data,0.1)
        d9=np.quantile(data,0.9)
        if d1==0:
            print("Attention: D1 est égal à zéro, le rapport peut être infini")
            return np.inf
        return d9/d1
        
        
    def rapport_interquartile(self, data=None):
        """rapport interquartile (Q3/Q1)"""
        if data is None:
           data = self.data
        data = np.array(data)

        if len(data) == 0:
           print("Attention: données vides")
           return np.nan
    
        if np.all(np.isnan(data)):
           print("Attention: toutes les données sont NaN")
           return np.nan
    
        if np.any(np.isnan(data)):
           data = data[~np.isnan(data)]
    
        if np.any(data <= 0):
           print("Attention: des valeurs <= 0 existent, le rapport peut être infini")
    
        q1 = np.quantile(data, 0.25)
        q3 = np.quantile(data, 0.75)
    
        if q1 == 0:
           return np.inf
        return q3 / q1
    

    def courbe_concentration(self, data=None):
        """courbe de concentration (part cumulative)"""
        if data is None:
            data = self.data
        return np.cumsum(np.sort(data)[::-1]) / np.sum(data)
    def rapport_interdecile(self, data=None):
        """rapport interdecile (D9/D1)"""
        if data is None:
           data=self.data
        data = np.array(data)
        if len(data) == 0:
           return np.nan
        d1 = np.quantile(data, 0.1)
        d9 = np.quantile(data, 0.9)
        return d9 / d1 if d1 != 0 else np.inf

    # ===PARAMETRES DE DEPENDANCE ===

    def correlation_pearson(self, y, x=None):
        """coefficient de correlation de Pearson"""
        if x is None:
            x = self.data
        return np.corrcoef(x, y)[0,1]

    def correlation_spearman(self, y, x=None):
        """coefficient de correlation de Spearman (rang)"""
        if x is None:
            x = self.data
        return spearmanr(x, y)[0]

    def correlation_kendall(self, y, x=None):
        """coefficient de correlation de Kendall (tau)"""
        if x is None:
            x = self.data
        return kendalltau(x, y)[0]

    def covariance(self, y, x=None):
        """covariance entre deux variables"""
        if x is None:
            x = self.data
        return np.cov(x, y, ddof=1)[0,1]

    def correlation_partielle(self, y, z, x=None):
        """correlation partielle entre x et y en controllant par z"""
        if x is None:
            x = self.data
        r_xy = self.correlation_pearson(y, x)
        r_xz = self.correlation_pearson(z, x)
        r_yz = self.correlation_pearson(z, y)
        denom = np.sqrt((1 - r_xz**2) * (1 - r_yz**2))
        return (r_xy - r_xz * r_yz) / denom if denom != 0 else np.nan

    def correlation_semi_partielle(self, y, z, x=None):
        """correlation semi-partielle"""
        if x is None:
            x = self.data
        r_xy = self.correlation_pearson(y, x)
        r_xz = self.correlation_pearson(z, x)
        r_yz = self.correlation_pearson(z, y)
        return (r_xy - r_xz * r_yz) / np.sqrt(1 - r_yz**2) if abs(r_yz) != 1 else np.nan

    def correlation_distance(self, y, x=None):
        """correlation de distance"""
        if x is None:
            x = self.data
        return stats.distance_correlation(x, y)

    def correlation_quadrant(self, y, x=None):
        """correlation par quadrant"""
        if x is None:
            x = self.data
        med_x, med_y = np.median(x), np.median(y)
        return np.mean(np.sign(x - med_x) * np.sign(y - med_y))

    def dependence_mutuelle(self, y, bins=10, x=None):
        """information mutuelle"""
        if x is None:
            x = self.data
        hist, _, _ = np.histogram2d(x, y, bins=bins)
        hist = hist / np.sum(hist)
        hist_x, hist_y = np.sum(hist, axis=1), np.sum(hist, axis=0)
        mi = 0
        for i in range(bins):
            for j in range(bins):
                if hist[i,j] > 0:
                    mi += hist[i,j] * np.log(hist[i,j] / (hist_x[i] * hist_y[j]))
        return mi

    def autocorrelation(self, lag=1, data=None):
        """autocorrelation"""
        if data is None:
            data = self.data
        if len(data) <= lag:
            return np.nan
        return np.corrcoef(data[:-lag], data[lag:])[0,1]

    def autocovariance(self, lag=1, data=None):
        """autocovariance"""
        if data is None:
            data = self.data
        if len(data) <= lag:
            return np.nan
        return np.cov(data[:-lag], data[lag:], ddof=1)[0,1]

    def autocorrelation_partielle(self, lag=1, data=None):
        """autocorrelation partielle (approximation)"""
        if lag == 1:
            return self.autocorrelation(1, data)
        return np.nan

    def coefficient_concordance(self, y, x=None):
        """coefficient de concordance de Kendall"""
        if x is None:
            x = self.data
        n = len(x)
        concordant = sum((x[i]-x[j])*(y[i]-y[j]) > 0 for i in range(n) for j in range(i+1, n))
        discordant = sum((x[i]-x[j])*(y[i]-y[j]) < 0 for i in range(n) for j in range(i+1, n))
        return (concordant - discordant) / (concordant + discordant) if (concordant + discordant) > 0 else 0

    def correlation_point_biserial(self, y, x=None):
        """correlation point-biseriale"""
        if x is None:
            x = self.data
        y_binary = (y > np.median(y)).astype(float)
        return np.corrcoef(x, y_binary)[0,1]

    def coefficient_determination(self, y, x=None):
        """coefficient de determination R²"""
        if x is None:
            x = self.data
        return self.correlation_pearson(y, x)**2

    def correlation_alpha(self, items=None):
        """alpha de Cronbach"""
        if items is None:
            items = self.data
        if items.ndim == 1:
            return 1.0
        k = items.shape[1]
        var_total = np.var(np.sum(items, axis=1), ddof=1)
        var_sum = np.sum([np.var(items[:, i], ddof=1) for i in range(k)])
        return (k/(k-1)) * (1 - var_sum/var_total) if var_total > 0 and k > 1 else np.nan

    def correlation_matricielle(self, data=None):
        """matrice de correlation"""
        if data is None:
            data = self.data
        if data.ndim == 1:
            return np.array([[1.0]])
        return np.corrcoef(data.T)

    def correlation_rank_fisher(self, y, x=None):
        """transformation de Fisher de la correlation de rang"""
        r = self.correlation_spearman(y, x)
        return 0.5 * np.log((1+r)/(1-r)) if abs(r) < 1 else np.nan

    def dependance_copule(self, y, x=None):
        """coefficient de dependance base sur les copules"""
        if x is None:
            x = self.data
        u = stats.rankdata(x) / (len(x) + 1)
        v = stats.rankdata(y) / (len(y) + 1)
        return np.corrcoef(u, v)[0,1]

    def correlation_biweight(self, y, x=None):
        """correlation biweight (robuste)"""
        if x is None:
            x = self.data
        med_x, med_y = np.median(x), np.median(y)
        mad_x, mad_y = np.median(np.abs(x-med_x)), np.median(np.abs(y-med_y))
        if mad_x == 0 or mad_y == 0:
            return 0
        u, v = (x-med_x)/(9*mad_x), (y-med_y)/(9*mad_y)
        u, v = np.clip(u, -1, 1), np.clip(v, -1, 1)
        a, b = (1-u**2)**2, (1-v**2)**2
        num = np.sum(a*b*np.sign(u)*np.sign(v))
        denom = np.sqrt(np.sum((a*np.sign(u))**2) * np.sum((b*np.sign(v))**2))
        return num/denom if denom != 0 else 0

    def correlation_pearson_robuste(self, y, trim=0.1, x=None):
        """correlation de Pearson avec trimming"""
        if x is None:
            x = self.data
        n = len(x)
        k = int(n * trim)
        if k == 0:
            return self.correlation_pearson(y, x)
        idx = np.argsort(x)
        idx_keep = idx[k:n-k]
        return np.corrcoef(x[idx_keep], y[idx_keep])[0,1]

    def correlation_spearman_robuste(self, y, trim=0.1, x=None):
        """correlation de Spearman avec trimming"""
        if x is None:
            x = self.data
        n = len(x)
        k = int(n * trim)
        if k == 0:
            return self.correlation_spearman(y, x)
        idx = np.argsort(x)
        idx_keep = idx[k:n-k]
        return spearmanr(x[idx_keep], y[idx_keep])[0]

    def covariance_robuste(self, y, trim=0.1, x=None):
        """covariance robuste avec trimming"""
        if x is None:
            x = self.data
        n = len(x)
        k = int(n * trim)
        if k == 0:
            return self.covariance(y, x)
        idx = np.argsort(x)
        idx_keep = idx[k:n-k]
        return np.cov(x[idx_keep], y[idx_keep], ddof=1)[0,1]

    def correlation_canonique(self, X, Y):
        """correlation canonique entre deux ensembles de variables"""
        X = np.array(X)
        Y = np.array(Y)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if Y.ndim == 1:
            Y = Y.reshape(-1, 1)
        X_centered = X - np.mean(X, axis=0)
        Y_centered = Y - np.mean(Y, axis=0)
        C_xx = X_centered.T @ X_centered
        C_yy = Y_centered.T @ Y_centered
        C_xy = X_centered.T @ Y_centered
        try:
            C_xx_inv = np.linalg.pinv(C_xx)
            C_yy_inv = np.linalg.pinv(C_yy)
            M = C_xx_inv @ C_xy @ C_yy_inv @ C_xy.T
            eigvals = np.linalg.eigvals(M)
            return np.sqrt(np.max(np.real(eigvals[eigvals > 0])))
        except:
            return np.nan

    def correlation_cross(self, y, lag=0, x=None):
        """correlation croisee entre deux series"""
        if x is None:
            x = self.data
        if lag >= 0:
            return np.corrcoef(x[:-lag] if lag > 0 else x, y[lag:] if lag > 0 else y)[0,1]
        return np.corrcoef(x[-lag:], y[:lag])[0,1]

    def coherence_croisee(self, y, x=None):
        """coherence croisee (correlation absolue moyenne sur plusieurs lags)"""
        if x is None:
            x = self.data
        n = len(x)
        max_lag = min(10, n//4)
        correlations = []
        for lag in range(-max_lag, max_lag+1):
            if lag >= 0:
                if len(x[:-lag]) > 1 and len(y[lag:]) > 1:
                    correlations.append(abs(np.corrcoef(x[:-lag] if lag > 0 else x, y[lag:] if lag > 0 else y)[0,1]))
            else:
                if len(x[-lag:]) > 1 and len(y[:lag]) > 1:
                    correlations.append(abs(np.corrcoef(x[-lag:], y[:lag])[0,1]))
        return np.mean(correlations) if correlations else 0

    # ===PARAMETRES DE DISTRIBUTION EMPIRIQUE ===

    def fonction_repartition_emp(self, x, data=None):
        """fonction de repartition empirique F(x) = P(X <= x)"""
        if data is None:
            data = self.data
        return np.mean(data <= x)

    def fonction_quantile_emp(self, p, data=None):
        """fonction quantile empirique Q(p) = F^{-1}(p)"""
        if data is None:
            data = self.data
        return np.quantile(data, p)

    def densite_noyau(self, x, bandwidth='scott', data=None):
        """estimation de densite par noyau (KDE)"""
        if data is None:
            data = self.data
        kde = stats.gaussian_kde(data, bw_method=bandwidth)
        return kde(x)

    def fonction_survie(self, x, data=None):
        """fonction de survie empirique S(x) = P(X > x)"""
        if data is None:
            data = self.data
        return 1 - self.fonction_repartition_emp(x, data)

    def fonction_hasard_emp(self, x, data=None):
        """fonction de hasard empirique (approximation)"""
        if data is None:
            data = self.data
        survie = self.fonction_survie(x, data)
        if survie == 0:
            return np.inf
        h = np.std(data) * len(data)**(-1/5)
        f_x = self.densite_noyau(x, data=data)
        return f_x / survie

    def histogramme(self, bins='auto', data=None):
        """histogramme des donnees (comptes et bins)"""
        if data is None:
            data = self.data
        return np.histogram(data, bins=bins)

    def densite_histogramme(self, bins='auto', data=None):
        """densite normalisee par histogramme"""
        if data is None:
            data = self.data
        counts, bins = np.histogram(data, bins=bins, density=True)
        return counts, bins

    def ecart_inter_quantile(self, p_low=0.25, p_high=0.75, data=None):
        """ecart entre deux quantiles empiriques"""
        if data is None:
            data = self.data
        return np.quantile(data, p_high) - np.quantile(data, p_low)

    def ratio_quantile(self, p_low=0.1, p_high=0.9, data=None):
        """ratio entre deux quantiles empiriques"""
        if data is None:
            data = self.data
        if np.any(data <= 0):
            raise ValueError("Le ratio de quantiles necessite des valeurs positives")
        q_low = np.quantile(data, p_low)
        q_high = np.quantile(data, p_high)
        return q_high / q_low if q_low != 0 else np.inf

    def asymetrie_quantile_emp(self, data=None):
        """asymetrie basee sur les quantiles empiriques"""
        if data is None:
            data = self.data
        q1 = np.quantile(data, 0.25)
        q2 = np.quantile(data, 0.50)
        q3 = np.quantile(data, 0.75)
        return (q1 + q3 - 2*q2) / (q3 - q1) if (q3 - q1) != 0 else np.nan

    def aplatissement_quantile_emp(self, data=None):
        """aplatissement base sur les quantiles empiriques"""
        if data is None:
            data = self.data
        q1 = np.quantile(data, 0.25)
        q3 = np.quantile(data, 0.75)
        q01 = np.quantile(data, 0.1)
        q09 = np.quantile(data, 0.9)
        return (q3 - q1) / (q09 - q01) if (q09 - q01) != 0 else np.nan

    def variance_empirique(self, data=None):
        """variance empirique (population)"""
        return self.variance_pop(data)

    def ecart_type_empirique(self, data=None):
        """ecart-type empirique (population)"""
        return self.ecart_type(data, ddof=0)

    def skewness_empirique(self, data=None):
        """asymetrie empirique"""
        return self.coeff_asymetrie_fisher(data)

    def kurtosis_empirique(self, data=None):
        """kurtosis empirique (exces)"""
        return self.coefficient_aplatissement_fisher(data)
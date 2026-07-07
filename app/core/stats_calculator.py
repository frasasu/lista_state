
from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats as sps

from .dataframe import DataTable


def _clean(data: Sequence[Any]) -> np.ndarray:
    """Convertit une séquence hétérogène en tableau numpy de float, en
    ignorant les valeurs manquantes / non numériques (via pandas, qui gère
    déjà tous les cas limites correctement)."""
    s = pd.to_numeric(pd.Series(list(data)), errors="coerce")
    return s.dropna().to_numpy(dtype=float)


class StatsCalculator:
    """Statistiques descriptives et inférentielles, propulsées par
    numpy / scipy.stats / statsmodels."""

    def __init__(self, df: Optional[DataTable] = None):
        self.df = df

    def set_dataframe(self, df: DataTable):
        self.df = df

    # ==================================================================
    # TENDANCE CENTRALE
    # ==================================================================
    def mean(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        return float(np.mean(a)) if a.size else None

    def median(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        return float(np.median(a)) if a.size else None

    def mode(self, data: List[Any]) -> List[Any]:
        s = pd.Series([d for d in data if d is not None])
        if s.empty:
            return []
        return s.mode().tolist()

    def geometric_mean(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        a = a[a > 0]
        return float(sps.gmean(a)) if a.size else None

    def harmonic_mean(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        a = a[a > 0]
        return float(sps.hmean(a)) if a.size else None

    def quadratic_mean(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        return float(np.sqrt(np.mean(np.square(a)))) if a.size else None

    def weighted_mean(self, data: List[Union[int, float]], weights: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        w = _clean(weights)
        n = min(len(a), len(w))
        if n == 0:
            return None
        return float(np.average(a[:n], weights=w[:n]))

    def trimmed_mean(self, data: List[Union[int, float]], proportion: float = 0.1) -> Optional[float]:
        a = _clean(data)
        if not a.size:
            return None
        return float(sps.trim_mean(a, proportion))

    def midrange(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        return float((a.max() + a.min()) / 2) if a.size else None

    # ==================================================================
    # DISPERSION
    # ==================================================================
    def variance(self, data: List[Union[int, float]], ddof: int = 1) -> Optional[float]:
        a = _clean(data)
        return float(np.var(a, ddof=ddof)) if a.size > ddof else 0.0

    def std(self, data: List[Union[int, float]], ddof: int = 1) -> Optional[float]:
        a = _clean(data)
        return float(np.std(a, ddof=ddof)) if a.size > ddof else 0.0

    def range_stat(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        return float(a.max() - a.min()) if a.size else None

    def iqr(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        return float(sps.iqr(a)) if a.size else None

    def mad(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        return float(np.mean(np.abs(a - np.mean(a)))) if a.size else None

    def cv(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        m = np.mean(a) if a.size else 0
        return float(np.std(a, ddof=1) / m) if a.size > 1 and m != 0 else None

    def quantile(self, data: List[Union[int, float]], q: float) -> Optional[float]:
        a = _clean(data)
        return float(np.quantile(a, q)) if a.size else None

    def quantiles(self, data: List[Union[int, float]], probs: List[float]) -> List[float]:
        a = _clean(data)
        return [float(x) for x in np.quantile(a, probs)] if a.size else []

    def percentile(self, data: List[Union[int, float]], p: float) -> Optional[float]:
        return self.quantile(data, p / 100)

    def percentiles(self, data: List[Union[int, float]], ps: List[float]) -> List[float]:
        return self.quantiles(data, [p / 100 for p in ps])

    def skewness(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        return float(sps.skew(a, bias=False)) if a.size > 2 else None

    def kurtosis(self, data: List[Union[int, float]]) -> Optional[float]:
        a = _clean(data)
        return float(sps.kurtosis(a, bias=False)) if a.size > 3 else None

    def moment(self, data: List[Union[int, float]], k: int) -> Optional[float]:
        a = _clean(data)
        return float(sps.moment(a, moment=k)) if a.size else None

    # ==================================================================
    # COMPTAGE / FRÉQUENCES
    # ==================================================================
    def count(self, data: List[Any]) -> int:
        return sum(1 for d in data if d is not None)

    def count_all(self, data: List[Any]) -> int:
        return len(data)

    def count_unique(self, data: List[Any]) -> int:
        return pd.Series(data).nunique(dropna=True)

    def freq_table(self, data: List[Any]) -> Dict[Any, int]:
        return pd.Series(data).value_counts(dropna=True).to_dict()

    def missing_count(self, data: List[Any]) -> int:
        return int(pd.isna(pd.Series(data)).sum())

    def missing_ratio(self, data: List[Any]) -> float:
        n = len(data)
        return float(self.missing_count(data) / n) if n else 0.0

    def entropy(self, data: List[Any], base: float = 2.0) -> float:
        counts = pd.Series(data).value_counts(dropna=True)
        return float(sps.entropy(counts.to_numpy(), base=base)) if len(counts) else 0.0

    def gini(self, data: List[Union[int, float]]) -> Optional[float]:
        a = np.sort(_clean(data))
        if a.size == 0 or a.sum() == 0:
            return None
        n = a.size
        cum = np.cumsum(a)
        return float((n + 1 - 2 * np.sum(cum) / cum[-1]) / n)

    # ==================================================================
    # RELATIONS ENTRE VARIABLES
    # ==================================================================
    def covariance(self, x: List[Union[int, float]], y: List[Union[int, float]], ddof: int = 1) -> Optional[float]:
        df = pd.DataFrame({"x": pd.to_numeric(pd.Series(x), errors="coerce"),
                            "y": pd.to_numeric(pd.Series(y), errors="coerce")}).dropna()
        if len(df) < 2:
            return None
        return float(np.cov(df["x"], df["y"], ddof=ddof)[0, 1])

    def correlation(self, x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
        df = pd.DataFrame({"x": pd.to_numeric(pd.Series(x), errors="coerce"),
                            "y": pd.to_numeric(pd.Series(y), errors="coerce")}).dropna()
        if len(df) < 2 or df["x"].std() == 0 or df["y"].std() == 0:
            return float("nan")
        r, _ = sps.pearsonr(df["x"], df["y"])
        return float(r)

    def spearman_correlation(self, x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
        df = pd.DataFrame({"x": pd.to_numeric(pd.Series(x), errors="coerce"),
                            "y": pd.to_numeric(pd.Series(y), errors="coerce")}).dropna()
        if len(df) < 2:
            return float("nan")
        r, _ = sps.spearmanr(df["x"], df["y"])
        return float(r)

    def kendall_tau(self, x: List[Union[int, float]], y: List[Union[int, float]]) -> float:
        df = pd.DataFrame({"x": pd.to_numeric(pd.Series(x), errors="coerce"),
                            "y": pd.to_numeric(pd.Series(y), errors="coerce")}).dropna()
        if len(df) < 2:
            return float("nan")
        tau, _ = sps.kendalltau(df["x"], df["y"])
        return float(tau)

    def covariance_matrix(self, columns: List[str]) -> Dict[str, Dict[str, float]]:
        sub = self.df.frame[columns].apply(pd.to_numeric, errors="coerce")
        return sub.cov().round(6).to_dict()

    def correlation_matrix(self, columns: List[str], method: str = "pearson") -> Dict[str, Dict[str, float]]:
        sub = self.df.frame[columns].apply(pd.to_numeric, errors="coerce")
        return sub.corr(method=method).round(6).to_dict()

    # ==================================================================
    # DESCRIBE / DESCRIBE_ALL / SUMMARY
    # ==================================================================
    def describe(self, columns: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
        """Statistiques descriptives complètes, via `pandas.DataFrame.describe`
        enrichi de skewness/kurtosis/IQR (scipy)."""
        frame = self.df.frame
        numeric_cols = list(frame.select_dtypes(include=[np.number]).columns)
        cols = [c for c in (columns or numeric_cols) if c in frame.columns]

        result: Dict[str, Dict[str, float]] = {}
        for col in cols:
            series = pd.to_numeric(frame[col], errors="coerce").dropna()
            if series.empty:
                continue
            desc = series.describe()
            result[col] = {
                "count": float(desc["count"]),
                "mean": float(desc["mean"]),
                "std": float(desc["std"]) if not pd.isna(desc["std"]) else 0.0,
                "min": float(desc["min"]),
                "25%": float(desc["25%"]),
                "50%": float(desc["50%"]),
                "75%": float(desc["75%"]),
                "max": float(desc["max"]),
                "skewness": float(sps.skew(series, bias=False)) if len(series) > 2 else 0.0,
                "kurtosis": float(sps.kurtosis(series, bias=False)) if len(series) > 3 else 0.0,
                "iqr": float(sps.iqr(series)),
                "missing": int(frame[col].isna().sum()),
            }
        return result

    def describe_all(self) -> Dict[str, Dict[str, Any]]:
        """Décrit toutes les colonnes (numériques ET catégorielles)."""
        frame = self.df.frame
        result: Dict[str, Dict[str, Any]] = {}
        numeric_cols = set(frame.select_dtypes(include=[np.number]).columns)
        for col in frame.columns:
            if col in numeric_cols:
                result[col] = {"dtype": "numeric", **self.describe([col]).get(col, {})}
            else:
                vc = frame[col].value_counts(dropna=True)
                result[col] = {
                    "dtype": "categorical",
                    "count": int(frame[col].notna().sum()),
                    "unique": int(frame[col].nunique(dropna=True)),
                    "top": vc.index[0] if len(vc) else None,
                    "freq": int(vc.iloc[0]) if len(vc) else 0,
                    "missing": int(frame[col].isna().sum()),
                }
        return result

    def summary(self) -> Dict[str, Any]:
        frame = self.df.frame
        return {
            "shape": list(frame.shape),
            "columns": list(frame.columns),
            "dtypes": {c: str(t) for c, t in frame.dtypes.items()},
            "missing_total": int(frame.isna().sum().sum()),
            "missing_by_column": {c: int(v) for c, v in frame.isna().sum().items()},
            "numeric_columns": list(frame.select_dtypes(include=[np.number]).columns),
            "categorical_columns": list(frame.select_dtypes(exclude=[np.number]).columns),
        }

    # ==================================================================
    # TESTS D'HYPOTHÈSES (INFÉRENTIEL) — via scipy.stats
    # ==================================================================
    def t_test_onesample(self, data: List[Union[int, float]], mu: float) -> Dict[str, float]:
        a = _clean(data)
        if a.size < 2:
            return {"statistic": None, "p_value": None, "df": 0}
        res = sps.ttest_1samp(a, popmean=mu)
        return {"statistic": float(res.statistic), "p_value": float(res.pvalue), "df": int(a.size - 1)}

    def t_test_independent(self, group1: List[Union[int, float]], group2: List[Union[int, float]],
                            equal_var: bool = True) -> Dict[str, float]:
        a, b = _clean(group1), _clean(group2)
        if a.size < 2 or b.size < 2:
            return {"statistic": None, "p_value": None, "df": 0}
        res = sps.ttest_ind(a, b, equal_var=equal_var)
        df = (a.size + b.size - 2) if equal_var else None
        return {"statistic": float(res.statistic), "p_value": float(res.pvalue), "df": df}

    def paired_t_test(self, before: List[Union[int, float]], after: List[Union[int, float]]) -> Dict[str, float]:
        df = pd.DataFrame({"a": pd.to_numeric(pd.Series(before), errors="coerce"),
                            "b": pd.to_numeric(pd.Series(after), errors="coerce")}).dropna()
        if len(df) < 2:
            return {"statistic": None, "p_value": None, "df": 0}
        res = sps.ttest_rel(df["a"], df["b"])
        return {"statistic": float(res.statistic), "p_value": float(res.pvalue), "df": int(len(df) - 1)}

    def f_test(self, group1: List[Union[int, float]], group2: List[Union[int, float]]) -> Dict[str, float]:
        a, b = _clean(group1), _clean(group2)
        if a.size < 2 or b.size < 2:
            return {"statistic": None, "p_value": None}
        var_a, var_b = np.var(a, ddof=1), np.var(b, ddof=1)
        f_stat = var_a / var_b if var_b != 0 else float("inf")
        df1, df2 = a.size - 1, b.size - 1
        p = 2 * min(sps.f.cdf(f_stat, df1, df2), 1 - sps.f.cdf(f_stat, df1, df2))
        return {"statistic": float(f_stat), "p_value": float(p), "df1": df1, "df2": df2}

    def anova_oneway(self, *groups: List[Union[int, float]]) -> Dict[str, float]:
        """ANOVA à un facteur (scipy.stats.f_oneway)."""
        cleaned = [_clean(g) for g in groups if len(_clean(g)) > 1]
        if len(cleaned) < 2:
            return {"statistic": None, "p_value": None}
        res = sps.f_oneway(*cleaned)
        return {"statistic": float(res.statistic), "p_value": float(res.pvalue),
                "df_between": len(cleaned) - 1,
                "df_within": sum(len(g) for g in cleaned) - len(cleaned)}

    def chi2_test(self, observed: List[int], expected: Optional[List[float]] = None) -> Dict[str, float]:
        obs = np.asarray(observed, dtype=float)
        if expected is not None:
            exp = np.asarray(expected, dtype=float)
            stat, p = sps.chisquare(obs, exp)
            dof = obs.size - 1
        else:
            stat, p, dof, _ = sps.chi2_contingency(obs) if obs.ndim > 1 else (None, None, None, None)
            if stat is None:
                stat, p = sps.chisquare(obs)
                dof = obs.size - 1
        return {"statistic": float(stat), "p_value": float(p), "df": int(dof)}

    def chi2_contingency(self, table: List[List[int]]) -> Dict[str, Any]:
        """Test du chi² d'indépendance sur un tableau de contingence."""
        stat, p, dof, expected = sps.chi2_contingency(np.asarray(table))
        return {"statistic": float(stat), "p_value": float(p), "df": int(dof),
                "expected": expected.tolist()}

    def mann_whitney(self, group1: List[Union[int, float]], group2: List[Union[int, float]]) -> Dict[str, float]:
        a, b = _clean(group1), _clean(group2)
        if a.size < 1 or b.size < 1:
            return {"statistic": None, "p_value": None}
        res = sps.mannwhitneyu(a, b, alternative="two-sided")
        return {"statistic": float(res.statistic), "p_value": float(res.pvalue)}

    def kruskal_wallis(self, *groups: List[Union[int, float]]) -> Dict[str, float]:
        cleaned = [_clean(g) for g in groups if len(_clean(g)) > 0]
        if len(cleaned) < 2:
            return {"statistic": None, "p_value": None}
        res = sps.kruskal(*cleaned)
        return {"statistic": float(res.statistic), "p_value": float(res.pvalue)}

    def shapiro_wilk(self, data: List[Union[int, float]]) -> Dict[str, float]:
        a = _clean(data)
        if a.size < 3:
            return {"statistic": None, "p_value": None}
        stat, p = sps.shapiro(a)
        return {"statistic": float(stat), "p_value": float(p)}

    def ks_test(self, data: List[Union[int, float]], dist: str = "norm") -> Dict[str, float]:
        a = _clean(data)
        if a.size < 2:
            return {"statistic": None, "p_value": None}
        params = (float(np.mean(a)), float(np.std(a, ddof=1))) if dist in ("norm", "normal") else ()
        dist_name = "norm" if dist in ("norm", "normal") else dist
        stat, p = sps.kstest(a, dist_name, args=params)
        return {"statistic": float(stat), "p_value": float(p)}

    def anderson_darling(self, data: List[Union[int, float]]) -> Dict[str, Any]:
        a = _clean(data)
        if a.size < 3:
            return {"statistic": None, "significance_levels": [], "critical_values": []}
        res = sps.anderson(a, dist="norm")
        return {
            "statistic": float(res.statistic),
            "significance_levels": [float(x) for x in res.significance_level],
            "critical_values": [float(x) for x in res.critical_values],
        }

    # ==================================================================
    # AGRÉGATION / PIVOT / TABLEAUX CROISÉS (pandas natif)
    # ==================================================================
    def aggregate(self, group_col: str, agg_dict: Dict[str, str]) -> DataTable:
        return self.df.groupby_agg([group_col], agg_dict)

    def pivot_table(self, index: str, columns: str, values: str, aggfunc: str = "mean") -> DataTable:
        pivot = pd.pivot_table(self.df.frame, index=index, columns=columns,
                                values=values, aggfunc=aggfunc).reset_index()
        pivot.columns = [str(c) for c in pivot.columns]
        return DataTable(df=pivot)

    def cross_tab(self, col1: str, col2: str) -> Dict[str, Dict[str, int]]:
        return pd.crosstab(self.df.frame[col1], self.df.frame[col2]).to_dict()

    # ==================================================================
    # RÉ-ÉCHANTILLONNAGE
    # ==================================================================
    def bootstrap(self, data: List[Union[int, float]], n_samples: int = 1000,
                   statistic: Callable = np.mean, ci: float = 0.95) -> Dict[str, float]:
        a = _clean(data)
        if a.size == 0:
            return {"estimate": None, "ci_lower": None, "ci_upper": None}
        rng = np.random.default_rng()
        boot_stats = np.array([
            statistic(rng.choice(a, size=a.size, replace=True)) for _ in range(n_samples)
        ])
        alpha = (1 - ci) / 2
        return {
            "estimate": float(statistic(a)),
            "ci_lower": float(np.quantile(boot_stats, alpha)),
            "ci_upper": float(np.quantile(boot_stats, 1 - alpha)),
            "std_error": float(np.std(boot_stats, ddof=1)),
        }

    def jackknife(self, data: List[Union[int, float]], statistic: Callable = None) -> Dict[str, float]:
        a = _clean(data)
        statistic = statistic or np.mean
        n = a.size
        if n < 2:
            return {"estimate": None, "std_error": None}
        leave_one_out = np.array([statistic(np.delete(a, i)) for i in range(n)])
        estimate = float(statistic(a))
        bias = (n - 1) * (float(np.mean(leave_one_out)) - estimate)
        se = float(np.sqrt((n - 1) / n * np.sum((leave_one_out - np.mean(leave_one_out)) ** 2)))
        return {"estimate": estimate - bias, "std_error": se}

    # ==================================================================
    # SÉRIES TEMPORELLES — via pandas / statsmodels
    # ==================================================================
    def lag(self, data: List[Any], k: int = 1) -> List[Any]:
        return pd.Series(data).shift(k).where(lambda s: s.notna(), None).tolist()

    def diff(self, data: List[Union[int, float]], k: int = 1) -> List[Optional[float]]:
        s = pd.to_numeric(pd.Series(data), errors="coerce").diff(k)
        return s.where(pd.notnull(s), None).tolist()

    def pct_change(self, data: List[Union[int, float]], k: int = 1) -> List[Optional[float]]:
        s = pd.to_numeric(pd.Series(data), errors="coerce").pct_change(k)
        return s.where(pd.notnull(s), None).tolist()

    def moving_average(self, data: List[Union[int, float]], window: int = 3) -> List[Optional[float]]:
        s = pd.to_numeric(pd.Series(data), errors="coerce").rolling(window=window).mean()
        return s.where(pd.notnull(s), None).tolist()

    def ewma(self, data: List[Union[int, float]], alpha: float = 0.3) -> List[Optional[float]]:
        s = pd.to_numeric(pd.Series(data), errors="coerce").ewm(alpha=alpha).mean()
        return s.where(pd.notnull(s), None).tolist()

    def autocorrelation(self, data: List[Union[int, float]], lag: int = 1) -> Optional[float]:
        s = pd.to_numeric(pd.Series(data), errors="coerce").dropna()
        if len(s) <= lag:
            return None
        return float(s.autocorr(lag=lag))

    def acf(self, data: List[Union[int, float]], nlags: int = 10) -> List[float]:
        from statsmodels.tsa.stattools import acf as sm_acf
        a = _clean(data)
        nlags = min(nlags, max(a.size - 1, 0))
        if a.size < 2:
            return []
        return [float(x) for x in sm_acf(a, nlags=nlags, fft=True)]

    def pacf(self, data: List[Union[int, float]], nlags: int = 10) -> List[float]:
        from statsmodels.tsa.stattools import pacf as sm_pacf
        a = _clean(data)
        nlags = min(nlags, max(a.size // 2 - 1, 0))
        if a.size < 4 or nlags < 1:
            return []
        return [float(x) for x in sm_pacf(a, nlags=nlags)]

    def adf_test(self, data: List[Union[int, float]]) -> Dict[str, Any]:
        """Test de racine unitaire (stationnarité) — Augmented Dickey-Fuller."""
        from statsmodels.tsa.stattools import adfuller
        a = _clean(data)
        if a.size < 4:
            return {"statistic": None, "p_value": None}
        stat, p, _, _, crit, _ = adfuller(a)
        return {"statistic": float(stat), "p_value": float(p),
                "critical_values": {k: float(v) for k, v in crit.items()}}

    def kpss_test(self, data: List[Union[int, float]]) -> Dict[str, Any]:
        from statsmodels.tsa.stattools import kpss
        a = _clean(data)
        if a.size < 4:
            return {"statistic": None, "p_value": None}
        stat, p, _, crit = kpss(a, nlags="auto")
        return {"statistic": float(stat), "p_value": float(p),
                "critical_values": {k: float(v) for k, v in crit.items()}}

    def seasonal_decompose(self, data: List[Union[int, float]], period: int, model: str = "additive") -> Dict[str, List[float]]:
        from statsmodels.tsa.seasonal import seasonal_decompose as sm_decompose
        s = pd.Series(_clean(data))
        result = sm_decompose(s, period=period, model=model, extrapolate_trend="freq")
        return {
            "trend": result.trend.where(pd.notnull(result.trend), None).tolist(),
            "seasonal": result.seasonal.tolist(),
            "resid": result.resid.where(pd.notnull(result.resid), None).tolist(),
        }

    # ==================================================================
    # RÉGRESSION LINÉAIRE — statsmodels
    # ==================================================================
    def linear_regression(self, y: List[float], x_cols: Dict[str, List[float]]) -> Dict[str, Any]:
        """Régression linéaire OLS multiple via statsmodels."""
        import statsmodels.api as sm

        data = {"y": y, **x_cols}
        frame = pd.DataFrame(data).apply(pd.to_numeric, errors="coerce").dropna()
        if len(frame) < len(x_cols) + 2:
            return {"error": "Pas assez d'observations pour la régression"}
        X = sm.add_constant(frame[list(x_cols.keys())])
        model = sm.OLS(frame["y"], X).fit()
        return {
            "coefficients": model.params.to_dict(),
            "p_values": model.pvalues.to_dict(),
            "r_squared": float(model.rsquared),
            "adj_r_squared": float(model.rsquared_adj),
            "f_statistic": float(model.fvalue),
            "f_p_value": float(model.f_pvalue),
            "n_observations": int(model.nobs),
        }

    # ==================================================================
    # DISTANCES / SIMILARITÉS — scipy.spatial.distance
    # ==================================================================
    def euclidean_distance(self, v1: List[float], v2: List[float]) -> float:
        from scipy.spatial import distance
        return float(distance.euclidean(v1, v2))

    def manhattan_distance(self, v1: List[float], v2: List[float]) -> float:
        from scipy.spatial import distance
        return float(distance.cityblock(v1, v2))

    def minkowski_distance(self, v1: List[float], v2: List[float], p: float = 3) -> float:
        from scipy.spatial import distance
        return float(distance.minkowski(v1, v2, p=p))

    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        from scipy.spatial import distance
        return float(1 - distance.cosine(v1, v2))

    def jaccard_similarity(self, set1, set2) -> float:
        s1, s2 = set(set1), set(set2)
        union = s1 | s2
        return float(len(s1 & s2) / len(union)) if union else 0.0

    # ==================================================================
    # CLASSEMENT / SCORES — numpy / scipy.stats
    # ==================================================================
    def rank(self, data: List[Union[int, float]], method: str = "average") -> List[float]:
        a = np.asarray(_clean(data))
        return [float(r) for r in sps.rankdata(a, method=method)] if a.size else []

    def percentile_rank(self, data: List[Union[int, float]], value: Union[int, float]) -> float:
        a = _clean(data)
        return float(sps.percentileofscore(a, value)) if a.size else 0.0

    def zscore(self, data: List[Union[int, float]]) -> List[Optional[float]]:
        s = pd.to_numeric(pd.Series(data), errors="coerce")
        z = (s - s.mean()) / s.std(ddof=1)
        return z.where(pd.notnull(z), None).tolist()

    def min_max_scale(self, columns: Optional[List[str]] = None,
                       feature_range: Tuple[float, float] = (0, 1)) -> "DataTable":

        new_df = self._df.copy()
        cols = columns if columns else list(new_df.select_dtypes(include=[np.number]).columns)
        cols = [c for c in cols if c in new_df.columns]
        if not cols:
            return DataTable(df=new_df)
        sub = new_df[cols].apply(pd.to_numeric, errors="coerce")
        mask = sub.notna().all(axis=1)
        if mask.any():
             min_val = sub.loc[mask].min()
             max_val = sub.loc[mask].max()

             range_val = max_val - min_val
             range_val = range_val.replace(0, 1)

             scaled = (sub.loc[mask] - min_val) / range_val
             scaled = scaled * (feature_range[1] - feature_range[0]) + feature_range[0]

             new_df.loc[mask, cols] = scaled
        return DataTable(df=new_df)


    def robust_scale(self, data: List[Union[int, float]]) -> List[Optional[float]]:
        from scipy.stats import iqr
        s = pd.to_numeric(pd.Series(data), errors="coerce")
        mask = s.notna()
        scaled = pd.Series([None] * len(s), dtype="object")

        if mask.any():
            values = s[mask]
            median = values.median()
            iqr_val = iqr(values)

            if iqr_val == 0:
                scaled.loc[mask] = values - median
            else:
                scaled.loc[mask] = (values - median) / iqr_val
        return scaled.tolist()

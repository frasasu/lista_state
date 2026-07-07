

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd


def to_numeric(val: Any) -> Any:

    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float, np.integer, np.floating)):
        return val.item() if isinstance(val, (np.integer, np.floating)) else val
    if isinstance(val, str):
        stripped = val.strip()
        if not stripped:
            return None
        converted = pd.to_numeric(pd.Series([stripped]), errors="coerce").iloc[0]
        if pd.isna(converted):
            return val
        return converted.item() if hasattr(converted, "item") else converted
    return val


def is_numeric(val: Any) -> bool:
    """Vérifie si une valeur est (ou peut être convertie en) numérique."""
    if isinstance(val, bool):
        return False
    if isinstance(val, (int, float, np.integer, np.floating)):
        return True
    if isinstance(val, str):
        converted = pd.to_numeric(pd.Series([val]), errors="coerce").iloc[0]
        return not pd.isna(converted)
    return False


def ensure_list_length(value: Any, expected_length: int) -> List:
    """S'assure qu'une valeur est une liste de la longueur attendue (broadcast façon numpy)."""
    if value is None:
        return [None] * expected_length
    if not isinstance(value, list):
        return [value] * expected_length
    n = len(value)
    if n == expected_length:
        return value
    if n == 1:
        return value * expected_length
    if n > expected_length:
        return value[:expected_length]
    return value + [None] * (expected_length - n)


def _nan_to_none(series: pd.Series) -> List[Any]:
    """Convertit une Series pandas en liste Python en remplaçant NaN/NaT par None."""
    return series.where(pd.notnull(series), None).tolist()


def _records_nan_to_none(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for row in records:
        for k, v in row.items():
            if isinstance(v, float) and pd.isna(v):
                row[k] = None
            elif v is pd.NaT:
                row[k] = None
    return records


class DataTable:

    def __init__(self, data: Union[Dict[str, List], "pd.DataFrame", None] = None,
                 df: Optional[pd.DataFrame] = None):
        if df is not None:
            self._df = df
        elif isinstance(data, pd.DataFrame):
            self._df = data.copy()
        elif data is None:
            self._df = pd.DataFrame()
        else:
            self._df = pd.DataFrame(data)
            self._validate_columns_length(data)
        if self._df.index.name is not None or not self._df.index.equals(
            pd.RangeIndex(len(self._df))
        ):
            self._df = self._df.reset_index(drop=True)

    @staticmethod
    def _validate_columns_length(data: Dict[str, List]):
        if not isinstance(data, dict) or not data:
            return
        lengths = {col: (len(v) if v is not None else 0) for col, v in data.items()}
        first = next(iter(lengths.values()))
        for col, length in lengths.items():
            if length != first:
                raise ValueError(
                    f"La colonne '{col}' a {length} éléments, mais devrait en avoir {first}"
                )

    @property
    def frame(self) -> pd.DataFrame:
        """Accès direct au DataFrame pandas sous-jacent."""
        return self._df

    @property
    def attrs(self) -> Dict[str, Any]:
        return self._df.attrs

    @property
    def _attrs(self) -> Dict[str, Any]:
        return self._df.attrs

    @property
    def columns(self) -> List[str]:
        return list(self._df.columns)

    @property
    def shape(self) -> Tuple[int, int]:
        return self._df.shape

    def __len__(self) -> int:
        return len(self._df)

    def __repr__(self) -> str:
        return f"DataTable(shape={self.shape})\n{self._df!r}"

    def __getitem__(self, key: Union[str, int, slice, List]) -> Any:
        if isinstance(key, str):
            if key not in self._df.columns:
                return []
            return _nan_to_none(self._df[key])
        if isinstance(key, (int, np.integer)):
            row = self._df.iloc[int(key)]
            return _records_nan_to_none([row.to_dict()])[0]
        if isinstance(key, slice):
            return DataTable(df=self._df.iloc[key].reset_index(drop=True))
        if isinstance(key, list):
            if key and all(isinstance(k, (bool, np.bool_)) for k in key):
                return self.filter(key)
            return DataTable(df=self._df[key].reset_index(drop=True))
        return None

    def __setitem__(self, col: str, values: Any):
        n = len(self._df)
        if not isinstance(values, list):
            values = [values] * n if n else [values]
        if n == 0:
            self._df[col] = pd.Series(values, dtype="object") if values else values
            return
        if len(values) != n:
            if len(values) == 1:
                values = values * n
            else:
                raise ValueError(
                    f"La colonne '{col}' doit avoir {n} éléments, mais en a {len(values)}"
                )
        self._df[col] = values

    def copy(self) -> "DataTable":
        return DataTable(df=self._df.copy())

    def head(self, n: int = 5) -> "DataTable":
        return DataTable(df=self._df.head(n).reset_index(drop=True))

    @classmethod
    def from_records(cls, records: List[Dict[str, Any]]) -> "DataTable":
        return cls(df=pd.DataFrame.from_records(records))

    def to_dict(self, orient: str = "list") -> Any:
        if orient == "list":
            return {c: _nan_to_none(self._df[c]) for c in self._df.columns}
        if orient == "records":
            return _records_nan_to_none(self._df.to_dict(orient="records"))
        return self._df.to_dict(orient=orient)

    def select(self, columns: List[str]) -> "DataTable":
        cols = [c for c in columns if c in self._df.columns]
        return DataTable(df=self._df[cols].reset_index(drop=True))

    def drop(self, columns: List[str]) -> "DataTable":
        cols = [c for c in columns if c in self._df.columns]
        return DataTable(df=self._df.drop(columns=cols).reset_index(drop=True))

    def rename(self, mapping: Dict[str, str]) -> "DataTable":
        return DataTable(df=self._df.rename(columns=mapping))

    def filter(self, mask: Sequence[bool]) -> "DataTable":
        mask_arr = np.asarray(mask, dtype=bool)
        return DataTable(df=self._df.loc[mask_arr].reset_index(drop=True))

    def drop_duplicates(self, subset: Optional[List[str]] = None, keep: Union[str, bool] = "first") -> "DataTable":
        return DataTable(df=self._df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True))

    def drop_na(self, columns: Optional[List[str]] = None, how: str = "any",
                thresh: Optional[int] = None) -> "DataTable":
        kwargs: Dict[str, Any] = {"subset": columns}
        if thresh is not None:
            kwargs["thresh"] = thresh
        else:
            kwargs["how"] = how
        return DataTable(df=self._df.dropna(**kwargs).reset_index(drop=True))

    def fill_na(self, value: Any = None, method: Optional[str] = None,
                columns: Optional[List[str]] = None) -> "DataTable":
        new_df = self._df.copy()
        cols = columns if columns else list(new_df.columns)
        cols = [c for c in cols if c in new_df.columns]
        if method == "ffill":
            new_df[cols] = new_df[cols].ffill()
        elif method == "bfill":
            new_df[cols] = new_df[cols].bfill()
        else:
            new_df[cols] = new_df[cols].fillna(value)
        return DataTable(df=new_df)

    def replace(self, to_replace: Any, value: Any, columns: Optional[List[str]] = None) -> "DataTable":
        new_df = self._df.copy()
        cols = columns if columns else list(new_df.columns)
        cols = [c for c in cols if c in new_df.columns]
        new_df[cols] = new_df[cols].replace(to_replace, value)
        return DataTable(df=new_df)

    def clip(self, lower: Optional[float] = None, upper: Optional[float] = None,
             columns: Optional[List[str]] = None) -> "DataTable":
        new_df = self._df.copy()
        cols = columns if columns else list(new_df.select_dtypes(include=[np.number]).columns)
        cols = [c for c in cols if c in new_df.columns]
        new_df[cols] = new_df[cols].clip(lower=lower, upper=upper)
        return DataTable(df=new_df)

    def remove_outliers_iqr(self, column: str, factor: float = 1.5) -> "DataTable":
        if column not in self._df.columns:
            return self.copy()
        series = pd.to_numeric(self._df[column], errors="coerce")
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        low, high = q1 - factor * iqr, q3 + factor * iqr
        mask = series.isna() | series.between(low, high)
        return DataTable(df=self._df.loc[mask].reset_index(drop=True))

    def standardize(self, columns: Optional[List[str]] = None) -> "DataTable":
        """Standardisation (moyenne=0, écart-type=1) via scikit-learn StandardScaler."""
        new_df = self._df.copy()
        cols = columns if columns else list(new_df.select_dtypes(include=[np.number]).columns)
        cols = [c for c in cols if c in new_df.columns]
        if not cols:
            return DataTable(df=new_df)

        sub = new_df[cols].apply(pd.to_numeric, errors="coerce")
        mean = sub.mean()
        std = sub.std(ddof=0).replace(0, 1)

        standardized = (sub - mean) / std
        mask = sub.notna().all(axis=1)

        if mask.any():
            new_df.loc[mask, cols] = standardized.loc[mask]
        return DataTable(df=new_df)

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


    def one_hot_encode(self, column: str, prefix: Optional[str] = None,
                        drop_first: bool = False) -> "DataTable":
        """Encodage one-hot via `pandas.get_dummies`."""
        if column not in self._df.columns:
            return self.copy()
        dummies = pd.get_dummies(self._df[column], prefix=prefix or column, drop_first=drop_first)
        new_df = pd.concat([self._df.drop(columns=[column]), dummies.astype(int)], axis=1)
        return DataTable(df=new_df)

    def label_encode(self, column: str, prefix: Optional[str] = None) -> "DataTable":
        """Encodage par étiquettes via scikit-learn LabelEncoder."""
        if column not in self._df.columns:
            return self.copy()

        new_df = self._df.copy()
        values = new_df[column].astype(str)

        new_df[prefix or f"{column}_encoded"] = pd.Categorical(values).codes
        return DataTable(df=new_df)


    def merge(self, right: "DataTable", left_on: str, right_on: str, how: str = "inner") -> "DataTable":
        merged = pd.merge(
            self._df, right._df, left_on=left_on, right_on=right_on, how=how,
            suffixes=("", "_right"),
        )
        return DataTable(df=merged)

    def groupby_agg(self, by: List[str], aggregations: Dict[str, str]) -> "DataTable":
        """Agrégation groupée simple via `pandas.DataFrame.groupby().agg()`."""
        grouped = self._df.groupby(by, dropna=False).agg(aggregations).reset_index()
        return DataTable(df=grouped)


SimpleDataFrame = DataTable

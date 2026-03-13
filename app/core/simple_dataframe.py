# simple_dataframe.py
import math
import copy
from typing import Dict, List, Any, Optional, Union, Callable
from collections import defaultdict

class SimpleDataFrame:
    """
    Version simplifiée d'un DataFrame sans pandas.
    Stocke les données sous forme {colonne: [valeurs]}.
    """
    
    def __init__(self, data: Dict[str, List] = None):
        """Initialise un SimpleDataFrame à partir d'un dictionnaire {colonne: [valeurs]}"""
        self._data = data or {}
        self._attrs = {}
        # Vérifier que toutes les colonnes ont la même longueur
        self._validate_columns_length()
    
    def _validate_columns_length(self):
        """Valide que toutes les colonnes ont la même longueur"""
        if not self._data:
            return
        
        lengths = {}
        for col, values in self._data.items():
            lengths[col] = len(values) if values is not None else 0
        
        if lengths:
            first_len = next(iter(lengths.values()))
            for col, length in lengths.items():
                if length != first_len:
                    raise ValueError(
                        f"La colonne '{col}' a {length} éléments, "
                        f"mais devrait en avoir {first_len}"
                    )
    
    def _get_first_column(self) -> List:
        """Retourne la première colonne pour déterminer la longueur"""
        for col in self._data.values():
            return col
        return []
    
    @property
    def columns(self) -> List[str]:
        """Retourne la liste des noms de colonnes"""
        return list(self._data.keys())
    
    @property
    def shape(self) -> tuple:
        """Retourne (nombre_lignes, nombre_colonnes)"""
        if not self._data:
            return (0, 0)
        return (len(self._get_first_column()), len(self._data))
    
    def __len__(self) -> int:
        """Retourne le nombre de lignes"""
        return self.shape[0]
    
    def __getitem__(self, key: Union[str, int, slice]) -> Any:
        """Accès par nom de colonne ou index"""
        if isinstance(key, str):
            # Accès par nom de colonne
            return self._data.get(key, [])
        elif isinstance(key, int):
            # Accès par index de ligne
            return {col: values[key] for col, values in self._data.items()}
        elif isinstance(key, slice):
            # Slicing
            start, stop, step = key.indices(len(self))
            result = {}
            for col, values in self._data.items():
                result[col] = values[start:stop:step]
            return SimpleDataFrame(result)
        elif isinstance(key, list):
            # Accès par liste d'indices (pour le filtrage avancé)
            if all(isinstance(k, bool) for k in key):
                # Masque booléen
                return self.filter(key)
            # Liste d'indices
            result = {}
            for col, values in self._data.items():
                result[col] = [values[i] for i in key if i < len(values)]
            return SimpleDataFrame(result)
    
    def __setitem__(self, col: str, values: Any):
        """Définit une colonne avec gestion automatique des longueurs"""
        current_len = len(self) if self._data else 0
        
        # Si values n'est pas une liste, on le convertit
        if not isinstance(values, list):
            if current_len > 0:
                values = [values] * current_len
            else:
                values = [values]
        
        # Si le DataFrame est vide, on peut créer la colonne directement
        if current_len == 0:
            self._data[col] = values
            return
        
        # Vérifier la longueur
        if len(values) != current_len:
            if len(values) == 1:
                # Étendre la valeur unique à toutes les lignes
                values = values * current_len
            else:
                raise ValueError(
                    f"La colonne '{col}' doit avoir {current_len} éléments, "
                    f"mais en a {len(values)}"
                )
        
        self._data[col] = values
    
    def copy(self) -> 'SimpleDataFrame':
        """Retourne une copie profonde"""
        return SimpleDataFrame(copy.deepcopy(self._data))
    
    def head(self, n: int = 5) -> 'SimpleDataFrame':
        """Retourne les n premières lignes"""
        if n >= len(self):
            return self.copy()
        return self[:n]
    
    def tail(self, n: int = 5) -> 'SimpleDataFrame':
        """Retourne les n dernières lignes"""
        if n >= len(self):
            return self.copy()
        return self[-n:]
    
    def rename(self, columns: Dict[str, str]) -> 'SimpleDataFrame':
        """Renomme des colonnes"""
        new_data = {}
        for old_col, values in self._data.items():
            new_col = columns.get(old_col, old_col)
            new_data[new_col] = values
        return SimpleDataFrame(new_data)
    
    def drop(self, columns: List[str]) -> 'SimpleDataFrame':
        """Supprime des colonnes"""
        new_data = {col: values for col, values in self._data.items() 
                   if col not in columns}
        return SimpleDataFrame(new_data)
    
    def select(self, columns: List[str]) -> 'SimpleDataFrame':
        """Sélectionne des colonnes"""
        new_data = {col: self._data[col] for col in columns if col in self._data}
        return SimpleDataFrame(new_data)
    
    def filter(self, mask: List[bool]) -> 'SimpleDataFrame':
        """Filtre les lignes selon un masque booléen"""
        if len(mask) != len(self):
            raise ValueError("La longueur du masque ne correspond pas")
        
        result = {}
        for col, values in self._data.items():
            result[col] = [v for i, v in enumerate(values) if mask[i]]
        return SimpleDataFrame(result)
    
    def apply(self, func: Callable, col: str = None) -> Any:
        """Applique une fonction à une colonne ou à tout le DataFrame"""
        if col:
            return [func(v) for v in self._data[col]]
        else:
            result = {}
            for c, values in self._data.items():
                result[c] = [func(v) for v in values]
            return SimpleDataFrame(result)
    
    def to_dict(self, orient: str = 'list') -> Dict:
        """Convertit en dictionnaire (format pandas-like)"""
        if orient == 'list':
            return self._data
        elif orient == 'records':
            records = []
            for i in range(len(self)):
                record = {}
                for col in self.columns:
                    record[col] = self._data[col][i] if i < len(self._data[col]) else None
                records.append(record)
            return records
        return self._data
    
    @classmethod
    def from_records(cls, records: List[Dict]) -> 'SimpleDataFrame':
        """Crée un DataFrame à partir d'une liste de dictionnaires"""
        if not records:
            return cls({})
        
        columns = records[0].keys()
        data = {col: [] for col in columns}
        
        for record in records:
            for col in columns:
                data[col].append(record.get(col))
        
        return cls(data)
    
    def groupby(self, by: Union[str, List[str]]) -> 'GroupBy':
        """Prépare un groupby"""
        return GroupBy(self, by)
    
    def sort_values(self, by: str, ascending: bool = True) -> 'SimpleDataFrame':
        """Trie par une colonne"""
        if by not in self._data:
            return self.copy()
        
        # Créer une liste d'indices triés
        values = self._data[by]
        indices = list(range(len(values)))
        indices.sort(key=lambda i: values[i], reverse=not ascending)
        
        # Réorganiser les données
        result = {}
        for col, col_values in self._data.items():
            result[col] = [col_values[i] for i in indices]
        
        return SimpleDataFrame(result)
    
    def merge(self, right: 'SimpleDataFrame', left_on: str, right_on: str, 
              how: str = 'inner') -> 'SimpleDataFrame':
        """Fusionne deux DataFrames (jointure)"""
        left_data = self._data
        right_data = right._data
        
        # Créer un dictionnaire des valeurs de jointure
        left_dict = defaultdict(list)
        for i, val in enumerate(left_data[left_on]):
            left_dict[val].append(i)
        
        right_dict = defaultdict(list)
        for i, val in enumerate(right_data[right_on]):
            right_dict[val].append(i)
        
        # Déterminer les clés communes selon le type de jointure
        if how == 'inner':
            keys = set(left_dict.keys()) & set(right_dict.keys())
        elif how == 'left':
            keys = set(left_dict.keys())
        elif how == 'right':
            keys = set(right_dict.keys())
        else:  # outer
            keys = set(left_dict.keys()) | set(right_dict.keys())
        
        # Construire le résultat
        result = {col: [] for col in left_data.keys()}
        for col in right_data.keys():
            if col != right_on or col == left_on:
                result[col] = []
        
        for key in keys:
            left_indices = left_dict.get(key, [0])
            right_indices = right_dict.get(key, [0])
            
            for l_idx in left_indices:
                for r_idx in right_indices:
                    for col in left_data.keys():
                        result[col].append(left_data[col][l_idx])
                    for col in right_data.keys():
                        if col != right_on or col == left_on:
                            result[col].append(right_data[col][r_idx])
        
        return SimpleDataFrame(result)


class GroupBy:
    """Classe pour les opérations groupby"""
    
    def __init__(self, df: SimpleDataFrame, by: Union[str, List[str]]):
        self.df = df
        self.by = [by] if isinstance(by, str) else by
    
    def _get_groups(self) -> Dict:
        """Retourne les groupes"""
        groups = defaultdict(list)
        
        for i in range(len(self.df)):
            key = tuple(self.df[col][i] for col in self.by)
            groups[key].append(i)
        
        return groups
    
    def agg(self, aggregations: Dict[str, str]) -> SimpleDataFrame:
        """Agrège les groupes"""
        groups = self._get_groups()
        
        # Préparer le résultat
        result = {col: [] for col in self.by}
        for agg_col in aggregations.keys():
            result[agg_col] = []
        
        for key, indices in groups.items():
            # Ajouter les clés
            for i, col in enumerate(self.by):
                result[col].append(key[i])
            
            # Calculer les agrégations
            for agg_col, func in aggregations.items():
                values = [self.df[agg_col][i] for i in indices]
                
                # Filtrer les valeurs None et convertir en numérique
                numeric_values = []
                for v in values:
                    if v is not None:
                        if isinstance(v, (int, float)):
                            numeric_values.append(v)
                        else:
                            num_v = to_numeric(v)
                            if isinstance(num_v, (int, float)):
                                numeric_values.append(num_v)
                
                if func == 'sum':
                    result[agg_col].append(sum(numeric_values) if numeric_values else 0)
                elif func == 'mean' or func == 'avg':
                    result[agg_col].append(sum(numeric_values) / len(numeric_values) if numeric_values else None)
                elif func == 'count':
                    result[agg_col].append(len(values))
                elif func == 'min':
                    result[agg_col].append(min(numeric_values) if numeric_values else None)
                elif func == 'max':
                    result[agg_col].append(max(numeric_values) if numeric_values else None)
                else:
                    result[agg_col].append(None)
        
        return SimpleDataFrame(result)
    
    def __getitem__(self, col: str):
        """Permet l'accès aux colonnes pour l'agrégation"""
        return GroupByCol(self, col)


class GroupByCol:
    """Colonne d'un groupby"""
    
    def __init__(self, groupby: GroupBy, col: str):
        self.groupby = groupby
        self.col = col
    
    def sum(self) -> SimpleDataFrame:
        return self.groupby.agg({self.col: 'sum'})
    
    def mean(self) -> SimpleDataFrame:
        return self.groupby.agg({self.col: 'mean'})
    
    def count(self) -> SimpleDataFrame:
        return self.groupby.agg({self.col: 'count'})
    
    def min(self) -> SimpleDataFrame:
        return self.groupby.agg({self.col: 'min'})
    
    def max(self) -> SimpleDataFrame:
        return self.groupby.agg({self.col: 'max'})


# Fonctions de conversion
def to_numeric(val: Any) -> Union[int, float, Any]:
    """Convertit une valeur en numérique si possible"""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return None
        try:
            if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
                return int(val)
        except:
            pass
        try:
            if '.' in val or 'e' in val.lower():
                return float(val)
        except:
            pass
    return val


def is_numeric(val: Any) -> bool:
    """Vérifie si une valeur est numérique"""
    if isinstance(val, (int, float)):
        return True
    if isinstance(val, str):
        try:
            float(val)
            return True
        except:
            pass
    return False


def ensure_list_length(value: Any, expected_length: int) -> List:
    """S'assure qu'une valeur est une liste de la longueur attendue"""
    if value is None:
        return [None] * expected_length
    if not isinstance(value, list):
        return [value] * expected_length
    if len(value) == expected_length:
        return value
    if len(value) == 1:
        return value * expected_length
    # Si la liste est trop longue, on la tronque
    if len(value) > expected_length:
        return value[:expected_length]
    # Si la liste est trop courte, on la complète avec des None
    return value + [None] * (expected_length - len(value))
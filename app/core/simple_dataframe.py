# simple_dataframe.py
import math
import copy
from typing import Dict, List, Any, Optional, Union, Callable, Set
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

    def __getitem__(self, key: Union[str, int, slice, List]) -> Any:
        """Accès par nom de colonne ou index"""
        if isinstance(key, str):
            return self._data.get(key, [])
        elif isinstance(key, int):
            return {col: values[key] for col, values in self._data.items()}
        elif isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            result = {}
            for col, values in self._data.items():
                result[col] = values[start:stop:step]
            return SimpleDataFrame(result)
        elif isinstance(key, list):
            if all(isinstance(k, bool) for k in key):
                return self.filter(key)
            result = {}
            for col, values in self._data.items():
                result[col] = [values[i] for i in key if i < len(values)]
            return SimpleDataFrame(result)
        return None

    def __setitem__(self, col: str, values: Any):
        """Définit une colonne avec gestion automatique des longueurs"""
        current_len = len(self) if self._data else 0

        if not isinstance(values, list):
            if current_len > 0:
                values = [values] * current_len
            else:
                values = [values]

        if current_len == 0:
            self._data[col] = values
            return

        if len(values) != current_len:
            if len(values) == 1:
                values = values * current_len
            else:
                raise ValueError(
                    f"La colonne '{col}' doit avoir {current_len} éléments, "
                    f"mais en a {len(values)}"
                )

        self._data[col] = values

    # ========== FONCTIONS DE NETTOYAGE DES DONNÉES ==========

    def drop_na(self, columns: Optional[List[str]] = None, how: str = 'any', thresh: Optional[int] = None) -> 'SimpleDataFrame':
        """
        Supprime les lignes contenant des valeurs manquantes.

        Args:
            columns: Liste des colonnes à vérifier (toutes si None)
            how: 'any' (supprimer si une valeur manque) ou 'all' (supprimer si toutes les valeurs manquent)
            thresh: Seuil minimum de valeurs non-nulles pour garder la ligne

        Returns:
            SimpleDataFrame sans les lignes avec valeurs manquantes
        """
        cols_to_check = columns if columns else self.columns
        mask = []

        for i in range(len(self)):
            values = [self._data[col][i] for col in cols_to_check if col in self._data]

            if thresh is not None:
                # Garder si nombre de valeurs non-nulles >= thresh
                non_null_count = sum(1 for v in values if v is not None)
                mask.append(non_null_count >= thresh)
            elif how == 'all':
                # Garder si PAS toutes les valeurs sont nulles
                mask.append(not all(v is None for v in values))
            else:  # how == 'any'
                # Garder si PAS de valeurs nulles
                mask.append(all(v is not None for v in values))

        return self.filter(mask)

    def fill_na(self,value: Any = None, method: Optional[str] = None, columns: Optional[List[str]] = None) -> 'SimpleDataFrame':
        """
        Remplit les valeurs manquantes.

        Args:
            value: Valeur à utiliser pour remplir
            method: 'ffill' (forward fill) ou 'bfill' (backward fill)
            columns: Liste des colonnes à traiter (toutes si None)

        Returns:
            SimpleDataFrame avec valeurs manquantes remplies
        """
        result = self.copy()
        cols_to_fill = columns if columns else self.columns

        for col in cols_to_fill:
            if col not in result._data:
                continue

            values = result._data[col].copy()

            if method == 'ffill':
                # Remplir avec la dernière valeur non-nulle
                last_valid = None
                for i in range(len(values)):
                    if values[i] is not None:
                        last_valid = values[i]
                    elif last_valid is not None:
                        values[i] = last_valid

            elif method == 'bfill':
                # Remplir avec la prochaine valeur non-nulle
                next_valid = None
                for i in range(len(values) - 1, -1, -1):
                    if values[i] is not None:
                        next_valid = values[i]
                    elif next_valid is not None:
                        values[i] = next_valid

            else:
                # Remplir avec une valeur constante
                for i in range(len(values)):
                    if values[i] is None:
                        values[i] = value

            result._data[col] = values

        return result

    def drop_duplicates(self, subset: Optional[List[str]] = None, keep: str = 'first') -> 'SimpleDataFrame':
        """
        Supprime les lignes dupliquées.

        Args:
            subset: Colonnes à considérer pour les doublons (toutes si None)
            keep: 'first' (garder première occurrence), 'last' (garder dernière), False (supprimer tous les doublons)

        Returns:
            SimpleDataFrame sans doublons
        """
        if len(self) == 0:
            return self.copy()

        cols_to_check = subset if subset else self.columns
        seen = {}  # key -> dernier index vu
        indices_to_keep = []

        for i in range(len(self)):
            # Créer une clé basée sur les valeurs des colonnes
            key_parts = []
            for col in cols_to_check:
                val = self._data[col][i]
                # Convertir pour que None soit comparable
                key_parts.append(str(val) if val is not None else '___NONE___')
            key = tuple(key_parts)

            if keep == 'first':
                # Garder la première occurrence
                if key not in seen:
                    seen[key] = i
                    indices_to_keep.append(i)

            elif keep == 'last':
                # Pour last, on met à jour l'index à chaque fois
                seen[key] = i

            elif keep is False:
                # Compter les occurrences
                if key in seen:
                    seen[key] += 1
                else:
                    seen[key] = 1

        # Traitement pour keep='last'
        if keep == 'last':
            indices_to_keep = list(seen.values())

        # Traitement pour keep=False (garder les uniques)
        elif keep is False:
            indices_to_keep = [i for i in range(len(self))
                              if seen[tuple(str(self._data[col][i]) if self._data[col][i] is not None else '___NONE___'
                                           for col in cols_to_check)] == 1]

        # Filtrer pour garder les indices sélectionnés
        result = {}
        for col, values in self._data.items():
            result[col] = [values[i] for i in indices_to_keep]

        return SimpleDataFrame(result)


    def replace(self, to_replace: Any, value: Any, columns: Optional[List[str]] = None) -> 'SimpleDataFrame':
        """
        Remplace une valeur par une autre.

        Args:
            to_replace: Valeur à remplacer
            value: Nouvelle valeur
            columns: Colonnes à traiter (toutes si None)

        Returns:
            SimpleDataFrame avec valeurs remplacées
        """
        result = self.copy()
        cols_to_replace = columns if columns else self.columns

        for col in cols_to_replace:
            if col not in result._data:
                continue

            result._data[col] = [
                value if v == to_replace else v
                for v in result._data[col]
            ]

        return result

    def clip(self, lower: Optional[Union[int, float]] = None, upper: Optional[Union[int, float]] = None,
             columns: Optional[List[str]] = None) -> 'SimpleDataFrame':
        """
        Limite les valeurs à un intervalle [lower, upper].

        Args:
            lower: Borne inférieure
            upper: Borne supérieure
            columns: Colonnes à traiter (toutes si None)

        Returns:
            SimpleDataFrame avec valeurs limitées
        """
        result = self.copy()
        cols_to_clip = columns if columns else self.columns

        for col in cols_to_clip:
            if col not in result._data:
                continue

            new_values = []
            for v in result._data[col]:
                if v is None:
                    new_values.append(None)
                elif isinstance(v, (int, float)):
                    if lower is not None and v < lower:
                        new_values.append(lower)
                    elif upper is not None and v > upper:
                        new_values.append(upper)
                    else:
                        new_values.append(v)
                else:
                    new_values.append(v)

            result._data[col] = new_values

        return result

    def detect_outliers_iqr(self, column: str, factor: float = 1.5) -> List[bool]:
        """
        Détecte les outliers dans une colonne avec la méthode IQR.

        Args:
            column: Nom de la colonne
            factor: Multiplicateur pour l'intervalle (1.5 par défaut)

        Returns:
            Masque booléen (True pour les outliers)
        """
        if column not in self._data:
            raise ValueError(f"Colonne '{column}' introuvable")

        # Récupérer les valeurs de la colonne
        original_values = self._data[column]

        # Extraire les valeurs numériques pour le calcul des quartiles
        numeric_values = []
        for v in original_values:
            num_v = to_numeric(v)
            if isinstance(num_v, (int, float)):
                numeric_values.append(num_v)

        # Si pas de valeurs numériques, retourner un masque de False
        if not numeric_values:
            return [False] * len(self)

        # Calculer Q1, Q3 et IQR
        sorted_vals = sorted(numeric_values)
        n = len(sorted_vals)

        # Indices pour les quartiles
        q1_idx = n // 4
        q3_idx = 3 * n // 4

        q1 = sorted_vals[q1_idx]
        q3 = sorted_vals[q3_idx]

        iqr = q3 - q1
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr

        # Détecter les outliers
        mask = []
        for v in original_values:
            num_v = to_numeric(v)

            # Vérification explicite du type avant comparaison
            if isinstance(num_v, (int, float)):
                # Comparaison sécurisée entre nombres
                is_outlier = num_v < lower_bound or num_v > upper_bound
                mask.append(is_outlier)
            else:
                # Valeur non-numérique ou None → pas un outlier
                mask.append(False)

        return mask

    def remove_outliers_iqr(self, column: str, factor: float = 1.5) -> 'SimpleDataFrame':
        """
        Supprime les outliers d'une colonne avec la méthode IQR.

        Args:
            column: Nom de la colonne
            factor: Multiplicateur pour l'intervalle

        Returns:
            SimpleDataFrame sans les outliers
        """
        mask = self.detect_outliers_iqr(column, factor)
        # Inverser le masque pour garder les non-outliers
        keep_mask = [not m for m in mask]
        return self.filter(keep_mask)

    def standardize(self, columns: Optional[List[str]] = None) -> 'SimpleDataFrame':
        """
        Standardise les colonnes (moyenne=0, écart-type=1).

        Args:
            columns: Colonnes à standardiser (toutes si None)

        Returns:
            SimpleDataFrame avec colonnes standardisées
        """
        result = self.copy()
        cols_to_std = columns if columns else self.columns

        for col in cols_to_std:
            if col not in result._data:
                continue

            values = result._data[col]
            numeric_values = [to_numeric(v) for v in values if v is not None]
            numeric_values = [v for v in numeric_values if isinstance(v, (int, float))]

            if not numeric_values:
                continue

            mean_val = sum(numeric_values) / len(numeric_values)
            std_val = math.sqrt(sum((x - mean_val) ** 2 for x in numeric_values) / len(numeric_values))

            if std_val == 0:
                continue

            new_values = []
            for v in values:
                if v is None:
                    new_values.append(None)
                else:
                    num_v = to_numeric(v)
                    if isinstance(num_v, (int, float)):
                        new_values.append((num_v - mean_val) / std_val)
                    else:
                        new_values.append(v)

            result._data[col] = new_values

        return result

    def min_max_scale(self, columns: Optional[List[str]] = None, feature_range: tuple = (0, 1)) -> 'SimpleDataFrame':
        """
        Normalise les colonnes dans un intervalle [min, max].

        Args:
            columns: Colonnes à normaliser (toutes si None)
            feature_range: Intervalle cible (min, max)

        Returns:
            SimpleDataFrame avec colonnes normalisées
        """
        result = self.copy()
        cols_to_scale = columns if columns else self.columns
        a, b = feature_range

        for col in cols_to_scale:
            if col not in result._data:
                continue

            values = result._data[col]
            numeric_values = [to_numeric(v) for v in values if v is not None]
            numeric_values = [v for v in numeric_values if isinstance(v, (int, float))]

            if not numeric_values:
                continue

            min_val = min(numeric_values)
            max_val = max(numeric_values)

            if min_val == max_val:
                continue

            new_values = []
            for v in values:
                if v is None:
                    new_values.append(None)
                else:
                    num_v = to_numeric(v)
                    if isinstance(num_v, (int, float)):
                        # Formule: X_scaled = a + (X - min) * (b - a) / (max - min)
                        scaled = a + (num_v - min_val) * (b - a) / (max_val - min_val)
                        new_values.append(scaled)
                    else:
                        new_values.append(v)

            result._data[col] = new_values

        return result

    def one_hot_encode(self, column: str, prefix: Optional[str] = None, drop_first: bool = False) -> 'SimpleDataFrame':
        """
        Applique un one-hot encoding à une colonne catégorielle.

        Args:
            column: Colonne à encoder
            prefix: Préfixe pour les nouvelles colonnes
            drop_first: Supprimer la première catégorie pour éviter la multicolinéarité

        Returns:
            SimpleDataFrame avec colonnes encodées
        """
        if column not in self._data:
            raise ValueError(f"Colonne '{column}' introuvable")

        result = self.copy()
        prefix = prefix or column

        # Récupérer les valeurs uniques
        unique_values = set()
        for v in result._data[column]:
            if v is not None:
                unique_values.add(str(v))

        # Trier pour avoir un ordre cohérent
        sorted_values = sorted(unique_values)

        if drop_first and sorted_values:
            sorted_values = sorted_values[1:]

        # Créer les colonnes one-hot
        for val in sorted_values:
            col_name = f"{prefix}_{val}"
            new_col = []
            for v in result._data[column]:
                if v is None:
                    new_col.append(None)
                else:
                    new_col.append(1 if str(v) == val else 0)
            result[col_name] = new_col

        # Optionnel: supprimer la colonne originale
        # result = result.drop([column])

        return result

    def label_encode(self, column: str, prefix: Optional[str] = None) -> 'SimpleDataFrame':
        """
        Applique un label encoding à une colonne catégorielle.

        Args:
            column: Colonne à encoder
            prefix: Préfixe pour la nouvelle colonne

        Returns:
            SimpleDataFrame avec colonne encodée
        """
        if column not in self._data:
            raise ValueError(f"Colonne '{column}' introuvable")

        result = self.copy()
        prefix = prefix or f"{column}_encoded"

        # Créer un mapping valeur -> entier
        unique_values = {}
        next_code = 0

        for v in result._data[column]:
            if v is not None and v not in unique_values:
                unique_values[v] = next_code
                next_code += 1

        # Créer la colonne encodée
        encoded_col = []
        for v in result._data[column]:
            if v is None:
                encoded_col.append(None)
            else:
                encoded_col.append(unique_values[v])

        result[prefix] = encoded_col

        return result

    def info(self) -> Dict[str, Any]:
        """Retourne des informations sur le DataFrame"""
        info = {
            'shape': self.shape,
            'columns': self.columns,
            'dtypes': {},
            'null_counts': {},
            'memory_usage': 0
        }

        for col in self.columns:
            values = self._data[col]
            null_count = sum(1 for v in values if v is None)

            # Déterminer le type dominant
            types = {}
            for v in values:
                if v is not None:
                    t = type(v).__name__
                    types[t] = types.get(t, 0) + 1

            dtype = max(types, key=types.get) if types else 'unknown'

            info['dtypes'][col] = dtype
            info['null_counts'][col] = null_count

            # Estimation mémoire (approximative)
            for v in values:
                if isinstance(v, (int, float)):
                    info['memory_usage'] += 8
                elif isinstance(v, str):
                    info['memory_usage'] += len(v)
                else:
                    info['memory_usage'] += 4

        return info

    def describe(self, columns: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
        """
        Retourne des statistiques descriptives.

        Args:
            columns: Colonnes à décrire (toutes si None)

        Returns:
            Dictionnaire de statistiques par colonne
        """
        cols_to_desc = columns if columns else self.columns
        result = {}

        for col in cols_to_desc:
            if col not in self._data:
                continue

            values = [to_numeric(v) for v in self._data[col] if v is not None]
            numeric_values = [v for v in values if isinstance(v, (int, float))]

            if not numeric_values:
                continue

            sorted_vals = sorted(numeric_values)
            n = len(sorted_vals)

            stats = {
                'count': n,
                'mean': sum(numeric_values) / n,
                'std': math.sqrt(sum((x - sum(numeric_values)/n) ** 2 for x in numeric_values) / n),
                'min': sorted_vals[0],
                '25%': sorted_vals[n // 4],
                '50%': sorted_vals[n // 2],
                '75%': sorted_vals[3 * n // 4],
                'max': sorted_vals[-1]
            }

            result[col] = stats

        return result

    # ========== MÉTHODES EXISTANTES ==========

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

        values = self._data[by]
        indices = list(range(len(values)))
        indices.sort(key=lambda i: values[i], reverse=not ascending)

        result = {}
        for col, col_values in self._data.items():
            result[col] = [col_values[i] for i in indices]

        return SimpleDataFrame(result)

    def merge(self, right: 'SimpleDataFrame', left_on: str, right_on: str,
              how: str = 'inner') -> 'SimpleDataFrame':
        """
        Fusionne deux DataFrames (jointure).

        Args:
            right: DataFrame à joindre
            left_on: Colonne de jointure dans le DataFrame de gauche (self)
            right_on: Colonne de jointure dans le DataFrame de droite
            how: Type de jointure: 'inner', 'left', 'right', 'outer'

        Returns:
            SimpleDataFrame résultant de la jointure
        """
        # Vérifier que les colonnes de jointure existent
        if left_on not in self._data:
            raise ValueError(f"Colonne de jointure gauche '{left_on}' introuvable")
        if right_on not in right._data:
            raise ValueError(f"Colonne de jointure droite '{right_on}' introuvable")

        left_data = self._data
        right_data = right._data

        # Créer un dictionnaire des indices pour chaque clé dans le DataFrame gauche
        left_dict = defaultdict(list)
        for i, val in enumerate(left_data[left_on]):
            left_dict[val].append(i)

        # Créer un dictionnaire des indices pour chaque clé dans le DataFrame droit
        right_dict = defaultdict(list)
        for i, val in enumerate(right_data[right_on]):
            right_dict[val].append(i)

        # Déterminer les clés à traiter selon le type de jointure
        if how == 'inner':
            keys = set(left_dict.keys()) & set(right_dict.keys())
        elif how == 'left':
            keys = set(left_dict.keys())
        elif how == 'right':
            keys = set(right_dict.keys())
        elif how == 'outer':
            keys = set(left_dict.keys()) | set(right_dict.keys())
        else:
            raise ValueError(f"Type de jointure inconnu: {how}. Utilisez 'inner', 'left', 'right' ou 'outer'")

        # Préparer les colonnes du résultat
        result = {}

        # Ajouter toutes les colonnes de gauche (sauf left_on qui sera ajoutée plus tard)
        for col in left_data.keys():
            if col != left_on:
                result[col] = []

        # Ajouter toutes les colonnes de droite (sauf right_on)
        for col in right_data.keys():
            if col != right_on:
                # Éviter les doublons de noms de colonnes
                if col in result:
                    new_col = f"{col}_right"
                    result[new_col] = []
                else:
                    result[col] = []

        # Ajouter la colonne de jointure (une seule fois)
        result[left_on] = []

        # Pour chaque clé, faire le produit cartésien des indices correspondants
        for key in keys:
            left_indices = left_dict.get(key, [])
            right_indices = right_dict.get(key, [])

            # Si une des listes est vide (pour outer join)
            if not left_indices:
                left_indices = [None]
            if not right_indices:
                right_indices = [None]

            for l_idx in left_indices:
                for r_idx in right_indices:
                    # Ajouter la valeur de la clé de jointure
                    if l_idx is not None:
                        result[left_on].append(left_data[left_on][l_idx])
                    else:
                        result[left_on].append(right_data[right_on][r_idx])

                    # Ajouter les valeurs des colonnes de gauche
                    for col in left_data.keys():
                        if col != left_on:
                            if l_idx is not None:
                                result[col].append(left_data[col][l_idx])
                            else:
                                result[col].append(None)

                    # Ajouter les valeurs des colonnes de droite
                    for col in right_data.keys():
                        if col != right_on:
                            # Gérer le renommage si nécessaire
                            dest_col = col
                            if col in left_data and col != left_on:
                                dest_col = f"{col}_right"

                            if r_idx is not None:
                                result[dest_col].append(right_data[col][r_idx])
                            else:
                                result[dest_col].append(None)

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

        result = {col: [] for col in self.by}
        for agg_col in aggregations.keys():
            result[agg_col] = []

        for key, indices in groups.items():
            for i, col in enumerate(self.by):
                result[col].append(key[i])

            for agg_col, func in aggregations.items():
                values = [self.df[agg_col][i] for i in indices]

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


# ========== FONCTIONS UTILITAIRES ==========

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
    if len(value) > expected_length:
        return value[:expected_length]
    return value + [None] * (expected_length - len(value))


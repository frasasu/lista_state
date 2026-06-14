import matplotlib.pyplot as plt
import numpy as np
from scipy import stats as scipy_stats
from scipy.stats import gaussian_kde, norm, expon, uniform
import warnings
warnings.filterwarnings('ignore')
from stat_descriptive import stat_fonctions


class stat_visualisations(stat_fonctions):
    """
    Classe de visualisation qui herite de stat_fonctions.
    Toutes les méthodes statistiques (moyen_arth, ecart_type, correlation_pearson,
    indice_gini, courbe_lorenz, etc.) sont automatiquement disponibles.
    """

    def __init__(self, data):
        """Constructeur - appelle le constructeur parent"""
        super().__init__(data)
        print(f"Instance stat_visualisations créée avec {len(self.data)} données")

    # === UTILITAIRE INTERNE ===
    @staticmethod
    def _construire_noms(autres_noms, n_toutes):
        """
        Construit la liste de noms cohérente avec le nombre de séries total.
        Si l'appelant passe déjà autant de noms que de séries, on les utilise tels quels.
        Sinon on préfixe 'Distribution 1' pour self.data et on tronque/complète.
        """
        if autres_noms is None:
            return [f'Dist{i+1}' for i in range(n_toutes)]
        autres_noms = list(autres_noms)
        if len(autres_noms) == n_toutes:
            # L'utilisateur a fourni un nom pour chaque série (y compris self.data)
            return autres_noms
        else:
            # L'utilisateur a fourni un nom par série supplémentaire seulement
            noms = ['Distribution 1'] + autres_noms
            # Ajuster si toujours décalé
            if len(noms) < n_toutes:
                noms += [f'Dist{i+1}' for i in range(len(noms), n_toutes)]
            return noms[:n_toutes]

        # GRAPHIQUES DE BASE 

    def graph_histogramme(self, bins='auto', figsize=(10, 6), title=None):
        """Graphique 1: Histogramme"""
        plt.figure(figsize=figsize)
        plt.hist(self.data, bins=bins, density=True, alpha=0.7, edgecolor='black', color='steelblue')
        plt.xlabel('Valeurs', fontsize=12)
        plt.ylabel('Densité', fontsize=12)
        title = title or f'Histogramme (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_boxplot(self, figsize=(8, 6), title=None):
        """Graphique 2: Boxplot (boîte à moustaches)"""
        plt.figure(figsize=figsize)
        bp = plt.boxplot(self.data, vert=True, patch_artist=True,
                         boxprops=dict(facecolor='steelblue', alpha=0.7),
                         medianprops=dict(color='red', linewidth=2),
                         whiskerprops=dict(color='black', linewidth=1),
                         capprops=dict(color='black', linewidth=1))
        plt.ylabel('Valeurs', fontsize=12)
        title = title or f'Boxplot (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_violin(self, figsize=(8, 6), title=None):
        """Graphique 3: Violin plot"""
        plt.figure(figsize=figsize)
        parts = plt.violinplot(self.data, vert=True, showmeans=True, showmedians=True)
        for pc in parts['bodies']:
            pc.set_facecolor('steelblue')
            pc.set_alpha(0.7)
            pc.set_edgecolor('black')
        parts['cmeans'].set_color('red')
        parts['cmeans'].set_linewidth(2)
        parts['cmedians'].set_color('darkgreen')
        parts['cmedians'].set_linewidth(2)
        plt.ylabel('Valeurs', fontsize=12)
        title = title or f'Violin Plot (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_densite_kde(self, bandwidth='scott', figsize=(10, 6), title=None):
        """Graphique 4: Densité par noyau (KDE)"""
        plt.figure(figsize=figsize)
        plt.hist(self.data, bins=30, density=True, alpha=0.3,
                 edgecolor='black', color='lightblue', label='Histogramme')
        kde = gaussian_kde(self.data, bw_method=bandwidth)
        x_range = np.linspace(min(self.data), max(self.data), 200)
        plt.plot(x_range, kde(x_range), 'r-', linewidth=2.5, label='Densité KDE')
        plt.xlabel('Valeurs', fontsize=12)
        plt.ylabel('Densité', fontsize=12)
        title = title or f'Estimation de Densité par Noyau (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_ecdf(self, figsize=(10, 6), title=None):
        """Graphique 5: Fonction de répartition empirique (ECDF)"""
        plt.figure(figsize=figsize)
        x_sorted = np.sort(self.data)
        y_ecdf = np.arange(1, len(self.data) + 1) / len(self.data)
        plt.step(x_sorted, y_ecdf, where='post', linewidth=2.5,
                 color='steelblue', label='ECDF')
        plt.xlabel('Valeurs', fontsize=12)
        plt.ylabel('F(x) = P(X ≤ x)', fontsize=12)
        plt.ylim(0, 1.05)
        title = title or f'Fonction de Répartition Empirique (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_qqplot(self, dist='norm', figsize=(8, 8), title=None):
        """Graphique 6: QQ-plot pour vérifier la normalité"""
        plt.figure(figsize=figsize)
        scipy_stats.probplot(self.data, dist=dist, plot=plt)
        title = title or f'QQ-plot (Test de Normalité)'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_pp_plot(self, distribution='norm', figsize=(8, 8), title=None):
        """Graphique 7: PP-plot (Probability-Probability plot)"""
        plt.figure(figsize=figsize)
        x_sorted = np.sort(self.data)
        n = len(x_sorted)
        p_emp = (np.arange(1, n+1) - 0.5) / n
        if distribution == 'norm':
            p_theo = norm.cdf(x_sorted, loc=self.moyen_arth(), scale=self.ecart_type())
            nom_dist = 'Normale'
        elif distribution == 'exp':
            p_theo = expon.cdf(x_sorted, scale=self.moyen_arth())
            nom_dist = 'Exponentielle'
        else:
            p_theo = norm.cdf(x_sorted, loc=self.moyen_arth(), scale=self.ecart_type())
            nom_dist = 'Normale'
        plt.scatter(p_theo, p_emp, alpha=0.6, s=30, c='steelblue')
        plt.plot([0, 1], [0, 1], 'r--', linewidth=2, label='y = x')
        plt.xlabel(f'Probabilités théoriques ({nom_dist})', fontsize=12)
        plt.ylabel('Probabilités empiriques', fontsize=12)
        title = title or f'PP-plot (Distribution {nom_dist})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_stem_plot(self, figsize=(12, 5), title=None):
        """Graphique 8: Diagramme en bâtons (stem plot)"""
        plt.figure(figsize=figsize)
        plt.stem(range(len(self.data)), self.data, linefmt='b-', markerfmt='bo', basefmt='r-')
        plt.xlabel('Index', fontsize=12)
        plt.ylabel('Valeurs', fontsize=12)
        title = title or f'Diagramme en Bâtons (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_frequency_polygon(self, bins=20, figsize=(10, 6), title=None):
        """Graphique 9: Polygone des fréquences"""
        plt.figure(figsize=figsize)
        counts, bins_edges = np.histogram(self.data, bins=bins)
        bin_centers = (bins_edges[:-1] + bins_edges[1:]) / 2
        plt.plot(bin_centers, counts, 'o-', linewidth=2, markersize=6, color='steelblue')
        plt.fill_between(bin_centers, counts, alpha=0.2, color='steelblue')
        plt.xlabel('Valeurs', fontsize=12)
        plt.ylabel('Fréquence', fontsize=12)
        title = title or f'Polygone des Fréquences (bins={bins})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_cumulative_histogram(self, bins=30, figsize=(10, 6), title=None):
        """Graphique 10: Histogramme cumulatif"""
        plt.figure(figsize=figsize)
        plt.hist(self.data, bins=bins, cumulative=True, density=True, alpha=0.7,
                 edgecolor='black', color='steelblue', label='Cumulatif')
        plt.xlabel('Valeurs', fontsize=12)
        plt.ylabel('Fréquence cumulée', fontsize=12)
        title = title or f'Histogramme Cumulatif (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    #       GRAPHIQUES DE DISPERSION 

    def graph_scatter(self, y, figsize=(10, 6), title=None):
        """Graphique 11: Nuage de points avec droite de régression"""
        n = min(len(self.data), len(y))
        x_plot = self.data[:n]
        y_plot = y[:n]
        plt.figure(figsize=figsize)
        plt.scatter(x_plot, y_plot, alpha=0.6, s=50, c='steelblue', label='Données')
        z = np.polyfit(x_plot, y_plot, 1)
        p = np.poly1d(z)
        x_range = np.linspace(min(x_plot), max(x_plot), 100)
        plt.plot(x_range, p(x_range), 'r-', linewidth=2.5,
                 label=f'Régression: y = {z[0]:.2f}x + {z[1]:.2f}')
        r_pearson = self.correlation_pearson(y_plot)
        plt.text(0.05, 0.95, f'Pearson r = {r_pearson:.4f}\nR² = {r_pearson**2:.4f}',
                 transform=plt.gca().transAxes, fontsize=11,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        plt.xlabel('Variable X', fontsize=12)
        plt.ylabel('Variable Y', fontsize=12)
        title = title or 'Nuage de points avec droite de régression'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_swarm_plot(self, figsize=(8, 6), title=None):
        """Graphique 12: Swarm plot (points individuels)"""
        plt.figure(figsize=figsize)
        y = np.ones_like(self.data) + np.random.normal(0, 0.02, len(self.data))
        plt.scatter(self.data, y, alpha=0.5, s=20, c='steelblue')
        plt.xlabel('Valeurs', fontsize=12)
        plt.yticks([1], ['Données'])
        plt.ylim(0.9, 1.1)
        title = title or f'Swarm Plot (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        plt.show()

    def graph_bean_plot(self, figsize=(8, 6), title=None):
        """Graphique 13: Bean plot (densité miroir)"""
        plt.figure(figsize=figsize)
        kde = gaussian_kde(self.data)
        x_range = np.linspace(min(self.data), max(self.data), 200)
        y_kde = kde(x_range)
        plt.fill_betweenx(x_range, -y_kde/np.max(y_kde), 0, alpha=0.5, color='steelblue')
        plt.fill_betweenx(x_range, 0, y_kde/np.max(y_kde), alpha=0.5, color='steelblue')
        plt.axvline(x=0, color='black', linewidth=1)
        plt.ylabel('Valeurs', fontsize=12)
        plt.xlabel('Densité relative', fontsize=12)
        title = title or f'Bean Plot (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_strip_plot(self, figsize=(8, 6), title=None):
        """Graphique 14: Strip plot (points alignés)"""
        plt.figure(figsize=figsize)
        x_jitter = np.random.normal(0, 0.04, len(self.data))
        plt.scatter(self.data, x_jitter, alpha=0.5, s=15, c='steelblue')
        plt.xlabel('Valeurs', fontsize=12)
        plt.yticks([0], [''])
        plt.ylim(-0.2, 0.2)
        title = title or f'Strip Plot (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        plt.show()

    def graph_violin_scatter(self, figsize=(10, 6), title=None):
        """Graphique 15: Violin plot avec points individuels"""
        plt.figure(figsize=figsize)
        parts = plt.violinplot(self.data, vert=True, showmeans=True, showmedians=True)
        for pc in parts['bodies']:
            pc.set_facecolor('steelblue')
            pc.set_alpha(0.5)
        y_jitter = np.random.normal(1, 0.04, len(self.data))
        plt.scatter(self.data, y_jitter, alpha=0.3, s=10, c='red')
        plt.ylabel('Valeurs', fontsize=12)
        plt.xticks([1], ['Données'])
        title = title or f'Violin Plot avec Points (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_rug_plot(self, figsize=(10, 2), title=None):
        """Graphique 16: Rug plot (marques sur l'axe)"""
        plt.figure(figsize=figsize)
        plt.eventplot(self.data, orientation='horizontal', colors='steelblue', linewidths=1)
        plt.yticks([1], [''])
        plt.xlabel('Valeurs', fontsize=12)
        title = title or f'Rug Plot (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        plt.show()

    def graph_jitter_plot(self, figsize=(10, 4), title=None):
        """Graphique 17: Jitter plot (points avec bruit)"""
        plt.figure(figsize=figsize)
        x = np.arange(len(self.data))
        y_jitter = self.data + np.random.normal(0, 0.05 * np.std(self.data), len(self.data))
        plt.scatter(x, y_jitter, alpha=0.5, s=15, c='steelblue')
        plt.xlabel('Index', fontsize=12)
        plt.ylabel('Valeurs (avec jitter)', fontsize=12)
        title = title or f'Jitter Plot (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_dot_plot(self, figsize=(10, 4), title=None):
        """Graphique 18: Dot plot (points alignés verticalement)"""
        plt.figure(figsize=figsize)
        unique_vals, counts = np.unique(self.data, return_counts=True)
        plt.plot(unique_vals, counts, 'o-', markersize=8, color='steelblue', linewidth=1)
        plt.fill_between(unique_vals, counts, alpha=0.2, color='steelblue')
        plt.xlabel('Valeurs', fontsize=12)
        plt.ylabel('Fréquence', fontsize=12)
        title = title or f'Dot Plot (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    # GRAPHIQUES DE CONCENTRATION 

    def graph_courbe_lorenz(self, figsize=(8, 8), title=None):
        """Graphique 19: Courbe de Lorenz"""
        plt.figure(figsize=figsize)
        x, y = self.courbe_lorenz()
        plt.plot(x, y, 'b-', linewidth=2.5, label='Courbe de Lorenz')
        plt.plot([0, 1], [0, 1], 'r--', linewidth=1.5, label='Égalité parfaite', alpha=0.7)
        plt.fill_between(x, x, y, alpha=0.2, color='gray')
        gini = self.indice_gini()
        plt.text(0.6, 0.2, f'Indice de Gini = {gini:.4f}',
                 fontsize=12, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        plt.xlabel('Proportion cumulée de la population', fontsize=12)
        plt.ylabel('Proportion cumulée des richesses', fontsize=12)
        title = title or f'Courbe de Lorenz (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('scaled')
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.show()

    def graph_concentration_curve(self, figsize=(8, 8), title=None):
        """Graphique 20: Courbe de concentration"""
        plt.figure(figsize=figsize)
        x = np.linspace(0, 1, len(self.data))
        y = self.courbe_concentration()
        plt.plot(x, y, 'g-', linewidth=2.5, label='Courbe de concentration')
        plt.fill_between(x, 0, y, alpha=0.2, color='green')
        plt.xlabel('Proportion de la population', fontsize=12)
        plt.ylabel('Proportion cumulée', fontsize=12)
        title = title or f'Courbe de Concentration (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_pie_chart_parts(self, n_parts=5, figsize=(8, 8), title=None):
        """Graphique 21: Diagramme circulaire des parts"""
        plt.figure(figsize=figsize)
        parts = np.array_split(self.data, n_parts)
        sommes_parts = [np.sum(part) for part in parts]
        labels = [f'Partie {i+1}\n{somme:.1f}' for i, somme in enumerate(sommes_parts)]
        colors = plt.cm.viridis(np.linspace(0, 1, n_parts))
        plt.pie(sommes_parts, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        title = title or f'Répartition en {n_parts} parts'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.show()

    def graph_bar_chart_concentration(self, figsize=(10, 6), title=None):
        """Graphique 22: Diagramme à barres de concentration"""
        plt.figure(figsize=figsize)
        data_sorted = np.sort(self.data)[::-1]
        plt.bar(range(len(data_sorted)), data_sorted, color='steelblue', alpha=0.7, edgecolor='black')
        plt.xlabel('Indice (ordre décroissant)', fontsize=12)
        plt.ylabel('Valeurs', fontsize=12)
        title = title or f'Diagramme de Concentration (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
        plt.show()

    def graph_pareto_chart(self, figsize=(12, 6), title=None):
        """Graphique 23: Diagramme de Pareto"""
        fig, ax1 = plt.subplots(figsize=figsize)
        data_sorted = np.sort(self.data)[::-1]
        cumsum = np.cumsum(data_sorted)
        cumsum_percent = cumsum / cumsum[-1] * 100
        ax1.bar(range(len(data_sorted)), data_sorted, color='steelblue', alpha=0.7, label='Valeurs')
        ax1.set_xlabel('Indice', fontsize=12)
        ax1.set_ylabel('Valeurs', fontsize=12, color='steelblue')
        ax1.tick_params(axis='y', labelcolor='steelblue')
        ax2 = ax1.twinx()
        ax2.plot(range(len(cumsum_percent)), cumsum_percent, 'r-', linewidth=2, marker='o', label='Cumul %')
        ax2.set_ylabel('Pourcentage cumulé (%)', fontsize=12, color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        ax2.axhline(y=80, color='gray', linestyle='--', alpha=0.5)
        title = title or f'Diagramme de Pareto (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        fig.tight_layout()
        plt.show()

    def graph_herfindahl_chart(self, figsize=(8, 6), title=None):
        """Graphique 24: Indice de Herfindahl (visualisation)"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        total = np.sum(self.data)
        parts = self.data / total
        squared_parts = parts ** 2
        ax1.bar(range(len(squared_parts)), squared_parts, color='steelblue', alpha=0.7)
        ax1.set_xlabel('Indice', fontsize=10)
        ax1.set_ylabel('p_i²', fontsize=10)
        ax1.set_title(f'Herfindahl = {self.concentration_herfindahl():.4f}')
        ax1.grid(True, alpha=0.3)
        ax2.pie(parts, autopct='%1.0f%%', startangle=90)
        ax2.set_title('Parts relatives')
        title = title or f'Indice de Herfindahl'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_gini_chart(self, figsize=(10, 6), title=None):
        """Graphique 25: Visualisation de l'indice de Gini"""
        plt.figure(figsize=figsize)
        x, y = self.courbe_lorenz()
        plt.plot(x, y, 'b-', linewidth=2.5, label='Courbe de Lorenz')
        plt.plot([0, 1], [0, 1], 'r--', linewidth=1.5, label='Égalité parfaite')
        plt.fill_between(x, x, y, alpha=0.3, color='gray', label='Aire d\'inégalité')
        gini = self.indice_gini()
        plt.text(0.6, 0.3, f'Gini = {gini:.4f}\nAire = {gini/2:.4f}',
                 fontsize=12, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        plt.xlabel('Proportion cumulée de la population', fontsize=12)
        plt.ylabel('Proportion cumulée des richesses', fontsize=12)
        title = title or f'Indice de Gini = {gini:.4f}'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('scaled')
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.show()

    #    GRAPHIQUES DE DÉPENDANCE 

    def graph_heatmap_correlation(self, autres_variables, noms_variables=None, figsize=(10, 8), title=None):
        """Graphique 26: Heatmap de corrélation"""
        toutes_vars = [self.data] + list(autres_variables)
        min_len = min(len(var) for var in toutes_vars)
        toutes_vars = [var[:min_len] for var in toutes_vars]
        matrice = np.array(toutes_vars)
        corr_matrix = np.corrcoef(matrice)
        n_vars = len(toutes_vars)
        if noms_variables is None:
            noms = [f'Var{i+1}' for i in range(n_vars)]
        elif len(noms_variables) == n_vars:
            noms = list(noms_variables)
        else:
            noms = list(noms_variables)[:n_vars]
            while len(noms) < n_vars:
                noms.append(f'Var{len(noms)+1}')
        plt.figure(figsize=figsize)
        im = plt.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        for i in range(n_vars):
            for j in range(n_vars):
                plt.text(j, i, f'{corr_matrix[i, j]:.2f}',
                         ha="center", va="center",
                         color="white" if abs(corr_matrix[i, j]) > 0.5 else "black",
                         fontsize=9)
        plt.xticks(range(n_vars), noms, rotation=45, ha='right')
        plt.yticks(range(n_vars), noms)
        plt.colorbar(im, label='Coefficient de corrélation')
        title = title or 'Matrice de Corrélation (Heatmap)'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_correlation_matrix(self, autres_variables, noms_variables=None, figsize=(8, 6), title=None):
        """Graphique 27: Matrice de corrélation (tableau)"""
        toutes_vars = [self.data] + list(autres_variables)
        min_len = min(len(var) for var in toutes_vars)
        toutes_vars = [var[:min_len] for var in toutes_vars]
        matrice = np.array(toutes_vars)
        corr_matrix = np.corrcoef(matrice)
        n_vars = len(toutes_vars)
        if noms_variables is None:
            noms = [f'Var{i+1}' for i in range(n_vars)]
        elif len(noms_variables) == n_vars:
            noms = list(noms_variables)
        else:
            noms = list(noms_variables)[:n_vars]
            while len(noms) < n_vars:
                noms.append(f'Var{len(noms)+1}')
        fig, ax = plt.subplots(figsize=figsize)
        ax.axis('tight')
        ax.axis('off')
        table_data = [[f'{val:.3f}' for val in row] for row in corr_matrix]
        table = ax.table(cellText=table_data, rowLabels=noms, colLabels=noms,
                         cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        title = title or 'Matrice de Corrélation'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.show()

    def graph_autocorrelation(self, max_lags=20, figsize=(10, 6), title=None):
        """Graphique 28: Autocorrélogramme (ACF)"""
        try:
            from statsmodels.graphics.tsaplots import plot_acf
            plt.figure(figsize=figsize)
            plot_acf(self.data, lags=min(max_lags, len(self.data)//2), alpha=0.05, ax=plt.gca())
            title = title or f'Autocorrélogramme (n={len(self.data)})'
            plt.title(title, fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.show()
        except ImportError:
            print("Installation de statsmodels requise: pip install statsmodels")

    def graph_cross_correlation(self, y, max_lags=20, figsize=(10, 6), title=None):
        """Graphique 29: Corrélation croisée"""
        n = min(len(self.data), len(y))
        x_plot = self.data[:n]
        y_plot = np.array(y[:n])
        plt.figure(figsize=figsize)
        lags = range(-min(max_lags, n//2), min(max_lags, n//2) + 1)
        correlations = []
        for lag in lags:
            if lag >= 0:
                corr = np.corrcoef(x_plot[:-lag] if lag > 0 else x_plot,
                                   y_plot[lag:] if lag > 0 else y_plot)[0, 1]
            else:
                corr = np.corrcoef(x_plot[-lag:], y_plot[:lag])[0, 1]
            correlations.append(corr if not np.isnan(corr) else 0)
        plt.bar(lags, correlations, color='steelblue', alpha=0.7, edgecolor='black')
        plt.axhline(y=0, color='red', linestyle='-', linewidth=1)
        plt.xlabel('Décalage (lag)', fontsize=12)
        plt.ylabel('Corrélation croisée', fontsize=12)
        title = title or f'Corrélation Croisée (n={n})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_partial_correlation(self, y, z, figsize=(8, 6), title=None):
        """Graphique 30: Corrélation partielle"""
        n = min(len(self.data), len(y), len(z))
        x_plot = self.data[:n]
        y_plot = np.array(y[:n])
        z_plot = np.array(z[:n])
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        axes[0].scatter(x_plot, y_plot, alpha=0.6, c='steelblue')
        r_simple = self.correlation_pearson(y_plot)
        axes[0].set_xlabel('X', fontsize=10)
        axes[0].set_ylabel('Y', fontsize=10)
        axes[0].set_title(f'Corrélation simple: r = {r_simple:.3f}')
        axes[0].grid(True, alpha=0.3)
        from scipy.stats import linregress
        slope_xz, _, _, _, _ = linregress(z_plot, x_plot)
        slope_yz, _, _, _, _ = linregress(z_plot, y_plot)
        resid_x = x_plot - slope_xz * z_plot
        resid_y = y_plot - slope_yz * z_plot
        axes[1].scatter(resid_x, resid_y, alpha=0.6, c='darkorange')
        r_partial = self.correlation_partielle(y_plot, z_plot)
        axes[1].set_xlabel('Résidus de X | Z', fontsize=10)
        axes[1].set_ylabel('Résidus de Y | Z', fontsize=10)
        axes[1].set_title(f'Corrélation partielle: r = {r_partial:.3f}')
        axes[1].grid(True, alpha=0.3)
        title = title or 'Corrélation Simple vs Partielle'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_pairplot(self, autres_variables, noms_variables=None, figsize=(12, 10), title=None):
        """Graphique 31: Pairplot (matrice de scatter)"""
        toutes_vars = [self.data] + list(autres_variables)
        min_len = min(len(var) for var in toutes_vars)
        toutes_vars = [var[:min_len] for var in toutes_vars]
        n_vars = len(toutes_vars)
        if noms_variables is None:
            noms = [f'Var{i+1}' for i in range(n_vars)]
        elif len(noms_variables) == n_vars:
            noms = list(noms_variables)
        else:
            noms = list(noms_variables)[:n_vars]
            while len(noms) < n_vars:
                noms.append(f'Var{len(noms)+1}')
        fig, axes = plt.subplots(n_vars, n_vars, figsize=figsize)
        for i in range(n_vars):
            for j in range(n_vars):
                if i == j:
                    axes[i, j].hist(toutes_vars[i], bins=20, color='steelblue', alpha=0.7)
                else:
                    axes[i, j].scatter(toutes_vars[j], toutes_vars[i], alpha=0.3, s=5, c='steelblue')
                if i == n_vars-1:
                    axes[i, j].set_xlabel(noms[j], fontsize=8, rotation=45)
                if j == 0:
                    axes[i, j].set_ylabel(noms[i], fontsize=8, rotation=0)
                axes[i, j].tick_params(axis='both', labelsize=6)
        title = title or 'Pairplot (Matrice de scatter)'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_scatter_matrix(self, autres_variables, noms_variables=None, figsize=(12, 10), title=None):
        """Graphique 32: Matrice de scatter avec corrélations"""
        self.graph_pairplot(autres_variables, noms_variables, figsize, title)

    def graph_correlation_circle(self, autres_variables, noms_variables=None, figsize=(8, 8), title=None):
        """Graphique 33: Cercle de corrélation (ACP simplifié)"""
        toutes_vars = [self.data] + list(autres_variables)
        min_len = min(len(var) for var in toutes_vars)
        toutes_vars = [var[:min_len] for var in toutes_vars]
        n_vars = len(toutes_vars)
        matrice = np.array(toutes_vars).T
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        pca.fit(matrice)
        correlations = pca.components_.T
        if noms_variables is None:
            noms = [f'Var{i+1}' for i in range(n_vars)]
        elif len(noms_variables) == n_vars:
            noms = list(noms_variables)
        else:
            noms = list(noms_variables)[:n_vars]
            while len(noms) < n_vars:
                noms.append(f'Var{len(noms)+1}')
        plt.figure(figsize=figsize)
        circle = plt.Circle((0, 0), 1, fill=False, linestyle='--', color='gray')
        plt.gca().add_artist(circle)
        for i, (x, y) in enumerate(correlations):
            plt.arrow(0, 0, x, y, head_width=0.05, head_length=0.05,
                      fc='steelblue', ec='steelblue', alpha=0.7)
            plt.text(x*1.1, y*1.1, noms[i], fontsize=10, ha='center', va='center')
        plt.xlim(-1.1, 1.1)
        plt.ylim(-1.1, 1.1)
        plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        plt.axvline(x=0, color='gray', linestyle='-', alpha=0.3)
        plt.xlabel(f'Dimension 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', fontsize=12)
        plt.ylabel(f'Dimension 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', fontsize=12)
        title = title or 'Cercle de Corrélation (ACP)'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.show()

    def graph_biplot(self, autres_variables, noms_variables=None, figsize=(10, 8), title=None):
        """Graphique 34: Biplot (ACP avec individus et variables)"""
        toutes_vars = [self.data] + list(autres_variables)
        min_len = min(len(var) for var in toutes_vars)
        toutes_vars = [var[:min_len] for var in toutes_vars]
        n_vars = len(toutes_vars)
        matrice = np.array(toutes_vars).T
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        scores = pca.fit_transform(matrice)
        loadings = pca.components_.T
        if noms_variables is None:
            noms = [f'Var{i+1}' for i in range(n_vars)]
        elif len(noms_variables) == n_vars:
            noms = list(noms_variables)
        else:
            noms = list(noms_variables)[:n_vars]
            while len(noms) < n_vars:
                noms.append(f'Var{len(noms)+1}')
        plt.figure(figsize=figsize)
        plt.scatter(scores[:, 0], scores[:, 1], alpha=0.5,
                    c='lightblue', edgecolor='black', s=30)
        for i, (x, y) in enumerate(loadings):
            plt.arrow(0, 0, x*3, y*3, head_width=0.1, head_length=0.1,
                      fc='red', ec='red', alpha=0.7)
            plt.text(x*3.2, y*3.2, noms[i], fontsize=10,
                     ha='center', va='center', color='red')
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', fontsize=12)
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', fontsize=12)
        title = title or 'Biplot (ACP)'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    #   GRAPHIQUES DE FORME 

    def graph_skewness_plot(self, figsize=(10, 6), title=None):
        """Graphique 35: Visualisation de l'asymétrie"""
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        skew_val = self.coeff_asymetrie_fisher()
        axes[0].hist(self.data, bins=30, density=True, alpha=0.7,
                     color='steelblue', edgecolor='black')
        axes[0].axvline(x=self.moyen_arth(), color='red', linewidth=2,
                        label=f'Moyenne = {self.moyen_arth():.2f}')
        axes[0].axvline(x=self.mediane(), color='green', linewidth=2,
                        label=f'Médiane = {self.mediane():.2f}')
        axes[0].set_xlabel('Valeurs', fontsize=10)
        axes[0].set_ylabel('Densité', fontsize=10)
        axes[0].set_title(f'Distribution (Skewness = {skew_val:.3f})')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        color = 'red' if skew_val < 0 else ('green' if skew_val > 0 else 'blue')
        axes[1].bar(['Asymétrie'], [skew_val], color=color, alpha=0.7, edgecolor='black')
        axes[1].axhline(y=0, color='black', linewidth=1)
        axes[1].set_ylabel('Coefficient d\'asymétrie', fontsize=10)
        axes[1].set_title(
            f'Asymétrie: {"Positive" if skew_val > 0 else "Négative" if skew_val < 0 else "Nulle"}')
        axes[1].grid(True, alpha=0.3, axis='y')
        title = title or f'Visualisation de l\'Asymétrie (Skewness = {skew_val:.3f})'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_kurtosis_plot(self, figsize=(10, 6), title=None):
        """Graphique 36: Visualisation de l'aplatissement"""
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        kurt_val = self.coefficient_aplatissement_fisher()
        x_range = np.linspace(min(self.data), max(self.data), 200)
        kde = gaussian_kde(self.data)
        axes[0].plot(x_range, kde(x_range), 'b-', linewidth=2, label='Distribution observée')
        norm_kde = norm.pdf(x_range, loc=self.moyen_arth(), scale=self.ecart_type())
        axes[0].plot(x_range, norm_kde, 'r--', linewidth=2, label='Distribution normale')
        axes[0].set_xlabel('Valeurs', fontsize=10)
        axes[0].set_ylabel('Densité', fontsize=10)
        axes[0].set_title(f'Comparaison (Kurtosis = {kurt_val:.3f})')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        color = 'purple' if kurt_val > 0 else ('orange' if kurt_val < 0 else 'gray')
        axes[1].bar(['Aplatissement'], [kurt_val], color=color, alpha=0.7, edgecolor='black')
        axes[1].axhline(y=0, color='black', linewidth=1)
        axes[1].set_ylabel('Coefficient d\'aplatissement (excès)', fontsize=10)
        kurt_type = ('Leptokurtique (pointue)' if kurt_val > 0
                     else ('Platykurtique (plate)' if kurt_val < 0 else 'Mésokurtique (normale)'))
        axes[1].set_title(f'Aplatissement: {kurt_type}')
        axes[1].grid(True, alpha=0.3, axis='y')
        title = title or f'Visualisation de l\'Aplatissement (Kurtosis = {kurt_val:.3f})'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_ridge_plot(self, n_parts=3, figsize=(12, 6), title=None):
        """Graphique 37: Ridge plot (densités superposées par parties)"""
        fig, ax = plt.subplots(figsize=figsize)
        parts = np.array_split(self.data, n_parts)
        noms_parts = [f'Partie {i+1}' for i in range(n_parts)]
        couleurs = ['steelblue', 'orange', 'darkgreen', 'red', 'purple', 'brown']
        x_range = np.linspace(min(self.data), max(self.data), 200)
        for i, (part, nom, couleur) in enumerate(zip(parts, noms_parts, couleurs[:n_parts])):
            if len(part) > 1:
                kde = gaussian_kde(part)
                y_kde = kde(x_range)
                ax.fill_between(x_range, i, i + y_kde / max(y_kde) * 0.8,
                                alpha=0.5, color=couleur, label=nom)
        ax.set_xlabel('Valeurs', fontsize=12)
        ax.set_ylabel('Densité relative', fontsize=12)
        ax.set_yticks([i + 0.4 for i in range(n_parts)])
        ax.set_yticklabels(noms_parts)
        title = title or f'Ridge Plot (Distribution par parties - n={len(self.data)})'
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.show()

    def graph_joyplot(self, n_parts=4, figsize=(12, 8), title=None):
        """Graphique 38: Joy plot (densités superposées)"""
        fig, ax = plt.subplots(figsize=figsize)
        parts = np.array_split(self.data, n_parts)
        noms_parts = [f'Groupe {i+1}' for i in range(n_parts)]
        couleurs = plt.cm.viridis(np.linspace(0, 1, n_parts))
        x_range = np.linspace(min(self.data), max(self.data), 200)
        for i, (part, nom, couleur) in enumerate(zip(parts, noms_parts, couleurs)):
            if len(part) > 1:
                kde = gaussian_kde(part)
                y_kde = kde(x_range)
                y_kde_norm = y_kde / max(y_kde) * 0.8
                ax.fill_between(x_range, i + y_kde_norm, i, alpha=0.6, color=couleur, label=nom)
                ax.plot(x_range, i + y_kde_norm, color=couleur, linewidth=1)
        ax.set_xlabel('Valeurs', fontsize=12)
        ax.set_ylabel('Groupes', fontsize=12)
        ax.set_yticks([i + 0.4 for i in range(n_parts)])
        ax.set_yticklabels(noms_parts)
        title = title or f'Joy Plot (Densités superposées - n={len(self.data)})'
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        plt.show()

    def graph_multi_density(self, autres_donnees, autres_noms=None, figsize=(10, 6), title=None):
        """Graphique 39: Densités multiples (superposition)"""
        plt.figure(figsize=figsize)
        toutes_donnees = [self.data] + list(autres_donnees)
        tous_noms = self._construire_noms(autres_noms, len(toutes_donnees))
        couleurs = ['steelblue', 'orange', 'green', 'red', 'purple', 'brown']
        x_range = np.linspace(min(np.concatenate(toutes_donnees)),
                              max(np.concatenate(toutes_donnees)), 200)
        for i, (data, nom, couleur) in enumerate(zip(toutes_donnees, tous_noms, couleurs)):
            if len(data) > 1:
                kde = gaussian_kde(data)
                plt.plot(x_range, kde(x_range), linewidth=2, color=couleur, label=nom)
        plt.xlabel('Valeurs', fontsize=12)
        plt.ylabel('Densité', fontsize=12)
        title = title or 'Comparaison des densités'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_hill_plot(self, max_k=None, figsize=(10, 6), title=None):
        """Graphique 40: Hill plot (indice de queue)"""
        data_sorted = np.sort(self.data)[::-1]
        n = len(data_sorted)
        if max_k is None:
            max_k = min(n//2, 100)
        k_range = range(2, max_k)
        hill_estimates = []
        for k in k_range:
            hill = (np.mean(np.log(data_sorted[:k] / data_sorted[k]))
                    if data_sorted[k] > 0 else np.nan)
            hill_estimates.append(hill)
        plt.figure(figsize=figsize)
        plt.plot(list(k_range), hill_estimates, 'b-', linewidth=1.5)
        plt.axhline(y=np.nanmean(hill_estimates[-20:]), color='r', linestyle='--',
                    label=f'Estimation finale: {np.nanmean(hill_estimates[-20:]):.3f}')
        plt.xlabel('k (nombre d\'extrêmes)', fontsize=12)
        plt.ylabel('Indice de queue (Hill)', fontsize=12)
        title = title or f'Hill Plot (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_tail_plot(self, figsize=(10, 6), title=None):
        """Graphique 41: Queue de distribution (tail plot)"""
        data_sorted = np.sort(self.data)
        n = len(data_sorted)
        exceedances = 1 - np.arange(1, n+1) / n
        plt.figure(figsize=figsize)
        plt.loglog(data_sorted, exceedances, 'b-', linewidth=2, label='Queue supérieure')
        plt.loglog(data_sorted, 1 - exceedances, 'r-', linewidth=2, label='Queue inférieure')
        plt.xlabel('Valeurs (échelle log)', fontsize=12)
        plt.ylabel('Probabilité de dépassement (échelle log)', fontsize=12)
        title = title or f'Queue de Distribution (Tail Plot - n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    #    GRAPHIQUES TEMPORELS 

    def graph_time_series(self, figsize=(12, 5), title=None):
        """Graphique 42: Série temporelle"""
        plt.figure(figsize=figsize)
        plt.plot(self.data, 'b-', linewidth=1.5, alpha=0.7)
        plt.scatter(range(len(self.data)), self.data, s=10, c='steelblue', alpha=0.5)
        plt.xlabel('Temps', fontsize=12)
        plt.ylabel('Valeurs', fontsize=12)
        title = title or f'Série Temporelle (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_seasonal_plot(self, period=12, figsize=(12, 6), title=None):
        """Graphique 43: Saisonnalité"""
        n = len(self.data)
        n_periods = n // period
        if n_periods < 2:
            print(f"Pas assez de données pour {period} périodes")
            return
        data_reshaped = self.data[:n_periods*period].reshape(n_periods, period)
        plt.figure(figsize=figsize)
        for i in range(n_periods):
            plt.plot(range(period), data_reshaped[i, :], 'o-', alpha=0.5, label=f'Cycle {i+1}')
        plt.plot(range(period), np.mean(data_reshaped, axis=0),
                 'k-', linewidth=2.5, label='Moyenne')
        plt.xlabel('Position dans la période', fontsize=12)
        plt.ylabel('Valeurs', fontsize=12)
        title = title or f'Graphique Saisonnier (période={period})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend(loc='best')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_trend_plot(self, figsize=(12, 6), title=None):
        """Graphique 44: Tendance avec lissage"""
        plt.figure(figsize=figsize)
        plt.plot(self.data, 'b-', alpha=0.4, label='Données originales')
        from scipy.signal import savgol_filter
        if len(self.data) > 10:
            trend = savgol_filter(self.data, min(11, len(self.data)//5*2+1), 3)
            plt.plot(trend, 'r-', linewidth=2.5, label='Tendance (filtre SG)')
        window = min(5, len(self.data)//4)
        if window > 1:
            ma = np.convolve(self.data, np.ones(window)/window, mode='valid')
            plt.plot(range(window-1, len(self.data)), ma, 'g--',
                     linewidth=2, label=f'MA({window})')
        plt.xlabel('Temps', fontsize=12)
        plt.ylabel('Valeurs', fontsize=12)
        title = title or f'Tendance et Lissage (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_acf_pacf(self, max_lags=20, figsize=(12, 8), title=None):
        """Graphique 45: ACF et PACF"""
        try:
            from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
            plot_acf(self.data, lags=min(max_lags, len(self.data)//2), ax=ax1, alpha=0.05)
            ax1.set_title('Autocorrélation (ACF)')
            ax1.grid(True, alpha=0.3)
            plot_pacf(self.data, lags=min(max_lags, len(self.data)//2),
                      ax=ax2, alpha=0.05, method='ywm')
            ax2.set_title('Autocorrélation Partielle (PACF)')
            ax2.grid(True, alpha=0.3)
            title = title or f'ACF et PACF (n={len(self.data)})'
            fig.suptitle(title, fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.show()
        except ImportError:
            print("Installation de statsmodels requise: pip install statsmodels")

    def graph_spectral_density(self, figsize=(10, 6), title=None):
        """Graphique 46: Densité spectrale"""
        from scipy import signal
        plt.figure(figsize=figsize)
        f, Pxx = signal.periodogram(self.data, fs=1, window='hann')
        plt.semilogy(f[1:], Pxx[1:], 'b-', linewidth=1.5)
        plt.xlabel('Fréquence', fontsize=12)
        plt.ylabel('Densité spectrale de puissance', fontsize=12)
        title = title or f'Densité Spectrale (Periodogramme - n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_decomposition(self, period=None, figsize=(14, 10), title=None):
        """Graphique 47: Décomposition temporelle (trend + seasonal + residual)"""
        from scipy import signal
        n = len(self.data)
        if period is None:
            period = max(2, n // 10)
        window = min(period*2+1, n//4*2+1)
        if window % 2 == 0:
            window += 1
        trend = signal.savgol_filter(self.data, window, 3)
        detrended = self.data - trend
        n_periods = n // period
        if n_periods >= 2:
            seasonal = np.zeros(n)
            for i in range(period):
                indices = list(range(i, n, period))
                if len(indices) > 0:
                    seasonal[indices] = np.mean(detrended[indices])
            residual = detrended - seasonal
        else:
            seasonal = np.zeros(n)
            residual = detrended
        fig, axes = plt.subplots(4, 1, figsize=figsize)
        axes[0].plot(self.data, 'b-', linewidth=1)
        axes[0].set_title('Série originale')
        axes[0].grid(True, alpha=0.3)
        axes[1].plot(trend, 'r-', linewidth=1.5)
        axes[1].set_title('Tendance')
        axes[1].grid(True, alpha=0.3)
        axes[2].plot(seasonal, 'g-', linewidth=1)
        axes[2].set_title('Composante saisonnière')
        axes[2].grid(True, alpha=0.3)
        axes[3].plot(residual, 'k-', linewidth=0.8)
        axes[3].axhline(y=0, color='gray', linestyle='--')
        axes[3].set_title('Résidus')
        axes[3].grid(True, alpha=0.3)
        for ax in axes:
            ax.set_xlim(0, n-1)
        title = title or f'Décomposition Temporelle (période={period})'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_lag_plot(self, max_lag=1, figsize=(8, 8), title=None):
        """Graphique 48: Diagramme de décalage (lag plot)"""
        if max_lag < 1:
            max_lag = 1
        fig, axes = plt.subplots(1, max_lag, figsize=(max_lag*6, 5))
        if max_lag == 1:
            axes = [axes]
        for lag in range(1, max_lag+1):
            ax = axes[lag-1]
            ax.scatter(self.data[:-lag], self.data[lag:], alpha=0.5, s=20, c='steelblue')
            ax.set_xlabel(f'X(t)', fontsize=10)
            ax.set_ylabel(f'X(t+{lag})', fontsize=10)
            ax.set_title(f'Lag {lag} (r={self.autocorrelation(lag):.3f})')
            ax.grid(True, alpha=0.3)
            min_val = min(np.min(self.data[:-lag]), np.min(self.data[lag:]))
            max_val = max(np.max(self.data[:-lag]), np.max(self.data[lag:]))
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.5)
        title = title or f'Lag Plots (n={len(self.data)})'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_phase_plot(self, lag=1, figsize=(8, 8), title=None):
        """Graphique 49: Diagramme de phase (espace d'état)"""
        plt.figure(figsize=figsize)
        plt.plot(self.data[:-lag], self.data[lag:], 'b-', alpha=0.5, linewidth=0.5)
        plt.scatter(self.data[:-lag], self.data[lag:], s=10, c='steelblue', alpha=0.5)
        plt.xlabel(f'X(t)', fontsize=12)
        plt.ylabel(f'X(t+{lag})', fontsize=12)
        title = title or f'Diagramme de Phase (lag={lag}, n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.show()

    #         GRAPHIQUES AVANCÉS 

    def graph_contour_plot(self, y, figsize=(10, 8), title=None):
        """Graphique 50: Contour plot (densité 2D)"""
        n = min(len(self.data), len(y))
        x_data = self.data[:n]
        y_data = np.array(y[:n])
        valid = np.isfinite(x_data) & np.isfinite(y_data)
        x_data = x_data[valid]
        y_data = y_data[valid]
        if len(x_data) < 4:
            print(f"ERREUR: Pas assez de données (n={len(x_data)})")
            plt.figure(figsize=figsize)
            plt.scatter(x_data, y_data, alpha=0.5, c='blue')
            plt.xlabel('Variable X')
            plt.ylabel('Variable Y')
            plt.title(title or 'Scatter Plot (données insuffisantes)')
            plt.show()
            return
        try:
            if np.std(x_data) == 0:
                x_data = x_data + np.random.normal(0, 1e-6, len(x_data))
            if np.std(y_data) == 0:
                y_data = y_data + np.random.normal(0, 1e-6, len(y_data))
            xy = np.vstack([x_data, y_data])
            kde = gaussian_kde(xy)
            x_range = np.linspace(x_data.min(), x_data.max(), 50)
            y_range = np.linspace(y_data.min(), y_data.max(), 50)
            X, Y = np.meshgrid(x_range, y_range)
            Z = kde(np.vstack([X.ravel(), Y.ravel()])).reshape(X.shape)
            plt.figure(figsize=figsize)
            contour = plt.contour(X, Y, Z, levels=10, cmap='viridis')
            plt.colorbar(contour, label='Densité')
            plt.scatter(x_data, y_data, alpha=0.3, s=10, c='red')
            plt.xlabel('Variable X', fontsize=12)
            plt.ylabel('Variable Y', fontsize=12)
            plt.title(title or 'Contour Plot (Densité 2D)', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Erreur: {e}")
            plt.figure(figsize=figsize)
            plt.scatter(x_data, y_data, alpha=0.5, c='blue')
            plt.xlabel('Variable X', fontsize=12)
            plt.ylabel('Variable Y', fontsize=12)
            plt.title(title or 'Scatter Plot', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.show()

    def graph_3d_scatter(self, y, z, figsize=(10, 8), title=None):
        """Graphique 51: Scatter 3D"""
        from mpl_toolkits.mplot3d import Axes3D
        n = min(len(self.data), len(y), len(z))
        x_plot = self.data[:n]
        y_plot = np.array(y[:n])
        z_plot = np.array(z[:n])
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        scatter = ax.scatter(x_plot, y_plot, z_plot, c=x_plot, cmap='viridis', s=20, alpha=0.6)
        ax.set_xlabel('X', fontsize=10)
        ax.set_ylabel('Y', fontsize=10)
        ax.set_zlabel('Z', fontsize=10)
        plt.colorbar(scatter, label='Valeur X')
        title = title or 'Nuage de points 3D'
        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.show()

    def graph_3d_surface(self, y, figsize=(10, 8), title=None):
        """Graphique 52: Surface 3D"""
        from mpl_toolkits.mplot3d import Axes3D
        n = min(len(self.data), len(y))
        x_plot = self.data[:n]
        y_plot = np.array(y[:n])
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        x_grid = np.linspace(min(x_plot), max(x_plot), 20)
        y_grid = np.linspace(min(y_plot), max(y_plot), 20)
        X, Y = np.meshgrid(x_grid, y_grid)
        from scipy.interpolate import griddata
        Z = griddata((x_plot, y_plot), np.zeros_like(x_plot), (X, Y), method='nearest')
        surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
        ax.set_xlabel('X', fontsize=10)
        ax.set_ylabel('Y', fontsize=10)
        ax.set_zlabel('Z', fontsize=10)
        plt.colorbar(surf)
        title = title or 'Surface 3D'
        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.show()

    def graph_hexbin_plot(self, y, figsize=(10, 8), title=None):
        """Graphique 53: Hexbin plot"""
        n = min(len(self.data), len(y))
        x_plot = self.data[:n]
        y_plot = np.array(y[:n])
        plt.figure(figsize=figsize)
        hb = plt.hexbin(x_plot, y_plot, gridsize=30, cmap='viridis', mincnt=1)
        plt.colorbar(hb, label='Nombre de points')
        plt.xlabel('Variable X', fontsize=12)
        plt.ylabel('Variable Y', fontsize=12)
        title = title or 'Hexbin Plot (Densité 2D par hexagones)'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_2d_density(self, y, figsize=(10, 8), title=None):
        """Graphique 54: Densité 2D"""
        n = min(len(self.data), len(y))
        x_plot = self.data[:n]
        y_plot = np.array(y[:n])
        plt.figure(figsize=figsize)
        xy = np.vstack([x_plot, y_plot])
        kde = gaussian_kde(xy)
        x_range = np.linspace(min(x_plot), max(x_plot), 100)
        y_range = np.linspace(min(y_plot), max(y_plot), 100)
        X, Y = np.meshgrid(x_range, y_range)
        positions = np.vstack([X.ravel(), Y.ravel()])
        Z = kde(positions).reshape(X.shape)
        im = plt.imshow(Z, extent=[min(x_plot), max(x_plot), min(y_plot), max(y_plot)],
                        origin='lower', cmap='viridis', aspect='auto')
        plt.colorbar(im, label='Densité')
        plt.scatter(x_plot, y_plot, alpha=0.2, s=5, c='red')
        plt.xlabel('Variable X', fontsize=12)
        plt.ylabel('Variable Y', fontsize=12)
        title = title or 'Densité 2D (KDE)'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.show()

    def graph_parallel_coordinates(self, autres_variables, noms_variables=None, figsize=(12, 6), title=None):
        """Graphique 55: Coordonnées parallèles"""
        toutes_vars = [self.data] + list(autres_variables)
        min_len = min(len(var) for var in toutes_vars)
        toutes_vars = [var[:min_len] for var in toutes_vars]
        n_vars = len(toutes_vars)
        matrice = np.array(toutes_vars).T
        noms = (list(noms_variables) if noms_variables is not None and len(noms_variables) == n_vars
                else [f'Var{i+1}' for i in range(n_vars)])
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        matrice_norm = scaler.fit_transform(matrice)
        plt.figure(figsize=figsize)
        for i in range(len(matrice_norm)):
            plt.plot(range(n_vars), matrice_norm[i, :], 'b-', alpha=0.1, linewidth=0.5)
        plt.xticks(range(n_vars), noms, rotation=45, ha='right')
        plt.xlabel('Variables', fontsize=12)
        plt.ylabel('Valeurs normalisées', fontsize=12)
        title = title or 'Coordonnées Parallèles'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_radar_chart(self, autres_variables, noms_variables=None, figsize=(8, 8), title=None):
        """Graphique 56: Diagramme radar"""
        toutes_vars = [self.data] + list(autres_variables)
        min_len = min(len(var) for var in toutes_vars)
        toutes_vars = [var[:min_len] for var in toutes_vars]
        n_vars = len(toutes_vars)
        moyennes = [np.mean(var) for var in toutes_vars]
        noms = (list(noms_variables) if noms_variables is not None and len(noms_variables) == n_vars
                else [f'Var{i+1}' for i in range(n_vars)])
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        moyennes_norm = scaler.fit_transform(np.array(moyennes).reshape(-1, 1)).flatten()
        angles = np.linspace(0, 2*np.pi, n_vars, endpoint=False).tolist()
        moyennes_norm = np.append(moyennes_norm, moyennes_norm[0])
        angles.append(angles[0])
        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection='polar'))
        ax.plot(angles, moyennes_norm, 'o-', linewidth=2, color='steelblue')
        ax.fill(angles, moyennes_norm, alpha=0.25, color='steelblue')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(noms)
        title = title or 'Diagramme Radar'
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.show()

    def graph_waterfall_plot(self, figsize=(12, 6), title=None):
        """Graphique 57: Waterfall plot (changement cumulatif)"""
        plt.figure(figsize=figsize)
        changes = np.diff(self.data)
        cumsum = np.cumsum(np.concatenate([[self.data[0]], changes]))
        bars = plt.bar(range(len(cumsum)), cumsum, width=0.8,
                       color='steelblue', alpha=0.7, edgecolor='black')
        for i, (bar, val) in enumerate(zip(bars, cumsum)):
            if i == 0:
                bar.set_color('green')
            elif val < cumsum[i-1]:
                bar.set_color('red')
            else:
                bar.set_color('green')
        plt.xlabel('Index', fontsize=12)
        plt.ylabel('Valeur cumulative', fontsize=12)
        title = title or f'Waterfall Plot (n={len(self.data)})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='y')
        plt.show()

    def graph_gantt_chart(self, start_times, durations, labels=None, figsize=(12, 6), title=None):
        """Graphique 58: Diagramme de Gantt"""
        plt.figure(figsize=figsize)
        for i, (start, duration) in enumerate(zip(start_times, durations)):
            plt.barh(i, duration, left=start, height=0.5,
                     color='steelblue', alpha=0.7, edgecolor='black')
            plt.text(start + duration/2, i, f'{duration:.1f}',
                     ha='center', va='center', fontsize=8)
        if labels:
            plt.yticks(range(len(labels)), labels)
        plt.xlabel('Temps', fontsize=12)
        plt.ylabel('Tâches', fontsize=12)
        title = title or 'Diagramme de Gantt'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        plt.show()

    def graph_sankey_diagram(self, categories, valeurs, figsize=(10, 8), title=None):
        """Graphique 59: Diagramme de Sankey """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        total = sum(valeurs)
        proportions = [v/total for v in valeurs]
        ax1.barh(categories, [total]*len(categories), color='lightblue', edgecolor='darkblue')
        ax1.set_title('Source', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Valeur totale')
        ax1.grid(True, alpha=0.3, axis='x')
        bars = ax2.barh(categories, valeurs, color='steelblue', edgecolor='darkblue')
        ax2.set_title('Distribution', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Valeurs')
        ax2.grid(True, alpha=0.3, axis='x')
        for i, (bar, val) in enumerate(zip(bars, valeurs)):
            ax2.text(bar.get_width() + total*0.02, bar.get_y() + bar.get_height()/2,
                     f'{val}', va='center', fontweight='bold')
        plt.suptitle(title or 'Diagramme de Sankey (version simplifiée)',
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_treemap(self, categories, valeurs, figsize=(10, 8), title=None):
        """Graphique 60: Treemap avec matplotlib """
        fig, ax = plt.subplots(figsize=figsize)
        sorted_indices = np.argsort(valeurs)[::-1]
        sorted_categories = [categories[i] for i in sorted_indices]
        sorted_valeurs = [valeurs[i] for i in sorted_indices]
        total = sum(valeurs)
        proportions = [v/total for v in sorted_valeurs]
        n = len(sorted_categories)
        cols = int(np.ceil(np.sqrt(n)))
        rows = int(np.ceil(n/cols))
        cell_width = 1.0 / cols
        cell_height = 1.0 / rows
        colors = plt.cm.viridis(np.linspace(0, 1, n))
        for idx, (cat, val, prop, color) in enumerate(
                zip(sorted_categories, sorted_valeurs, proportions, colors)):
            row = idx // cols
            col = idx % cols
            x = col * cell_width
            y = 1 - (row + 1) * cell_height
            width = cell_width * (0.5 + prop)
            height = cell_height
            x_center = x + (cell_width - width) / 2
            y_center = y + (cell_height - height) / 2
            rect = plt.Rectangle((x_center, y_center), width, height,
                                  facecolor=color, edgecolor='white', linewidth=2, alpha=0.8)
            ax.add_patch(rect)
            fontsize = max(6, min(12, int(width * 20)))
            ax.text(x_center + width/2, y_center + height/2, f'{cat}\n{val}',
                    ha='center', va='center', fontsize=fontsize, fontweight='bold',
                    color='white' if prop > 0.05 else 'black')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        ax.axis('off')
        plt.title(title or 'Treemap', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.show()

    def graph_sunburst(self, categories, valeurs, figsize=(10, 8), title=None):
        """Graphique 61: Sunburst chart avec matplotlib seulement"""
        fig, ax = plt.subplots(figsize=figsize)
        total = sum(valeurs)
        proportions = [v/total for v in valeurs]
        angles = [0]
        for prop in proportions:
            angles.append(angles[-1] + prop * 2 * np.pi)
        colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))
        radius_levels = [0.3, 0.6, 0.9]
        for level, radius in enumerate(radius_levels):
            if level == 0:
                for i, (start, end) in enumerate(zip(angles[:-1], angles[1:])):
                    theta = np.linspace(start, end, 50)
                    r = np.ones_like(theta) * radius
                    ax.fill_between(theta, 0, r, color=colors[i], alpha=0.9 - level*0.2)
                    if proportions[i] > 0.05:
                        mid_angle = (start + end) / 2
                        text_radius = radius / 2
                        x_text = text_radius * np.cos(mid_angle)
                        y_text = text_radius * np.sin(mid_angle)
                        ax.text(x_text, y_text, f'{categories[i][:10]}\n{valeurs[i]}',
                                ha='center', va='center', fontsize=8, fontweight='bold')
        for radius in radius_levels:
            theta = np.linspace(0, 2*np.pi, 100)
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            ax.plot(x, y, 'gray', linewidth=0.5, alpha=0.5)
        ax.set_aspect('equal')
        ax.axis('off')
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor=colors[i], alpha=0.7,
                           label=f'{cat}: {val} ({prop*100:.1f}%)')
            for i, (cat, val, prop) in enumerate(zip(categories, valeurs, proportions))
        ]
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5),
                  fontsize=8, title='Catégories')
        plt.title(title or 'Sunburst Chart', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.show()

    # GRAPHIQUES DE COMPARAISON 

    def graph_multiple_histograms(self, autres_donnees, autres_noms=None, bins=30,
                                  figsize=(12, 8), title=None):
        """Graphique 62: Histogrammes multiples"""
        toutes_donnees = [self.data] + list(autres_donnees)
        tous_noms = self._construire_noms(autres_noms, len(toutes_donnees))
        n = len(toutes_donnees)
        n_cols = min(3, n)
        n_rows = (n + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        if n_rows * n_cols == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        for i, (data, nom) in enumerate(zip(toutes_donnees, tous_noms)):
            axes[i].hist(data, bins=bins, density=True, alpha=0.7,
                         color='steelblue', edgecolor='black')
            axes[i].set_xlabel('Valeurs', fontsize=9)
            axes[i].set_ylabel('Densité', fontsize=9)
            axes[i].set_title(f'{nom} (n={len(data)})', fontsize=10)
            axes[i].grid(True, alpha=0.3)
        for i in range(len(toutes_donnees), len(axes)):
            axes[i].axis('off')
        title = title or 'Comparaison d\'Histogrammes'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_multiple_boxplots(self, autres_donnees, autres_noms=None,
                                figsize=(10, 6), title=None):
        """Graphique 63: Boxplots multiples"""
        toutes_donnees = [self.data] + list(autres_donnees)
        tous_noms = self._construire_noms(autres_noms, len(toutes_donnees))
        plt.figure(figsize=figsize)
        bp = plt.boxplot(toutes_donnees, labels=tous_noms, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('steelblue')
            patch.set_alpha(0.7)
        plt.ylabel('Valeurs', fontsize=12)
        title = title or 'Comparaison de Boxplots'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_multiple_violins(self, autres_donnees, autres_noms=None,
                               figsize=(10, 6), title=None):
        """Graphique 64: Violins multiples"""
        toutes_donnees = [self.data] + list(autres_donnees)
        tous_noms = self._construire_noms(autres_noms, len(toutes_donnees))
        plt.figure(figsize=figsize)
        positions = range(1, len(toutes_donnees)+1)
        parts = plt.violinplot(toutes_donnees, positions=positions,
                               showmeans=True, showmedians=True)
        for pc in parts['bodies']:
            pc.set_facecolor('steelblue')
            pc.set_alpha(0.7)
        plt.xticks(positions, tous_noms)
        plt.ylabel('Valeurs', fontsize=12)
        title = title or 'Comparaison de Violin Plots'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_overlay_densities(self, autres_donnees, autres_noms=None,
                                figsize=(10, 6), title=None):
        """Graphique 65: Densités superposées"""
        plt.figure(figsize=figsize)
        toutes_donnees = [self.data] + list(autres_donnees)
        tous_noms = self._construire_noms(autres_noms, len(toutes_donnees))
        couleurs = ['steelblue', 'orange', 'green', 'red', 'purple', 'brown']
        x_range = np.linspace(min(np.concatenate(toutes_donnees)),
                              max(np.concatenate(toutes_donnees)), 200)
        for i, (data, nom, couleur) in enumerate(zip(toutes_donnees, tous_noms, couleurs)):
            if len(data) > 1:
                kde = gaussian_kde(data)
                plt.plot(x_range, kde(x_range), linewidth=2, color=couleur, label=nom)
        plt.xlabel('Valeurs', fontsize=12)
        plt.ylabel('Densité', fontsize=12)
        title = title or 'Superposition des Densités'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_multi_qqplot(self, autres_donnees, autres_noms=None, figsize=(12, 8), title=None):
        """Graphique 66: QQ-plots multiples"""
        toutes_donnees = [self.data] + list(autres_donnees)
        tous_noms = self._construire_noms(autres_noms, len(toutes_donnees))
        n = len(toutes_donnees)
        n_cols = min(3, n)
        n_rows = (n + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        if n_rows * n_cols == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        for i, (data, nom) in enumerate(zip(toutes_donnees, tous_noms)):
            scipy_stats.probplot(data, dist="norm", plot=axes[i])
            axes[i].set_title(f'{nom} (n={len(data)})', fontsize=10)
            axes[i].grid(True, alpha=0.3)
        for i in range(len(toutes_donnees), len(axes)):
            axes[i].axis('off')
        title = title or 'Comparaison de QQ-plots'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_comparison_grid(self, autres_donnees, autres_noms=None,
                              figsize=(14, 10), title=None):
        """Graphique 67: Grille de comparaison (histogramme + boxplot + densité + qqplot)"""
        toutes_donnees = [self.data] + list(autres_donnees)
        tous_noms = self._construire_noms(autres_noms, len(toutes_donnees))
        n = len(toutes_donnees)
        fig, axes = plt.subplots(n, 4, figsize=figsize)
        if n == 1:
            axes = axes.reshape(1, -1)
        for i, (data, nom) in enumerate(zip(toutes_donnees, tous_noms)):
            axes[i, 0].hist(data, bins=30, density=True, alpha=0.7,
                            color='steelblue', edgecolor='black')
            axes[i, 0].set_ylabel(nom, fontsize=9)
            axes[i, 0].grid(True, alpha=0.3)
            if i == n-1:
                axes[i, 0].set_xlabel('Valeurs')
            axes[i, 1].boxplot(data, vert=True)
            axes[i, 1].grid(True, alpha=0.3)
            if i == n-1:
                axes[i, 1].set_xlabel('Boxplot')
            if len(data) > 1:
                kde = gaussian_kde(data)
                x_range = np.linspace(min(data), max(data), 200)
                axes[i, 2].plot(x_range, kde(x_range), 'b-', linewidth=1.5)
            axes[i, 2].grid(True, alpha=0.3)
            if i == n-1:
                axes[i, 2].set_xlabel('Densité')
            scipy_stats.probplot(data, dist="norm", plot=axes[i, 3])
            axes[i, 3].grid(True, alpha=0.3)
            if i == n-1:
                axes[i, 3].set_xlabel('QQ-plot')
        axes[0, 0].set_title('Histogramme', fontsize=10)
        axes[0, 1].set_title('Boxplot', fontsize=10)
        axes[0, 2].set_title('Densité KDE', fontsize=10)
        axes[0, 3].set_title('QQ-plot', fontsize=10)
        title = title or 'Grille de Comparaison des Distributions'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_facet_grid(self, categories, figsize=(12, 8), title=None):
        """Graphique 68: Facet grid (sous-groupes)"""
        unique_cats = np.unique(categories)
        n = len(unique_cats)
        n_cols = min(3, n)
        n_rows = (n + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        if n_rows * n_cols == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        for i, cat in enumerate(unique_cats):
            data_cat = self.data[categories == cat]
            if len(data_cat) > 0:
                axes[i].hist(data_cat, bins=20, density=True, alpha=0.7,
                             color='steelblue', edgecolor='black')
                axes[i].set_title(f'Catégorie {cat} (n={len(data_cat)})', fontsize=10)
                axes[i].set_xlabel('Valeurs', fontsize=8)
                axes[i].set_ylabel('Densité', fontsize=8)
                axes[i].grid(True, alpha=0.3)
        for i in range(n, len(axes)):
            axes[i].axis('off')
        title = title or 'Facet Grid par Catégorie'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_small_multiple(self, autres_donnees, autres_noms=None, figsize=(12, 8), title=None):
        """Graphique 69: Small multiples (mini graphiques)"""
        toutes_donnees = [self.data] + list(autres_donnees)
        tous_noms = self._construire_noms(autres_noms, len(toutes_donnees))
        n = len(toutes_donnees)
        n_cols = min(4, n)
        n_rows = (n + n_cols - 1) // n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        if n_rows * n_cols == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        for i, (data, nom) in enumerate(zip(toutes_donnees, tous_noms)):
            axes[i].plot(data, 'b-', linewidth=0.8, alpha=0.7)
            axes[i].set_title(nom, fontsize=9)
            axes[i].set_xticks([])
            axes[i].grid(True, alpha=0.3)
        for i in range(n, len(axes)):
            axes[i].axis('off')
        title = title or 'Small Multiples'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    #  GRAPHIQUES STATISTIQUES SPÉCIFIQUES 

    def graph_bland_altman(self, y, figsize=(10, 6), title=None):
        """Graphique 70: Bland-Altman plot"""
        n = min(len(self.data), len(y))
        x_plot = self.data[:n]
        y_plot = np.array(y[:n])
        mean = (x_plot + y_plot) / 2
        diff = x_plot - y_plot
        mean_diff = np.mean(diff)
        std_diff = np.std(diff)
        plt.figure(figsize=figsize)
        plt.scatter(mean, diff, alpha=0.6, c='steelblue')
        plt.axhline(y=mean_diff, color='red', linestyle='-', linewidth=2,
                    label=f'Biais: {mean_diff:.3f}')
        plt.axhline(y=mean_diff + 1.96*std_diff, color='gray', linestyle='--',
                    label='Limite supérieure (+1.96σ)')
        plt.axhline(y=mean_diff - 1.96*std_diff, color='gray', linestyle='--',
                    label='Limite inférieure (-1.96σ)')
        plt.xlabel('Moyenne des deux mesures', fontsize=12)
        plt.ylabel('Différence (X - Y)', fontsize=12)
        title = title or 'Bland-Altman Plot'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_forest_plot(self, effets, bornes_inf, bornes_sup, labels=None,
                          figsize=(10, 8), title=None):
        """Graphique 71: Forest plot"""
        # CORRECTION BUG B: convertir en np.array pour les opérations arithmétiques
        effets_arr     = np.array(effets,     dtype=float)
        bornes_inf_arr = np.array(bornes_inf, dtype=float)
        bornes_sup_arr = np.array(bornes_sup, dtype=float)
        plt.figure(figsize=figsize)
        y_pos = range(len(effets_arr))
        if labels is None:
            labels = [f'Étude {i+1}' for i in range(len(effets_arr))]
        plt.errorbar(effets_arr, y_pos,
                     xerr=[effets_arr - bornes_inf_arr, bornes_sup_arr - effets_arr],
                     fmt='o', color='steelblue', capsize=5, capthick=2, markersize=8)
        plt.axvline(x=0, color='red', linestyle='--', linewidth=1.5)
        plt.yticks(y_pos, labels)
        plt.xlabel('Effet (intervalle de confiance)', fontsize=12)
        title = title or 'Forest Plot (Méta-analyse)'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        plt.show()

    def graph_funnel_plot(self, effets, erreurs_standards, figsize=(10, 6), title=None):
        """Graphique 72: Funnel plot"""
        effets_arr = np.array(effets, dtype=float)
        erreurs_arr = np.array(erreurs_standards, dtype=float)
        plt.figure(figsize=figsize)
        plt.scatter(effets_arr, 1/erreurs_arr, alpha=0.6, c='steelblue')
        effet_moyen = np.mean(effets_arr)
        plt.axvline(x=effet_moyen, color='red', linestyle='--', linewidth=1.5,
                    label=f'Effet moyen = {effet_moyen:.3f}')
        plt.xlabel('Effet', fontsize=12)
        plt.ylabel('Précision (1 / Erreur standard)', fontsize=12)
        title = title or 'Funnel Plot (Détection de biais de publication)'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_raincloud_plot(self, autres_donnees=None, autres_noms=None,
                             figsize=(12, 6), title=None):
        """Graphique 73: Raincloud plot (boxplot + violon + points)"""
        toutes_donnees = [self.data]
        if autres_donnees is not None:
            toutes_donnees.extend(autres_donnees)
        tous_noms = self._construire_noms(autres_noms, len(toutes_donnees))
        fig, axes = plt.subplots(1, len(toutes_donnees), figsize=figsize)
        if len(toutes_donnees) == 1:
            axes = [axes]
        for i, (data, nom) in enumerate(zip(toutes_donnees, tous_noms)):
            parts = axes[i].violinplot(data, positions=[0],
                                       showmeans=False, showmedians=False)
            for pc in parts['bodies']:
                pc.set_facecolor('lightblue')
                pc.set_alpha(0.5)
            axes[i].boxplot(data, positions=[0], widths=0.3, patch_artist=True,
                            boxprops=dict(facecolor='white', alpha=0.7))
            y_jitter = np.random.normal(0, 0.04, len(data))
            axes[i].scatter(data, y_jitter, alpha=0.3, s=5, c='steelblue')
            axes[i].set_title(nom, fontsize=10)
            axes[i].set_xticks([0])
            axes[i].set_xticklabels([nom])
            axes[i].grid(True, alpha=0.3)
        title = title or 'Raincloud Plot'
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

    def graph_qqline_plot(self, figsize=(8, 8), title=None):
        """Graphique 74: QQ-plot avec ligne de régression"""
        plt.figure(figsize=figsize)
        data_sorted = np.sort(self.data)
        n = len(data_sorted)
        quantiles_theoriques = norm.ppf((np.arange(1, n+1) - 0.5) / n)
        plt.scatter(quantiles_theoriques, data_sorted, alpha=0.6, s=30, c='steelblue')
        z = np.polyfit(quantiles_theoriques, data_sorted, 1)
        p = np.poly1d(z)
        x_range = np.linspace(min(quantiles_theoriques), max(quantiles_theoriques), 100)
        plt.plot(x_range, p(x_range), 'r-', linewidth=2,
                 label=f'Régression: y = {z[0]:.2f}x + {z[1]:.2f}')
        plt.xlabel('Quantiles théoriques (Normale)', fontsize=12)
        plt.ylabel('Quantiles empiriques', fontsize=12)
        title = title or 'QQ-plot avec Ligne de Régression'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_lebailly_plot(self, figsize=(10, 6), title=None):
        """Graphique 75: Lebailly plot (log-normal plot)"""
        data_pos = self.data[self.data > 0]
        if len(data_pos) < len(self.data):
            print("Attention: des valeurs <= 0 ont été ignorées")
        log_data = np.log(data_pos)
        plt.figure(figsize=figsize)
        plt.hist(log_data, bins=30, density=True, alpha=0.7,
                 color='steelblue', edgecolor='black', label='Log-données')
        x_range = np.linspace(min(log_data), max(log_data), 200)
        plt.plot(x_range, norm.pdf(x_range, loc=np.mean(log_data), scale=np.std(log_data)),
                 'r-', linewidth=2, label='Normale ajustée')
        plt.xlabel('Log(Valeurs)', fontsize=12)
        plt.ylabel('Densité', fontsize=12)
        title = title or 'Lebailly Plot (Test de log-normalité)'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_cdf_confidence(self, confidence=0.95, figsize=(10, 6), title=None):
        """Graphique 76: CDF avec intervalle de confiance (Dvoretzky-Kiefer-Wolfowitz)"""
        plt.figure(figsize=figsize)
        x_sorted = np.sort(self.data)
        n = len(x_sorted)
        y_ecdf = np.arange(1, n+1) / n
        epsilon = np.sqrt(np.log(2 / (1 - confidence)) / (2 * n))
        plt.step(x_sorted, y_ecdf, where='post', linewidth=2.5,
                 color='steelblue', label='ECDF')
        plt.fill_between(x_sorted,
                         np.maximum(0, y_ecdf - epsilon),
                         np.minimum(1, y_ecdf + epsilon),
                         alpha=0.2, color='gray', label=f'IC à {confidence*100:.0f}%')
        plt.xlabel('Valeurs', fontsize=12)
        plt.ylabel('F(x)', fontsize=12)
        plt.ylim(0, 1.05)
        title = title or f'ECDF avec Intervalle de Confiance (n={n})'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def graph_quantile_plot(self, quantiles=None, figsize=(10, 6), title=None):
        """Graphique 77: Quantile plot (Q-Q plot des quantiles)"""
        if quantiles is None:
            quantiles = [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
        plt.figure(figsize=figsize)
        quant_emp = [np.quantile(self.data, q) for q in quantiles]
        plt.plot(quantiles, quant_emp, 'o-', linewidth=2, markersize=8, color='steelblue')
        plt.fill_between(quantiles, quant_emp, alpha=0.2, color='steelblue')
        plt.xlabel('Quantile théorique', fontsize=12)
        plt.ylabel('Valeur empirique', fontsize=12)
        title = title or 'Quantile Plot'
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.show()


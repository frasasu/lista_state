import io
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif obligatoire (pas de display)
import matplotlib.pyplot as plt
import matplotlib.cm as cm



# ---------------------------------------------------------------------------
# Classe de visualisation (SVG via matplotlib)
# ---------------------------------------------------------------------------
def _norm_ppf(p: float) -> float:
    """Approximation de l'inverse de la CDF normale (Beasley-Springer-Moro)"""
    if p <= 0:
        return -8.0
    if p >= 1:
        return 8.0
    import math
    # Rational approximation (Abramowitz & Stegun 26.2.17)
    c = [2.515517, 0.802853, 0.010328]
    d = [1.432788, 0.189269, 0.001308]
    sign = 1.0 if p >= 0.5 else -1.0
    p2 = p if p >= 0.5 else 1.0 - p
    t = math.sqrt(-2.0 * math.log(1.0 - p2))
    num = c[0] + c[1] * t + c[2] * t * t
    den = 1.0 + d[0] * t + d[1] * t * t + d[2] * t * t * t
    return sign * (t - num / den)

class Visualizer:
    """Génère des graphiques SVG via matplotlib."""

    def _fig_to_svg(self, fig) -> str:
        buf = io.StringIO()
        fig.savefig(buf, format='svg', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    def _make_fig(self, figsize=(10, 6)):
        fig, ax = plt.subplots(figsize=figsize)
        return fig, ax

    # ------------------------------------------------------------------
    def histogram(self, data: list, bins: int = 10, title: str = "Histogramme",
                  x_label: str = "", y_label: str = "Fréquence",
                  color: str = "#4ECDC4", density: bool = False) -> str:
        data = [x for x in data if x is not None and isinstance(x, (int, float))]
        if not data:
            return ""
        fig, ax = self._make_fig()
        ax.hist(data, bins=bins, color=color, edgecolor='white', density=density)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def scatter(self, x: list, y: list, title: str = "Scatter",
                x_label: str = "", y_label: str = "",
                color: str = "#FF6B6B", size: int = 4, alpha: float = 1.0) -> str:
        fig, ax = self._make_fig()
        ax.scatter(x, y, c=color, s=size * 5, alpha=alpha, edgecolors='none')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def line_chart(self, x: list, y_data: dict, title: str = "Ligne",
                   x_label: str = "", y_label: str = "Valeurs",
                   colors=None, markers: bool = True) -> str:
        default_colors = ['#4ECDC4', '#FF6B6B', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        fig, ax = self._make_fig()
        for i, (label, values) in enumerate(y_data.items()):
            c = (colors[i] if colors and i < len(colors) else default_colors[i % len(default_colors)])
            marker = 'o' if markers else None
            ax.plot(x, values, label=label, color=c, marker=marker, markersize=4, linewidth=2)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        ax.grid(alpha=0.3)
        if len(y_data) > 1:
            ax.legend()
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def boxplot(self, data_dict: dict, title: str = "Boîte à moustaches",
                x_label: str = "", y_label: str = "Valeurs") -> str:
        labels = list(data_dict.keys())
        data_lists = [
            [v for v in vals if v is not None and isinstance(v, (int, float))]
            for vals in data_dict.values()
        ]
        data_lists = [d for d in data_lists if d]  # Enlever les listes vides
        if not data_lists:
            return ""
        fig, ax = self._make_fig()
        bp = ax.boxplot(data_lists, labels=labels[:len(data_lists)], patch_artist=True,
                        notch=False, vert=True)
        colors_bp = ['#4ECDC4', '#FF6B6B', '#45B7D1', '#96CEB4', '#FFEAA7']
        for patch, color in zip(bp['boxes'], colors_bp * len(data_lists)):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def bar_chart(self, categories: list, values: list, title: str = "Barres",
                  x_label: str = "", y_label: str = "",
                  colors=None, stacked: bool = False) -> str:
        default_colors = ['#4ECDC4', '#FF6B6B', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
        bar_colors = colors if colors else [default_colors[i % len(default_colors)] for i in range(len(categories))]
        fig, ax = self._make_fig()
        x_pos = range(len(categories))
        bars = ax.bar(x_pos, values, color=bar_colors, edgecolor='white', width=0.6)
        ax.set_xticks(list(x_pos))
        ax.set_xticklabels([str(c) for c in categories], rotation=45, ha='right')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        # Valeurs au-dessus des barres
        for bar, val in zip(bars, values):
            if val is not None:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        f'{val:.2f}' if isinstance(val, float) else str(val),
                        ha='center', va='bottom', fontsize=9)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def heatmap(self, matrix: list, row_labels: list, col_labels: list,
                title: str = "Heatmap", x_label: str = "", y_label: str = "",
                cmap: str = "viridis") -> str:
        if not matrix:
            return ""
        data_arr = np.array(matrix, dtype=float)
        fig, ax = self._make_fig(figsize=(max(6, len(col_labels)), max(5, len(row_labels))))
        im = ax.imshow(data_arr, cmap=cmap, aspect='auto', vmin=-1, vmax=1)
        fig.colorbar(im, ax=ax, shrink=0.8)
        ax.set_xticks(range(len(col_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha='right', fontsize=9)
        ax.set_yticks(range(len(row_labels)))
        ax.set_yticklabels(row_labels, fontsize=9)
        # Annotations dans chaque cellule
        for i in range(len(row_labels)):
            for j in range(len(col_labels)):
                val = data_arr[i, j]
                if not np.isnan(val):
                    text_color = 'white' if abs(val) > 0.6 else 'black'
                    ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                            fontsize=8, color=text_color)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def pie_chart(self, labels: list, values: list, title: str = "Camembert") -> str:
        # Filtrer les valeurs <= 0
        pairs = [(l, v) for l, v in zip(labels, values) if v is not None and v > 0]
        if not pairs:
            return ""
        labels_f, values_f = zip(*pairs)
        fig, ax = self._make_fig(figsize=(8, 6))
        colors_pie = plt.cm.Set3(np.linspace(0, 1, len(labels_f)))
        wedges, texts, autotexts = ax.pie(
            values_f, labels=labels_f, autopct='%1.1f%%',
            colors=colors_pie, startangle=90,
            pctdistance=0.85, wedgeprops=dict(width=0.6)
        )
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(9)
        ax.set_title(title, fontsize=14, fontweight='bold')
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def qq_plot(self, data: list, dist: str = "normal", title: str = "Q-Q Plot",
                x_label: str = "Quantiles théoriques", y_label: str = "Quantiles observés") -> str:
        data_arr = np.array(sorted([x for x in data if x is not None and isinstance(x, (int, float))]))
        n = len(data_arr)
        if n < 2:
            return ""
        # Quantiles théoriques (distribution normale)
        theoretical = np.array([
            _norm_ppf((i - 0.5) / n) for i in range(1, n + 1)
        ])
        fig, ax = self._make_fig()
        ax.scatter(theoretical, data_arr, color='#4ECDC4', s=20, alpha=0.7, label='Données')
        # Ligne de référence
        mn, mx = theoretical.min(), theoretical.max()
        ax.plot([mn, mx], [mn * data_arr.std() + data_arr.mean(),
                            mx * data_arr.std() + data_arr.mean()],
                color='#FF6B6B', linewidth=2, label='Ligne de référence')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def acf_plot(self, data: list, nlags: int = 20,
                 title: str = "Autocorrélation",
                 x_label: str = "Décalage", y_label: str = "Autocorrélation") -> str:
        data_arr = np.array([x for x in data if x is not None and isinstance(x, (int, float))], dtype=float)
        n = len(data_arr)
        if n < 2:
            return ""
        nlags = min(nlags, n - 1)
        mean = data_arr.mean()
        var = ((data_arr - mean) ** 2).sum()
        acf_vals = []
        for lag in range(nlags + 1):
            if var == 0:
                acf_vals.append(0.0)
            else:
                cov = ((data_arr[lag:] - mean) * (data_arr[:n - lag] - mean)).sum()
                acf_vals.append(cov / var)
        lags = list(range(nlags + 1))
        conf = 1.96 / math.sqrt(n)
        fig, ax = self._make_fig()
        ax.bar(lags, acf_vals, color='#4ECDC4', width=0.3)
        ax.axhline(conf, color='#FF6B6B', linestyle='--', linewidth=1, label=f'IC 95% (±{conf:.3f})')
        ax.axhline(-conf, color='#FF6B6B', linestyle='--', linewidth=1)
        ax.axhline(0, color='black', linewidth=0.8)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        return self._fig_to_svg(fig)
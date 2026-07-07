
from __future__ import annotations

import io
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend non interactif (pas de fenêtre)
import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style="whitegrid", palette="Set2", font_scale=1.0)
_PALETTE = sns.color_palette("Set2", 10).as_hex()


class Visualizer:
    """Génère des graphiques SVG via Seaborn/Matplotlib."""

    # ------------------------------------------------------------------
    def _fig_to_svg(self, fig) -> str:
        buf = io.StringIO()
        fig.savefig(buf, format="svg", bbox_inches="tight")
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
        clean = pd.to_numeric(pd.Series(data), errors="coerce").dropna()
        if clean.empty:
            return ""
        fig, ax = self._make_fig()
        sns.histplot(clean, bins=bins, color=color, stat="density" if density else "count",
                     kde=True, edgecolor="white", ax=ax)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def scatter(self, x: list, y: list, title: str = "Scatter",
                x_label: str = "", y_label: str = "",
                color: str = "#FF6B6B", size: int = 4, alpha: float = 1.0) -> str:
        df = pd.DataFrame({"x": pd.to_numeric(pd.Series(x), errors="coerce"),
                            "y": pd.to_numeric(pd.Series(y), errors="coerce")}).dropna()
        if df.empty:
            return ""
        fig, ax = self._make_fig()
        sns.regplot(data=df, x="x", y="y", ax=ax, color=color,
                    scatter_kws={"s": size * 5, "alpha": alpha, "edgecolor": "none"},
                    line_kws={"color": "#333333", "linewidth": 1.5}, ci=95)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def line_chart(self, x: list, y_data: dict, title: str = "Ligne",
                   x_label: str = "", y_label: str = "Valeurs",
                   colors=None, markers: bool = True) -> str:
        fig, ax = self._make_fig()
        for i, (label, values) in enumerate(y_data.items()):
            c = colors[i] if colors and i < len(colors) else _PALETTE[i % len(_PALETTE)]
            sns.lineplot(x=x, y=values, label=label, color=c,
                         marker="o" if markers else None, markersize=5, linewidth=2, ax=ax)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        if len(y_data) > 1:
            ax.legend()
        else:
            ax.legend_.remove() if ax.legend_ else None
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def boxplot(self, data_dict: dict, title: str = "Boîte à moustaches",
                x_label: str = "", y_label: str = "Valeurs") -> str:
        frames = []
        for label, values in data_dict.items():
            clean = pd.to_numeric(pd.Series(values), errors="coerce").dropna()
            if len(clean):
                frames.append(pd.DataFrame({"groupe": label, "valeur": clean}))
        if not frames:
            return ""
        long_df = pd.concat(frames, ignore_index=True)
        fig, ax = self._make_fig()
        n_groups = long_df["groupe"].nunique()
        sns.boxplot(data=long_df, x="groupe", y="valeur", hue="groupe",
                    palette=_PALETTE[:n_groups], legend=False, ax=ax)
        sns.stripplot(data=long_df, x="groupe", y="valeur", color="black",
                      alpha=0.3, size=3, ax=ax)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def bar_chart(self, categories: list, values: list, title: str = "Barres",
                  x_label: str = "", y_label: str = "",
                  colors=None, stacked: bool = False) -> str:
        df = pd.DataFrame({"categorie": [str(c) for c in categories], "valeur": values})
        fig, ax = self._make_fig()
        bar_colors = colors if colors else _PALETTE
        sns.barplot(data=df, x="categorie", y="valeur", hue="categorie",
                    palette=bar_colors, legend=False, edgecolor="white", ax=ax)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", fontsize=9, padding=2)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def heatmap(self, matrix: list, row_labels: list, col_labels: list,
                title: str = "Heatmap", x_label: str = "", y_label: str = "",
                cmap: str = "viridis") -> str:
        if not matrix:
            return ""
        df = pd.DataFrame(np.array(matrix, dtype=float), index=row_labels, columns=col_labels)
        fig, ax = self._make_fig(figsize=(max(6, len(col_labels)), max(5, len(row_labels))))
        sns.heatmap(df, annot=True, fmt=".2f", cmap=cmap, vmin=-1, vmax=1,
                    linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def pie_chart(self, labels: list, values: list, title: str = "Camembert") -> str:
        pairs = [(l, v) for l, v in zip(labels, values) if v is not None and v > 0]
        if not pairs:
            return ""
        labels_f, values_f = zip(*pairs)
        fig, ax = self._make_fig(figsize=(8, 6))
        colors_pie = sns.color_palette("Set3", len(labels_f))
        wedges, texts, autotexts = ax.pie(
            values_f, labels=labels_f, autopct="%1.1f%%",
            colors=colors_pie, startangle=90,
            pctdistance=0.85, wedgeprops=dict(width=0.6),
        )
        for t in texts:
            t.set_fontsize(10)
        for at in autotexts:
            at.set_fontsize(9)
        ax.set_title(title, fontsize=14, fontweight="bold")
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def qq_plot(self, data: list, dist: str = "normal", title: str = "Q-Q Plot",
                x_label: str = "Quantiles théoriques", y_label: str = "Quantiles observés") -> str:
        from scipy import stats as sps
        clean = pd.to_numeric(pd.Series(data), errors="coerce").dropna().to_numpy()
        if clean.size < 2:
            return ""
        dist_name = "norm" if dist in ("normal", "norm") else dist
        fig, ax = self._make_fig()
        sps.probplot(clean, dist=dist_name, plot=ax)
        ax.get_lines()[0].set(markerfacecolor="#4ECDC4", markeredgecolor="none", markersize=5)
        ax.get_lines()[1].set(color="#FF6B6B", linewidth=2)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    def acf_plot(self, data: list, nlags: int = 20,
                 title: str = "Autocorrélation",
                 x_label: str = "Décalage", y_label: str = "Autocorrélation") -> str:
        from statsmodels.graphics.tsaplots import plot_acf
        clean = pd.to_numeric(pd.Series(data), errors="coerce").dropna().to_numpy()
        if clean.size < 2:
            return ""
        nlags = min(nlags, clean.size - 1)
        fig, ax = self._make_fig()
        plot_acf(clean, lags=nlags, ax=ax, color="#4ECDC4",
                 vlines_kwargs={"colors": "#4ECDC4"})
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    # ------------------------------------------------------------------
    # Graphiques additionnels "Pro" (nouveaux, exploitables depuis VISUALIZE)
    # ------------------------------------------------------------------
    def violin_plot(self, data_dict: dict, title: str = "Distribution (violon)",
                     x_label: str = "", y_label: str = "Valeurs") -> str:
        frames = []
        for label, values in data_dict.items():
            clean = pd.to_numeric(pd.Series(values), errors="coerce").dropna()
            if len(clean):
                frames.append(pd.DataFrame({"groupe": label, "valeur": clean}))
        if not frames:
            return ""
        long_df = pd.concat(frames, ignore_index=True)
        fig, ax = self._make_fig()
        n_groups = long_df["groupe"].nunique()
        sns.violinplot(data=long_df, x="groupe", y="valeur", hue="groupe",
                       palette=_PALETTE[:n_groups], legend=False, ax=ax)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)
        fig.tight_layout()
        return self._fig_to_svg(fig)

    def pairplot_svg(self, df: pd.DataFrame, columns: Optional[Sequence[str]] = None,
                      hue: Optional[str] = None) -> str:
        cols = list(columns) if columns else list(df.select_dtypes(include=[np.number]).columns)
        grid = sns.pairplot(df, vars=cols, hue=hue, palette=_PALETTE, corner=True)
        buf = io.StringIO()
        grid.figure.savefig(buf, format="svg", bbox_inches="tight")
        plt.close(grid.figure)
        buf.seek(0)
        return buf.getvalue()

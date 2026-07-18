# visualizer.py
import math
import random
from typing import Dict, List, Any, Optional, Union, Tuple
from .simple_dataframe import SimpleDataFrame, to_numeric
from .stats_calculator import StatsCalculator


class Visualizer:
    """
    Générateur de visualisations sans dépendances externes.
    Produit des graphiques SVG et HTML de qualité professionnelle supérieure.
    """

    def __init__(self, width: int = 800, height: int = 600, bg_color: str = "white"):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.margin = {'top': 70, 'right': 90, 'bottom': 80, 'left': 90}
        self.plot_width = width - self.margin['left'] - self.margin['right']
        self.plot_height = height - self.margin['top'] - self.margin['bottom']
        self.calc = StatsCalculator()

        # ── Palettes perceptuellement uniformes ──────────────────────────────
        self.palettes = {
            # Reproduit la palette ggplot2 (hue wheel équidistant, chroma=100, L=65)
            'ggplot2': ['#F8766D', '#A3A500', '#00BF7D', '#00B0F6', '#E76BF3'],
            # ColorBrewer Set2 (daltonisme-safe)
            'set2':    ['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F'],
            # Viridis (perceptuellement uniforme)
            'viridis': ['#440154', '#31688E', '#35B779', '#FDE725', '#443983', '#21918C'],
            # Okabe-Ito (standard pour daltoniens)
            'okabe':   ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7'],
            # Pastel raffiné
            'pastel':  ['#AEC6CF', '#FFD1DC', '#B5EAD7', '#C7CEEA', '#FFDAC1', '#E2F0CB'],
            'default': ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B2', '#937860'],
        }

        # ── Token de design ──────────────────────────────────────────────────
        self.font_family = "'Helvetica Neue', Helvetica, Arial, sans-serif"
        self.color_title   = "#1A1A2E"
        self.color_axis    = "#444455"
        self.color_tick    = "#666677"
        self.color_grid    = "#E8E8F0"
        self.color_bg_plot = "#FAFAFA"   # fond léger du plot area
        self.stroke_axis   = 1.5
        self.stroke_grid   = 0.8

    # ════════════════════════════════════════════════════════════════════════
    #  UTILITAIRES INTERNES
    # ════════════════════════════════════════════════════════════════════════

    def _scale_x(self, x: float, min_x: float, max_x: float) -> float:
        if max_x - min_x == 0:
            return self.margin['left'] + self.plot_width / 2
        return self.margin['left'] + (x - min_x) / (max_x - min_x) * self.plot_width

    def _scale_y(self, y: float, min_y: float, max_y: float) -> float:
        if max_y - min_y == 0:
            return self.margin['top'] + self.plot_height / 2
        return self.margin['top'] + self.plot_height - (y - min_y) / (max_y - min_y) * self.plot_height

    def _get_numeric_data(self, data: List[Any]) -> List[float]:
        return [to_numeric(x) for x in data if x is not None and isinstance(to_numeric(x), (int, float))]

    def _get_colors(self, n: int, palette: str = 'ggplot2') -> List[str]:
        colors = self.palettes.get(palette, self.palettes['ggplot2'])
        return [colors[i % len(colors)] for i in range(n)]

    def _fmt_num(self, val: float, decimals: int = 1) -> str:
        """Formatte un nombre avec suffixe k/M proprement."""
        if abs(val) >= 1e9:
            return f"{val/1e9:.1f}B"
        if abs(val) >= 1e6:
            return f"{val/1e6:.1f}M"
        if abs(val) >= 1e3:
            return f"{val/1e3:.0f}k"
        # Évite les labels comme "0.0" → "0"
        if val == int(val) and decimals == 1:
            return str(int(val))
        return f"{val:.{decimals}f}"

    def _nice_ticks(self, min_val: float, max_val: float, n: int = 5) -> List[float]:
        """Algorithme "nice ticks" inspiré de Wilkinson (d3-scale)."""
        if max_val == min_val:
            return [min_val]
        raw_step = (max_val - min_val) / n
        mag = 10 ** math.floor(math.log10(abs(raw_step)) if raw_step != 0 else 0)
        nice_steps = [1, 2, 2.5, 5, 10]
        step = min(nice_steps, key=lambda s: abs(s * mag - raw_step)) * mag
        start = math.floor(min_val / step) * step
        ticks = []
        t = start
        while t <= max_val + step * 0.01:
            if min_val - step * 0.01 <= t <= max_val + step * 0.01:
                ticks.append(round(t, 10))
            t = round(t + step, 10)
        return ticks

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convertit #RRGGBB en (r, g, b)."""
        h = hex_color.lstrip('#')
        if len(h) == 3:
            h = ''.join(c*2 for c in h)
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def _lighten(self, hex_color: str, factor: float = 0.4) -> str:
        """Éclaircit une couleur hex."""
        r, g, b = self._hex_to_rgb(hex_color)
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        return f'#{r:02X}{g:02X}{b:02X}'

    def _darken(self, hex_color: str, factor: float = 0.25) -> str:
        """Assombrit une couleur hex."""
        r, g, b = self._hex_to_rgb(hex_color)
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f'#{r:02X}{g:02X}{b:02X}'

    # ════════════════════════════════════════════════════════════════════════
    #  EN-TÊTE SVG ET AXES
    # ════════════════════════════════════════════════════════════════════════

    def _generate_svg_header(self, title: str = "", subtitle: str = "") -> List[str]:
        """En-tête SVG avec filtre drop-shadow, fond plot area, titres typographiés."""
        uid = f"clip{abs(hash(title)) % 100000}"
        svg = [
            f'<svg width="{self.width}" height="{self.height}" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink">',
            # ── Définitions (filtre ombre, clip) ────────────────────────────
            '<defs>',
            '  <filter id="shadow" x="-5%" y="-5%" width="115%" height="115%">',
            '    <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="rgba(0,0,0,0.10)"/>',
            '  </filter>',
            f'  <clipPath id="{uid}">',
            f'    <rect x="{self.margin["left"]}" y="{self.margin["top"]}" '
            f'width="{self.plot_width}" height="{self.plot_height}"/>',
            f'  </clipPath>',
            '</defs>',
            # ── Fond global ──────────────────────────────────────────────────
            f'<rect width="{self.width}" height="{self.height}" '
            f'fill="{self.bg_color}" rx="8"/>',
            # ── Fond de la zone de tracé ──────────────────────────────────────
            f'<rect x="{self.margin["left"]}" y="{self.margin["top"]}" '
            f'width="{self.plot_width}" height="{self.plot_height}" '
            f'fill="{self.color_bg_plot}" rx="3" filter="url(#shadow)"/>',
        ]

        # Titre principal
        if title:
            y_title = 28 if not subtitle else 24
            svg.append(
                f'<text x="{self.margin["left"]}" y="{y_title}" '
                f'font-family="{self.font_family}" font-size="16" font-weight="700" '
                f'fill="{self.color_title}" letter-spacing="-0.3">{title}</text>'
            )
        # Sous-titre
        if subtitle:
            svg.append(
                f'<text x="{self.margin["left"]}" y="46" '
                f'font-family="{self.font_family}" font-size="11" '
                f'fill="#888899" letter-spacing="0">{subtitle}</text>'
            )
        return svg

    def _generate_axes(self, x_label: str = "", y_label: str = "",
                       x_ticks: List[Tuple[float, str]] = None,
                       y_ticks: List[Tuple[float, str]] = None,
                       grid: bool = True) -> List[str]:
        """Axes avec grille fine, ticks propres, étiquettes bien positionnées."""
        svg = []
        bot = self.height - self.margin['bottom']
        left = self.margin['left']
        right = self.width - self.margin['right']
        top = self.margin['top']

        # ── Grille horizontale (Y) ───────────────────────────────────────────
        if grid and y_ticks:
            for y_pos, _ in y_ticks:
                svg.append(
                    f'<line x1="{left}" y1="{y_pos}" x2="{right}" y2="{y_pos}" '
                    f'stroke="{self.color_grid}" stroke-width="{self.stroke_grid}" />'
                )

        # ── Grille verticale (X) ─────────────────────────────────────────────
        if grid and x_ticks:
            for x_pos, _ in x_ticks:
                svg.append(
                    f'<line x1="{x_pos}" y1="{top}" x2="{x_pos}" y2="{bot}" '
                    f'stroke="{self.color_grid}" stroke-width="{self.stroke_grid}" />'
                )

        # ── Axe Y ───────────────────────────────────────────────────────────
        svg.append(
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bot}" '
            f'stroke="{self.color_axis}" stroke-width="{self.stroke_axis}" '
            f'stroke-linecap="square"/>'
        )
        # ── Axe X ───────────────────────────────────────────────────────────
        svg.append(
            f'<line x1="{left}" y1="{bot}" x2="{right}" y2="{bot}" '
            f'stroke="{self.color_axis}" stroke-width="{self.stroke_axis}" '
            f'stroke-linecap="square"/>'
        )

        # ── Label axe X ─────────────────────────────────────────────────────
        if x_label:
            svg.append(
                f'<text x="{left + self.plot_width/2}" y="{self.height - 10}" '
                f'text-anchor="middle" font-family="{self.font_family}" '
                f'font-size="12" font-weight="500" fill="{self.color_axis}">{x_label}</text>'
            )
        # ── Label axe Y ─────────────────────────────────────────────────────
        if y_label:
            mid_y = top + self.plot_height / 2
            svg.append(
                f'<text x="14" y="{mid_y}" text-anchor="middle" '
                f'font-family="{self.font_family}" font-size="12" font-weight="500" '
                f'fill="{self.color_axis}" '
                f'transform="rotate(-90 14 {mid_y})">{y_label}</text>'
            )

        # ── Ticks X ─────────────────────────────────────────────────────────
        if x_ticks:
            for x_pos, label in x_ticks:
                svg.extend([
                    f'<line x1="{x_pos}" y1="{bot}" x2="{x_pos}" y2="{bot+5}" '
                    f'stroke="{self.color_axis}" stroke-width="1"/>',
                    f'<text x="{x_pos}" y="{bot+18}" text-anchor="middle" '
                    f'font-family="{self.font_family}" font-size="10" '
                    f'fill="{self.color_tick}">{label}</text>'
                ])

        # ── Ticks Y ─────────────────────────────────────────────────────────
        if y_ticks:
            for y_pos, label in y_ticks:
                svg.extend([
                    f'<line x1="{left-5}" y1="{y_pos}" x2="{left}" y2="{y_pos}" '
                    f'stroke="{self.color_axis}" stroke-width="1"/>',
                    f'<text x="{left-8}" y="{y_pos+4}" text-anchor="end" '
                    f'font-family="{self.font_family}" font-size="10" '
                    f'fill="{self.color_tick}">{label}</text>'
                ])

        return svg

    def _add_legend(self, items: List[Tuple[str, str]], x: int = None, y: int = None) -> List[str]:
        """Légende élégante avec fond semi-transparent et bords arrondis."""
        if not items:
            return []
        svg = []
        lx = x or (self.width - self.margin['right'] + 8)
        ly = y or (self.margin['top'] + 10)
        box_h = 12
        line_h = 20
        padding = 8
        max_label = max(len(lbl) for lbl, _ in items)
        legend_w = max_label * 6.5 + 30

        # Fond
        svg.append(
            f'<rect x="{lx-padding}" y="{ly-padding}" '
            f'width="{legend_w}" height="{len(items)*line_h + padding*2}" '
            f'fill="rgba(255,255,255,0.92)" stroke="#DDDDEE" stroke-width="1" rx="5" '
            f'filter="url(#shadow)"/>'
        )
        for i, (label, color) in enumerate(items):
            yp = ly + i * line_h
            # Cercle de couleur (plus moderne que le carré)
            svg.append(
                f'<circle cx="{lx+6}" cy="{yp+6}" r="6" fill="{color}" />'
            )
            svg.append(
                f'<text x="{lx+18}" y="{yp+11}" '
                f'font-family="{self.font_family}" font-size="10" '
                f'fill="{self.color_axis}">{label}</text>'
            )
        return svg

    # ════════════════════════════════════════════════════════════════════════
    #  HISTOGRAMME
    # ════════════════════════════════════════════════════════════════════════

    def histogram(self, data: List[Any], bins: int = 10,
                  title: str = "Histogramme", x_label: str = "Valeurs",
                  y_label: str = "Fréquence", color: str = "#4C72B0",
                  density: bool = False, rug: bool = False,
                  fill_alpha: float = 0.8) -> str:
        numeric_data = self._get_numeric_data(data)
        if not numeric_data:
            return self._empty_chart("Aucune donnée numérique")

        n = len(numeric_data)
        min_val = min(numeric_data)
        max_val = max(numeric_data)

        # Règle de Sturges si bins trop petit
        bins = max(bins, int(math.ceil(math.log2(n) + 1)))
        bins = min(bins, 60)

        bin_width = (max_val - min_val) / bins if max_val > min_val else 1
        counts = [0] * bins
        for val in numeric_data:
            idx = min(int((val - min_val) / bin_width), bins - 1)
            counts[idx] += 1

        max_count = max(counts)
        total = n

        # Calcul de la courbe de densité normale (KDE gaussienne simple)
        mean_val = sum(numeric_data) / n
        std_val = math.sqrt(sum((x - mean_val)**2 for x in numeric_data) / n) or 1

        # Axe Y : nice ticks
        y_max = max_count * 1.05
        y_ticks_vals = self._nice_ticks(0, y_max, 5)
        y_ticks = [
            (self._scale_y(v, 0, y_max), self._fmt_num(v, 0))
            for v in y_ticks_vals
        ]

        # Axe X : nice ticks
        x_ticks_vals = self._nice_ticks(min_val, max_val, 6)
        x_ticks = [
            (self._scale_x(v, min_val, max_val), self._fmt_num(v))
            for v in x_ticks_vals
            if min_val <= v <= max_val
        ]

        stroke_color = self._darken(color, 0.15)
        light_color  = self._lighten(color, 0.55)

        svg = self._generate_svg_header(title, f"n = {n:,}  ·  μ = {self._fmt_num(mean_val)}  ·  σ = {self._fmt_num(std_val)}")
        svg.extend(self._generate_axes(x_label, y_label, x_ticks, y_ticks, grid=True))

        # ── Barres ──────────────────────────────────────────────────────────
        bar_area_w = self.plot_width / bins
        inner_pad  = bar_area_w * 0.04   # léger espacement entre barres
        bar_w      = bar_area_w - inner_pad * 2

        for i, count in enumerate(counts):
            x = self.margin['left'] + i * bar_area_w + inner_pad
            bar_h = (count / y_max) * self.plot_height if y_max else 0
            y = self.margin['top'] + self.plot_height - bar_h

            # Gradient simulé : barre avec bord supérieur plus sombre
            svg.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" '
                f'fill="{color}" fill-opacity="{fill_alpha}" '
                f'stroke="{stroke_color}" stroke-width="0.8" rx="2"/>'
            )
            # Surbrillance haut de la barre
            if bar_h > 4:
                svg.append(
                    f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="3" '
                    f'fill="{light_color}" fill-opacity="0.5" rx="2"/>'
                )

        # ── Courbe KDE (densité) ─────────────────────────────────────────────
        kde_pts = []
        n_kde = 200
        bw = 1.06 * std_val * n**(-0.2)  # silverman rule
        for k in range(n_kde + 1):
            xv = min_val + k * (max_val - min_val) / n_kde
            kde = sum(
                math.exp(-0.5 * ((xv - xi) / bw)**2)
                for xi in numeric_data
            ) / (n * bw * math.sqrt(2 * math.pi))
            # Rescaler KDE en fréquence
            kde_count = kde * n * bin_width
            cx = self._scale_x(xv, min_val, max_val)
            cy = self._scale_y(kde_count, 0, y_max)
            kde_pts.append(f"{cx:.2f},{cy:.2f}")

        if len(kde_pts) > 1:
            svg.append(
                f'<polyline points="{" ".join(kde_pts)}" fill="none" '
                f'stroke="{stroke_color}" stroke-width="2.5" '
                f'stroke-linejoin="round" stroke-linecap="round" opacity="0.85"/>'
            )

        # ── Rug plot ──────────────────────────────────────────────────────────
        if rug:
            bot = self.margin['top'] + self.plot_height
            for val in numeric_data:
                xr = self._scale_x(val, min_val, max_val)
                svg.append(
                    f'<line x1="{xr:.2f}" y1="{bot}" x2="{xr:.2f}" y2="{bot+6}" '
                    f'stroke="{stroke_color}" stroke-width="0.8" opacity="0.6"/>'
                )

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  BOXPLOT
    # ════════════════════════════════════════════════════════════════════════

    def boxplot(self, data: Union[List[Any], Dict[str, List[Any]]],
                title: str = "Boîte à moustaches", x_label: str = "",
                y_label: str = "Valeurs", horizontal: bool = False,
                notch: bool = False, show_points: bool = True) -> str:

        if isinstance(data, dict):
            categories = list(data.keys())
            values_list = [self._get_numeric_data(data[cat]) for cat in categories]
        else:
            categories = ['Données']
            values_list = [self._get_numeric_data(data)]

        categories = [c for c, v in zip(categories, values_list) if v]
        values_list = [v for v in values_list if v]

        if not categories:
            return self._empty_chart("Aucune donnée valide")

        stats_list = []
        all_values = []
        for vals in values_list:
            sv = sorted(vals)
            q1 = self.calc.quantile(sv, 0.25)
            q2 = self.calc.median(sv)
            q3 = self.calc.quantile(sv, 0.75)
            iqr = q3 - q1
            lo_w = max(min(vals), q1 - 1.5 * iqr)
            hi_w = min(max(vals), q3 + 1.5 * iqr)
            outliers = [x for x in vals if x < lo_w or x > hi_w]
            mean_v = sum(vals) / len(vals)
            stats_list.append({
                'q1': q1, 'median': q2, 'q3': q3, 'mean': mean_v,
                'lo_w': lo_w, 'hi_w': hi_w, 'outliers': outliers,
                'n': len(vals),
                'notch_lo': q2 - 1.58*iqr/math.sqrt(len(vals)) if notch else None,
                'notch_hi': q2 + 1.58*iqr/math.sqrt(len(vals)) if notch else None,
            })
            all_values.extend(vals)

        if not all_values:
            return self._empty_chart("Aucune donnée numérique")

        # Échelle Y avec marge
        y_ticks_vals = self._nice_ticks(min(all_values), max(all_values), 5)
        ymin = y_ticks_vals[0]
        ymax = y_ticks_vals[-1]
        y_pad = (ymax - ymin) * 0.08
        ymin -= y_pad
        ymax += y_pad

        y_ticks = [
            (self._scale_y(v, ymin, ymax), self._fmt_num(v))
            for v in y_ticks_vals
        ]

        n_groups = len(categories)
        group_spacing = self.plot_width / n_groups
        box_w = group_spacing * 0.45

        colors = self._get_colors(n_groups, 'ggplot2')

        svg = self._generate_svg_header(title)
        svg.extend(self._generate_axes(x_label, y_label, y_ticks=y_ticks, grid=True))

        for i, (cat, stats, color) in enumerate(zip(categories, stats_list, colors)):
            xc = self.margin['left'] + (i + 0.5) * group_spacing
            light = self._lighten(color, 0.55)
            dark  = self._darken(color, 0.15)

            y_q1     = self._scale_y(stats['q1'],     ymin, ymax)
            y_q3     = self._scale_y(stats['q3'],     ymin, ymax)
            y_med    = self._scale_y(stats['median'], ymin, ymax)
            y_lo_w   = self._scale_y(stats['lo_w'],   ymin, ymax)
            y_hi_w   = self._scale_y(stats['hi_w'],   ymin, ymax)
            y_mean   = self._scale_y(stats['mean'],   ymin, ymax)

            # ── Moustaches ──────────────────────────────────────────────────
            # Basse
            svg.append(
                f'<line x1="{xc:.2f}" y1="{y_q1:.2f}" x2="{xc:.2f}" y2="{y_lo_w:.2f}" '
                f'stroke="{dark}" stroke-width="1.5" stroke-dasharray="4,2"/>'
            )
            svg.append(
                f'<line x1="{xc-box_w*0.22:.2f}" y1="{y_lo_w:.2f}" '
                f'x2="{xc+box_w*0.22:.2f}" y2="{y_lo_w:.2f}" '
                f'stroke="{dark}" stroke-width="2"/>'
            )
            # Haute
            svg.append(
                f'<line x1="{xc:.2f}" y1="{y_q3:.2f}" x2="{xc:.2f}" y2="{y_hi_w:.2f}" '
                f'stroke="{dark}" stroke-width="1.5" stroke-dasharray="4,2"/>'
            )
            svg.append(
                f'<line x1="{xc-box_w*0.22:.2f}" y1="{y_hi_w:.2f}" '
                f'x2="{xc+box_w*0.22:.2f}" y2="{y_hi_w:.2f}" '
                f'stroke="{dark}" stroke-width="2"/>'
            )

            # ── Boîte ────────────────────────────────────────────────────────
            box_height = y_q1 - y_q3
            if notch and stats['notch_lo'] and stats['notch_hi']:
                y_nl = self._scale_y(stats['notch_lo'], ymin, ymax)
                y_nh = self._scale_y(stats['notch_hi'], ymin, ymax)
                notch_in = box_w * 0.28
                path = (
                    f"M {xc-box_w/2:.2f},{y_q3:.2f} "
                    f"L {xc-box_w/2:.2f},{y_nh:.2f} "
                    f"L {xc-notch_in:.2f},{y_med:.2f} "
                    f"L {xc-box_w/2:.2f},{y_nl:.2f} "
                    f"L {xc-box_w/2:.2f},{y_q1:.2f} "
                    f"L {xc+box_w/2:.2f},{y_q1:.2f} "
                    f"L {xc+box_w/2:.2f},{y_nl:.2f} "
                    f"L {xc+notch_in:.2f},{y_med:.2f} "
                    f"L {xc+box_w/2:.2f},{y_nh:.2f} "
                    f"L {xc+box_w/2:.2f},{y_q3:.2f} Z"
                )
                svg.append(
                    f'<path d="{path}" fill="{light}" stroke="{dark}" stroke-width="1.5"/>'
                )
            else:
                svg.append(
                    f'<rect x="{xc-box_w/2:.2f}" y="{y_q3:.2f}" '
                    f'width="{box_w:.2f}" height="{box_height:.2f}" '
                    f'fill="{light}" stroke="{dark}" stroke-width="1.5" rx="3"/>'
                )

            # ── Ligne médiane ─────────────────────────────────────────────────
            svg.append(
                f'<line x1="{xc-box_w/2:.2f}" y1="{y_med:.2f}" '
                f'x2="{xc+box_w/2:.2f}" y2="{y_med:.2f}" '
                f'stroke="{dark}" stroke-width="3" stroke-linecap="round"/>'
            )

            # ── Moyenne (losange) ────────────────────────────────────────────
            d = 4
            svg.append(
                f'<polygon points="{xc:.2f},{y_mean-d:.2f} {xc+d:.2f},{y_mean:.2f} '
                f'{xc:.2f},{y_mean+d:.2f} {xc-d:.2f},{y_mean:.2f}" '
                f'fill="white" stroke="{dark}" stroke-width="1.5"/>'
            )

            # ── Outliers ─────────────────────────────────────────────────────
            if show_points:
                for out in stats['outliers']:
                    yo = self._scale_y(out, ymin, ymax)
                    svg.append(
                        f'<circle cx="{xc:.2f}" cy="{yo:.2f}" r="3.5" '
                        f'fill="{color}" fill-opacity="0.6" stroke="white" stroke-width="1"/>'
                    )

            # ── Label catégorie ──────────────────────────────────────────────
            bot = self.margin['top'] + self.plot_height
            svg.append(
                f'<text x="{xc:.2f}" y="{bot+22}" text-anchor="middle" '
                f'font-family="{self.font_family}" font-size="11" '
                f'fill="{self.color_axis}">{cat}</text>'
            )
            # n sous le label
            svg.append(
                f'<text x="{xc:.2f}" y="{bot+36}" text-anchor="middle" '
                f'font-family="{self.font_family}" font-size="9" '
                f'fill="#AAAAAA">n={stats["n"]}</text>'
            )

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  SCATTER PLOT
    # ════════════════════════════════════════════════════════════════════════

    def scatter(self, x_data: List[Any], y_data: List[Any],
                title: str = "Nuage de points", x_label: str = "X",
                y_label: str = "Y", color: str = "#4C72B0",
                size: float = 4, alpha: float = 0.7,
                trend: bool = False, marginal: bool = False) -> str:

        if len(x_data) != len(y_data):
            return self._empty_chart("Les séries X et Y doivent avoir la même longueur")

        pairs = [
            (to_numeric(x), to_numeric(y)) for x, y in zip(x_data, y_data)
            if x is not None and y is not None
            and isinstance(to_numeric(x), (int, float))
            and isinstance(to_numeric(y), (int, float))
        ]

        if not pairs:
            return self._empty_chart("Aucune paire de données numériques")

        x_vals, y_vals = zip(*pairs)
        n = len(pairs)

        x_ticks_vals = self._nice_ticks(min(x_vals), max(x_vals), 5)
        y_ticks_vals = self._nice_ticks(min(y_vals), max(y_vals), 5)

        xmin, xmax = x_ticks_vals[0], x_ticks_vals[-1]
        ymin, ymax = y_ticks_vals[0], y_ticks_vals[-1]

        x_pad = (xmax - xmin) * 0.04
        y_pad = (ymax - ymin) * 0.04
        xmin -= x_pad; xmax += x_pad
        ymin -= y_pad; ymax += y_pad

        x_ticks = [(self._scale_x(v, xmin, xmax), self._fmt_num(v)) for v in x_ticks_vals]
        y_ticks = [(self._scale_y(v, ymin, ymax), self._fmt_num(v)) for v in y_ticks_vals]

        dark = self._darken(color, 0.2)

        # Régression linéaire
        r2 = None
        slope = intercept = None
        if trend and n > 1:
            sx = sum(x_vals); sy = sum(y_vals)
            sxy = sum(x*y for x,y in pairs)
            sxx = sum(x*x for x in x_vals)
            denom = n*sxx - sx*sx
            if denom != 0:
                slope = (n*sxy - sx*sy) / denom
                intercept = (sy - slope*sx) / n
                ymean = sy / n
                ss_tot = sum((y - ymean)**2 for y in y_vals)
                ss_res = sum((y - (slope*x + intercept))**2 for x,y in pairs)
                r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0

        corr = None
        if n > 1:
            mx = sum(x_vals)/n; my = sum(y_vals)/n
            num = sum((x-mx)*(y-my) for x,y in pairs)
            den = math.sqrt(sum((x-mx)**2 for x in x_vals) * sum((y-my)**2 for y in y_vals))
            corr = num/den if den else None

        subtitle = f"n = {n:,}"
        if corr is not None:
            subtitle += f"  ·  r = {corr:.3f}"

        svg = self._generate_svg_header(title, subtitle)
        svg.extend(self._generate_axes(x_label, y_label, x_ticks, y_ticks, grid=True))

        # ── Bande de confiance (95 %) de la régression ─────────────────────
        if trend and slope is not None:
            se_pts = []
            n_ci = 80
            x_step = (xmax - xmin) / n_ci
            s2 = sum((y - (slope*x + intercept))**2 for x,y in pairs) / max(n-2, 1)
            sxx = sum((x - sum(x_vals)/n)**2 for x in x_vals)
            xmean = sum(x_vals)/n

            upper_ci = []
            lower_ci = []
            for k in range(n_ci+1):
                xv = xmin + k * x_step
                yv = slope*xv + intercept
                se = math.sqrt(s2 * (1/n + (xv-xmean)**2/sxx)) if sxx else 0
                margin = 1.96 * se
                cx = self._scale_x(xv, xmin, xmax)
                upper_ci.append((cx, self._scale_y(yv+margin, ymin, ymax)))
                lower_ci.append((cx, self._scale_y(yv-margin, ymin, ymax)))

            poly_pts = ' '.join(f"{cx:.2f},{cy:.2f}" for cx,cy in upper_ci)
            poly_pts += ' ' + ' '.join(f"{cx:.2f},{cy:.2f}" for cx,cy in reversed(lower_ci))
            svg.append(
                f'<polygon points="{poly_pts}" fill="{color}" fill-opacity="0.12" stroke="none"/>'
            )

            # Ligne de régression
            cx1 = self._scale_x(xmin, xmin, xmax)
            cy1 = self._scale_y(slope*xmin + intercept, ymin, ymax)
            cx2 = self._scale_x(xmax, xmin, xmax)
            cy2 = self._scale_y(slope*xmax + intercept, ymin, ymax)
            svg.append(
                f'<line x1="{cx1:.2f}" y1="{cy1:.2f}" x2="{cx2:.2f}" y2="{cy2:.2f}" '
                f'stroke="{dark}" stroke-width="2.2" stroke-dasharray="8,4" opacity="0.85"/>'
            )
            if r2 is not None:
                svg.append(
                    f'<text x="{self.margin["left"]+self.plot_width-6}" '
                    f'y="{self.margin["top"]+18}" text-anchor="end" '
                    f'font-family="{self.font_family}" font-size="10.5" '
                    f'fill="{dark}">R² = {r2:.3f}</text>'
                )

        # ── Points ──────────────────────────────────────────────────────────
        for x, y in pairs:
            cx = self._scale_x(x, xmin, xmax)
            cy = self._scale_y(y, ymin, ymax)
            # Halo
            svg.append(
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{size+2.5}" '
                f'fill="{color}" fill-opacity="0.08" stroke="none"/>'
            )
            # Point
            svg.append(
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{size}" '
                f'fill="{color}" fill-opacity="{alpha}" stroke="white" stroke-width="0.8"/>'
            )

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  LINE CHART
    # ════════════════════════════════════════════════════════════════════════

    def line_chart(self, x_data: List[Any], y_data: Union[List[Any], Dict[str, List[Any]]],
                   title: str = "Graphique en lignes", x_label: str = "X",
                   y_label: str = "Y", colors: List[str] = None,
                   markers: bool = True, fill_area: bool = False,
                   smooth: bool = False) -> str:

        if isinstance(y_data, dict):
            series_names = list(y_data.keys())
            series_data  = [y_data[n] for n in series_names]
        else:
            series_names = ['Série 1']
            series_data  = [y_data]

        if not series_data:
            return self._empty_chart("Aucune donnée")

        all_points = []
        all_y_vals = []

        for y_vals in series_data:
            if len(x_data) != len(y_vals):
                return self._empty_chart("Les séries X et Y doivent avoir la même longueur")
            pts = [
                (to_numeric(x), to_numeric(y)) for x,y in zip(x_data, y_vals)
                if x is not None and y is not None
                and isinstance(to_numeric(x), (int, float))
                and isinstance(to_numeric(y), (int, float))
            ]
            if pts:
                all_points.append(pts)
                all_y_vals.extend(yv for _,yv in pts)

        if not all_points:
            return self._empty_chart("Aucune donnée numérique")

        x_vals_flat = [x for pts in all_points for x,_ in pts]
        x_ticks_vals = self._nice_ticks(min(x_vals_flat), max(x_vals_flat), 5)
        y_ticks_vals = self._nice_ticks(min(all_y_vals),  max(all_y_vals),  5)

        xmin, xmax = x_ticks_vals[0], x_ticks_vals[-1]
        ymin, ymax = y_ticks_vals[0], y_ticks_vals[-1]
        xpad = (xmax-xmin)*0.02; ypad = (ymax-ymin)*0.05
        xmin -= xpad; xmax += xpad
        ymin -= ypad; ymax += ypad

        x_ticks = [(self._scale_x(v, xmin, xmax), self._fmt_num(v)) for v in x_ticks_vals]
        y_ticks = [(self._scale_y(v, ymin, ymax), self._fmt_num(v)) for v in y_ticks_vals]

        colors_list = colors or self._get_colors(len(all_points), 'ggplot2')

        svg = self._generate_svg_header(title)
        svg.extend(self._generate_axes(x_label, y_label, x_ticks, y_ticks, grid=True))

        for i, (pts, color) in enumerate(zip(all_points, colors_list)):
            pts.sort(key=lambda p: p[0])
            dark  = self._darken(color, 0.15)
            light = self._lighten(color, 0.5)

            coords = [(self._scale_x(x, xmin, xmax), self._scale_y(y, ymin, ymax)) for x,y in pts]

            # ── Aire remplie ──────────────────────────────────────────────────
            if fill_area:
                bot_y = self.margin['top'] + self.plot_height
                area_pts = ' '.join(f"{cx:.2f},{cy:.2f}" for cx,cy in coords)
                area_pts += f" {coords[-1][0]:.2f},{bot_y} {coords[0][0]:.2f},{bot_y}"
                svg.append(
                    f'<polygon points="{area_pts}" fill="{color}" fill-opacity="0.15" stroke="none"/>'
                )

            # ── Ligne ─────────────────────────────────────────────────────────
            d = ' '.join(
                f"{'M' if j==0 else 'L'} {cx:.2f},{cy:.2f}"
                for j,(cx,cy) in enumerate(coords)
            )
            svg.append(
                f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.8" '
                f'stroke-linejoin="round" stroke-linecap="round"/>'
            )

            # ── Marqueurs ─────────────────────────────────────────────────────
            if markers:
                for cx, cy in coords:
                    svg.append(
                        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="4.5" '
                        f'fill="white" stroke="{color}" stroke-width="2"/>'
                    )

        # Légende
        if len(series_names) > 1:
            legend_items = list(zip(series_names, colors_list))
            svg.extend(self._add_legend(legend_items))

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  HEATMAP
    # ════════════════════════════════════════════════════════════════════════

    def heatmap(self, data: List[List[float]], row_labels: List[str] = None,
                col_labels: List[str] = None, title: str = "Carte de chaleur",
                x_label: str = "", y_label: str = "",
                cmap: str = 'viridis', annot: bool = True) -> str:

        if not data or not data[0]:
            return self._empty_chart("Aucune donnée")

        n_rows = len(data)
        n_cols = len(data[0])
        all_values = [v for row in data for v in row if v is not None]
        if not all_values:
            return self._empty_chart("Aucune valeur numérique")

        min_val = min(all_values)
        max_val = max(all_values)

        # ── Palette de couleurs de qualité ─────────────────────────────────
        def get_color(val):
            if val is None:
                return "#CCCCCC"
            t = (val - min_val) / (max_val - min_val) if max_val > min_val else 0.5
            t = max(0.0, min(1.0, t))
            if cmap == 'viridis':
                # Viridis fidèle (5 pivots interpolés)
                pivots = [
                    (0.00, (68,  1,  84)),
                    (0.25, (59, 82, 139)),
                    (0.50, (33, 145, 140)),
                    (0.75, (94, 201,  98)),
                    (1.00, (253, 231,  37)),
                ]
            elif cmap == 'coolwarm':
                pivots = [
                    (0.0,  (58, 76, 192)),
                    (0.5,  (221, 220, 220)),
                    (1.0,  (180,  4,  38)),
                ]
            elif cmap == 'hot':
                pivots = [
                    (0.0,  (10,  0,  0)),
                    (0.33, (255, 0,  0)),
                    (0.66, (255, 200, 0)),
                    (1.0,  (255, 255, 255)),
                ]
            else:  # blues
                pivots = [
                    (0.0, (247, 251, 255)),
                    (0.5, (107, 174, 214)),
                    (1.0, (8,   48, 107)),
                ]

            # Interpolation linéaire entre pivots
            for k in range(len(pivots)-1):
                t0, c0 = pivots[k]
                t1, c1 = pivots[k+1]
                if t0 <= t <= t1:
                    f = (t - t0) / (t1 - t0) if t1 > t0 else 0
                    r = int(c0[0] + f*(c1[0]-c0[0]))
                    g = int(c0[1] + f*(c1[1]-c0[1]))
                    b = int(c0[2] + f*(c1[2]-c0[2]))
                    return f'rgb({r},{g},{b})'
            r,g,b = pivots[-1][1]
            return f'rgb({r},{g},{b})'

        def text_color(val):
            """Couleur de texte contrastante (blanc/noir) selon la luminance."""
            if val is None:
                return "#333"
            t = (val - min_val)/(max_val - min_val) if max_val > min_val else 0.5
            return "white" if (t < 0.45 or t > 0.85) else "#1A1A2E"

        # Marges ajustées pour les labels
        extra_left = max((max(len(l) for l in row_labels)*6 if row_labels else 0), 0)
        extra_top  = 50 if col_labels else 0

        cell_w = self.plot_width  / n_cols
        cell_h = self.plot_height / n_rows

        svg = self._generate_svg_header(title)

        # ── Cellules ─────────────────────────────────────────────────────────
        for i in range(n_rows):
            for j in range(n_cols):
                x = self.margin['left'] + j * cell_w
                y = self.margin['top']  + i * cell_h
                col = get_color(data[i][j])

                svg.append(
                    f'<rect x="{x:.2f}" y="{y:.2f}" '
                    f'width="{cell_w:.2f}" height="{cell_h:.2f}" '
                    f'fill="{col}" stroke="white" stroke-width="1.5" rx="1"/>'
                )
                if annot and data[i][j] is not None:
                    fc = text_color(data[i][j])
                    fs = max(7, min(13, int(cell_h * 0.38)))
                    svg.append(
                        f'<text x="{x+cell_w/2:.2f}" y="{y+cell_h/2+1:.2f}" '
                        f'text-anchor="middle" dominant-baseline="middle" '
                        f'font-family="{self.font_family}" font-size="{fs}" '
                        f'font-weight="600" fill="{fc}">{data[i][j]:.2f}</text>'
                    )

        # ── Labels colonnes ───────────────────────────────────────────────────
        if col_labels:
            for j, label in enumerate(col_labels[:n_cols]):
                x = self.margin['left'] + j*cell_w + cell_w/2
                y = self.margin['top'] - 8
                svg.append(
                    f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="middle" '
                    f'font-family="{self.font_family}" font-size="10" font-weight="600" '
                    f'fill="{self.color_axis}">{label}</text>'
                )

        # ── Labels lignes ─────────────────────────────────────────────────────
        if row_labels:
            for i, label in enumerate(row_labels[:n_rows]):
                x = self.margin['left'] - 8
                y = self.margin['top'] + i*cell_h + cell_h/2
                svg.append(
                    f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="end" '
                    f'dominant-baseline="middle" '
                    f'font-family="{self.font_family}" font-size="10" font-weight="600" '
                    f'fill="{self.color_axis}">{label}</text>'
                )

        # ── Barre de couleur continue ────────────────────────────────────────
        bar_x     = self.width - self.margin['right'] + 12
        bar_y     = self.margin['top']
        bar_h     = self.plot_height
        bar_w     = 16
        n_steps   = 200

        for k in range(n_steps):
            t  = k / n_steps
            y1 = bar_y + (1 - t) * bar_h
            y2 = bar_y + (1 - (k+1)/n_steps) * bar_h
            col = get_color(min_val + t*(max_val-min_val))
            svg.append(
                f'<rect x="{bar_x:.2f}" y="{y2:.2f}" width="{bar_w}" '
                f'height="{y1-y2+0.5:.2f}" fill="{col}" stroke="none"/>'
            )

        # Contour barre de couleur
        svg.append(
            f'<rect x="{bar_x:.2f}" y="{bar_y:.2f}" width="{bar_w}" height="{bar_h:.2f}" '
            f'fill="none" stroke="{self.color_axis}" stroke-width="0.8"/>'
        )

        # Labels min / max de la colorbar
        n_cb_ticks = 5
        for k in range(n_cb_ticks):
            t   = k / (n_cb_ticks - 1)
            val = min_val + t*(max_val - min_val)
            y   = bar_y + bar_h*(1-t)
            svg.extend([
                f'<line x1="{bar_x+bar_w:.2f}" y1="{y:.2f}" '
                f'x2="{bar_x+bar_w+3:.2f}" y2="{y:.2f}" '
                f'stroke="{self.color_axis}" stroke-width="0.8"/>',
                f'<text x="{bar_x+bar_w+7:.2f}" y="{y+4:.2f}" '
                f'font-family="{self.font_family}" font-size="9" '
                f'fill="{self.color_tick}">{self._fmt_num(val)}</text>',
            ])

        # Label colorbar
        if x_label:
            mid_y = bar_y + bar_h/2
            svg.append(
                f'<text x="{bar_x+bar_w+30:.2f}" y="{mid_y:.2f}" '
                f'text-anchor="middle" font-family="{self.font_family}" font-size="10" '
                f'fill="{self.color_axis}" '
                f'transform="rotate(90 {bar_x+bar_w+30:.2f} {mid_y:.2f})">{x_label}</text>'
            )

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  VIOLIN PLOT
    # ════════════════════════════════════════════════════════════════════════

    def violin_plot(self, data: Union[List[Any], Dict[str, List[Any]]],
                    title: str = "Violin Plot", x_label: str = "",
                    y_label: str = "Valeurs", bw_method: float = 0.3) -> str:

        if isinstance(data, dict):
            categories = list(data.keys())
            values_list = [self._get_numeric_data(data[cat]) for cat in categories]
        else:
            categories = ['Données']
            values_list = [self._get_numeric_data(data)]

        categories  = [c for c,v in zip(categories, values_list) if v]
        values_list = [v for v in values_list if v]

        if not categories:
            return self._empty_chart("Aucune donnée valide")

        all_values = []
        stats_list = []
        for vals in values_list:
            sv = sorted(vals)
            mean_v = sum(vals)/len(vals)
            std_v  = math.sqrt(sum((x-mean_v)**2 for x in vals)/len(vals)) or 1e-9
            stats_list.append({
                'q1':     self.calc.quantile(sv, 0.25),
                'median': self.calc.median(sv),
                'q3':     self.calc.quantile(sv, 0.75),
                'mean':   mean_v,
                'std':    std_v,
                'n':      len(vals),
            })
            all_values.extend(vals)

        if not all_values:
            return self._empty_chart("Aucune donnée numérique")

        y_ticks_vals = self._nice_ticks(min(all_values), max(all_values), 5)
        ymin, ymax = y_ticks_vals[0], y_ticks_vals[-1]
        ypad = (ymax - ymin) * 0.08
        ymin -= ypad; ymax += ypad

        y_ticks = [(self._scale_y(v, ymin, ymax), self._fmt_num(v)) for v in y_ticks_vals]

        n_groups     = len(categories)
        group_spacing = self.plot_width / n_groups
        violin_w     = group_spacing * 0.42
        box_w        = violin_w * 0.28
        colors       = self._get_colors(n_groups, 'ggplot2')

        svg = self._generate_svg_header(title)
        svg.extend(self._generate_axes(x_label, y_label, y_ticks=y_ticks, grid=True))

        for i, (cat, stats, color, vals) in enumerate(zip(categories, stats_list, colors, values_list)):
            xc    = self.margin['left'] + (i+0.5)*group_spacing
            light = self._lighten(color, 0.5)
            dark  = self._darken(color, 0.15)

            # ── KDE ──────────────────────────────────────────────────────────
            n_pts = 80
            bw = 1.06 * stats['std'] * stats['n']**(-0.2) * bw_method
            bw = max(bw, 1e-9)

            ys_arr, dens_arr = [], []
            for k in range(n_pts):
                yv = ymin + k*(ymax-ymin)/(n_pts-1)
                d = sum(
                    math.exp(-0.5*((yv-xi)/bw)**2)
                    for xi in vals
                ) / (len(vals)*bw*math.sqrt(2*math.pi))
                ys_arr.append(yv)
                dens_arr.append(d)

            max_d = max(dens_arr) or 1
            widths = [d/max_d*violin_w for d in dens_arr]

            pts_left  = []
            pts_right = []
            for yv, w in zip(ys_arr, widths):
                cy = self._scale_y(yv, ymin, ymax)
                pts_left.append( (xc-w, cy))
                pts_right.append((xc+w, cy))

            # Forme violon fermée
            poly = ' '.join(f"{x:.2f},{y:.2f}" for x,y in pts_left)
            poly += ' ' + ' '.join(f"{x:.2f},{y:.2f}" for x,y in reversed(pts_right))
            svg.append(
                f'<polygon points="{poly}" fill="{light}" fill-opacity="0.85" '
                f'stroke="{color}" stroke-width="1.5" stroke-linejoin="round"/>'
            )

            # ── Mini boxplot centré ───────────────────────────────────────────
            y_q1  = self._scale_y(stats['q1'],     ymin, ymax)
            y_q3  = self._scale_y(stats['q3'],     ymin, ymax)
            y_med = self._scale_y(stats['median'], ymin, ymax)
            y_mea = self._scale_y(stats['mean'],   ymin, ymax)

            # IQR box
            svg.append(
                f'<rect x="{xc-box_w/2:.2f}" y="{y_q3:.2f}" '
                f'width="{box_w:.2f}" height="{y_q1-y_q3:.2f}" '
                f'fill="white" fill-opacity="0.9" stroke="{dark}" stroke-width="1.5" rx="2"/>'
            )
            # Médiane
            svg.append(
                f'<line x1="{xc-box_w/2:.2f}" y1="{y_med:.2f}" '
                f'x2="{xc+box_w/2:.2f}" y2="{y_med:.2f}" '
                f'stroke="{dark}" stroke-width="2.5" stroke-linecap="round"/>'
            )
            # Moyenne (point blanc)
            svg.append(
                f'<circle cx="{xc:.2f}" cy="{y_mea:.2f}" r="3.5" '
                f'fill="white" stroke="{dark}" stroke-width="1.5"/>'
            )

            # ── Label + n ─────────────────────────────────────────────────────
            bot = self.margin['top'] + self.plot_height
            svg.append(
                f'<text x="{xc:.2f}" y="{bot+20}" text-anchor="middle" '
                f'font-family="{self.font_family}" font-size="11" '
                f'fill="{self.color_axis}">{cat}</text>'
            )
            svg.append(
                f'<text x="{xc:.2f}" y="{bot+33}" text-anchor="middle" '
                f'font-family="{self.font_family}" font-size="9" fill="#AAAAAA">'
                f'n={stats["n"]}</text>'
            )

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  ACF PLOT
    # ════════════════════════════════════════════════════════════════════════

    def acf_plot(self, data: List[Any], nlags: int = 20,
                 title: str = "Autocorrélation", x_label: str = "Décalage",
                 y_label: str = "Autocorrélation") -> str:

        numeric_data = self._get_numeric_data(data)
        if len(numeric_data) < 2:
            return self._empty_chart("Pas assez de données")

        acf_values = [1.0]
        for lag in range(1, min(nlags, len(numeric_data)-1)):
            acf = self.calc.autocorrelation(numeric_data, lag)
            acf_values.append(acf if not math.isnan(acf) else 0)

        lags = list(range(len(acf_values)))
        n = len(numeric_data)
        conf_int = 1.96 / math.sqrt(n)

        all_vals = acf_values + [conf_int, -conf_int]
        y_ticks_vals = self._nice_ticks(min(all_vals)*1.15, max(all_vals)*1.15, 5)
        ymin, ymax = y_ticks_vals[0], y_ticks_vals[-1]

        y_ticks = [(self._scale_y(v, ymin, ymax), f"{v:.2f}") for v in y_ticks_vals]

        n_bars = len(acf_values)
        bar_spacing = self.plot_width / n_bars
        bar_w = bar_spacing * 0.55

        # Axe X : tous les lag en x_ticks
        x_ticks = []
        step = max(1, n_bars // 10)
        for k in range(0, n_bars, step):
            xc = self.margin['left'] + (k + 0.5)*bar_spacing
            x_ticks.append((xc, str(k)))

        svg = self._generate_svg_header(title, f"n = {n:,}  ·  IC 95 % = ±{conf_int:.3f}")
        svg.extend(self._generate_axes(x_label, y_label, x_ticks, y_ticks, grid=True))

        # ── Ligne de référence zéro ──────────────────────────────────────────
        y_zero = self._scale_y(0, ymin, ymax)
        svg.append(
            f'<line x1="{self.margin["left"]}" y1="{y_zero:.2f}" '
            f'x2="{self.width-self.margin["right"]}" y2="{y_zero:.2f}" '
            f'stroke="{self.color_axis}" stroke-width="1" opacity="0.5"/>'
        )

        # ── Bande de confiance ───────────────────────────────────────────────
        y_ci_hi = self._scale_y( conf_int, ymin, ymax)
        y_ci_lo = self._scale_y(-conf_int, ymin, ymax)
        svg.append(
            f'<rect x="{self.margin["left"]}" y="{y_ci_hi:.2f}" '
            f'width="{self.plot_width}" height="{y_ci_lo-y_ci_hi:.2f}" '
            f'fill="#4C72B0" fill-opacity="0.10" stroke="none"/>'
        )
        for yi, dash in [(y_ci_hi, ""), (y_ci_lo, "")]:
            svg.append(
                f'<line x1="{self.margin["left"]}" y1="{yi:.2f}" '
                f'x2="{self.width-self.margin["right"]}" y2="{yi:.2f}" '
                f'stroke="#4C72B0" stroke-width="1.2" stroke-dasharray="6,3" opacity="0.7"/>'
            )

        # ── Barres ───────────────────────────────────────────────────────────
        for k, val in enumerate(acf_values):
            xc  = self.margin['left'] + (k+0.5)*bar_spacing
            xl  = xc - bar_w/2
            color = "#4C72B0" if val >= 0 else "#DD8452"
            dark  = self._darken(color, 0.2)

            if val >= 0:
                y_top = self._scale_y(val, ymin, ymax)
                y_bot = self._scale_y(0,   ymin, ymax)
            else:
                y_top = self._scale_y(0,   ymin, ymax)
                y_bot = self._scale_y(val, ymin, ymax)

            h = max(y_bot - y_top, 1)
            svg.append(
                f'<rect x="{xl:.2f}" y="{y_top:.2f}" width="{bar_w:.2f}" height="{h:.2f}" '
                f'fill="{color}" fill-opacity="0.75" stroke="{dark}" stroke-width="0.8" rx="2"/>'
            )

            # Lag 0 marqué différemment
            if k == 0:
                svg.append(
                    f'<rect x="{xl:.2f}" y="{y_top:.2f}" width="{bar_w:.2f}" height="{h:.2f}" '
                    f'fill="none" stroke="{dark}" stroke-width="1.5" rx="2"/>'
                )

        svg.append('</svg>')
        return '\n'.join(svg)
    def bar_chart(self, x_data, y_data,
                  title="Graphique en barres",
                  x_label="X", y_label="Y",
                  colors=None,
                  stacked=False,
                  show=True,
                  orientation="vertical",
                  bar_gap=0.25):

        # ── Normalisation des données ──────────────────────────────────────
        if isinstance(y_data, dict):
            series_names  = list(y_data.keys())
            series_values = [y_data[n] for n in series_names]
        else:
            series_names  = ['Série 1']
            series_values = [y_data]

        n_categories = len(x_data)
        n_series     = len(series_names)

        # Conversion numérique
        numeric_series = []
        for sv in series_values:
            row = []
            for v in sv:
                nv = to_numeric(v)
                row.append(nv if isinstance(nv, (int, float)) else 0.0)
            numeric_series.append(row[:n_categories])

        if not numeric_series or n_categories == 0:
            return self._empty_chart("Aucune donnée à afficher")

        palette = colors or self._get_colors(n_series, 'ggplot2')
        colors_ = [palette[i % len(palette)] for i in range(n_series)]

        # ── Calcul des bornes Y ────────────────────────────────────────────
        if stacked:
            col_totals = [
                sum(numeric_series[s][i] for s in range(n_series))
                for i in range(n_categories)
            ]
            y_max_data = max(col_totals) if col_totals else 1
            y_min_data = 0.0
        else:
            all_vals   = [v for sv in numeric_series for v in sv]
            y_max_data = max(all_vals) if all_vals else 1
            y_min_data = min(0.0, min(all_vals)) if all_vals else 0.0

        y_ticks_vals = self._nice_ticks(y_min_data, y_max_data, 5)
        ymin = y_ticks_vals[0]
        ymax = y_ticks_vals[-1]
        ymax += (ymax - ymin) * 0.05  # marge haute 5 %

        y_ticks = [
            (self._scale_y(v, ymin, ymax), self._fmt_num(v))
            for v in y_ticks_vals
        ]

        # ── Géométrie des barres ───────────────────────────────────────────
        group_w  = self.plot_width / n_categories
        gap      = group_w * bar_gap
        usable_w = group_w - gap
        bar_w    = usable_w if stacked else usable_w / n_series
        y_zero   = self._scale_y(0.0, ymin, ymax)

        # ── Ticks axe X ───────────────────────────────────────────────────
        x_ticks = [
            (self.margin['left'] + (i + 0.5) * group_w, str(x_data[i])[:18])
            for i in range(n_categories)
        ]

        svg = self._generate_svg_header(title)
        svg.extend(self._generate_axes(x_label, y_label, x_ticks, y_ticks, grid=True))

        # ── Dessin des barres ──────────────────────────────────────────────
        for i in range(n_categories):
            group_left = self.margin['left'] + i * group_w + gap / 2

            if stacked:
                cumulative = 0.0
                for s in range(n_series):
                    val   = numeric_series[s][i]
                    color = colors_[s]
                    dark  = self._darken(color, 0.15)
                    light = self._lighten(color, 0.45)

                    bar_top_val = cumulative + val
                    bx = group_left
                    by = self._scale_y(bar_top_val, ymin, ymax)
                    bh = abs(self._scale_y(cumulative, ymin, ymax) - by)

                    if bh > 0:
                        is_top = (s == n_series - 1)
                        rx_val = "2" if is_top else "0"
                        svg.append(
                            f'<rect x="{bx:.2f}" y="{by:.2f}" '
                            f'width="{bar_w:.2f}" height="{bh:.2f}" '
                            f'fill="{color}" fill-opacity="0.88" '
                            f'stroke="{dark}" stroke-width="0.6" rx="{rx_val}"/>'
                        )
                        if bh > 5:
                            svg.append(
                                f'<rect x="{bx:.2f}" y="{by:.2f}" '
                                f'width="{bar_w:.2f}" height="3" '
                                f'fill="{light}" fill-opacity="0.4" rx="{rx_val}"/>'
                            )
                        if bh > 16 and val != 0:
                            svg.append(
                                f'<text x="{bx + bar_w/2:.2f}" y="{by + bh/2 + 4:.2f}" '
                                f'text-anchor="middle" '
                                f'font-family="{self.font_family}" font-size="9" '
                                f'fill="white" font-weight="600">{self._fmt_num(val)}</text>'
                            )
                    cumulative += val

            else:  # groupées
                for s in range(n_series):
                    val   = numeric_series[s][i]
                    color = colors_[s]
                    dark  = self._darken(color, 0.15)
                    light = self._lighten(color, 0.45)

                    bx = group_left + s * bar_w
                    by = self._scale_y(max(val, 0.0), ymin, ymax) if val >= 0 \
                         else self._scale_y(0.0, ymin, ymax)
                    bh = max(abs(self._scale_y(val, ymin, ymax) - y_zero), 1)

                    svg.append(
                        f'<rect x="{bx:.2f}" y="{by:.2f}" '
                        f'width="{bar_w:.2f}" height="{bh:.2f}" '
                        f'fill="{color}" fill-opacity="0.88" '
                        f'stroke="{dark}" stroke-width="0.6" rx="3"/>'
                    )
                    if bh > 5:
                        svg.append(
                            f'<rect x="{bx:.2f}" y="{by:.2f}" '
                            f'width="{bar_w:.2f}" height="3" '
                            f'fill="{light}" fill-opacity="0.45" rx="3"/>'
                        )
                    if bh > 8 and val != 0:
                        label_y = by - 4 if val >= 0 else by + bh + 12
                        svg.append(
                            f'<text x="{bx + bar_w/2:.2f}" y="{label_y:.2f}" '
                            f'text-anchor="middle" '
                            f'font-family="{self.font_family}" font-size="9" '
                            f'fill="{self.color_tick}">{self._fmt_num(val)}</text>'
                        )

        # ── Légende (multi-séries uniquement) ─────────────────────────────
        if n_series > 1:
            svg.extend(self._add_legend(list(zip(series_names, colors_))))

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  EMPTY CHART
    # ════════════════════════════════════════════════════════════════════════

    def _empty_chart(self, message: str = "Aucune donnée à afficher") -> str:
        return '\n'.join([
            f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="{self.width}" height="{self.height}" fill="{self.bg_color}" rx="8"/>',
            f'<text x="{self.width/2}" y="{self.height/2}" text-anchor="middle" '
            f'font-family="{self.font_family}" font-size="14" fill="#999AAA">{message}</text>',
            '</svg>',
        ])
# ════════════════════════════════════════════════════════════════════════
#  1. PIE CHART  –  Camembert avec labels et pourcentages
# ════════════════════════════════════════════════════════════════════════

    def pie_chart(self, labels: List[str], values: List[Any],
                  title: str = "Camembert",
                  colors: List[str] = None,
                  donut: bool = False,
                  show_pct: bool = True) -> str:

        nums = []
        for v in values:
            nv = to_numeric(v)
            nums.append(nv if isinstance(nv, (int, float)) and nv > 0 else 0.0)

        total = sum(nums)
        if total == 0:
            return self._empty_chart("Aucune donnée valide")

        palette = colors or self._get_colors(len(labels), 'ggplot2')
        cx = self.width / 2
        cy = self.margin['top'] + self.plot_height / 2
        r  = min(self.plot_width, self.plot_height) / 2 * 0.82
        r_inner = r * 0.48 if donut else 0

        svg = self._generate_svg_header(title)

        start_angle = -math.pi / 2  # commence à 12h
        for i, (label, val) in enumerate(zip(labels, nums)):
            if val == 0:
                continue
            sweep = 2 * math.pi * val / total
            end_angle = start_angle + sweep
            color = palette[i % len(palette)]
            dark  = self._darken(color, 0.15)

            # Coordonnées arc
            x1o = cx + r * math.cos(start_angle)
            y1o = cy + r * math.sin(start_angle)
            x2o = cx + r * math.cos(end_angle)
            y2o = cy + r * math.sin(end_angle)

            large = 1 if sweep > math.pi else 0

            if donut:
                x1i = cx + r_inner * math.cos(end_angle)
                y1i = cy + r_inner * math.sin(end_angle)
                x2i = cx + r_inner * math.cos(start_angle)
                y2i = cy + r_inner * math.sin(start_angle)
                path = (
                    f"M {x1o:.2f},{y1o:.2f} "
                    f"A {r:.2f},{r:.2f} 0 {large} 1 {x2o:.2f},{y2o:.2f} "
                    f"L {x1i:.2f},{y1i:.2f} "
                    f"A {r_inner:.2f},{r_inner:.2f} 0 {large} 0 {x2i:.2f},{y2i:.2f} Z"
                )
            else:
                path = (
                    f"M {cx:.2f},{cy:.2f} "
                    f"L {x1o:.2f},{y1o:.2f} "
                    f"A {r:.2f},{r:.2f} 0 {large} 1 {x2o:.2f},{y2o:.2f} Z"
                )

            svg.append(
                f'<path d="{path}" fill="{color}" fill-opacity="0.88" '
                f'stroke="white" stroke-width="2"/>'
            )

            # Label au milieu du secteur
            mid_angle = start_angle + sweep / 2
            lr = r * (0.65 if not donut else 0.72)
            lx = cx + lr * math.cos(mid_angle)
            ly = cy + lr * math.sin(mid_angle)

            pct = val / total * 100
            if pct >= 4:
                svg.append(
                    f'<text x="{lx:.2f}" y="{ly:.2f}" text-anchor="middle" '
                    f'dominant-baseline="middle" font-family="{self.font_family}" '
                    f'font-size="10" font-weight="700" fill="white">'
                    f'{pct:.1f}%</text>'
                )

            start_angle = end_angle

        # Légende à droite
        legend_items = [(lbl, palette[i % len(palette)]) for i, lbl in enumerate(labels)]
        svg.extend(self._add_legend(legend_items))

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  2. AREA CHART  –  Zones empilées ou superposées
    # ════════════════════════════════════════════════════════════════════════

    def area_chart(self, x_data: List[Any],
                   y_data: Union[List[Any], Dict[str, List[Any]]],
                   title: str = "Graphique en aires",
                   x_label: str = "X", y_label: str = "Y",
                   colors: List[str] = None,
                   stacked: bool = False,
                   alpha: float = 0.55) -> str:

        if isinstance(y_data, dict):
            series_names  = list(y_data.keys())
            series_values = [y_data[n] for n in series_names]
        else:
            series_names  = ['Série 1']
            series_values = [y_data]

        n_series = len(series_names)
        palette  = colors or self._get_colors(n_series, 'ggplot2')

        # Conversion numérique
        parsed = []
        for sv in series_values:
            pts = []
            for x, y in zip(x_data, sv):
                nx, ny = to_numeric(x), to_numeric(y)
                if isinstance(nx, (int, float)) and isinstance(ny, (int, float)):
                    pts.append((nx, ny))
            parsed.append(pts)

        if not parsed or not parsed[0]:
            return self._empty_chart("Aucune donnée numérique")

        x_vals = [x for pts in parsed for x, _ in pts]
        all_y  = [y for pts in parsed for _, y in pts]

        if stacked:
            n_pts = len(parsed[0])
            stacked_tops = [sum(parsed[s][i][1] for s in range(n_series)) for i in range(n_pts)]
            y_max = max(stacked_tops) * 1.05
            y_min = 0.0
        else:
            y_max = max(all_y) * 1.05
            y_min = min(0.0, min(all_y))

        x_ticks_vals = self._nice_ticks(min(x_vals), max(x_vals), 5)
        y_ticks_vals = self._nice_ticks(y_min, y_max, 5)
        xmin, xmax   = x_ticks_vals[0], x_ticks_vals[-1]
        ymin, ymax   = y_ticks_vals[0], y_ticks_vals[-1]

        x_ticks = [(self._scale_x(v, xmin, xmax), self._fmt_num(v)) for v in x_ticks_vals]
        y_ticks = [(self._scale_y(v, ymin, ymax), self._fmt_num(v)) for v in y_ticks_vals]

        svg = self._generate_svg_header(title)
        svg.extend(self._generate_axes(x_label, y_label, x_ticks, y_ticks, grid=True))

        bot_y = self.margin['top'] + self.plot_height
        baselines = [0.0] * len(parsed[0])  # pour stacked

        for s, (pts, color) in enumerate(zip(parsed, palette)):
            dark = self._darken(color, 0.15)
            pts_sorted = sorted(pts, key=lambda p: p[0])

            if stacked:
                top_coords    = [(self._scale_x(x, xmin, xmax),
                                  self._scale_y(baselines[i] + y, ymin, ymax))
                                 for i, (x, y) in enumerate(pts_sorted)]
                bottom_coords = [(self._scale_x(pts_sorted[i][0], xmin, xmax),
                                  self._scale_y(baselines[i], ymin, ymax))
                                 for i in range(len(pts_sorted))]
                poly_pts = ' '.join(f"{cx:.2f},{cy:.2f}" for cx, cy in top_coords)
                poly_pts += ' ' + ' '.join(f"{cx:.2f},{cy:.2f}" for cx, cy in reversed(bottom_coords))
                for i, (x, y) in enumerate(pts_sorted):
                    baselines[i] += y
            else:
                coords   = [(self._scale_x(x, xmin, xmax), self._scale_y(y, ymin, ymax))
                            for x, y in pts_sorted]
                poly_pts = ' '.join(f"{cx:.2f},{cy:.2f}" for cx, cy in coords)
                poly_pts += f" {coords[-1][0]:.2f},{bot_y} {coords[0][0]:.2f},{bot_y}"

            svg.append(
                f'<polygon points="{poly_pts}" fill="{color}" '
                f'fill-opacity="{alpha}" stroke="none"/>'
            )

            # Ligne de contour
            line_pts = top_coords if stacked else [(self._scale_x(x, xmin, xmax),
                                                    self._scale_y(y, ymin, ymax))
                                                   for x, y in pts_sorted]
            d = ' '.join(f"{'M' if j==0 else 'L'} {cx:.2f},{cy:.2f}"
                         for j, (cx, cy) in enumerate(line_pts))
            svg.append(
                f'<path d="{d}" fill="none" stroke="{dark}" stroke-width="2" '
                f'stroke-linejoin="round" stroke-linecap="round"/>'
            )

        if n_series > 1:
            svg.extend(self._add_legend(list(zip(series_names, palette))))

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  3. BUBBLE CHART  –  Nuage de points avec taille variable
    # ════════════════════════════════════════════════════════════════════════

    def bubble_chart(self, x_data: List[Any], y_data: List[Any],
                     size_data: List[Any],
                     labels: List[str] = None,
                     title: str = "Bubble Chart",
                     x_label: str = "X", y_label: str = "Y",
                     color: str = "#4C72B0",
                     max_radius: float = 35) -> str:

        rows = []
        for x, y, s in zip(x_data, y_data, size_data):
            nx, ny, ns = to_numeric(x), to_numeric(y), to_numeric(s)
            if all(isinstance(v, (int, float)) for v in [nx, ny, ns]):
                rows.append((nx, ny, ns))

        if not rows:
            return self._empty_chart("Aucune donnée numérique")

        x_vals = [r[0] for r in rows]
        y_vals = [r[1] for r in rows]
        s_vals = [r[2] for r in rows]
        s_max  = max(s_vals) or 1

        x_ticks_vals = self._nice_ticks(min(x_vals), max(x_vals), 5)
        y_ticks_vals = self._nice_ticks(min(y_vals), max(y_vals), 5)
        xmin, xmax = x_ticks_vals[0], x_ticks_vals[-1]
        ymin, ymax = y_ticks_vals[0], y_ticks_vals[-1]
        pad = 0.05
        xmin -= (xmax-xmin)*pad; xmax += (xmax-xmin)*pad
        ymin -= (ymax-ymin)*pad; ymax += (ymax-ymin)*pad

        x_ticks = [(self._scale_x(v, xmin, xmax), self._fmt_num(v)) for v in x_ticks_vals]
        y_ticks = [(self._scale_y(v, ymin, ymax), self._fmt_num(v)) for v in y_ticks_vals]

        dark  = self._darken(color, 0.2)
        light = self._lighten(color, 0.4)

        svg = self._generate_svg_header(title, f"n = {len(rows):,}")
        svg.extend(self._generate_axes(x_label, y_label, x_ticks, y_ticks, grid=True))

        # Trier par taille décroissante (grandes bulles en arrière-plan)
        indexed = sorted(enumerate(rows), key=lambda t: -t[1][2])

        for idx, (x, y, s) in indexed:
            r  = max(3, math.sqrt(s / s_max) * max_radius)
            cx = self._scale_x(x, xmin, xmax)
            cy = self._scale_y(y, ymin, ymax)

            svg.append(
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" '
                f'fill="{color}" fill-opacity="0.55" stroke="{dark}" stroke-width="1.2"/>'
            )
            # Reflet
            svg.append(
                f'<circle cx="{cx-r*0.28:.2f}" cy="{cy-r*0.28:.2f}" r="{r*0.22:.2f}" '
                f'fill="white" fill-opacity="0.35" stroke="none"/>'
            )
            if labels and idx < len(labels) and r > 10:
                svg.append(
                    f'<text x="{cx:.2f}" y="{cy+3:.2f}" text-anchor="middle" '
                    f'font-family="{self.font_family}" font-size="{max(8, int(r*0.38))}" '
                    f'fill="{dark}" font-weight="600">{str(labels[idx])[:8]}</text>'
                )

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  4. STACKED BAR CHART  –  Raccourci de bar_chart(stacked=True)
    # ════════════════════════════════════════════════════════════════════════

    def stacked_bar(self, x_data: List[Any],
                    y_data: Dict[str, List[Any]],
                    title: str = "Barres empilées",
                    x_label: str = "X", y_label: str = "Y",
                    colors: List[str] = None,
                    normalized: bool = False) -> str:

        if normalized:
            # Convertir en pourcentages
            n_cats = len(x_data)
            keys   = list(y_data.keys())
            totals = []
            for i in range(n_cats):
                t = sum(to_numeric(y_data[k][i]) or 0 for k in keys)
                totals.append(t or 1)
            y_data_norm = {
                k: [(to_numeric(y_data[k][i]) or 0) / totals[i] * 100
                    for i in range(n_cats)]
                for k in keys
            }
            return self.bar_chart(x_data, y_data_norm, title=title,
                                  x_label=x_label, y_label=y_label or "(%)",
                                  colors=colors, stacked=True)
        return self.bar_chart(x_data, y_data, title=title,
                              x_label=x_label, y_label=y_label,
                              colors=colors, stacked=True)

    # ════════════════════════════════════════════════════════════════════════
    #  5. HORIZONTAL BAR  –  bar_chart orienté horizontalement
    # ════════════════════════════════════════════════════════════════════════

    def hbar_chart(self, categories: List[str], values: List[Any],
                   title: str = "Barres horizontales",
                   x_label: str = "Valeurs", y_label: str = "",
                   color: str = None,
                   sort: bool = True) -> str:

        nums = []
        for v in values:
            nv = to_numeric(v)
            nums.append(nv if isinstance(nv, (int, float)) else 0.0)

        if sort:
            paired = sorted(zip(nums, categories), reverse=True)
            nums, categories = zip(*paired) if paired else ([], [])
            nums       = list(nums)
            categories = list(categories)

        if not nums:
            return self._empty_chart("Aucune donnée")

        bar_color = color or self._get_colors(1, 'default')[0]
        dark      = self._darken(bar_color, 0.15)
        light     = self._lighten(bar_color, 0.45)

        n = len(categories)
        x_max = max(nums) * 1.05 or 1
        x_min = min(0.0, min(nums))

        x_ticks_vals = self._nice_ticks(x_min, x_max, 5)
        xmin_t = x_ticks_vals[0]
        xmax_t = x_ticks_vals[-1]

        x_ticks = [(self._scale_x(v, xmin_t, xmax_t), self._fmt_num(v)) for v in x_ticks_vals]

        bar_h    = self.plot_height / n * 0.65
        bar_gap  = self.plot_height / n * 0.35
        x_zero   = self._scale_x(0.0, xmin_t, xmax_t)

        svg = self._generate_svg_header(title)
        svg.extend(self._generate_axes(x_label, y_label, x_ticks=x_ticks, grid=True))

        for i, (cat, val) in enumerate(zip(categories, nums)):
            by = self.margin['top'] + i * (bar_h + bar_gap) + bar_gap / 2
            bx = self._scale_x(min(val, 0.0), xmin_t, xmax_t)
            bw = abs(self._scale_x(val, xmin_t, xmax_t) - x_zero)
            bw = max(bw, 1)

            svg.append(
                f'<rect x="{bx:.2f}" y="{by:.2f}" '
                f'width="{bw:.2f}" height="{bar_h:.2f}" '
                f'fill="{bar_color}" fill-opacity="0.88" '
                f'stroke="{dark}" stroke-width="0.6" rx="3"/>'
            )
            if bar_h > 5:
                svg.append(
                    f'<rect x="{bx:.2f}" y="{by:.2f}" '
                    f'width="{bw:.2f}" height="3" '
                    f'fill="{light}" fill-opacity="0.45" rx="3"/>'
                )

            # Label catégorie à gauche
            svg.append(
                f'<text x="{self.margin["left"]-6}" y="{by + bar_h/2 + 4:.2f}" '
                f'text-anchor="end" font-family="{self.font_family}" '
                f'font-size="10" fill="{self.color_axis}">{str(cat)[:20]}</text>'
            )
            # Valeur à droite de la barre
            if bw > 12:
                svg.append(
                    f'<text x="{bx+bw+4:.2f}" y="{by + bar_h/2 + 4:.2f}" '
                    f'font-family="{self.font_family}" font-size="9" '
                    f'fill="{self.color_tick}">{self._fmt_num(val)}</text>'
                )

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  6. STEP CHART  –  Graphique en escalier (séries temporelles discrètes)
    # ════════════════════════════════════════════════════════════════════════

    def step_chart(self, x_data: List[Any],
                   y_data: Union[List[Any], Dict[str, List[Any]]],
                   title: str = "Graphique en escalier",
                   x_label: str = "X", y_label: str = "Y",
                   colors: List[str] = None,
                   fill_area: bool = False) -> str:

        if isinstance(y_data, dict):
            series_names  = list(y_data.keys())
            series_values = [y_data[n] for n in series_names]
        else:
            series_names  = ['Série 1']
            series_values = [y_data]

        n_series = len(series_names)
        palette  = colors or self._get_colors(n_series, 'ggplot2')

        parsed = []
        for sv in series_values:
            pts = []
            for x, y in zip(x_data, sv):
                nx, ny = to_numeric(x), to_numeric(y)
                if isinstance(nx, (int, float)) and isinstance(ny, (int, float)):
                    pts.append((nx, ny))
            parsed.append(sorted(pts, key=lambda p: p[0]))

        all_x = [x for pts in parsed for x, _ in pts]
        all_y = [y for pts in parsed for _, y in pts]
        if not all_x:
            return self._empty_chart("Aucune donnée numérique")

        x_ticks_vals = self._nice_ticks(min(all_x), max(all_x), 5)
        y_ticks_vals = self._nice_ticks(min(0.0, min(all_y)), max(all_y), 5)
        xmin, xmax = x_ticks_vals[0], x_ticks_vals[-1]
        ymin, ymax = y_ticks_vals[0], y_ticks_vals[-1]
        ymax += (ymax - ymin) * 0.05

        x_ticks = [(self._scale_x(v, xmin, xmax), self._fmt_num(v)) for v in x_ticks_vals]
        y_ticks = [(self._scale_y(v, ymin, ymax), self._fmt_num(v)) for v in y_ticks_vals]

        bot_y = self.margin['top'] + self.plot_height

        svg = self._generate_svg_header(title)
        svg.extend(self._generate_axes(x_label, y_label, x_ticks, y_ticks, grid=True))

        for pts, color in zip(parsed, palette):
            dark = self._darken(color, 0.15)
            step_coords = []
            for i, (x, y) in enumerate(pts):
                cx = self._scale_x(x, xmin, xmax)
                cy = self._scale_y(y, ymin, ymax)
                if i > 0:
                    step_coords.append((cx, step_coords[-1][1]))  # horizontal
                step_coords.append((cx, cy))

            d = ' '.join(f"{'M' if j==0 else 'L'} {cx:.2f},{cy:.2f}"
                         for j, (cx, cy) in enumerate(step_coords))
            svg.append(
                f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.5" '
                f'stroke-linejoin="miter" stroke-linecap="square"/>'
            )

            if fill_area:
                poly = ' '.join(f"{cx:.2f},{cy:.2f}" for cx, cy in step_coords)
                poly += f" {step_coords[-1][0]:.2f},{bot_y} {step_coords[0][0]:.2f},{bot_y}"
                svg.append(
                    f'<polygon points="{poly}" fill="{color}" fill-opacity="0.15" stroke="none"/>'
                )

        if n_series > 1:
            svg.extend(self._add_legend(list(zip(series_names, palette))))

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  7. RADAR / SPIDER CHART  –  Graphique en toile d'araignée
    # ════════════════════════════════════════════════════════════════════════

    def radar_chart(self, categories: List[str],
                    data: Union[List[Any], Dict[str, List[Any]]],
                    title: str = "Radar Chart",
                    colors: List[str] = None,
                    fill_alpha: float = 0.20) -> str:

        if isinstance(data, dict):
            series_names  = list(data.keys())
            series_values = [[to_numeric(v) or 0 for v in data[n]] for n in series_names]
        else:
            series_names  = ['Série 1']
            series_values = [[to_numeric(v) or 0 for v in data]]

        n_axes   = len(categories)
        n_series = len(series_names)
        palette  = colors or self._get_colors(n_series, 'ggplot2')

        if n_axes < 3:
            return self._empty_chart("Au moins 3 catégories requises")

        cx   = self.margin['left'] + self.plot_width  / 2
        cy   = self.margin['top']  + self.plot_height / 2
        r    = min(self.plot_width, self.plot_height) / 2 * 0.78
        step = 2 * math.pi / n_axes

        # Max global pour normalisation
        all_vals = [v for sv in series_values for v in sv]
        vmax = max(all_vals) if all_vals else 1

        svg = self._generate_svg_header(title)

        # ── Grilles concentriques (5 niveaux) ─────────────────────────────
        for level in range(1, 6):
            rr = r * level / 5
            pts = ' '.join(
                f"{cx + rr*math.cos(i*step - math.pi/2):.2f},"
                f"{cy + rr*math.sin(i*step - math.pi/2):.2f}"
                for i in range(n_axes)
            )
            svg.append(
                f'<polygon points="{pts}" fill="none" stroke="{self.color_grid}" '
                f'stroke-width="{self.stroke_grid}"/>'
            )

        # ── Axes rayonnants ───────────────────────────────────────────────
        for i in range(n_axes):
            ax = cx + r * math.cos(i * step - math.pi/2)
            ay = cy + r * math.sin(i * step - math.pi/2)
            svg.append(
                f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{ax:.2f}" y2="{ay:.2f}" '
                f'stroke="{self.color_grid}" stroke-width="{self.stroke_grid}"/>'
            )
            # Label axe
            lx = cx + (r + 18) * math.cos(i * step - math.pi/2)
            ly = cy + (r + 18) * math.sin(i * step - math.pi/2)
            svg.append(
                f'<text x="{lx:.2f}" y="{ly:.2f}" text-anchor="middle" '
                f'dominant-baseline="middle" font-family="{self.font_family}" '
                f'font-size="10" font-weight="600" fill="{self.color_axis}">'
                f'{categories[i]}</text>'
            )

        # ── Polygones des séries ──────────────────────────────────────────
        for sv, color in zip(series_values, palette):
            dark = self._darken(color, 0.15)
            pts_list = []
            for i, v in enumerate(sv[:n_axes]):
                ratio = min(v / vmax, 1.0) if vmax else 0
                px = cx + r * ratio * math.cos(i * step - math.pi/2)
                py = cy + r * ratio * math.sin(i * step - math.pi/2)
                pts_list.append((px, py))

            pts = ' '.join(f"{px:.2f},{py:.2f}" for px, py in pts_list)
            svg.append(
                f'<polygon points="{pts}" fill="{color}" fill-opacity="{fill_alpha}" '
                f'stroke="{dark}" stroke-width="2" stroke-linejoin="round"/>'
            )
            for px, py in pts_list:
                svg.append(
                    f'<circle cx="{px:.2f}" cy="{py:.2f}" r="4" '
                    f'fill="white" stroke="{dark}" stroke-width="1.8"/>'
                )

        if n_series > 1:
            svg.extend(self._add_legend(list(zip(series_names, palette))))

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  8. WATERFALL CHART  –  Variation cumulative (bridge chart)
    # ════════════════════════════════════════════════════════════════════════

    def waterfall(self, labels: List[str], values: List[Any],
                  title: str = "Waterfall",
                  x_label: str = "", y_label: str = "Valeur",
                  color_pos: str = "#55A868",
                  color_neg: str = "#C44E52",
                  color_total: str = "#4C72B0",
                  total_indices: List[int] = None) -> str:

        nums = [to_numeric(v) or 0 for v in values]
        n    = len(nums)
        if n == 0:
            return self._empty_chart("Aucune donnée")

        # Calcul des bases et sommets
        total_idx = set(total_indices or [n - 1])
        bases, tops = [], []
        running = 0.0
        for i, v in enumerate(nums):
            if i in total_idx:
                bases.append(0.0)
                tops.append(running + v if i == n - 1 else running)
            else:
                bases.append(running if v >= 0 else running + v)
                tops.append(running + v if v >= 0 else running)
                running += v

        all_vals = bases + tops
        y_ticks_vals = self._nice_ticks(min(all_vals), max(all_vals), 5)
        ymin = y_ticks_vals[0] - (y_ticks_vals[-1] - y_ticks_vals[0]) * 0.05
        ymax = y_ticks_vals[-1] + (y_ticks_vals[-1] - y_ticks_vals[0]) * 0.05

        y_ticks = [(self._scale_y(v, ymin, ymax), self._fmt_num(v)) for v in y_ticks_vals]

        group_w = self.plot_width / n
        gap     = group_w * 0.22
        bar_w   = group_w - gap

        x_ticks = [
            (self.margin['left'] + (i + 0.5) * group_w, str(labels[i])[:14])
            for i in range(n)
        ]

        svg = self._generate_svg_header(title)
        svg.extend(self._generate_axes(x_label, y_label, x_ticks, y_ticks, grid=True))

        # Ligne de base zéro
        y_zero = self._scale_y(0.0, ymin, ymax)
        svg.append(
            f'<line x1="{self.margin["left"]}" y1="{y_zero:.2f}" '
            f'x2="{self.width - self.margin["right"]}" y2="{y_zero:.2f}" '
            f'stroke="{self.color_axis}" stroke-width="1" opacity="0.4"/>'
        )

        prev_top_x = None
        prev_top_y = None

        for i, (base, top, val) in enumerate(zip(bases, tops, nums)):
            bx   = self.margin['left'] + i * group_w + gap / 2
            by   = self._scale_y(top,  ymin, ymax)
            bh   = abs(self._scale_y(base, ymin, ymax) - by)
            bh   = max(bh, 1)

            if i in total_idx:
                color = color_total
            else:
                color = color_pos if val >= 0 else color_neg

            dark  = self._darken(color, 0.15)
            light = self._lighten(color, 0.4)

            svg.append(
                f'<rect x="{bx:.2f}" y="{by:.2f}" width="{bar_w:.2f}" height="{bh:.2f}" '
                f'fill="{color}" fill-opacity="0.88" stroke="{dark}" stroke-width="0.8" rx="3"/>'
            )
            if bh > 5:
                svg.append(
                    f'<rect x="{bx:.2f}" y="{by:.2f}" width="{bar_w:.2f}" height="3" '
                    f'fill="{light}" fill-opacity="0.4" rx="3"/>'
                )

            # Connecteur pointillé entre barres
            top_cx = bx + bar_w
            top_cy = self._scale_y(top if val >= 0 else base, ymin, ymax)
            if prev_top_x is not None and i not in total_idx:
                svg.append(
                    f'<line x1="{prev_top_x:.2f}" y1="{prev_top_y:.2f}" '
                    f'x2="{bx:.2f}" y2="{prev_top_y:.2f}" '
                    f'stroke="{self.color_tick}" stroke-width="1" stroke-dasharray="4,3"/>'
                )
            prev_top_x = top_cx
            prev_top_y = top_cy

            # Label valeur
            sign = "+" if val > 0 and i not in total_idx else ""
            label_y = by - 5 if val >= 0 else by + bh + 13
            svg.append(
                f'<text x="{bx + bar_w/2:.2f}" y="{label_y:.2f}" '
                f'text-anchor="middle" font-family="{self.font_family}" '
                f'font-size="9" fill="{dark}" font-weight="600">'
                f'{sign}{self._fmt_num(val)}</text>'
            )

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  9. LOLLIPOP CHART  –  Points sur tiges (alternative élégante au bar)
    # ════════════════════════════════════════════════════════════════════════

    def lollipop(self, categories: List[str], values: List[Any],
                 title: str = "Lollipop Chart",
                 x_label: str = "", y_label: str = "Valeurs",
                 color: str = None,
                 sort: bool = True,
                 horizontal: bool = True) -> str:

        nums = [to_numeric(v) or 0 for v in values]
        if sort:
            paired     = sorted(zip(nums, categories), reverse=True)
            nums, categories = zip(*paired) if paired else ([], [])
            nums       = list(nums)
            categories = list(categories)

        if not nums:
            return self._empty_chart("Aucune donnée")

        dot_color = color or self._get_colors(1, 'ggplot2')[0]
        dark      = self._darken(dot_color, 0.2)

        n = len(categories)
        x_max = max(nums) * 1.05 or 1
        x_min = min(0.0, min(nums))

        x_ticks_vals = self._nice_ticks(x_min, x_max, 5)
        xmin_t = x_ticks_vals[0]
        xmax_t = x_ticks_vals[-1]
        x_ticks = [(self._scale_x(v, xmin_t, xmax_t), self._fmt_num(v)) for v in x_ticks_vals]

        row_h = self.plot_height / n
        x_zero = self._scale_x(0.0, xmin_t, xmax_t)

        svg = self._generate_svg_header(title)
        svg.extend(self._generate_axes(x_label, y_label, x_ticks=x_ticks, grid=True))

        for i, (cat, val) in enumerate(zip(categories, nums)):
            cy  = self.margin['top'] + (i + 0.5) * row_h
            ex  = self._scale_x(val, xmin_t, xmax_t)

            # Tige
            svg.append(
                f'<line x1="{x_zero:.2f}" y1="{cy:.2f}" x2="{ex:.2f}" y2="{cy:.2f}" '
                f'stroke="{self.color_grid}" stroke-width="1.5"/>'
            )
            # Point
            svg.append(
                f'<circle cx="{ex:.2f}" cy="{cy:.2f}" r="6" '
                f'fill="{dot_color}" stroke="white" stroke-width="2"/>'
            )
            # Label catégorie
            svg.append(
                f'<text x="{self.margin["left"]-6}" y="{cy+4:.2f}" '
                f'text-anchor="end" font-family="{self.font_family}" '
                f'font-size="10" fill="{self.color_axis}">{str(cat)[:22]}</text>'
            )
            # Valeur
            offset = 12 if val >= 0 else -10
            svg.append(
                f'<text x="{ex+offset:.2f}" y="{cy+4:.2f}" '
                f'font-family="{self.font_family}" font-size="9" '
                f'fill="{dark}" font-weight="600">{self._fmt_num(val)}</text>'
            )

        svg.append('</svg>')
        return '\n'.join(svg)

    # ════════════════════════════════════════════════════════════════════════
    #  10. DUAL AXIS LINE CHART  –  Deux axes Y (ex. PIB + inflation)
    # ════════════════════════════════════════════════════════════════════════

    def dual_axis(self, x_data: List[Any],
                  y1_data: List[Any], y2_data: List[Any],
                  y1_label: str = "Y1", y2_label: str = "Y2",
                  title: str = "Double axe",
                  x_label: str = "X",
                  color1: str = "#4C72B0",
                  color2: str = "#DD8452",
                  markers: bool = True) -> str:

        pairs1 = [(to_numeric(x), to_numeric(y)) for x, y in zip(x_data, y1_data)
                  if isinstance(to_numeric(x), (int, float)) and isinstance(to_numeric(y), (int, float))]
        pairs2 = [(to_numeric(x), to_numeric(y)) for x, y in zip(x_data, y2_data)
                  if isinstance(to_numeric(x), (int, float)) and isinstance(to_numeric(y), (int, float))]

        if not pairs1 or not pairs2:
            return self._empty_chart("Données insuffisantes")

        x_all  = [x for x, _ in pairs1 + pairs2]
        y1vals = [y for _, y in pairs1]
        y2vals = [y for _, y in pairs2]

        x_ticks_vals = self._nice_ticks(min(x_all), max(x_all), 5)
        y1_ticks_v   = self._nice_ticks(min(y1vals), max(y1vals), 5)
        y2_ticks_v   = self._nice_ticks(min(y2vals), max(y2vals), 5)

        xmin, xmax  = x_ticks_vals[0], x_ticks_vals[-1]
        y1min, y1max = y1_ticks_v[0], y1_ticks_v[-1]
        y2min, y2max = y2_ticks_v[0], y2_ticks_v[-1]
        y1max += (y1max - y1min) * 0.05
        y2max += (y2max - y2min) * 0.05

        dark1 = self._darken(color1, 0.15)
        dark2 = self._darken(color2, 0.15)

        x_ticks  = [(self._scale_x(v, xmin, xmax), self._fmt_num(v)) for v in x_ticks_vals]
        y1_ticks = [(self._scale_y(v, y1min, y1max), self._fmt_num(v)) for v in y1_ticks_v]

        # Axe Y2 custom (côté droit)
        right_x = self.width - self.margin['right']
        y2_tick_elems = []
        for v in y2_ticks_v:
            yp = self._scale_y(v, y2min, y2max)
            y2_tick_elems.append((yp, self._fmt_num(v)))

        svg = self._generate_svg_header(title)
        svg.extend(self._generate_axes(x_label, y1_label, x_ticks, y1_ticks, grid=True))

        # ── Axe Y2 droit ──────────────────────────────────────────────────
        bot = self.height - self.margin['bottom']
        top = self.margin['top']
        svg.append(
            f'<line x1="{right_x}" y1="{top}" x2="{right_x}" y2="{bot}" '
            f'stroke="{color2}" stroke-width="1.5" stroke-linecap="square"/>'
        )
        for yp, lbl in y2_tick_elems:
            svg.extend([
                f'<line x1="{right_x}" y1="{yp:.2f}" x2="{right_x+5}" y2="{yp:.2f}" '
                f'stroke="{color2}" stroke-width="1"/>',
                f'<text x="{right_x+8}" y="{yp+4:.2f}" font-family="{self.font_family}" '
                f'font-size="10" fill="{color2}">{lbl}</text>',
            ])
        # Label Y2
        mid_y = top + self.plot_height / 2
        svg.append(
            f'<text x="{right_x+30}" y="{mid_y}" text-anchor="middle" '
            f'font-family="{self.font_family}" font-size="12" font-weight="500" '
            f'fill="{color2}" transform="rotate(90 {right_x+30} {mid_y})">{y2_label}</text>'
        )

        # ── Série 1 ────────────────────────────────────────────────────────
        coords1 = sorted([(self._scale_x(x, xmin, xmax), self._scale_y(y, y1min, y1max))
                          for x, y in pairs1], key=lambda p: p[0])
        d1 = ' '.join(f"{'M' if j==0 else 'L'} {cx:.2f},{cy:.2f}"
                      for j, (cx, cy) in enumerate(coords1))
        svg.append(
            f'<path d="{d1}" fill="none" stroke="{color1}" stroke-width="2.8" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
        )
        if markers:
            for cx, cy in coords1:
                svg.append(
                    f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="4.5" '
                    f'fill="white" stroke="{color1}" stroke-width="2"/>'
                )

        # ── Série 2 ────────────────────────────────────────────────────────
        coords2 = sorted([(self._scale_x(x, xmin, xmax), self._scale_y(y, y2min, y2max))
                          for x, y in pairs2], key=lambda p: p[0])
        d2 = ' '.join(f"{'M' if j==0 else 'L'} {cx:.2f},{cy:.2f}"
                      for j, (cx, cy) in enumerate(coords2))
        svg.append(
            f'<path d="{d2}" fill="none" stroke="{color2}" stroke-width="2.8" '
            f'stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="7,3"/>'
        )
        if markers:
            for cx, cy in coords2:
                svg.append(
                    f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="4.5" '
                    f'fill="white" stroke="{color2}" stroke-width="2"/>'
                )

        # Légende
        svg.extend(self._add_legend([(y1_label, color1), (y2_label, color2)]))

        svg.append('</svg>')
        return '\n'.join(svg)


# ═══════════════════════════════════════════════════════════════════════════
#  FONCTIONS D'EXPORT  (signatures inchangées)
# ═══════════════════════════════════════════════════════════════════════════

def save_svg(svg_content: str, filename: str):
    """Sauvegarde le contenu SVG dans un fichier."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg_content)


def svg_to_html(svg_content: str, title: str = "Lista State - Visualisation") -> str:
    """Convertit du SVG en page HTML complète."""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: #F2F3F7;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 24px;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.10), 0 1px 4px rgba(0,0,0,0.06);
            padding: 24px;
            display: inline-block;
        }}
        svg {{
            display: block;
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class="card">
        {svg_content}
    </div>
</body>
</html>"""
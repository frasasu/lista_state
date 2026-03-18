
# 📊 Lista State

**Democratizing Data Analysis**  
*A statistical software project by students of the Université du Burundi*



---

## 🎯 About The Project

**Lista State** is an innovative data analysis software created entirely by students from the *Institut de Statistique Appliquée* at the **Université du Burundi**. Born from a classroom project, this tool was designed to make statistics accessible and understandable for everyone — from fellow students to professional researchers.

The name **"Lista"** reflects our core mission: to bring clarity and order to complex data, transforming raw numbers into meaningful insights that can inform decisions in business, healthcare, education, and public policy.

At its heart, Lista State functions as a **digital laboratory for data**. Users can easily import their information, explore it through simple menus, automatically compute key statistical measures (averages, trends, correlations) and generate visual representations with a single click. All of this is powered by a **custom-built Domain Specific Language (DSL)** that feels intuitive and requires no deep programming background.

What makes Lista State truly special is its **origin**. It stands as a proud testament to the talent, creativity, and academic rigor fostered at the University of Burundi. Developed by passionate young statisticians, this project demonstrates that high-quality, practical solutions can emerge from local initiative and collaboration. Lista State is more than just software; it is a symbol of what Burundian students can achieve and a contribution to the global community of data enthusiasts.

---

## ✨ Key Features

- **🧩 Intuitive DSL** – Write simple commands like `Load`, `Transform`, `Analyze` to manipulate data.
- **📂 Multi‑format Import** – Load CSV, Excel.
- **🔧 Data Wrangling** – Filter, select, drop, join, group by, and create new features with ease.
- **📈 Statistical Analysis** – Compute descriptive statistics, correlations, t‑tests, ANOVA, and more.
- **💾 Portable Sessions** – All your tables, analyses and settings are saved in a single `.lst` file.
- **🎨 Modern UI** – Clean, responsive interface with dark/light themes and customisable appearance.
- **🌍 100% Student‑Made** – Entirely developed by Burundian students as a proof of local innovation.

---

## 🚀 Getting Started

### Prerequisites

- Python **3.8** or higher
- pip (Python package manager)
- Recommended: 8 GB RAM, 2 GB free disk space

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/frasasu/lista_state.git
   cd lista-state
   ```

2. **Run the application**
   ```bash
   python main.py
   ```

### First Steps

- Click **"Data Analysis"** in the left sidebar to open the DSL editor.
- Type your first command, e.g. `Load demo as data` (a built‑in demo table is available).
- Press **Run**  to execute.
- Explore the results in the right panel.

---

## 📝 Example DSL Script

```dsl
# ============================================
# ANALYSE ÉCONOMIQUE DES PAYS AFRICAINS
# ============================================

# 1. CHARGEMENT DES DONNÉES
Load donnees_economiques as eco

# 2. APERÇU GÉNÉRAL
Analyze eco [
    total_lignes = COUNT(*),
    pays_distincts = COUNT(Country),
    annees = COUNT(Year)
] with show=true

# 3. STATISTIQUES GLOBALES
Analyze eco [
    pib_total = SUM(GDP),
    pib_moyen = AVG(GDP),
    pib_max = MAX(GDP),
    pib_min = MIN(GDP),
    inflation_moyenne = AVG(Inflation),
    investissement_moyen = AVG(Investmest),
    export_moyen = AVG(Exports),
    import_moyen = AVG(Imports)
] with show=true

# 4. CRÉATION DE FEATURES (INDICATEURS ÉCONOMIQUES)
Transform eco [
    create_feature(
        balance_commerciale = Exports - Imports,
        taux_ouverture = (Exports + Imports) * 100 / GDP,
        categorie_pib = CASE 
            WHEN GDP < 590 THEN "Très faible"
            WHEN GDP < 21000000000 THEN "Faible"
            WHEN GDP < 11100000000000 THEN "Moyen"
            ELSE "Élevé"
        END,
        categorie_inflation = CASE 
            WHEN Inflation < 2 THEN "Faible"
            WHEN Inflation < 5 THEN "Modérée"
            WHEN Inflation < 10 THEN "Élevée"
            ELSE "Hyperinflation"
        END,
        decennie = CASE 
            WHEN Year < 2010 THEN "2000-2009"
            ELSE "2010-2023"
        END
    )
] as eco_enriched

# 5. STATISTIQUES PAR PAYS
Transform eco_enriched [
    group_by(Country),
    agg(
        pib_moyen = AVG(GDP),
        pib_total = SUM(GDP),
        pib_croissance = (MAX(GDP) - MIN(GDP)) * 100 / MIN(GDP),
        inflation_moyenne = AVG(Inflation),
        investissement_moyen = AVG(Investmest),
        balance_moyenne = AVG(balance_commerciale),
        taux_ouverture_moyen = AVG(taux_ouverture)
    )
] as stats_pays

# 6. TOP 10 PAYS PAR PIB MOYEN
Transform stats_pays [
    create_feature(
        rang = RANK() OVER (ORDER BY pib_moyen DESC)
    ),
    filter(rang <= 10)
] as top10_pib

# 7. PAYS PAR CATÉGORIE DE PIB
Transform eco_enriched [
    group_by(categorie_pib),
    agg(
        nombre_pays = COUNT(Country),
        pib_moyen = AVG(GDP),
        inflation_moyenne = AVG(Inflation)
    )
] as stats_categorie_pib


# 8. ÉVOLUTION TEMPORELLE PAR DÉCENNIE
Transform eco_enriched [
    group_by(decennie),
    agg(
        pib_moyen = AVG(GDP),
        inflation_moyenne = AVG(Inflation),
        investissement_moyen = AVG(Investmest),
        balance_moyenne = AVG(balance_commerciale)
    )
] as stats_decennie


# 9. ANALYSE DE L'INFLATION
Transform eco_enriched [
    group_by(categorie_inflation),
    agg(
        nombre_observations = COUNT(*),
        pays_distincts = COUNT(Country),
        pib_moyen = AVG(GDP),
        investissement_moyen = AVG(Investmest)
    )
] as stats_inflation


# 10. CORRÉLATIONS ÉCONOMIQUES
Analyze eco_enriched [
    corr_pib_invest = CORR(GDP, Investmest),
    corr_pib_inflation = CORR(GDP, Inflation),
    corr_export_import = CORR(Exports, Imports),
    corr_balance_pib = CORR(balance_commerciale, GDP)
] with show=true

# 11. PAYS AVEC FORTE CROISSANCE
Transform stats_pays [
    filter(pib_croissance > 200)
] as pays_croissance_elevee



# 12. ANALYSE PAR PÉRIODE (AVANT/APRÈS 2010)
Transform eco_enriched [
    group_by(decennie),
    agg(
        pib_moyen = AVG(GDP),
        inflation_moyenne = AVG(Inflation),
        investissement_moyen = AVG(Investmest)
    )
] as stats_periode


# 13. PAYS LES PLUS STABLES (FAIBLE INFLATION)
Transform eco_enriched [
    filter(Inflation < 3),
    group_by(Country),
    agg(
        annees_stables = COUNT(*),
        pib_moyen = AVG(GDP)
    )
] as pays_stables


# 14. RELATION INVESTISSEMENT-PIB
Transform eco_enriched [
    create_feature(
        ratio_invest_pib = Investmest * 100 / GDP
    )
] as eco_ratio

Analyze eco_ratio [
    ratio_moyen = AVG(ratio_invest_pib),
    ratio_max = MAX(ratio_invest_pib),
    ratio_min = MIN(ratio_invest_pib)
] with show=true

# 15. RAPPORT FINAL
Analyze eco_enriched [
    pays_analyses = COUNT(Country),
    annees_couvertes = COUNT(Year),
    pib_total_afrique = SUM(GDP),
    pays_plus_riche = MAX(GDP),
    pays_plus_stable = MIN(Inflation)
] with show=true
```




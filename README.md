
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
# Load a sample table
Load employes as emp

# Keep only adults and add a derived column
Transform emp [
    filter(age > 18),
    create_feature(age_group = CASE
        WHEN age < 25 THEN "young"
        WHEN age < 40 THEN "mid"
        ELSE "senior" END
    )
] as enriched

# Compute basic statistics
Analyze enriched [
    total = COUNT(*),
    avg_salary = AVG(salaire),
    oldest = MAX(age)
] with show=true
```




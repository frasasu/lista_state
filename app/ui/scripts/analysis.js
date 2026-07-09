import { DataCore } from "./DataCore.js";

class AnalysisManager{
    constructor() {
        this.core = DataCore;
        this.currentAnalysisName = null;
        this.editor = document.querySelector(".analysis .left .top #editor");
        this.lineNumbers = document.getElementById('lineNumbers');
        this.list_analysis = document.querySelector(".analysis .left .bottom .under .liste-analysis");
    }

    Init(){
        setTimeout(() => {
            if (this.core.payload.analysis) {
                this.displayListAnalysis();
            }

           const first_analysis = Object.keys(this.core.payload.analysis)[0];
           if (first_analysis){
                this.displayAnalysis(first_analysis);
                this.currentAnalysisName = first_analysis;
                this.displayListAnalysis();
           }
        }, 300);
    }

    shwowAnalysis(me){
        this.saveCurrentAnalysis();
        this.currentAnalysisName = me.innerText;
        this.displayAnalysis(me.innerText);
        this.highlightCurrentAnalysis();
    }

    displayAnalysis(name){
       const content_analysis = this.core.payload.analysis[name];
       this.editor.value="";
       this.editor.value = content_analysis || "";
       this.updateLineNumbers();
    }

    displayListAnalysis(){
        const names_analysis = Object.keys(this.core.payload.analysis);
        this.list_analysis.innerHTML = "";

        for (let name of names_analysis){
            let div = document.createElement("div");
            div.className= "div";
            div.innerHTML =`<div class="${name === this.currentAnalysisName ? 'active' : ''}" onclick="analysisManager.shwowAnalysis(this)" ondblclick="analysisManager.deleteAnalysis(this.innerText)">${name}</div>`
            this.list_analysis.appendChild(div);
        }
    }

    /** Met en surbrillance, dans la liste, l'élément correspondant à la session (analyse) courante. */
    highlightCurrentAnalysis() {
        if (!this.list_analysis) return;
        this.list_analysis.querySelectorAll(".div div").forEach(item => {
            item.classList.toggle("active", item.textContent === this.currentAnalysisName);
        });
    }

    updateLineNumbers() {
        const lines = this.editor.value.split('\n').length;
        let lineNumbersHTML = '';
        for (let i = 1; i <= Math.max(lines, 10); i++) {
            lineNumbersHTML += i + '<br>';
        }
        this.lineNumbers.innerHTML = lineNumbersHTML;
    }

    EventListeners() {
        this.updateLineNumbers();

        this.editor.addEventListener('input', () => {
            this.updateLineNumbers();
        });

        this.editor.addEventListener('scroll', () => {
            this.lineNumbers.scrollTop = this.editor.scrollTop;
        });

        document.querySelector(".analysis .left .bottom .box .new").addEventListener("click", (e)=>{
            e.preventDefault();
            document.getElementById("modal-new-analysis").style.display="flex";
        });

        document.querySelector(".analysis .left .bottom .box .delete").addEventListener("click", (e)=>{
            e.preventDefault();
            document.getElementById("modal-delete-analysis").style.display="flex";
        });

        document.querySelector(".modal-delete-analysis .modal-content .btns .cancel").addEventListener("click", (e)=>{
             document.getElementById("modal-delete-analysis").style.display="none";
        });

        document.querySelector(".modal-new-analysis .modal-content .btns .cancel").addEventListener("click", (e)=>{
             document.getElementById("modal-new-analysis").style.display="none";
        });

        document.querySelector(".modal-new-analysis .modal-content .btns .add_new").addEventListener("click", async (e)=>{
             e.preventDefault();

             const name_analysis_new = document.querySelector(".modal-new-analysis .modal-content .input input").value;

             const names_analysis = Object.keys(this.core.payload.analysis);
             if (names_analysis.includes(name_analysis_new)){
                alert(`L'analyse ${name_analysis_new} existe déjà.`);
                return;
             }

            this.core.payload.analysis[name_analysis_new] = "# Nouvelle analyse\nLoad demo as data\nDescribe demo";
            this.currentAnalysisName = name_analysis_new;
            this.displayAnalysis(this.currentAnalysisName);
            this.displayListAnalysis();
            await this.core.save();
            document.getElementById("modal-new-analysis").style.display="none";
            alert(`Le fichier d'analyse ${name_analysis_new} est sauvegardé avec succès.`);
        });

        document.querySelector(".modal-delete-analysis .modal-content .btns .delete").addEventListener("click", async (e)=>{
            e.preventDefault();

            const name_delete = document.querySelector(".modal-delete-analysis .modal-content .input input").value.trim();
            this.deleteAnalysis(name_delete);
        });

        document.addEventListener("keydown", (e)=>{
            if(e.ctrlKey && (e.key === "d" || e.key === "D")){
                e.preventDefault();
                if (this.currentAnalysisName){
                    this.deleteAnalysis(this.currentAnalysisName);
                }
            }
        });

        document.querySelector(".analysis .left .bottom .box .run").addEventListener("click", async (e) => {
            e.preventDefault();
            await this.runAnalysis();
        });

        // Ajouter un écouteur pour la touche Echap en plein écran
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && document.fullscreenElement) {
                document.exitFullscreen();
            }
        });
    }

    async deleteAnalysis(name){
        if(!this.core.sessionName){
            alert("Aucune session selectionnée!");
            return;
        }

        const names_analysis = Object.keys(this.core.payload.analysis);

        if(!names_analysis.includes(name)){
            alert(`Le fichier d'analyse ${name} n'existe pas!`);
            return;
        }

        const confirmDelete = confirm(`Êtes-vous sûr de vouloir supprimer l'analyse "${name}" ?\nCette action est irréversible !`);

        if (!confirmDelete) {
            return;
        }

        delete this.core.payload.analysis[name];
        const remainingAnalysis = Object.keys(this.core.payload.analysis);
        this.currentAnalysisName = remainingAnalysis[0] || null;
        this.displayAnalysis(this.currentAnalysisName);
        this.displayListAnalysis();
        await this.core.save();
        document.getElementById("modal-delete-analysis").style.display="none";
        alert(`L'analyse ${name} supprimée avec succès!`);
    }

    async saveCurrentAnalysis(){
        if(!this.currentAnalysisName){
            alert(`Aucune analyse selectionnée!`);
            return;
        }

        const content_analysis = this.editor.value;
        this.core.payload.analysis[this.currentAnalysisName] = content_analysis;
        await this.core.save();
    }

    async runAnalysis() {
        const code = this.editor.value;
        const settings = this.core.getSettings();
        const runBtn = document.querySelector(".analysis .left .bottom .box .run");

        await this.saveCurrentAnalysis();

        this.showAnalysisLoading();
        if (runBtn) {
            runBtn.classList.add("running");
            runBtn.style.pointerEvents = "none";
        }

        try {
            const result = await pywebview.api.evaluate_dsl(code, this.core.payload);

            if (result.success) {
                this.core.payload = result.datas;
                displayEvaluatorResults(result.messages, settings);
                await this.core.save();
            } else {
                displayEvaluatorResults(result.messages || [{
                    type: 'error',
                    content: result.errors?.join('\n') || 'Erreur inconnue'
                }], settings);
            }
        } catch (error) {
            // Filet de sécurité : si l'appel pywebview échoue lui-même (ex: réponse
            // non sérialisable), on affiche quand même une erreur visible au lieu
            // de laisser le panneau de résultats vide sans aucune explication.
            console.error("Erreur lors de l'exécution de l'analyse:", error);
            displayEvaluatorResults([{
                type: 'error',
                content: `Erreur inattendue lors de l'exécution : ${error?.message || error}`
            }], settings);
        } finally {
            if (runBtn) {
                runBtn.classList.remove("running");
                runBtn.style.pointerEvents = "";
            }
        }
    }

    /** Affiche un indicateur "Analyse en cours..." dans le panneau de résultats. */
    showAnalysisLoading() {
        const rightPanel = document.querySelector(".analysis .right");
        if (!rightPanel) return;

        rightPanel.innerHTML = `
            <div class="analysis-loading">
                <div class="analysis-loading-spinner"></div>
                <div class="analysis-loading-text">Analyse en cours...</div>
            </div>
        `;
    }
}

// ========== FONCTIONS D'AFFICHAGE DES RÉSULTATS ==========

function displayEvaluatorResults(results, settings = {}) {
    const rightPanel = document.querySelector(".analysis .right");
    if (!rightPanel) return;

    rightPanel.innerHTML = "";

    if (!results || results.length === 0) {
        rightPanel.innerHTML = '<div class="no-results">Aucun résultat à afficher</div>';
        return;
    }

    const resultsContainer = document.createElement("div");
    resultsContainer.className = "evaluator-results";

    // Grouper les résultats par type
    const groupedResults = {
        table: [],
        analysis: [],
        stats: [],
        describe: [],
        describe_all: [],
        summary: [],
        svg: [],
        info: [],
        success: [],
        error: []
    };

    results.forEach(result => {
        if (result.type === 'svg') {
            groupedResults.svg.push(result);
        } else if (result.type === 'analysis' && result.content?.type === 'stats') {
            groupedResults.stats.push(result);
        } else if (result.type === 'analysis' && result.content?.type === 'describe') {
            groupedResults.describe.push(result.content);
        } else if (result.type === 'analysis' && result.content?.type === 'describe_all') {
            groupedResults.describe_all.push(result.content);
        } else if (result.type === 'analysis' && result.content?.type === 'summary') {
            groupedResults.summary.push(result.content);
        } else if (groupedResults[result.type]) {
            groupedResults[result.type].push(result);
        } else {
            groupedResults.info.push(result);
        }
    });

    // Afficher les erreurs en premier
    if (groupedResults.error.length > 0) {
        const errorSection = createErrorSection(groupedResults.error);
        resultsContainer.appendChild(errorSection);
    }

    // Afficher les graphiques SVG
    if (groupedResults.svg.length > 0) {
        const svgSection = createSVGSection(groupedResults.svg);
        resultsContainer.appendChild(svgSection);
    }

    // Afficher les tables
    if (groupedResults.table.length > 0) {
        const tableSection = createTableSection(groupedResults.table);
        resultsContainer.appendChild(tableSection);
    }

    // Afficher les résumés
    if (groupedResults.summary.length > 0) {
        groupedResults.summary.forEach(summary => {
            const summarySection = createSummarySection(summary);
            resultsContainer.appendChild(summarySection);
        });
    }

    // Afficher les statistiques descriptives
    if (groupedResults.describe.length > 0) {
        groupedResults.describe.forEach(describe => {
            const describeSection = createDescribeSection(describe);
            resultsContainer.appendChild(describeSection);
        });
    }

    // Afficher les statistiques complètes
    if (groupedResults.describe_all.length > 0) {
        groupedResults.describe_all.forEach(describeAll => {
            const describeAllSection = createDescribeAllSection(describeAll);
            resultsContainer.appendChild(describeAllSection);
        });
    }

    // Afficher les analyses standards
    if (groupedResults.analysis.length > 0) {
        const analysisSection = createAnalysisSection(groupedResults.analysis);
        resultsContainer.appendChild(analysisSection);
    }

    // Afficher les statistiques avancées
    if (groupedResults.stats.length > 0) {
        const statsSection = createStatsSection(groupedResults.stats);
        resultsContainer.appendChild(statsSection);
    }

    // Afficher les informations et succès
    if (groupedResults.success.length > 0 || groupedResults.info.length > 0) {
        const infoSection = createInfoSection([...groupedResults.success, ...groupedResults.info]);
        resultsContainer.appendChild(infoSection);
    }

    rightPanel.appendChild(resultsContainer);
}

// ========== SECTION POUR LES STATISTIQUES DESCRIPTIVES ==========

function createDescribeSection(results) {
    const section = document.createElement("div");
    section.className = "results-section describe-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = `📊 Statistiques descriptives - ${results.target || 'Table'}`;
    section.appendChild(title);
    addSectionCopyButton(title, () => section);

    const results_data = results.results || {};
    const format = results.format || 'table';

    if (Object.keys(results_data).length === 0) {
        const emptyMsg = document.createElement("div");
        emptyMsg.className = "empty-message";
        emptyMsg.textContent = "Aucune colonne numérique trouvée";
        section.appendChild(emptyMsg);
        return section;
    }

    if (format === 'table') {
        // Format tableau
        const tableWrapper = document.createElement("div");
        tableWrapper.className = "table-wrapper stats-table";

        const table = document.createElement("table");
        table.className = "stats-table";

        // En-tête
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");
        
        const thMetric = document.createElement("th");
        thMetric.textContent = "Métrique";
        headerRow.appendChild(thMetric);
        
        Object.keys(results_data).forEach(col => {
            const th = document.createElement("th");
            th.textContent = col;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Corps
        const tbody = document.createElement("tbody");
        
        // Liste des métriques
        const metrics = [
            { key: 'count', label: 'Count' },
            { key: 'mean', label: 'Mean' },
            { key: 'std', label: 'Std Dev' },
            { key: 'min', label: 'Min' },
            { key: '25%', label: '25%' },
            { key: '50%', label: '50% (Median)' },
            { key: '75%', label: '75%' },
            { key: 'max', label: 'Max' },
            { key: 'skew', label: 'Skewness' },
            { key: 'kurt', label: 'Kurtosis' }
        ];

        metrics.forEach(metric => {
            const row = document.createElement("tr");
            
            const tdMetric = document.createElement("td");
            tdMetric.className = "metric-name";
            tdMetric.textContent = metric.label;
            row.appendChild(tdMetric);
            
            Object.keys(results_data).forEach(col => {
                const td = document.createElement("td");
                const value = results_data[col]?.[metric.key];
                
                if (value === undefined || value === null || isNaN(value)) {
                    td.textContent = "-";
                    td.className = "null-value";
                } else if (typeof value === 'number') {
                    td.textContent = value.toFixed(4);
                    td.className = "number-value";
                } else {
                    td.textContent = value;
                }
                
                row.appendChild(td);
            });
            
            tbody.appendChild(row);
        });

        table.appendChild(tbody);
        tableWrapper.appendChild(table);
        section.appendChild(tableWrapper);

    } else {
        // Format cartes
        const cardsGrid = document.createElement("div");
        cardsGrid.className = "stats-cards-grid";

        Object.entries(results_data).forEach(([colName, stats]) => {
            const card = document.createElement("div");
            card.className = "stats-card";

            const cardHeader = document.createElement("div");
            cardHeader.className = "stats-card-header";
            cardHeader.innerHTML = `<h3>${colName}</h3>`;
            card.appendChild(cardHeader);

            const cardBody = document.createElement("div");
            cardBody.className = "stats-card-body";

            const statsList = [
                { label: 'Count', value: stats.count },
                { label: 'Mean', value: stats.mean },
                { label: 'Std Dev', value: stats.std },
                { label: 'Min', value: stats.min },
                { label: '25%', value: stats['25%'] },
                { label: 'Median', value: stats['50%'] },
                { label: '75%', value: stats['75%'] },
                { label: 'Max', value: stats.max },
                { label: 'Skewness', value: stats.skew },
                { label: 'Kurtosis', value: stats.kurt }
            ];

            statsList.forEach(stat => {
                const statRow = document.createElement("div");
                statRow.className = "stat-row";
                
                const statLabel = document.createElement("span");
                statLabel.className = "stat-label";
                statLabel.textContent = stat.label + ":";
                
                const statValue = document.createElement("span");
                statValue.className = "stat-value";
                
                if (stat.value === undefined || stat.value === null || isNaN(stat.value)) {
                    statValue.textContent = "-";
                    statValue.classList.add("null-value");
                } else if (typeof stat.value === 'number') {
                    statValue.textContent = stat.value.toFixed(4);
                } else {
                    statValue.textContent = stat.value;
                }
                
                statRow.appendChild(statLabel);
                statRow.appendChild(statValue);
                cardBody.appendChild(statRow);
            });

            card.appendChild(cardBody);
            cardsGrid.appendChild(card);
        });

        section.appendChild(cardsGrid);
    }

    return section;
}

// ========== SECTION POUR LES STATISTIQUES COMPLÈTES ==========

function createDescribeAllSection(results) {
    const section = document.createElement("div");
    section.className = "results-section describe-all-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = `📈 Statistiques complètes - ${results.target || 'Table'}`;
    section.appendChild(title);
    addSectionCopyButton(title, () => section);

    // Informations générales
    if (results.shape) {
        const infoBar = document.createElement("div");
        infoBar.className = "info-bar";
        infoBar.innerHTML = `
            <span class="info-badge">📊 ${results.shape[0]} lignes</span>
            <span class="info-badge">📋 ${results.shape[1]} colonnes</span>
        `;
        section.appendChild(infoBar);
    }

    const results_data = results.results || {};
    const format = results.format || 'detailed';

    const tabsContainer = document.createElement("div");
    tabsContainer.className = "stats-tabs";

    const numericTab = document.createElement("div");
    numericTab.className = "stats-tab active";
    numericTab.textContent = "Numériques";
    
    const categoricalTab = document.createElement("div");
    categoricalTab.className = "stats-tab";
    categoricalTab.textContent = "Catégorielles";

    tabsContainer.appendChild(numericTab);
    tabsContainer.appendChild(categoricalTab);
    section.appendChild(tabsContainer);

    // Conteneur pour les données numériques
    const numericContainer = document.createElement("div");
    numericContainer.className = "stats-content active";

    // Conteneur pour les données catégorielles
    const categoricalContainer = document.createElement("div");
    categoricalContainer.className = "stats-content";

    // Séparer les colonnes par type
    const numericCols = [];
    const categoricalCols = [];

    Object.entries(results_data).forEach(([colName, info]) => {
        if (info.type === 'numeric') {
            numericCols.push([colName, info]);
        } else {
            categoricalCols.push([colName, info]);
        }
    });

    // Afficher les colonnes numériques
    if (numericCols.length > 0) {
        const numericGrid = document.createElement("div");
        numericGrid.className = "stats-cards-grid";

        numericCols.forEach(([colName, stats]) => {
            const card = document.createElement("div");
            card.className = "stats-card numeric";

            const cardHeader = document.createElement("div");
            cardHeader.className = "stats-card-header";
            cardHeader.innerHTML = `<h3>${colName}</h3><span class="col-type">🔢 numérique</span>`;
            card.appendChild(cardHeader);

            const cardBody = document.createElement("div");
            cardBody.className = "stats-card-body";

            const statsList = [
                { label: 'Count', value: stats.count },
                { label: 'Missing', value: stats.missing },
                { label: 'Mean', value: stats.mean },
                { label: 'Std Dev', value: stats.std },
                { label: 'Min', value: stats.min },
                { label: 'Max', value: stats.max },
                { label: 'Median', value: stats.median }
            ];

            statsList.forEach(stat => {
                const statRow = document.createElement("div");
                statRow.className = "stat-row";
                
                const statLabel = document.createElement("span");
                statLabel.className = "stat-label";
                statLabel.textContent = stat.label + ":";
                
                const statValue = document.createElement("span");
                statValue.className = "stat-value";
                
                if (stat.value === undefined || stat.value === null || isNaN(stat.value)) {
                    statValue.textContent = "-";
                    statValue.classList.add("null-value");
                } else if (typeof stat.value === 'number') {
                    statValue.textContent = stat.value.toFixed(4);
                } else {
                    statValue.textContent = stat.value;
                }
                
                statRow.appendChild(statLabel);
                statRow.appendChild(statValue);
                cardBody.appendChild(statRow);
            });

            card.appendChild(cardBody);
            numericGrid.appendChild(card);
        });

        numericContainer.appendChild(numericGrid);
    } else {
        const emptyMsg = document.createElement("div");
        emptyMsg.className = "empty-message";
        emptyMsg.textContent = "Aucune colonne numérique";
        numericContainer.appendChild(emptyMsg);
    }

    // Afficher les colonnes catégorielles
    if (categoricalCols.length > 0) {
        const categoricalGrid = document.createElement("div");
        categoricalGrid.className = "stats-cards-grid";

        categoricalCols.forEach(([colName, stats]) => {
            const card = document.createElement("div");
            card.className = "stats-card categorical";

            const cardHeader = document.createElement("div");
            cardHeader.className = "stats-card-header";
            cardHeader.innerHTML = `<h3>${colName}</h3><span class="col-type">🏷️ catégorielle</span>`;
            card.appendChild(cardHeader);

            const cardBody = document.createElement("div");
            cardBody.className = "stats-card-body";

            const statsList = [
                { label: 'Count', value: stats.count },
                { label: 'Missing', value: stats.missing },
                { label: 'Unique', value: stats.unique },
                { label: 'Top', value: stats.top },
                { label: 'Freq', value: stats.freq },
                { label: 'Entropy', value: stats.entropy }
            ];

            statsList.forEach(stat => {
                const statRow = document.createElement("div");
                statRow.className = "stat-row";
                
                const statLabel = document.createElement("span");
                statLabel.className = "stat-label";
                statLabel.textContent = stat.label + ":";
                
                const statValue = document.createElement("span");
                statValue.className = "stat-value";
                
                if (stat.value === undefined || stat.value === null) {
                    statValue.textContent = "-";
                } else if (typeof stat.value === 'number' && stat.label === 'Entropy') {
                    statValue.textContent = stat.value.toFixed(4);
                } else {
                    statValue.textContent = stat.value;
                }
                
                statRow.appendChild(statLabel);
                statRow.appendChild(statValue);
                cardBody.appendChild(statRow);
            });

            card.appendChild(cardBody);
            categoricalGrid.appendChild(card);
        });

        categoricalContainer.appendChild(categoricalGrid);
    } else {
        const emptyMsg = document.createElement("div");
        emptyMsg.className = "empty-message";
        emptyMsg.textContent = "Aucune colonne catégorielle";
        categoricalContainer.appendChild(emptyMsg);
    }

    section.appendChild(numericContainer);
    section.appendChild(categoricalContainer);

    // Gestion des onglets
    numericTab.addEventListener('click', () => {
        numericTab.classList.add('active');
        categoricalTab.classList.remove('active');
        numericContainer.classList.add('active');
        categoricalContainer.classList.remove('active');
    });

    categoricalTab.addEventListener('click', () => {
        categoricalTab.classList.add('active');
        numericTab.classList.remove('active');
        categoricalContainer.classList.add('active');
        numericContainer.classList.remove('active');
    });

    return section;
}

// ========== SECTION POUR LE RÉSUMÉ ==========

function createSummarySection(results) {
    const section = document.createElement("div");
    section.className = "results-section summary-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = `📋 Résumé - ${results.target || 'Table'}`;
    section.appendChild(title);
    addSectionCopyButton(title, () => section);

    const results_data = results.results || {};

    const summaryGrid = document.createElement("div");
    summaryGrid.className = "summary-grid";

    const metrics = [
        { label: 'Lignes', value: results_data.shape?.[0] },
        { label: 'Colonnes', value: results_data.shape?.[1] },
        { label: 'Total cellules', value: results_data.total_cells },
        { label: 'Cellules manquantes', value: results_data.missing_cells },
        { label: 'Colonnes numériques', value: results_data.numeric_columns },
        { label: 'Colonnes catégorielles', value: results_data.categorical_columns }
    ];

    metrics.forEach(metric => {
        const card = document.createElement("div");
        card.className = "summary-card";

        const value = document.createElement("div");
        value.className = "summary-value";
        value.textContent = metric.value !== undefined ? metric.value : '-';

        const label = document.createElement("div");
        label.className = "summary-label";
        label.textContent = metric.label;

        card.appendChild(value);
        card.appendChild(label);
        summaryGrid.appendChild(card);
    });

    section.appendChild(summaryGrid);

    // Liste des colonnes
    if (results_data.columns && results_data.columns.length > 0) {
        const columnsList = document.createElement("div");
        columnsList.className = "columns-list";

        const columnsTitle = document.createElement("div");
        columnsTitle.className = "columns-title";
        columnsTitle.textContent = "Colonnes:";
        columnsList.appendChild(columnsTitle);

        const columnsGrid = document.createElement("div");
        columnsGrid.className = "columns-grid";

        results_data.columns.forEach(col => {
            const colTag = document.createElement("span");
            colTag.className = "column-tag";
            colTag.textContent = col;
            columnsGrid.appendChild(colTag);
        });

        columnsList.appendChild(columnsGrid);
        section.appendChild(columnsList);
    }

    return section;
}

// ========== SECTION POUR LES GRAPHIQUES SVG ==========

function createSVGSection(svgs) {
    const section = document.createElement("div");
    section.className = "results-section svg-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '📈 Graphiques';
    section.appendChild(title);

    svgs.forEach((svg, index) => {
        const card = document.createElement("div");
        card.className = "svg-card";
        card.dataset.index = index;

        const header = document.createElement("div");
        header.className = "svg-header";
        header.innerHTML = `<span class="svg-title">${svg.content?.title || 'Graphique'}</span>`;
        card.appendChild(header);

        const container = document.createElement("div");
        container.className = "svg-container";
        
        // Injection directe du SVG
        container.innerHTML = svg.content?.content || '';
        
        // Ajouter des contrôles
        const controls = document.createElement("div");
        controls.className = "svg-controls";
        
        // Créer les boutons avec des gestionnaires d'événements directs
        const downloadBtn = document.createElement("button");
        downloadBtn.innerHTML = '💾 Télécharger';
        downloadBtn.title = "Télécharger l'image au format PNG dans le dossier Téléchargements";
        downloadBtn.onclick = function(e) {
            e.stopPropagation();
            downloadSVGAsPNG(container, svg.content?.title);
        };

        const fullscreenBtn = document.createElement("button");
        fullscreenBtn.innerHTML = '🖥️ Plein écran';
        fullscreenBtn.onclick = function(e) {
            e.stopPropagation();
            toggleFullscreen(container);
        };

        controls.appendChild(downloadBtn);
        controls.appendChild(fullscreenBtn);
        
        card.appendChild(controls);
        card.appendChild(container);
        section.appendChild(card);
    });

    return section;
}

// ========== SECTION POUR LES STATISTIQUES AVANCÉES ==========

function createStatsSection(stats) {
    const section = document.createElement("div");
    section.className = "results-section stats-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '📊 Statistiques avancées';
    section.appendChild(title);
    addSectionCopyButton(title, () => section);

    stats.forEach(stat => {
        const card = document.createElement("div");
        card.className = "stats-card";

        const header = document.createElement("div");
        header.className = "stats-header";
        header.innerHTML = `
            <span class="stats-name">${stat.content?.name || 'Analyse statistique'}</span>
            <span class="stats-target">cible: ${stat.content?.target || '?'}</span>
        `;
        card.appendChild(header);

        if (stat.content?.results) {
            const grid = document.createElement("div");
            grid.className = "stats-results-grid";

            Object.entries(stat.content.results).forEach(([key, value]) => {
                const item = document.createElement("div");
                item.className = "stats-result-item";

                let formattedValue = value;
                if (typeof value === 'number') {
                    formattedValue = value.toFixed(6);
                } else if (value === null || value === undefined) {
                    formattedValue = "NULL";
                } else if (typeof value === 'boolean') {
                    formattedValue = value ? "Vrai" : "Faux";
                } else if (typeof value === 'object') {
                    const values = []
                    Object.entries(value).forEach(([key,val])=>{
                        let content = `${key} = ${val}`;
                           values.push(content);
                    });

                    formattedValue = values.join(';');
                }

                item.innerHTML = `
                    <span class="result-key">${key}:</span>
                    <span class="result-value">${formattedValue}</span>
                `;
                grid.appendChild(item);
            });

            card.appendChild(grid);
        }

        section.appendChild(card);
    });

    return section;
}


// ========== FONCTIONS EXISTANTES ==========

function createErrorSection(errors) {
    const section = document.createElement("div");
    section.className = "results-section error-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '❌ Erreurs';
    section.appendChild(title);
    addSectionCopyButton(title, () => section);

    errors.forEach(error => {
        const errorCard = document.createElement("div");
        errorCard.className = "error-card";

        let errorMessage = error.content;
        if (typeof error.content === 'object') {
            errorMessage = error.content.message || JSON.stringify(error.content);
        }

        errorCard.innerHTML = `
            <div class="error-line">Ligne ${error.line || '?'}</div>
            <div class="error-message">${errorMessage}</div>
        `;
        section.appendChild(errorCard);
    });

    return section;
}

function createTableSection(tables) {
    const section = document.createElement("div");
    section.className = "results-section table-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '📊 Tables';
    section.appendChild(title);
    addSectionCopyButton(title, () => section);

    tables.forEach(table => {
        const tableCard = document.createElement("div");
        tableCard.className = "table-card";

        const tableHeader = document.createElement("div");
        tableHeader.className = "table-header";
        tableHeader.innerHTML = `
            <span class="table-name">${table.content.name || 'Table'}</span>
            <span class="table-dimensions">${table.content.shape?.[0] || 0} lignes × ${table.content.shape?.[1] || 0} colonnes</span>
        `;
        tableHeader.appendChild(createCopyButton(() => tableCard, '📋 Copier le tableau'));
        tableCard.appendChild(tableHeader);

        if (table.content.preview && table.content.preview.length > 0) {
            const tableWrapper = document.createElement("div");
            tableWrapper.className = "table-wrapper";

            const htmlTable = document.createElement("table");
            htmlTable.className = "data-preview";

            const thead = document.createElement("thead");
            const headerRow = document.createElement("tr");

            const thIndex = document.createElement("th");
            thIndex.textContent = "#";
            headerRow.appendChild(thIndex);

            table.content.columns.forEach(col => {
                const th = document.createElement("th");
                th.textContent = col;
                th.title = `Type: ${table.content.types?.[table.content.columns.indexOf(col)] || 'unknown'}`;
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            htmlTable.appendChild(thead);

            const tbody = document.createElement("tbody");
            table.content.preview.forEach((row, idx) => {
                const tr = document.createElement("tr");

                const tdIndex = document.createElement("td");
                tdIndex.className = "row-index";
                tdIndex.textContent = idx + 1;
                tr.appendChild(tdIndex);

                table.content.columns.forEach(col => {
                    const td = document.createElement("td");
                    let value = row[col];

                    if (value === null || value === undefined) {
                        td.textContent = "NULL";
                        td.className = "null-value";
                    } else if (typeof value === 'boolean') {
                        td.textContent = value ? "✓" : "✗";
                        td.className = value ? "boolean-true" : "boolean-false";
                    } else if (typeof value === 'number') {
                        td.textContent = value;
                        td.className = "number-value";
                    } else {
                        td.textContent = String(value);
                    }

                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            htmlTable.appendChild(tbody);

            tableWrapper.appendChild(htmlTable);
            tableCard.appendChild(tableWrapper);

            if (table.content.shape && table.content.shape[0] > table.content.preview.length) {
                const moreInfo = document.createElement("div");
                moreInfo.className = "table-more-info";
                moreInfo.textContent = `... et ${table.content.shape[0] - table.content.preview.length} lignes supplémentaires`;
                tableCard.appendChild(moreInfo);
            }
        }

        section.appendChild(tableCard);
    });

    return section;
}

function createAnalysisSection(analyses) {
    const section = document.createElement("div");
    section.className = "results-section analysis-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '📈 Analyses';
    section.appendChild(title);
    addSectionCopyButton(title, () => section);

    analyses.forEach(analysis => {
        const analysisCard = document.createElement("div");
        analysisCard.className = "analysis-card";

        const analysisHeader = document.createElement("div");
        analysisHeader.className = "analysis-header";
        analysisHeader.innerHTML = `
            <span class="analysis-name">${analysis.content.name || 'Analyse'}</span>
            <span class="analysis-target">cible: ${analysis.content.target || '?'}</span>
        `;
        analysisCard.appendChild(analysisHeader);

        if (analysis.content.results) {
            const resultsGrid = document.createElement("div");
            resultsGrid.className = "analysis-results-grid";

            Object.entries(analysis.content.results).forEach(([key, value]) => {
                const resultItem = document.createElement("div");
                resultItem.className = "analysis-result-item";

                let formattedValue = value;
                if (typeof value === 'number') {
                    formattedValue = value.toFixed(4);
                } else if (value === null || value === undefined) {
                    formattedValue = "NULL";
                } else if (typeof value === 'boolean') {
                    formattedValue = value ? "Vrai" : "Faux";
                } else if (typeof value === 'object') {
                    formattedValue = JSON.stringify(value);
                }

                resultItem.innerHTML = `
                    <span class="result-key">${key}:</span>
                    <span class="result-value">${formattedValue}</span>
                `;
                resultsGrid.appendChild(resultItem);
            });

            analysisCard.appendChild(resultsGrid);
        }

        if (analysis.content.options && Object.keys(analysis.content.options).length > 0) {
            const options = document.createElement("div");
            options.className = "analysis-options";
            options.innerHTML = `<span>Options: ${JSON.stringify(analysis.content.options)}</span>`;
            analysisCard.appendChild(options);
        }

        section.appendChild(analysisCard);
    });

    return section;
}

function createInfoSection(messages) {
    const section = document.createElement("div");
    section.className = "results-section info-section";

    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = 'ℹ️ Informations';
    section.appendChild(title);
    addSectionCopyButton(title, () => section);

    messages.forEach(msg => {
        const infoCard = document.createElement("div");
        infoCard.className = `info-card ${msg.type}`;

        let icon = '📌';
        if (msg.type === 'success') icon = '✅';
        if (msg.type === 'info') icon = 'ℹ️';

        infoCard.innerHTML = `
            <span class="info-icon">${icon}</span>
            <span class="info-message">${msg.content || msg.content?.message || JSON.stringify(msg.content)}</span>
            ${msg.line ? `<span class="info-line">ligne ${msg.line}</span>` : ''}
        `;
        section.appendChild(infoCard);
    });

    return section;
}

// ========== FONCTIONS UTILITAIRES DE COPIE (POUR LES RAPPORTS) ==========
// Ces fonctions permettent de copier un tableau ou un bloc de résultats
// dans le presse-papiers, en conservant la mise en forme (couleurs, gras...)
// afin de pouvoir le coller directement dans un éditeur comme Word.

/**
 * Recopie récursivement les styles calculés (couleur, fond, bordures, etc.)
 * en tant que style inline sur le clone, pour que la mise en forme survive
 * au collage dans un éditeur externe qui n'a pas accès à notre feuille CSS.
 */
function inlineComputedStyles(source, clone) {
    const PROPS_TO_INLINE = [
        'color', 'background-color', 'background', 'font-weight', 'font-style',
        'font-size', 'font-family', 'text-align', 'text-decoration-line',
        'border-top', 'border-right', 'border-bottom', 'border-left',
        'border-collapse', 'border-spacing', 'border-radius',
        'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
        'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
        'vertical-align', 'white-space', 'width'
    ];

    const computed = window.getComputedStyle(source);
    let styleStr = clone.getAttribute('style') || '';
    PROPS_TO_INLINE.forEach(prop => {
        const value = computed.getPropertyValue(prop);
        if (value) styleStr += `${prop}:${value};`;
    });
    clone.setAttribute('style', styleStr);

    const sourceChildren = source.children;
    const cloneChildren = clone.children;
    for (let i = 0; i < sourceChildren.length; i++) {
        if (cloneChildren[i]) inlineComputedStyles(sourceChildren[i], cloneChildren[i]);
    }
}

/**
 * Copie un élément DOM (tableau, carte de résultats, section entière, ...)
 * dans le presse-papiers au format riche (HTML, avec couleurs/mise en forme)
 * et texte brut en secours, pour un collage direct dans Word / un éditeur.
 */
async function copyElementToClipboard(element, buttonEl) {
    if (!element) return;

    try {
        const clone = element.cloneNode(true);

        // Ne pas copier les boutons de contrôle (copier/télécharger/plein écran...)
        clone.querySelectorAll('.no-copy').forEach(el => el.remove());

        inlineComputedStyles(element, clone);

        const htmlContent = `<div style="font-family: Arial, Helvetica, sans-serif; font-size: 13px;">${clone.outerHTML}</div>`;
        const textContent = element.innerText;

        if (navigator.clipboard && window.ClipboardItem) {
            const item = new ClipboardItem({
                'text/html': new Blob([htmlContent], { type: 'text/html' }),
                'text/plain': new Blob([textContent], { type: 'text/plain' })
            });
            await navigator.clipboard.write([item]);
        } else if (navigator.clipboard) {
            await navigator.clipboard.writeText(textContent);
        } else {
            throw new Error('Presse-papiers non disponible');
        }

        if (buttonEl) {
            const original = buttonEl.innerHTML;
            buttonEl.innerHTML = '✅ Copié !';
            buttonEl.disabled = true;
            setTimeout(() => {
                buttonEl.innerHTML = original;
                buttonEl.disabled = false;
            }, 2000);
        }
    } catch (error) {
        console.error("Erreur lors de la copie:", error);
        alert("Erreur lors de la copie dans le presse-papiers");
    }
}

/**
 * Crée un bouton de copie réutilisable. `getTarget` peut être un élément DOM
 * ou une fonction retournant l'élément à copier (utile quand l'élément est
 * créé après le bouton).
 */
function createCopyButton(getTarget, label = '📋 Copier') {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'copy-btn no-copy';
    btn.innerHTML = label;
    btn.title = "Copier pour coller dans un rapport (Word, etc.)";
    btn.onclick = function(e) {
        e.stopPropagation();
        const target = typeof getTarget === 'function' ? getTarget() : getTarget;
        copyElementToClipboard(target, btn);
    };
    return btn;
}

/**
 * Ajoute un bouton de copie dans l'en-tête (section-title) d'une section de
 * résultats, permettant de copier tout le contenu de la section (hors titre)
 * en une seule fois.
 */
function addSectionCopyButton(titleEl, contentGetter) {
    titleEl.classList.add('section-title-with-copy');
    titleEl.appendChild(createCopyButton(contentGetter, '📋 Copier'));
}

// ========== FONCTIONS UTILITAIRES POUR LES SVG ==========

// Fonction de téléchargement : convertit le SVG en image PNG et la télécharge
// directement dans le dossier "Téléchargements" de l'utilisateur (comportement
// natif du navigateur/webview déclenché par l'attribut download d'un <a>).
function downloadSVGAsPNG(container, titleHint) {
    const svg = container.querySelector('svg');
    if (!svg) {
        console.error("SVG non trouvé");
        alert("Impossible de trouver le graphique à télécharger");
        return;
    }

    try {
        const svgClone = svg.cloneNode(true);

        if (!svgClone.getAttribute('xmlns')) {
            svgClone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
        }

        // Déterminer une taille correcte pour le rendu (attribut, viewBox ou taille réelle affichée)
        const bbox = svg.getBoundingClientRect();
        let width = parseFloat(svgClone.getAttribute('width')) || bbox.width;
        let height = parseFloat(svgClone.getAttribute('height')) || bbox.height;

        if (!width || !height) {
            const viewBox = svgClone.getAttribute('viewBox');
            if (viewBox) {
                const parts = viewBox.split(/\s+/).map(Number);
                width = width || parts[2] || 800;
                height = height || parts[3] || 600;
            }
        }

        width = width || 800;
        height = height || 600;

        svgClone.setAttribute('width', width);
        svgClone.setAttribute('height', height);

        const serializer = new XMLSerializer();
        const source = '<?xml version="1.0" encoding="UTF-8"?>\n' + serializer.serializeToString(svgClone);

        const svgBlob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' });
        const svgUrl = URL.createObjectURL(svgBlob);

        const img = new Image();
        img.onload = function() {
            try {
                // Facteur d'échelle pour obtenir un PNG net (haute résolution)
                const scale = 2;
                const canvas = document.createElement('canvas');
                canvas.width = width * scale;
                canvas.height = height * scale;

                const ctx = canvas.getContext('2d');
                // Fond blanc pour éviter un rendu transparent/noir une fois collé ailleurs
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.scale(scale, scale);
                ctx.drawImage(img, 0, 0, width, height);

                URL.revokeObjectURL(svgUrl);

                canvas.toBlob(function(pngBlob) {
                    if (!pngBlob) {
                        alert("Erreur lors de la génération du fichier PNG");
                        return;
                    }

                    const safeName = (titleHint || 'graphique')
                        .toString()
                        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
                        .replace(/[^a-zA-Z0-9-_]+/g, '_')
                        .replace(/^_+|_+$/g, '') || 'graphique';
                    const filename = `${safeName}.png`;

                    // Priorité à l'API native pywebview (fiable sur toutes les
                    // plateformes desktop : ouvre une vraie boîte de dialogue
                    // "Enregistrer sous", proposant le dossier Téléchargements).
                    if (typeof pywebview !== 'undefined' && pywebview.api && pywebview.api.save_chart_image) {
                        const reader = new FileReader();
                        reader.onload = async function() {
                            try {
                                const result = await pywebview.api.save_chart_image(reader.result, filename);
                                if (result && result.error) {
                                    alert(`Erreur lors de l'enregistrement de l'image : ${result.error}`);
                                }
                                // result.cancelled === true -> l'utilisateur a annulé, rien à faire
                            } catch (err) {
                                console.error("Erreur save_chart_image:", err);
                                alert("Erreur lors de l'enregistrement de l'image");
                            }
                        };
                        reader.onerror = function() {
                            alert("Erreur lors de la lecture de l'image générée");
                        };
                        reader.readAsDataURL(pngBlob);
                        return;
                    }

                    // Repli navigateur classique (utile hors de l'application desktop,
                    // par exemple pendant le développement dans un simple navigateur).
                    const pngUrl = URL.createObjectURL(pngBlob);
                    const a = document.createElement('a');
                    a.href = pngUrl;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);

                    setTimeout(() => URL.revokeObjectURL(pngUrl), 200);
                }, 'image/png');
            } catch (err) {
                console.error("Erreur lors de la conversion en PNG:", err);
                alert("Erreur lors du téléchargement de l'image");
            }
        };

        img.onerror = function(err) {
            console.error("Erreur de chargement du SVG pour conversion:", err);
            URL.revokeObjectURL(svgUrl);
            alert("Erreur lors du téléchargement de l'image");
        };

        img.src = svgUrl;

    } catch (error) {
        console.error("Erreur lors du téléchargement:", error);
        alert("Erreur lors du téléchargement de l'image");
    }
}

// Fonction plein écran améliorée
function toggleFullscreen(container) {
    if (!container) return;

    if (!document.fullscreenElement) {
        // Passer en plein écran
        if (container.requestFullscreen) {
            container.requestFullscreen();
        } else if (container.webkitRequestFullscreen) { // Safari
            container.webkitRequestFullscreen();
        } else if (container.msRequestFullscreen) { // IE/Edge
            container.msRequestFullscreen();
        }
        
        // Ajouter un bouton de sortie
        const exitBtn = document.createElement('button');
        exitBtn.className = 'fullscreen-exit-btn';
        exitBtn.innerHTML = '✖ Quitter le plein écran';
        exitBtn.style.position = 'fixed';
        exitBtn.style.top = '20px';
        exitBtn.style.right = '20px';
        exitBtn.style.zIndex = '10000';
        exitBtn.style.padding = '10px 20px';
        exitBtn.style.background = '#ff6b6b';
        exitBtn.style.color = 'white';
        exitBtn.style.border = 'none';
        exitBtn.style.borderRadius = '5px';
        exitBtn.style.cursor = 'pointer';
        exitBtn.style.fontSize = '16px';
        exitBtn.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
        
        exitBtn.onclick = function() {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) { // Safari
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) { // IE/Edge
                document.msExitFullscreen();
            }
        };
        
        document.body.appendChild(exitBtn);
        
        // Nettoyer quand on quitte le plein écran
        const onFullscreenChange = function() {
            if (!document.fullscreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement) {
                const btn = document.querySelector('.fullscreen-exit-btn');
                if (btn) btn.remove();
                document.removeEventListener('fullscreenchange', onFullscreenChange);
                document.removeEventListener('webkitfullscreenchange', onFullscreenChange);
                document.removeEventListener('msfullscreenchange', onFullscreenChange);
            }
        };
        
        document.addEventListener('fullscreenchange', onFullscreenChange);
        document.addEventListener('webkitfullscreenchange', onFullscreenChange);
        document.addEventListener('msfullscreenchange', onFullscreenChange);
        
    } else {
        // Quitter le plein écran
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
}

// Rendre les fonctions accessibles globalement (pour les anciens appels)
window.downloadSVG = function(btn) {
    const card = btn.closest('.svg-card');
    const container = card?.querySelector('.svg-container');
    const titleHint = card?.querySelector('.svg-title')?.textContent;
    if (container) downloadSVGAsPNG(container, titleHint);
};

window.toggleFullscreen = function(btn) {
    const card = btn.closest('.svg-card');
    const container = card?.querySelector('.svg-container');
    if (container) toggleFullscreen(container);
};

// Export
export { displayEvaluatorResults };

// Initialisation
const analysisManager = new AnalysisManager();
analysisManager.Init();
analysisManager.EventListeners();

window.analysisManager = analysisManager;
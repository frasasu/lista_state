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
            div.innerHTML =`<div onclick="analysisManager.shwowAnalysis(this)" ondblclick="analysisManager.deleteAnalysis(this.innerText)">${name}</div>`
            this.list_analysis.appendChild(div);
        }
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
                alert(`L'analyse ${name_analysis_new} sest deja faite.`);
                return;
             }

            this.core.payload.analysis[name_analysis_new] = "#Analyse effectuee";
            this.currentAnalysisName = name_analysis_new;
            this.displayAnalysis(this.currentAnalysisName);
            this.displayListAnalysis();
            await this.core.save();
            document.getElementById("modal-new-analysis").style.display="none";
            alert(`Le fichier d'analyse ${name_analysis_new} est sauvegarde avec success.`);
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
    }

    async deleteAnalysis(name){

        if(!this.core.sessionName){
            alert("Aucune session selectionnee!");
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
            alert(`L'analyse ${name} supprimee avec success!`);
    }

    async saveCurrentAnalysis(){
        if(!this.currentAnalysisName){
            alert(`Aucune analyse selectionnee!`);
            return;
        }

        const content_analysis = this.editor.value;
        this.core.payload.analysis[this.currentAnalysisName] = content_analysis;
        await this.core.save();
    }

    // analysis.js - Modifier la méthode runAnalysis
async runAnalysis() {
    const code = this.editor.value;
    const settings = this.core.getSettings();
    
    await this.saveCurrentAnalysis();
    
    const result = await pywebview.api.evaluate_dsl(code, this.core.payload);
    
    if (result.success) {
        this.core.payload = result.datas;
        
        // Appliquer les préférences d'affichage
        displayEvaluatorResults(result.messages, settings);
        
        await this.core.save();
    } else {
        displayEvaluatorResults(result.messages || [{
            type: 'error',
            content: result.errors?.join('\n') || 'Erreur inconnue'
        }], settings);
    }
}
}

// Fonction pour afficher les résultats de l'évaluateur
function displayEvaluatorResults(results) {
    const rightPanel = document.querySelector(".analysis .right");
    if (!rightPanel) return;
    
    // Vider le panneau
    rightPanel.innerHTML = "";
    
    if (!results || results.length === 0) {
        rightPanel.innerHTML = '<div class="no-results">Aucun résultat à afficher</div>';
        return;
    }
    
    // Créer un conteneur pour les résultats
    const resultsContainer = document.createElement("div");
    resultsContainer.className = "evaluator-results";
    
    // Grouper les résultats par type
    const groupedResults = {
        table: [],
        analysis: [],
        info: [],
        success: [],
        error: [],
        plot: []
    };
    
    results.forEach(result => {
        if (groupedResults[result.type]) {
            groupedResults[result.type].push(result);
        } else {
            groupedResults.info.push(result);
        }
    });
    
    // Afficher les erreurs en premier (si présentes)
    if (groupedResults.error.length > 0) {
        const errorSection = createErrorSection(groupedResults.error);
        resultsContainer.appendChild(errorSection);
    }
    
    // Afficher les tables
    if (groupedResults.table.length > 0) {
        const tableSection = createTableSection(groupedResults.table);
        resultsContainer.appendChild(tableSection);
    }
    
    // Afficher les analyses
    if (groupedResults.analysis.length > 0) {
        const analysisSection = createAnalysisSection(groupedResults.analysis);
        resultsContainer.appendChild(analysisSection);
    }
    
    // Afficher les succès et infos
    if (groupedResults.success.length > 0 || groupedResults.info.length > 0) {
        const infoSection = createInfoSection([...groupedResults.success, ...groupedResults.info]);
        resultsContainer.appendChild(infoSection);
    }
    
    rightPanel.appendChild(resultsContainer);
}

// Créer une section d'erreurs
function createErrorSection(errors) {
    const section = document.createElement("div");
    section.className = "results-section error-section";
    
    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '❌ Erreurs';
    section.appendChild(title);
    
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

// Créer une section de tables
function createTableSection(tables) {
    const section = document.createElement("div");
    section.className = "results-section table-section";
    
    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '📊 Tables';
    section.appendChild(title);
    
    tables.forEach(table => {
        const tableCard = document.createElement("div");
        tableCard.className = "table-card";
        
        const tableHeader = document.createElement("div");
        tableHeader.className = "table-header";
        tableHeader.innerHTML = `
            <span class="table-name">${table.content.name || 'Table'}</span>
            <span class="table-dimensions">${table.content.shape?.[0] || 0} lignes × ${table.content.shape?.[1] || 0} colonnes</span>
        `;
        tableCard.appendChild(tableHeader);
        
        if (table.content.preview && table.content.preview.length > 0) {
            const tableWrapper = document.createElement("div");
            tableWrapper.className = "table-wrapper";
            
            const htmlTable = document.createElement("table");
            htmlTable.className = "data-preview";
            
            // En-têtes
            const thead = document.createElement("thead");
            const headerRow = document.createElement("tr");
            
            // Ajouter les numéros de ligne
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
            
            // Corps du tableau
            const tbody = document.createElement("tbody");
            table.content.preview.forEach((row, idx) => {
                const tr = document.createElement("tr");
                
                // Numéro de ligne
                const tdIndex = document.createElement("td");
                tdIndex.className = "row-index";
                tdIndex.textContent = idx + 1;
                tr.appendChild(tdIndex);
                
                table.content.columns.forEach(col => {
                    const td = document.createElement("td");
                    let value = row[col];
                    
                    // Formater la valeur selon son type
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
            
            // Info sur le nombre total de lignes
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

// Créer une section d'analyses
function createAnalysisSection(analyses) {
    const section = document.createElement("div");
    section.className = "results-section analysis-section";
    
    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = '📈 Analyses';
    section.appendChild(title);
    
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

// Créer une section d'informations et succès
function createInfoSection(messages) {
    const section = document.createElement("div");
    section.className = "results-section info-section";
    
    const title = document.createElement("div");
    title.className = "section-title";
    title.innerHTML = 'ℹ️ Informations';
    section.appendChild(title);
    
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

// Exporter la fonction pour l'utiliser ailleurs
export { displayEvaluatorResults };

const analysisManager = new AnalysisManager();
analysisManager.Init();
analysisManager.EventListeners();

window.analysisManager = analysisManager

